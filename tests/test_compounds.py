import pytest


@pytest.mark.asyncio
class TestCompoundsEndpoints:
    """Test cases for Compound endpoints"""

    async def test_create_compound(self, test_client_rest, creator):
        """Test creating a new compound"""
        map_id = await creator.create_map("Bayou")

        response = await test_client_rest.post(
            "http://test/compounds",
            json={
                "name": "Arden Parish",
                "map_id": map_id,
                "double_clue": True,
                "x_relative": 45.5,
                "y_relative": 32.1,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Arden Parish"
        assert data["map_id"] == map_id
        assert data["double_clue"] is True
        assert data["x_relative"] == 45.5
        assert data["y_relative"] == 32.1

    async def test_create_duplicate_compound(self, test_client_rest, creator):
        """Test creating a compound with duplicate name"""
        map_id = await creator.create_map("Bayou")
        await creator.create_compound("Arden Parish", map_id)

        response = await test_client_rest.post(
            "http://test/compounds",
            json={"name": "Arden Parish", "map_id": map_id, "double_clue": False},
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_get_all_compounds(self, test_client_rest, creator):
        """Test getting all compounds with pagination"""
        map_id = await creator.create_map("Bayou")
        await creator.create_compound("Compound1", map_id)
        await creator.create_compound("Compound2", map_id)
        await creator.create_compound("Compound3", map_id)

        response = await test_client_rest.get("http://test/compounds?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_compounds_pagination(self, test_client_rest, creator):
        """Test pagination for compounds"""
        map_id = await creator.create_map("Bayou")
        for i in range(5):
            await creator.create_compound(f"Compound{i}", map_id)

        response = await test_client_rest.get("http://test/compounds?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_compound_by_name(self, test_client_rest, creator):
        """Test getting a specific compound by name"""
        map_id = await creator.create_map("Bayou")
        await creator.create_compound("Arden Parish", map_id, True, 50.0, 60.0)

        response = await test_client_rest.get("http://test/compounds/Arden%20Parish")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Arden Parish"
        assert data["map_id"] == map_id
        assert data["double_clue"] is True
        assert data["x_relative"] == 50.0
        assert data["y_relative"] == 60.0

    async def test_get_nonexistent_compound(self, test_client_rest):
        """Test getting a compound that doesn't exist"""
        response = await test_client_rest.get("http://test/compounds/NonExistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_compound(self, test_client_rest, creator):
        """Test updating a compound"""
        map_id = await creator.create_map("Bayou")
        await creator.create_compound("Arden Parish", map_id, False, 10.0, 20.0)

        response = await test_client_rest.patch(
            "http://test/compounds/Arden%20Parish",
            json={"x_relative": 100.0, "y_relative": 200.0, "double_clue": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Arden Parish"
        assert data["x_relative"] == 100.0
        assert data["y_relative"] == 200.0
        assert data["double_clue"] is True

    async def test_update_partial_compound(self, test_client_rest, creator):
        """Test partial update of a compound"""
        map_id = await creator.create_map("Bayou")
        await creator.create_compound("Arden Parish", map_id, False, 10.0, 20.0)

        response = await test_client_rest.patch(
            "http://test/compounds/Arden%20Parish", json={"x_relative": 150.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["x_relative"] == 150.0
        assert data["y_relative"] == 20.0  # Should remain unchanged
        assert data["double_clue"] is False  # Should remain unchanged

    async def test_update_nonexistent_compound(self, test_client_rest):
        """Test updating a compound that doesn't exist"""
        response = await test_client_rest.patch(
            "http://test/compounds/NonExistent", json={"x_relative": 100.0}
        )

        assert response.status_code == 404

    async def test_delete_compound(self, test_client_rest, creator):
        """Test deleting a compound"""
        map_id = await creator.create_map("Bayou")
        await creator.create_compound("ToDelete", map_id)

        response = await test_client_rest.delete("http://test/compounds/ToDelete")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await test_client_rest.get("http://test/compounds/ToDelete")
        assert get_response.status_code == 404

    async def test_delete_nonexistent_compound(self, test_client_rest):
        """Test deleting a compound that doesn't exist"""
        response = await test_client_rest.delete("http://test/compounds/NonExistent")

        assert response.status_code == 404
