import requests


class HttpClient:
    """封装 HTTP 请求，所有接口测试通过它发送请求"""

    def __init__(self, base_url: str, timeout: int = 30, logger=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logger
        self._current_test = ""   # ← 新增：当前用例名

    def _log_response(self, response: requests.Response):
        """统一记录请求和响应信息"""
        if self.logger is None:
            return

        # 带上当前用例名
        prefix = f"[{self._current_test}] " if self._current_test else ""
        
        self.logger.info(
            f"{prefix}[{response.request.method}] {response.request.url}"
        )
        self.logger.info(f"{prefix}  Status: {response.status_code}")
        resp_text = response.text[:500]
        if len(response.text) > 500:
            resp_text += "...[truncated]"
        self.logger.info(f"{prefix}  Response: {resp_text}")

    def get(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.get(url, **kwargs)
        self._log_response(resp)
        return resp

    def post(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.post(url, **kwargs)
        self._log_response(resp)
        return resp

    def put(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.put(url, **kwargs)
        self._log_response(resp)
        return resp

    def delete(self, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.delete(url, **kwargs)
        self._log_response(resp)
        return resp