from datetime import timedelta
from typing import Literal

import pytest

from models.enums.gamemode import GameModeEnum
from models.enums.wl_status import WLStatusEnum
from tests.creator import Creator


@pytest.mark.asyncio
class TestAnalyticsEndpoints:
    """Test cases for Analytics endpoints"""

    wl_statuses_mapping = {
        "W": WLStatusEnum.WIN,
        "L": WLStatusEnum.LOSE,
        "F": WLStatusEnum.FLEE,
    }

    async def create_match(
        self,
        creator: Creator,
        player_1_id: int,
        player_2_id: int,
        player_3_id: int,
        match_result: Literal["W", "L", "F"],
    ) -> int:
        return await creator.create_match(
            player_1_id=player_1_id,
            player_2_id=player_2_id,
            player_3_id=player_3_id,
            wl_status=self.wl_statuses_mapping[match_result],
        )

    async def test_teammate_analytics(self, test_client_rest, creator, dbsession):
        """Test analytics with no matches"""

        player_omega = await creator.create_player("Omega")

        A = await creator.create_player("Alfa")
        B = await creator.create_player("Beta")
        C = await creator.create_player("Charlie")
        D = await creator.create_player("Delta")

        # this is A lot of different match combinations
        matches_map = [
            # 4 wind A and B
            *(("W", A, B),) * 4,
            # 5 losses A and B
            *(("L", A, B),) * 5,
            # 1 flee for them
            ("F", A, B),
            # 8 wins for A and C
            *(("W", A, C),) * 8,
            # 6 losses for A and C
            *(("L", A, C),) * 6,
            # 3 wins for C and D
            *(("W", D, C),) * 3,
        ]

        for match in matches_map:
            await self.create_match(
                creator=creator,
                player_1_id=player_omega,
                match_result=match[0],
                player_2_id=match[1],
                player_3_id=match[2],
            )

        # 2 clash matches
        await creator.create_match(
            player_1_id=player_omega,
            wl_status=WLStatusEnum.WIN,
            player_2_id=A,
            player_3_id=B,
            game_mode=GameModeEnum.CLASH,
        )
        await creator.create_match(
            player_1_id=player_omega,
            wl_status=WLStatusEnum.LOSE,
            player_2_id=A,
            player_3_id=B,
            game_mode=GameModeEnum.CLASH,
        )

        response = await test_client_rest.get("/analytics/teammates")
        assert response.status_code == 200
        data = response.json()

        assert data["matches_total"] == len(matches_map)

        assert len(data["by_teammates"]) == 4
        assert len(data["by_team_compositions"]) == 3

        assert data["by_teammates"][0]["total_matches"] == 24
        assert data["by_team_compositions"][0]["total_matches"] == 10

        # New compound stats keys must be present and zero by default
        first_tm = data["by_teammates"][0]
        for key in ("kills", "deaths", "assists"):
            assert key in first_tm
            assert first_tm[key] == 0

        response_clash = await test_client_rest.get(
            "/analytics/teammates?game_mode=clash"
        )

        assert response_clash.status_code == 200
        data = response_clash.json()

        assert data["matches_total"] == 2

        assert len(data["by_teammates"]) == 2
        assert len(data["by_team_compositions"]) == 1

        assert data["by_teammates"][0]["total_matches"] == 2
        assert data["by_team_compositions"][0]["total_matches"] == 2
        assert data["by_team_compositions"][0]["winrate"] == 50.0

    async def test_weapon_analytics(self, test_client_rest, creator, dbsession):
        """Each match has 2 weapons (slot_a + slot_b) for player_1.
        Weapon should be aggregated whenever it was present in any slot.
        """
        player_1 = await creator.create_player("Solo")

        rifle_t = await creator.create_weapon_type("rifle_wpn")
        pistol_t = await creator.create_weapon_type("pistol_wpn")

        winfield = await creator.create_weapon("Winfield_wpn", rifle_t)
        sparks = await creator.create_weapon("Sparks_wpn", rifle_t)
        pax = await creator.create_weapon("Pax_wpn", pistol_t)

        # Helper to build a match with chosen weapons and wl_status + KDA
        async def mk(slot_a, slot_b, wl, kills=0, deaths=0, assists=0):
            mpd = await creator.create_match_player_data(
                player_id=player_1,
                slot_a_weapon_id=slot_a,
                slot_b_weapon_id=slot_b,
                kills=kills,
                deaths=deaths,
                assists=assists,
            )
            return await creator.create_match(
                player_1_id=player_1,
                player_1_match_data_id=mpd,
                wl_status=wl,
                playtime=timedelta(minutes=10),
            )

        # 3 wins with Winfield+Pax (winfield=3 matches, pax=3 matches)
        for _ in range(3):
            await mk(winfield, pax, WLStatusEnum.WIN, kills=2, deaths=0, assists=1)
        # 1 loss with Sparks+Pax (sparks=1 match, pax=4 matches)
        await mk(sparks, pax, WLStatusEnum.LOSE, kills=1, deaths=1, assists=0)
        # 1 flee with Winfield+Sparks (winfield=4 matches, sparks=2 matches)
        await mk(winfield, sparks, WLStatusEnum.FLEE, kills=0, deaths=0, assists=0)

        # match without wl_status should be excluded
        await mk(winfield, pax, None)

        await dbsession.commit()

        response = await test_client_rest.get("/analytics/weapons")
        assert response.status_code == 200
        data = response.json()

        # 5 matches with wl_status set
        assert data["matches_total"] == 5

        weapons = {w["weapon_id"]: w for w in data["by_weapons"]}
        assert weapons[winfield]["total_matches"] == 4  # 3 wins + 1 flee
        assert weapons[winfield]["wins"] == 3
        assert weapons[winfield]["flees"] == 1
        assert weapons[winfield]["losses"] == 0
        # match share denominator = matches_total
        assert weapons[winfield]["match_share"] == pytest.approx(4 / 5 * 100)

        assert weapons[sparks]["total_matches"] == 2  # 1 loss + 1 flee
        assert weapons[sparks]["losses"] == 1
        assert weapons[sparks]["flees"] == 1

        assert weapons[pax]["total_matches"] == 4  # 3 wins + 1 loss
        assert weapons[pax]["wins"] == 3
        assert weapons[pax]["losses"] == 1
        assert weapons[pax]["winrate"] == 75.0

        # K/D/A summed over matches the weapon was in (team-level, single
        # player here so equals player KDA)
        # winfield: 3 wins (k=2,d=0,a=1) + 1 flee (0,0,0) = (6,0,3)
        assert weapons[winfield]["kills"] == 6
        assert weapons[winfield]["deaths"] == 0
        assert weapons[winfield]["assists"] == 3

        # pax: 3 wins (2,0,1) + 1 loss (1,1,0) = (7,1,3)
        assert weapons[pax]["kills"] == 7
        assert weapons[pax]["deaths"] == 1
        assert weapons[pax]["assists"] == 3

        # match length present
        assert weapons[winfield]["median_playtime_seconds"] == 600

    async def test_map_analytics(self, test_client_rest, creator, dbsession):
        player_1 = await creator.create_player("Solo")
        rifle_t = await creator.create_weapon_type("rifle_map")
        pistol_t = await creator.create_weapon_type("pistol_map")
        wpn_a = await creator.create_weapon("A_map", rifle_t)
        wpn_b = await creator.create_weapon("B_map", pistol_t)

        map_lawson = await creator.create_map("Lawson")
        map_stillwater = await creator.create_map("Stillwater")

        async def mk(map_id, wl, kills=0, deaths=0, assists=0):
            mpd = await creator.create_match_player_data(
                player_id=player_1,
                slot_a_weapon_id=wpn_a,
                slot_b_weapon_id=wpn_b,
                kills=kills,
                deaths=deaths,
                assists=assists,
            )
            return await creator.create_match(
                player_1_id=player_1,
                player_1_match_data_id=mpd,
                wl_status=wl,
                map_id=map_id,
                playtime=timedelta(minutes=15),
            )

        # 3 wins on Lawson, 1 loss on Lawson
        for _ in range(3):
            await mk(map_lawson, WLStatusEnum.WIN, kills=3, deaths=0, assists=1)
        await mk(map_lawson, WLStatusEnum.LOSE, kills=1, deaths=1)

        # 2 wins, 2 losses, 1 flee on Stillwater
        for _ in range(2):
            await mk(map_stillwater, WLStatusEnum.WIN, kills=2)
        for _ in range(2):
            await mk(map_stillwater, WLStatusEnum.LOSE, deaths=1)
        await mk(map_stillwater, WLStatusEnum.FLEE)

        # 1 match without map (map_id=None)
        await mk(None, WLStatusEnum.LOSE, kills=0, deaths=1)

        await dbsession.commit()

        response = await test_client_rest.get("/analytics/maps")
        assert response.status_code == 200
        data = response.json()

        # 4 + 5 + 1 = 10 matches with wl_status set
        assert data["matches_total"] == 10
        # Three groups: Lawson, Stillwater, NULL map
        assert len(data["by_maps"]) == 3

        by_id = {m["map_id"]: m for m in data["by_maps"]}

        lawson = by_id[map_lawson]
        assert lawson["map_name"] == "Lawson"
        assert lawson["total_matches"] == 4
        assert lawson["wins"] == 3
        assert lawson["losses"] == 1
        assert lawson["winrate"] == 75.0
        assert lawson["match_share"] == pytest.approx(4 / 10 * 100)
        # KDA: 3 wins (3,0,1) + 1 loss (1,1,0) = (10,1,3)
        assert lawson["kills"] == 10
        assert lawson["deaths"] == 1
        assert lawson["assists"] == 3
        assert lawson["median_playtime_seconds"] == 900

        stillwater = by_id[map_stillwater]
        assert stillwater["total_matches"] == 5
        assert stillwater["wins"] == 2
        assert stillwater["losses"] == 2
        assert stillwater["flees"] == 1
        assert stillwater["winrate"] == 40.0

        # Null map bucket
        assert None in by_id
        assert by_id[None]["total_matches"] == 1
        assert by_id[None]["map_name"] is None

    async def test_teammate_kda(self, test_client_rest, creator, dbsession):
        """Teammate KDA should be summed from teammate's own match_player_data."""
        player_omega = await creator.create_player("Omega")
        teammate = await creator.create_player("Teammate")

        rifle_t = await creator.create_weapon_type("rifle_kda")
        wpn = await creator.create_weapon("Wpn_kda", rifle_t)

        async def mk(wl, k, d, a):
            mpd_main = await creator.create_match_player_data(
                player_id=player_omega,
                slot_a_weapon_id=wpn,
                slot_b_weapon_id=wpn,
            )
            mpd_t = await creator.create_match_player_data(
                player_id=teammate,
                slot_a_weapon_id=wpn,
                slot_b_weapon_id=wpn,
                kills=k,
                deaths=d,
                assists=a,
            )
            return await creator.create_match(
                player_1_id=player_omega,
                player_1_match_data_id=mpd_main,
                player_2_id=teammate,
                player_2_match_data_id=mpd_t,
                wl_status=wl,
            )

        await mk(WLStatusEnum.WIN, 3, 0, 1)
        await mk(WLStatusEnum.WIN, 2, 1, 0)
        await mk(WLStatusEnum.LOSE, 0, 1, 2)

        await dbsession.commit()
        response = await test_client_rest.get("/analytics/teammates")
        assert response.status_code == 200
        data = response.json()

        by_id = {t["teammate_id"]: t for t in data["by_teammates"]}
        assert by_id[teammate]["kills"] == 5
        assert by_id[teammate]["deaths"] == 2
        assert by_id[teammate]["assists"] == 3
        assert by_id[teammate]["total_matches"] == 3
