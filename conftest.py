import yaml
import pytest
import allure
from pathlib import Path
from datetime import datetime
from loguru import logger
from common.http_client import HttpClient

# 全局变量，存储“最终通过但经历过重试”的用例名
_rerun_tests = set()


def load_config():
    """加载 config.yaml 配置文件"""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def config():
    """全局配置 fixture，整个测试会话只加载一次"""
    return load_config()


@pytest.fixture(scope="session")
def _raw_client(config):
    """创建原始的 HTTP 客户端，配置日志文件（内部使用）"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"api_test_{timestamp}.log"

    # 移除 loguru 默认的终端输出，只写文件
    logger.remove()
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO",
        encoding="utf-8"
    )

    return HttpClient(
        base_url=config["base_url"],
        timeout=config.get("timeout", 30),
        logger=logger
    )


@pytest.fixture
def client(_raw_client, request):
    """
    每个用例执行前，注入当前用例名。
    如果当前是重试，日志里会标记 ⚠️RERUN。
    """
    current_test = request.node.name
    is_rerun = (
        hasattr(request.node, "execution_count")
        and request.node.execution_count > 1
    )

    if is_rerun:
        current_test = f"⚠️RERUN[{request.node.execution_count}] {current_test}"

    _raw_client._current_test = current_test
    return _raw_client


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    收集“最终通过但经历过重试”的用例，打上 unstable 标签。
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        exec_count = getattr(item, "execution_count", 1)
        # 只关注：经历过重试 且 最终通过 的用例
        if exec_count > 1 and report.passed:
            original = getattr(item, "original_name", None) or item.name
            _rerun_tests.add(original)
            allure.dynamic.tag("unstable")


def pytest_sessionfinish(session):
    """测试结束后，打印不稳定用例清单（最终通过但经历过重试）"""
    if _rerun_tests:
        print("\n" + "=" * 50)
        print(f"⚠️  不稳定用例（最终通过，但经历过重试）：{len(_rerun_tests)} 条")
        for name in sorted(_rerun_tests):
            print(f"  - {name}")
        print("❗ 请人工检查以上用例，是否存在偶发性缺陷")
        print("=" * 50)