import pytest


@pytest.mark.asyncio
class TestPlayersEndpoints:
    """Test cases for Player endpoints"""

    async def test_create_player(self, test_client_rest):
        """Test creating a new player"""
        response = await test_client_rest.post(
            "http://test/players",
            json={
                "username": "Hunter123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "Hunter123"
        assert "id" in data

    async def test_create_player_without_data(self, test_client_rest):
        """Test creating a player with default values"""
        response = await test_client_rest.post("http://test/players", json={})

        assert response.status_code == 400

    async def test_get_all_players(self, test_client_rest, creator):
        """Test getting all players"""
        await creator.create_player(username="Player1")
        await creator.create_player(username="Player2")
        await creator.create_player(username="Player3")

        response = await test_client_rest.get("http://test/players")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_players_pagination(self, test_client_rest, creator):
        """Test pagination for players"""
        for i in range(5):
            await creator.create_player(username=f"Player{i}")

        response = await test_client_rest.get("http://test/players?skip=1&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_player_by_id(self, test_client_rest, creator):
        """Test getting a specific player by ID"""
        player_id = await creator.create_player(
            username="TestHunter",
        )

        response = await test_client_rest.get(f"http://test/players/{player_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == player_id
        assert data["username"] == "TestHunter"

    async def test_get_nonexistent_player(self, test_client_rest):
        """Test getting a player that doesn't exist"""
        response = await test_client_rest.get("http://test/players/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_player(self, test_client_rest, creator):
        """Test updating a player"""
        player_id = await creator.create_player(
            username="OldName",
        )

        response = await test_client_rest.patch(
            f"http://test/players/{player_id}",
            json={
                "username": "NewName",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "NewName"

    async def test_update_nonexistent_player(self, test_client_rest):
        """Test updating a player that doesn't exist"""
        response = await test_client_rest.patch(
            "http://test/players/9999", json={"verified_user": True}
        )

        assert response.status_code == 404

    async def test_delete_player(self, test_client_rest, creator):
        """Test deleting a player"""
        player_id = await creator.create_player(username="ToDelete")

        response = await test_client_rest.delete(f"http://test/players/{player_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await test_client_rest.get(f"http://test/players/{player_id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent_player(self, test_client_rest):
        """Test deleting a player that doesn't exist"""
        response = await test_client_rest.delete("http://test/players/9999")

        assert response.status_code == 404

    async def test_deactivated_player(self, test_client_rest, creator):
        """Test deactivating a player"""
        await creator.create_player(username="Player1")
        player_2_id = await creator.create_player(username="Player2")

        response = await test_client_rest.patch(
            f"http://test/players/{player_2_id}",
            json={
                "is_disabled": "true",
            },
        )

        assert response.status_code == 200

        response = await test_client_rest.get("http://test/players")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = await test_client_rest.get(
            "http://test/players?include_disabled=true"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response = await test_client_rest.patch(
            f"http://test/players/{player_2_id}",
            json={
                "is_disabled": "false",
            },
        )
        assert response.status_code == 200

        response = await test_client_rest.get("http://test/players")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
