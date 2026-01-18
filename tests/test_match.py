import datetime
from datetime import date, timedelta

import pytest
import sqlalchemy as sa

import models.db_models as m
from models.enums.gamemode import GameModeEnum


@pytest.mark.asyncio
class TestMatchEndpoints:
    """Test cases for Match endpoints"""

    async def test_create_full_steps(self, test_client_rest, creator, dbsession):
        """Test creating a basic match"""
        # Create prerequisites
        player_1_id = await creator.create_player(username="Major")
        player_2_id = await creator.create_player(username="Sociophile")
        player_3_id = await creator.create_player(username="N0X")
        rifle_type_id = await creator.create_weapon_type("Rifle")
        pistol_type_id = await creator.create_weapon_type("Pistol")
        winfield_id = await creator.create_weapon("Winfield", rifle_type_id)
        pax_id = await creator.create_weapon("Pax", pistol_type_id)
        fmj_ammo_id = await creator.create_ammo_type("FMJ Ammo")

        match_date = datetime.date(2021, 5, 15)
        # Create match
        response = await test_client_rest.post(
            "http://test/matches",
            json={
                "date": match_date.isoformat(),
                "player_1_id": player_1_id,
                "player_2_id": player_2_id,
                "player_3_id": player_3_id,
                "slot_a_weapon_id": winfield_id,
                "slot_b_weapon_id": pax_id,
                "slot_b_ammo_a_id": fmj_ammo_id,
                "slot_b_dual_wielding": True,
                "game_mode": "clash",
            },
        )

        assert response.status_code == 201
        data = response.json()
        match_id = data["match_id"]
        assert match_id is not None

        match_query = sa.select(
            m.Match.player_2_match_data_id,
            m.Match.player_3_match_data_id,
            m.Match.wl_status,
            m.Match.date,
            m.Match.playtime,
            m.Match.game_mode,
        )

        match_data = (await dbsession.execute(match_query)).mappings().fetchone()

        assert match_data == {
            "player_2_match_data_id": None,
            "player_3_match_data_id": None,
            "wl_status": None,
            "date": match_date,
            "playtime": None,
            "game_mode": GameModeEnum.CLASH,
        }
        match_player_query = sa.select(
            m.MatchPlayerData.player_id,
            m.MatchPlayerData.slot_a_weapon_id,
            m.MatchPlayerData.slot_a_ammo_a_id,
            m.MatchPlayerData.slot_a_ammo_b_id,
            m.MatchPlayerData.slot_a_dual_wielding,
            m.MatchPlayerData.slot_b_weapon_id,
            m.MatchPlayerData.slot_b_ammo_a_id,
            m.MatchPlayerData.slot_b_ammo_b_id,
            m.MatchPlayerData.slot_b_dual_wielding,
            m.MatchPlayerData.kills,
            m.MatchPlayerData.deaths,
            m.MatchPlayerData.assists,
            m.MatchPlayerData.bounty,
        )
        match_player_data = (
            (await dbsession.execute(match_player_query)).mappings().fetchone()
        )
        expected_match_player_result = {
            "assists": 0,
            "bounty": 0,
            "deaths": 0,
            "kills": 0,
            "player_id": player_1_id,
            "slot_a_ammo_a_id": None,
            "slot_a_ammo_b_id": None,
            "slot_a_dual_wielding": False,
            "slot_a_weapon_id": winfield_id,
            "slot_b_ammo_a_id": fmj_ammo_id,
            "slot_b_ammo_b_id": None,
            "slot_b_dual_wielding": True,
            "slot_b_weapon_id": pax_id,
        }
        assert match_player_data == expected_match_player_result

        map_id = await creator.create_map("Lawson Delta")
        compound_1_id = await creator.create_compound("Fort Carmick", map_id)
        compound_2_id = await creator.create_compound("Nickols Prison", map_id)
        playtime = timedelta(minutes=15, seconds=44)

        response = await test_client_rest.post(
            "http://test/matches/results",
            json={
                "match_id": match_id,
                "wl_status": "win",
                "kills_total": 4,
                "kills": 1,
                "assists": 1,
                "deaths": 2,
                "bounty": 656,
                "playtime": playtime.total_seconds(),
                "map_id": map_id,
                "fights_places_ids": [compound_1_id, compound_2_id],
            },
        )

        playtime = await dbsession.scalar(
            sa.select(m.Match.playtime).where(m.Match.id == match_id)
        )

        assert playtime == playtime

        assert response.status_code == 201
        data = response.json()
        assert data["match_id"] == match_id

        match_player_data = (
            (await dbsession.execute(match_player_query)).mappings().fetchone()
        )

        expected_match_player_result.update(
            {
                "assists": 1,
                "bounty": 656,
                "deaths": 2,
                "kills": 1,
            }
        )

        assert match_player_data == expected_match_player_result

        fight_location_results = (
            (
                await dbsession.execute(
                    sa.select(m.M2MFightLocations.compound_id)
                    .where(m.M2MFightLocations.match_id == match_id)
                    .order_by(m.M2MFightLocations.fight_ordering.asc())
                )
            )
            .scalars()
            .all()
        )

        assert fight_location_results == [compound_1_id, compound_2_id]

    @pytest.mark.skip
    async def test_create_match_with_multiple_players(self, test_client, creator):
        """Test creating a match with multiple players"""

    @pytest.mark.skip
    async def test_create_match_without_player_1_data(self, test_client, creator):
        """Test that creating match without player_1_data fails"""
        player_id = await creator.create_player(username="Player1")

        response = await test_client.post(
            "http://test/matches",
            json={
                "player_1_id": player_id,
                "fights_places_ids": [],
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_get_all_matches(self, test_client_rest, creator):
        """Test getting all matches"""
        # Create prerequisites
        (
            compound_id,
            map_id,
            match_1_id,
            match_2_id,
            player_id,
        ) = await self.create_matches(creator)

        # Get all matches
        response = await test_client_rest.get("http://test/matches")

        assert response.status_code == 200
        data = response.json()

        assert data["total_results"] == 2
        data = data["data"]
        assert len(data) == 2

        first_match, second_match = data

        assert first_match["id"] == match_1_id
        assert first_match["map_id"] == map_id
        assert first_match["fights_places_ids"] == [compound_id]
        assert first_match["player_1_id"] == player_id
        assert first_match["kills_total"] == 5
        assert first_match["playtime"] == timedelta(minutes=15, seconds=44).seconds

        assert second_match["map_id"] == map_id
        assert second_match["id"] == match_2_id
        assert second_match["kills_total"] == 8
        assert second_match["playtime"] == timedelta(minutes=20, seconds=1).seconds

    async def test_ordering(self, test_client_rest, creator):
        await self.create_matches(creator)

        response = await test_client_rest.get("http://test/matches?ordering=desc")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        first_match, second_match = data

        assert datetime.date.fromisoformat(
            first_match["date"]
        ) > datetime.date.fromisoformat(second_match["date"])

        response = await test_client_rest.get("http://test/matches?ordering=asc")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2

        first_match, second_match = data

        assert datetime.date.fromisoformat(
            first_match["date"]
        ) < datetime.date.fromisoformat(second_match["date"])

    async def create_matches(self, creator):
        player_id = await creator.create_player(username="Player1")
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon("Winfield", weapon_type_id)
        player_data_id_m1 = await creator.create_match_player_data(
            player_id=player_id,
            slot_a_weapon_id=weapon_id,
            slot_b_weapon_id=weapon_id,
        )
        player_data_id_m2 = await creator.create_match_player_data(
            player_id=player_id,
            slot_a_weapon_id=weapon_id,
            slot_b_weapon_id=weapon_id,
        )
        map_id = await creator.create_map()
        compound_id = await creator.create_compound(map_id=map_id)
        # Create matches
        match_1_id = await creator.create_match(
            match_date=date(2025, 1, 20),
            player_1_id=player_id,
            player_1_match_data_id=player_data_id_m1,
            kills_total=5,
            map_id=map_id,
            playtime=timedelta(minutes=15, seconds=44),
            game_mode=GameModeEnum.HUNT,
        )
        match_2_id = await creator.create_match(
            match_date=date(2025, 1, 10),
            player_1_id=player_id,
            player_1_match_data_id=player_data_id_m2,
            kills_total=8,
            map_id=map_id,
            playtime=timedelta(minutes=20, seconds=1),
            game_mode=GameModeEnum.CLASH,
        )
        await creator.create_fight_location(
            match_id=match_1_id,
            compound_id=compound_id,
        )
        await creator.create_fight_location(
            match_id=match_2_id,
            compound_id=compound_id,
        )
        return compound_id, map_id, match_1_id, match_2_id, player_id

    @pytest.mark.skip
    async def test_get_match_by_id(self, test_client, creator):
        """Test getting a specific match by ID"""
        # Create match
        player_id = await creator.create_player(username="Player1")
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon("Winfield", weapon_type_id)

        player_data_id = await creator.create_match_player_data(
            player_id=player_id,
            slot_a_weapon_id=weapon_id,
            slot_b_weapon_id=weapon_id,
        )

        match_id = await creator.create_match(
            player_1_id=player_id,
            player_1_match_data=player_data_id,
            kills_total=10,
        )

        # Get match
        response = await test_client.get(f"http://test/matches/{match_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == match_id
        assert data["player_1_id"] == player_id
        assert data["kills_total"] == 10

    async def test_get_nonexistent_match(self, test_client_rest):
        """Test getting a match that doesn't exist"""
        response = await test_client_rest.get("http://test/matches/specific/9999")

        assert response.status_code == 404

    async def test_add_results_to_nonexistent_match(self, test_client_rest):
        """Test adding results to a match that doesn't exist"""
        response = await test_client_rest.post(
            "http://test/matches/results",
            json={
                "match_id": 9999,
                "wl_status": "win",
                "kills_total": 10,
                "kills": 5,
                "assists": 3,
                "deaths": 1,
                "bounty": 500,
                "playtime": "PT20M",
                "map_id": 1,
                "fights_places_ids": [],
            },
        )

        assert response.status_code == 404

    async def test_delete_match(self, test_client_rest, creator, dbsession):
        """Test getting all matches"""
        # Create prerequisites
        (
            compound_id,
            map_id,
            match_1_id,
            match_2_id,
            player_id,
        ) = await self.create_matches(creator)

        data = await dbsession.scalar(sa.select(m.Match.id))
        assert data
        data = await dbsession.scalar(sa.select(m.MatchPlayerData.id))
        assert data
        data = await dbsession.scalar(sa.select(m.M2MFightLocations.match_id))
        assert data

        await test_client_rest.delete(f"http://test/matches/{match_1_id}")
        await test_client_rest.delete(f"http://test/matches/{match_2_id}")

        data = await dbsession.scalar(sa.select(m.Match.id))
        assert not data
        data = await dbsession.scalar(sa.select(m.MatchPlayerData.id))
        assert not data
        data = await dbsession.scalar(sa.select(m.M2MFightLocations.match_id))
        assert not data


@pytest.mark.asyncio
class TestMatchUpdateEndpoint:
    """Test cases for PATCH /matches/{match_id} endpoint"""

    async def test_update_match_basic(self, test_client_rest, creator, dbsession):
        """Test updating match with corrected data"""
        # Create prerequisites
        map_id = await creator.create_map("Bayou")
        player_1_id = await creator.create_player(username="Player1")
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_1_id = await creator.create_weapon("Winfield", weapon_type_id)
        weapon_2_id = await creator.create_weapon("Vetterli", weapon_type_id)
        ammo_id = await creator.create_ammo_type("Compact Ammo")

        compound_1 = await creator.create_compound("Compound1", map_id)
        compound_2 = await creator.create_compound("Compound2", map_id)
        compound_3 = await creator.create_compound("Compound3", map_id)

        # Create initial match with player data
        player_data_id = await creator.create_match_player_data(
            player_id=player_1_id,
            slot_a_weapon_id=weapon_1_id,
            slot_b_weapon_id=weapon_2_id,
            slot_a_ammo_a_id=ammo_id,
            kills=5,
            assists=2,
            deaths=1,
            bounty=250,
        )

        match_id = await creator.create_match(
            player_1_id=player_1_id,
            player_1_match_data_id=player_data_id,
            wl_status="win",
            kills_total=5,
        )

        # Add initial fight locations
        await creator.create_fight_location(match_id, compound_1, 0)
        await creator.create_fight_location(match_id, compound_2, 1)

        # Update the match with corrected data
        update_data = {
            "date": "2025-11-10",
            "player_1_id": player_1_id,
            "player_2_id": None,
            "player_3_id": None,
            "slot_a_weapon_id": weapon_2_id,  # Changed weapon
            "slot_a_ammo_a_id": ammo_id,
            "slot_a_ammo_b_id": None,
            "slot_a_dual_wielding": False,
            "slot_b_weapon_id": weapon_1_id,  # Swapped weapons
            "slot_b_ammo_a_id": None,
            "slot_b_ammo_b_id": None,
            "slot_b_dual_wielding": False,
            "wl_status": "lose",  # Changed from win to lose
            "kills_total": 8,  # Updated kills
            "kills": 8,
            "assists": 3,  # Updated assists
            "deaths": 2,  # Updated deaths
            "bounty": 300,  # Updated bounty
            "playtime": "PT25M",  # 25 minutes in ISO 8601 format
            "map_id": map_id,
            "fights_places_ids": [
                compound_1,
                compound_2,
                compound_3,
            ],  # Added third location
        }

        response = await test_client_rest.patch(
            f"http://test/matches/{match_id}", json=update_data
        )
        if response.status_code == 422:
            print(response.text)
        assert response.status_code == 200
        data = response.json()
        assert data["match_id"] == match_id

        # Verify the match was updated
        get_response = await test_client_rest.get(
            f"http://test/matches/specific/{match_id}"
        )
        assert get_response.status_code == 200
        match_data = get_response.json()["data"][0]

        # Verify match fields were updated
        assert match_data["wl_status"] == "lose"
        assert match_data["kills_total"] == 8

        player_data = match_data["player_1_data"]

        assert player_data["slot_a_weapon_id"] == weapon_2_id
        assert player_data["slot_b_weapon_id"] == weapon_1_id
        assert player_data["kills"] == 8
        assert player_data["assists"] == 3
        assert player_data["deaths"] == 2

        fight_locations = match_data["fights_places_ids"]

        assert fight_locations[0] == compound_1
        assert fight_locations[1] == compound_2
        assert fight_locations[2] == compound_3

    async def test_update_nonexistent_match(self, test_client_rest, creator):
        """Test updating a match that doesn't exist returns 404"""
        # Create prerequisites for valid data
        player_id = await creator.create_player(username="Player1")
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon("Winfield", weapon_type_id)
        ammo_id = await creator.create_ammo_type("Compact Ammo")

        # Try to update non-existent match
        update_data = {
            "date": "2025-11-10",
            "player_1_id": player_id,
            "player_2_id": None,
            "player_3_id": None,
            "slot_a_weapon_id": weapon_id,
            "slot_a_ammo_a_id": ammo_id,
            "slot_a_ammo_b_id": None,
            "slot_a_dual_wielding": False,
            "slot_b_weapon_id": weapon_id,
            "slot_b_ammo_a_id": None,
            "slot_b_ammo_b_id": None,
            "slot_b_dual_wielding": False,
            "wl_status": "win",
            "kills_total": 5,
            "kills": 5,
            "assists": 2,
            "deaths": 1,
            "bounty": 250,
            "playtime": "PT20M",
            "map_id": 1,
            "fights_places_ids": [],
        }

        response = await test_client_rest.patch(
            "http://test/matches/9999",
            json=update_data,  # Non-existent match ID
        )

        assert response.status_code == 404
