import pytest


@pytest.mark.asyncio
class TestMapsEndpoints:
    """Test cases for Map endpoints"""

    async def test_create_map(self, test_client_rest):
        """Test creating a new map"""
        response = await test_client_rest.post(
            "http://test/maps", json={"name": "Bayou"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Bayou"

    async def test_create_duplicate_map(self, test_client_rest, creator):
        """Test creating a map with duplicate name"""
        await creator.create_map("DeSalle")

        response = await test_client_rest.post(
            "http://test/maps", json={"name": "DeSalle"}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_get_all_maps(self, test_client_rest, creator):
        """Test getting all maps"""
        await creator.create_map("Bayou")
        await creator.create_map("DeSalle")
        await creator.create_map("Lawson")

        response = await test_client_rest.get("http://test/maps")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        map_names = [m["name"] for m in data]
        assert "Bayou" in map_names
        assert "DeSalle" in map_names
        assert "Lawson" in map_names

    async def test_get_map_by_name(self, test_client_rest, creator):
        """Test getting a specific map by name"""
        await creator.create_map("Bayou")

        response = await test_client_rest.get("http://test/maps/Bayou")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Bayou"

    async def test_get_nonexistent_map(self, test_client_rest):
        """Test getting a map that doesn't exist"""
        response = await test_client_rest.get("http://test/maps/NonExistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_delete_map(self, test_client_rest, creator):
        """Test deleting a map"""
        await creator.create_map("ToDelete")

        response = await test_client_rest.delete("http://test/maps/ToDelete")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await test_client_rest.get("http://test/maps/ToDelete")
        assert get_response.status_code == 404

    async def test_delete_nonexistent_map(self, test_client_rest):
        """Test deleting a map that doesn't exist"""
        response = await test_client_rest.delete("http://test/maps/NonExistent")

        assert response.status_code == 404
