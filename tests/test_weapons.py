import pytest
import models.enums.weapon_modifiers as mod


@pytest.mark.asyncio
class TestWeaponsEndpoints:
    """Test cases for Weapon endpoints"""

    async def test_create_weapon(self, test_client_rest, creator):
        """Test creating a new weapon"""
        weapon_type_id = await creator.create_weapon_type("Rifle")

        response = await test_client_rest.post(
            "http://test/weapons",
            json={
                "name": "Winfield M1873C Marksman",
                "weapon_type_id": weapon_type_id,
                "size": 2,
                "price": 75,
                "sights": mod.SightsEnum.MARKSMAN,
                "ammo_size": mod.AmmoSizeEnum.COMPACT,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Winfield M1873C Marksman"
        assert data["weapon_type_id"] == weapon_type_id
        assert data["size"] == 2
        assert data["price"] == 75
        assert "id" in data

    async def test_create_duplicate_weapon(self, test_client_rest, creator):
        """Test creating a weapon with duplicate name"""
        weapon_type_id = await creator.create_weapon_type("Rifle")

        await test_client_rest.post(
            "http://test/weapons",
            json={
                "name": "Winfield M1873C Marksman",
                "weapon_type_id": weapon_type_id,
                "size": 2,
                "price": 75,
                "sights": mod.SightsEnum.MARKSMAN,
                "ammo_size": mod.AmmoSizeEnum.COMPACT,
            },
        )
        response = await test_client_rest.post(
            "http://test/weapons",
            json={
                "name": "Winfield M1873C Marksman",
                "weapon_type_id": weapon_type_id,
                "size": 2,
                "price": 75,
                "sights": mod.SightsEnum.MARKSMAN,
                "ammo_size": mod.AmmoSizeEnum.COMPACT,
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_get_all_weapons(self, test_client_rest, creator):
        """Test getting all weapons"""
        weapon_type_id = await creator.create_weapon_type("Rifle")
        await creator.create_weapon("Weapon1", weapon_type_id)
        await creator.create_weapon("Weapon2", weapon_type_id)
        await creator.create_weapon("Weapon3", weapon_type_id)

        response = await test_client_rest.get("http://test/weapons")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_weapons_pagination(self, test_client_rest, creator):
        """Test pagination for weapons"""
        weapon_type_id = await creator.create_weapon_type("Rifle")
        for i in range(5):
            await creator.create_weapon(f"Weapon{i}", weapon_type_id)

        response = await test_client_rest.get("http://test/weapons?skip=1&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_weapon_by_id(self, test_client_rest, creator):
        """Test getting a specific weapon by ID"""
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon(
            "Winfield",
            weapon_type_id,
        )

        response = await test_client_rest.get(f"http://test/weapons/{weapon_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == weapon_id
        assert data["name"] == "Winfield"
        assert data["weapon_type_id"] == weapon_type_id

    async def test_get_nonexistent_weapon(self, test_client_rest):
        """Test getting a weapon that doesn't exist"""
        response = await test_client_rest.get("http://test/weapons/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_weapon(self, test_client_rest, creator):
        """Test updating a weapon"""
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon("Winfield", weapon_type_id, price=75)

        response = await test_client_rest.patch(
            f"http://test/weapons/{weapon_id}", json={"price": 100, "weight": 4.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 100
        assert data["name"] == "Winfield"  # Should remain unchanged

    async def test_update_partial_weapon(self, test_client_rest, creator):
        """Test partial update of a weapon"""
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon("Winfield", weapon_type_id, price=75)

        response = await test_client_rest.patch(
            f"http://test/weapons/{weapon_id}", json={"price": 80}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 80
        assert data["name"] == "Winfield"  # Should remain unchanged

    async def test_update_nonexistent_weapon(self, test_client_rest):
        """Test updating a weapon that doesn't exist"""
        response = await test_client_rest.patch(
            "http://test/weapons/9999", json={"price": 100}
        )

        assert response.status_code == 404

    async def test_delete_weapon(self, test_client_rest, creator):
        """Test deleting a weapon"""
        weapon_type_id = await creator.create_weapon_type("Rifle")
        weapon_id = await creator.create_weapon("ToDelete", weapon_type_id)

        response = await test_client_rest.delete(f"http://test/weapons/{weapon_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await test_client_rest.get(f"http://test/weapons/{weapon_id}")
        assert get_response.status_code == 404

    async def test_delete_nonexistent_weapon(self, test_client_rest):
        """Test deleting a weapon that doesn't exist"""
        response = await test_client_rest.delete("http://test/weapons/9999")

        assert response.status_code == 404
