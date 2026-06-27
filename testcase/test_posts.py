import pytest
import allure  # 新增：导入 allure
import yaml
from pathlib import Path
import random

def load_test_data(filename: str):
    """加载 data/ 目录下的 YAML 测试数据文件"""
    data_path = Path(__file__).parent.parent / "data" / filename
    with open(data_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    

@pytest.fixture
def created_post_id(client):
    """
    前置：创建一条帖子，返回帖子 ID
    后置：删除这条帖子
    """
    # ====== SETUP：创建帖子 ======
    payload = load_test_data("posts_data.yaml")["fixture_payload"]
    resp = client.post("/posts", json=payload)
    assert resp.status_code == 201
    post_id = resp.json()["id"]
    print(f"\n✅ [SETUP] 创建帖子成功，ID = {post_id}")
    
    yield post_id   # ← 把 post_id 传给用例
    
    # ====== TEARDOWN：删除帖子 ======
    delete_resp = client.delete(f"/posts/{post_id}")
    print(f"\n🗑️ [TEARDOWN] 删除帖子 ID = {post_id}，状态码 = {delete_resp.status_code}")


class TestPosts:
    """帖子模块接口测试"""

    @allure.tag("smoke")       # 新增：给 allure 报告加标签
    @pytest.mark.smoke
    def test_get_all_posts(self, client):
        """正向：获取所有帖子"""
        resp = client.get("/posts")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    @allure.tag("smoke")       # 新增：给 allure 报告加标签
    @pytest.mark.smoke
    def test_get_single_post(self, client):
        """正向：获取单个帖子"""
        resp = client.get("/posts/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert "title" in data
        assert "body" in data

    def test_get_post_not_found(self, client):
        """异常：访问不存在的帖子"""
        resp = client.get("/posts/99999")
        assert resp.status_code == 404

    @pytest.mark.parametrize("post_id", load_test_data("posts_data.yaml")["post_ids"])  # 数据外置
    def test_get_multiple_posts(self, client, post_id):
        """数据驱动：批量验证多个帖子 ID 都能查到"""
        resp = client.get(f"/posts/{post_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == post_id

    def test_create_post(self, client):
        """正向：创建帖子"""
        payload = load_test_data("posts_data.yaml")["create_payload"]
        resp = client.post("/posts", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["id"] is not None
    
    def test_post_lifecycle(self, client, created_post_id):
        """场景：创建帖子 → 验证能查到 → 测试结束后自动删除"""
        # created_post_id 已经是创建好的帖子 ID
        resp = client.get(f"/posts/{created_post_id}")
        assert resp.status_code == 200
        # 用例结束，fixture 自动执行 teardown 删除帖子

    def test_maybe_fail(self, client):
        """模拟偶发失败：50% 概率断言失败"""
        resp = client.get("/posts/1")
        assert resp.status_code == 200
        if random.random() > 0.5:
            assert 1 == 2  # 故意失败
