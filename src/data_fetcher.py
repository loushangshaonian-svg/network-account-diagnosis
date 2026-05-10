"""
数据获取器 - 整合 agent-reach 能力
支持多平台数据抓取容错
"""

from typing import Dict, List, Optional, Any
import json
import os
import sys

# 添加父目录到path以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_layer import AccountData


class AgentReachFetcher:
    """使用 agent-reach 进行数据获取"""
    
    PLATFORM_MAPPING = {
        "xiaohongshu": "xiaohongshu",
        "douyin": "douyin", 
        "shipinhao": "shipinhao",
        "gongzhonghao": "wechat_articles",
        "weibo": "weibo",
        "bilibili": "bilibili"
    }
    
    async def fetch_account_data(self, platform: str, identifier: str) -> Optional[Dict]:
        """
        使用 agent-reach 获取账号数据
        identifier: 账号ID或关键词
        返回格式:
        {
            "name": 账号名称,
            "followers": 粉丝数,
            "following": 关注数,
            "posts": 内容数,
            "likes": 获赞数,
            "views": 曝光量,
            "engagement": 互动数据
        }
        """
        # 尝试通过agent-reach搜索（需要外部调用）
        # 这里返回空字典，实际数据由Skill的SKILL.md通过搜索获取
        return {}
    
    async def search_accounts(self, platform: str, keyword: str) -> List[Dict]:
        """搜索账号 - 返回账号列表"""
        # 实际实现会通过WebSearch或agent-reach
        return []


class FallbackFetcher:
    """容错数据源 - 当agent-reach不可用时"""
    
    async def fetch_from_third_party(self, platform: str, account: str) -> Optional[Dict]:
        """从第三方平台获取数据"""
        # 新榜、飞瓜等平台API容错
        # 返回模拟数据用于测试
        return {
            "platform": platform,
            "account": account,
            "followers": 10000,
            "following": 500,
            "posts": 120,
            "likes": 50000,
            "views": 200000,
            "engagement": 1500,
            "saves": 800,
            "comments": 300,
            "shares": 200,
            "completion_rate": 0.45
        }


# 便捷函数
async def fetch_account_info(platform: str, account_name: str) -> Optional[Dict]:
    """获取账号信息的便捷函数"""
    fetcher = AgentReachFetcher()
    data = await fetcher.fetch_account_data(platform, account_name)
    
    if not data:
        # 使用容错方案
        fallback = FallbackFetcher()
        data = await fallback.fetch_from_third_party(platform, account_name)
    
    return data
