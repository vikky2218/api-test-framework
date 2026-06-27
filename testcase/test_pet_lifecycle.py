import pytest
import allure


class TestPetLifecycle:
    """宠物商店全链路测试：创建 → 查询 → 更新 → 删除"""

    @allure.tag("smoke", "lifecycle")
    @pytest.mark.smoke
    def test_pet_crud_flow(self, client):
        """
        场景：完整宠物生命周期
        1. 创建一只宠物，拿到 ID
        2. 用这个 ID 查询，验证创建成功
        3. 更新宠物状态，验证状态变化
        4. 删除宠物，验证删除成功
        """
        # ========== 1. 创建宠物 ==========
        create_payload = {
            "id": 0,          # 传 0 表示由服务端自动生成 ID
            "name": "doggo",
            "status": "available"
        }
        create_resp = client.post("/pet", json=create_payload)
        assert create_resp.status_code == 200
        pet_id = create_resp.json()["id"]
        assert pet_id > 0, "创建后未返回有效 ID"

        # ========== 2. 查询宠物 ==========
        get_resp = client.get(f"/pet/{pet_id}")
        assert get_resp.status_code == 200
        pet_data = get_resp.json()
        assert pet_data["name"] == "doggo"
        assert pet_data["status"] == "available"

        # ========== 3. 更新宠物状态 ==========
        update_payload = {
            "id": pet_id,
            "name": "doggo",
            "status": "sold"        # 改为已售出
        }
        update_resp = client.put("/pet", json=update_payload)
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "sold"

        # ========== 4. 再次查询，确认状态真的变了 ==========
        get_again = client.get(f"/pet/{pet_id}")
        assert get_again.status_code == 200
        assert get_again.json()["status"] == "sold"

        # ========== 5. 删除宠物 ==========
        delete_resp = client.delete(f"/pet/{pet_id}")
        assert delete_resp.status_code == 200

        # ========== 6. 验证删除后再查返回 404 ==========
        get_deleted = client.get(f"/pet/{pet_id}")
        assert get_deleted.status_code == 404