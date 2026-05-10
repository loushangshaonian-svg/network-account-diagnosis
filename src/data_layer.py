"""
数据层: 账号搜索 + 数据抓取
支持关键词搜索和链接直接抓取两种模式
"""

import re
import json
import os
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class AccountData:
    """账号数据结构"""
    platform: str
    account_name: str
    account_id: str
    followers: int = 0
    following: int = 0
    posts: int = 0
    total_likes: int = 0
    total_views: int = 0
    engagement_rate: float = 0.0
    raw_data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class DataFetcher:
    """数据抓取器 - 支持多种数据源"""
    
    def __init__(self):
        self.platforms = self._load_platform_config()
        
    def _load_platform_config(self) -> Dict:
        import yaml
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "platforms.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    async def fetch_by_keyword(self, keyword: str, platforms: List[str] = None) -> List[AccountData]:
        """通过关键词搜索账号"""
        results = []
        platforms = platforms or list(self.platforms.keys())
        
        for platform in platforms:
            if platform == "xiaohongshu":
                accounts = await self._search_xiaohongshu(keyword)
            elif platform == "douyin":
                accounts = await self._search_douyin(keyword)
            elif platform == "shipinhao":
                accounts = await self._search_shipinhao(keyword)
            elif platform == "gongzhonghao":
                accounts = await self._search_gongzhonghao(keyword)
            results.extend(accounts)
        
        return results
    
    async def fetch_by_url(self, url: str) -> Optional[AccountData]:
        """通过链接直接抓取账号数据"""
        if "xiaohongshu.com" in url or "xhslink.com" in url:
            return await self._fetch_xiaohongshu(url)
        elif "douyin.com" in url:
            return await self._fetch_douyin(url)
        elif "channels.weixin.qq.com" in url or "video.qq.com" in url:
            return await self._fetch_shipinhao(url)
        elif "mp.weixin.qq.com" in url:
            return await self._fetch_gongzhonghao(url)
        return None
    
    async def _search_xiaohongshu(self, keyword: str) -> List[AccountData]:
        """搜索小红书账号 - 使用WebSearch/agent-reach能力"""
        # 实际实现会调用 agent-reach 工具搜索
        # 这里返回模拟数据用于测试
        return [AccountData(
            platform="xiaohongshu",
            account_name=keyword,
            account_id="xhs_123456",
            followers=12500,
            following=380,
            posts=156,
            total_likes=45200,
            total_views=280000,
            engagement_rate=0.032
        )]
    
    async def _search_douyin(self, keyword: str) -> List[AccountData]:
        """搜索抖音账号"""
        return [AccountData(
            platform="douyin",
            account_name=keyword,
            account_id="dy_789012",
            followers=8500,
            following=420,
            posts=89,
            total_likes=32000,
            total_views=450000,
            engagement_rate=0.028
        )]
    
    async def _search_shipinhao(self, keyword: str) -> List[AccountData]:
        """搜索视频号"""
        return [AccountData(
            platform="shipinhao",
            account_name=keyword,
            account_id="sp_345678",
            followers=6200,
            following=0,
            posts=45,
            total_likes=18000,
            total_views=120000,
            engagement_rate=0.015
        )]
    
    async def _search_gongzhonghao(self, keyword: str) -> List[AccountData]:
        """搜索公众号"""
        return [AccountData(
            platform="gongzhonghao",
            account_name=keyword,
            account_id="wx_901234",
            followers=15200,
            following=0,
            posts=234,
            total_likes=0,
            total_views=380000,
            engagement_rate=0.022
        )]
    
    async def _fetch_xiaohongshu(self, url: str) -> Optional[AccountData]:
        """抓取小红书账号数据"""
        # 通过URL提取账号ID，然后获取详细数据
        return AccountData(
            platform="xiaohongshu",
            account_name="示例账号",
            account_id="xhs_123456",
            followers=12500,
            following=380,
            posts=156,
            total_likes=45200,
            total_views=280000,
            engagement_rate=0.032
        )
    
    async def _fetch_douyin(self, url: str) -> Optional[AccountData]:
        """抓取抖音账号数据"""
        return AccountData(
            platform="douyin",
            account_name="示例账号",
            account_id="dy_789012",
            followers=8500,
            following=420,
            posts=89,
            total_likes=32000,
            total_views=450000,
            engagement_rate=0.028
        )
    
    async def _fetch_shipinhao(self, url: str) -> Optional[AccountData]:
        """抓取视频号数据"""
        return AccountData(
            platform="shipinhao",
            account_name="示例账号",
            account_id="sp_345678",
            followers=6200,
            following=0,
            posts=45,
            total_likes=18000,
            total_views=120000,
            engagement_rate=0.015
        )
    
    async def _fetch_gongzhonghao(self, url: str) -> Optional[AccountData]:
        """抓取公众号数据"""
        return AccountData(
            platform="gongzhonghao",
            account_name="示例账号",
            account_id="wx_901234",
            followers=15200,
            following=0,
            posts=234,
            total_likes=0,
            total_views=380000,
            engagement_rate=0.022
        )
