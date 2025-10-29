import pytest


@pytest.mark.asyncio
class TestWeaponTypesEndpoints:
    """Test cases for WeaponType endpoints"""

    async def test_create_weapon_type(self, test_client_rest):
        """Test creating a new weapon type"""
        response = await test_client_rest.post(
            "http://test/weapon-types", json={"name": "Rifle"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Rifle"
        assert "id" in data

    async def test_get_all_weapon_types(self, test_client_rest, creator):
        """Test getting all weapon types"""
        await creator.create_weapon_type("Rifle")
        await creator.create_weapon_type("Pistol")
        await creator.create_weapon_type("Shotgun")

        response = await test_client_rest.get("http://test/weapon-types")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [wt["name"] for wt in data]
        assert "Rifle" in names
        assert "Pistol" in names
        assert "Shotgun" in names

    async def test_get_weapon_types_pagination(self, test_client_rest, creator):
        """Test pagination for weapon types"""
        for i in range(5):
            await creator.create_weapon_type(f"Type{i}")

        response = await test_client_rest.get("http://test/weapon-types?skip=1&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_weapon_type_by_id(self, test_client_rest, creator):
        """Test getting a specific weapon type by ID"""
        weapon_type_id = await creator.create_weapon_type("Rifle")

        response = await test_client_rest.get(
            f"http://test/weapon-types/{weapon_type_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == weapon_type_id
        assert data["name"] == "Rifle"

    async def test_get_nonexistent_weapon_type(self, test_client_rest):
        """Test getting a weapon type that doesn't exist"""
        response = await test_client_rest.get("http://test/weapon-types/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_weapon_type(self, test_client_rest, creator):
        """Test updating a weapon type"""
        weapon_type_id = await creator.create_weapon_type("Rifle")

        response = await test_client_rest.patch(
            f"http://test/weapon-types/{weapon_type_id}", json={"name": "Assault Rifle"}
        )

        assert response.status_code == 202

    async def test_update_nonexistent_weapon_type(self, test_client_rest):
        """Test updating a weapon type that doesn't exist"""
        response = await test_client_rest.patch(
            "http://test/weapon-types/9999", json={"name": "NewName"}
        )

        assert response.status_code == 404

    async def test_delete_weapon_type(self, test_client_rest, creator):
        """Test deleting a weapon type"""
        weapon_type_id = await creator.create_weapon_type("ToDelete")

        response = await test_client_rest.delete(
            f"http://test/weapon-types/{weapon_type_id}"
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await test_client_rest.get(
            f"http://test/weapon-types/{weapon_type_id}"
        )
        assert get_response.status_code == 404

    async def test_delete_nonexistent_weapon_type(self, test_client_rest):
        """Test deleting a weapon type that doesn't exist"""
        response = await test_client_rest.delete("http://test/weapon-types/9999")

        assert response.status_code == 404
