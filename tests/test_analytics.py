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
