import pytest


@pytest.mark.asyncio
class TestAmmoTypesEndpoints:
    """Test cases for AmmoType endpoints"""

    async def test_create_ammo_type(self, test_client_rest):
        """Test creating a new ammo type"""
        response = await test_client_rest.post(
            "http://test/ammo-types", json={"name": "Compact Ammo"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Compact Ammo"
        assert "id" in data

    async def test_get_all_ammo_types(self, test_client_rest, creator):
        """Test getting all ammo types"""
        await creator.create_ammo_type("Compact Ammo")
        await creator.create_ammo_type("Medium Ammo")
        await creator.create_ammo_type("Long Ammo")

        response = await test_client_rest.get("http://test/ammo-types")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [at["name"] for at in data]
        assert "Compact Ammo" in names
        assert "Medium Ammo" in names
        assert "Long Ammo" in names

    async def test_get_ammo_types_pagination(self, test_client_rest, creator):
        """Test pagination for ammo types"""
        for i in range(5):
            await creator.create_ammo_type(f"Ammo{i}")

        response = await test_client_rest.get("http://test/ammo-types?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_ammo_type_by_id(self, test_client_rest, creator):
        """Test getting a specific ammo type by ID"""
        ammo_type_id = await creator.create_ammo_type("Compact Ammo")

        response = await test_client_rest.get(f"http://test/ammo-types/{ammo_type_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ammo_type_id
        assert data["name"] == "Compact Ammo"

    async def test_get_nonexistent_ammo_type(self, test_client_rest):
        """Test getting an ammo type that doesn't exist"""
        response = await test_client_rest.get("http://test/ammo-types/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_ammo_type(self, test_client_rest, creator):
        """Test updating an ammo type"""
        ammo_type_id = await creator.create_ammo_type("Compact Ammo")

        response = await test_client_rest.patch(
            f"http://test/ammo-types/{ammo_type_id}",
            json={"name": "Compact Ammunition"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Compact Ammunition"
        assert data["id"] == ammo_type_id

    async def test_update_nonexistent_ammo_type(self, test_client_rest):
        """Test updating an ammo type that doesn't exist"""
        response = await test_client_rest.patch(
            "http://test/ammo-types/9999", json={"name": "NewName"}
        )

        assert response.status_code == 404

    async def test_delete_ammo_type(self, test_client_rest, creator):
        """Test deleting an ammo type"""
        ammo_type_id = await creator.create_ammo_type("ToDelete")

        response = await test_client_rest.delete(
            f"http://test/ammo-types/{ammo_type_id}"
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await test_client_rest.get(
            f"http://test/ammo-types/{ammo_type_id}"
        )
        assert get_response.status_code == 404

    async def test_delete_nonexistent_ammo_type(self, test_client_rest):
        """Test deleting an ammo type that doesn't exist"""
        response = await test_client_rest.delete("http://test/ammo-types/9999")

        assert response.status_code == 404
