"""
测试诊断系统的完整流程
验证所有模块的集成
"""

import asyncio
import logging
from src.main import diagnose_account

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_diagnosis():
    """测试诊断功能"""
    
    print("=" * 80)
    print("网络账号运营诊断专家 - 系统测试")
    print("=" * 80)
    print()
    
    # 测试用例1: 单品牌多平台诊断
    print("\n【测试1】单品牌多平台诊断")
    print("-" * 80)
    report1 = await diagnose_account("予茉女装")
    print(report1)
    print("\n" + "=" * 80 + "\n")
    
    # 测试用例2: 指定平台诊断
    print("\n【测试2】指定平台诊断 (小红书 + 抖音)")
    print("-" * 80)
    report2 = await diagnose_account(
        "予茉女装",
        platforms=["xiaohongshu", "douyin"]
    )
    print(report2)
    print("\n" + "=" * 80 + "\n")
    
    # 测试用例3: URL直接诊断
    print("\n【测试3】URL直接诊断")
    print("-" * 80)
    url = "https://www.xiaohongshu.com/user/profile/000000"
    report3 = await diagnose_account(url, is_url=True)
    print(report3)
    print("\n" + "=" * 80 + "\n")
    
    print("✓ 所有测试完成！")


if __name__ == "__main__":
    asyncio.run(test_diagnosis())
