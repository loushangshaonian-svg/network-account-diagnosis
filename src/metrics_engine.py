"""
指标计算引擎
包含基础指标、特化指标、对比分析
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import math

@dataclass
class MetricResult:
    """指标计算结果"""
    name: str
    value: float
    unit: str  # "%", "次", "个", "万"
    change: float = 0.0  # 环比变化
    change_rate: float = 0.0  # 变化百分比
    status: str = "normal"  # normal/warning/critical
    benchmark: float = 0.0  # 行业基准
    gap: float = 0.0  # 与基准差距

class MetricsEngine:
    """指标计算引擎"""

    # 行业基准数据
    BENCHMARKS = {
        "xiaohongshu": {
            "engagement_rate": 0.035,  # 3.5%
            "follower_growth_rate": 0.02,  # 2%/周
            "save_rate": 0.05,  # 5%
            "comment_rate": 0.008,  # 0.8%
        },
        "douyin": {
            "engagement_rate": 0.04,
            "follower_growth_rate": 0.015,
            "completion_rate": 0.45,  # 45%
            "like_rate": 0.03,
        },
        "shipinhao": {
            "engagement_rate": 0.02,
            "forward_rate": 0.01,
            "follower_growth_rate": 0.01,
        },
        "gongzhonghao": {
            "open_rate": 0.03,  # 3%
            "share_rate": 0.005,
            "follower_growth_rate": 0.005,
        }
    }

    def calculate_basic_metrics(self, account_data: Dict) -> Dict[str, MetricResult]:
        """计算基础指标"""
        results = {}

        # 粉丝增长率
        if "prev_followers" in account_data:
            growth = account_data["followers"] - account_data["prev_followers"]
            growth_rate = growth / account_data["prev_followers"] if account_data["prev_followers"] > 0 else 0
            results["follower_growth"] = MetricResult(
                name="粉丝增长率",
                value=growth_rate * 100,
                unit="%",
                change=growth,
                change_rate=growth_rate * 100
            )

        # 互动率
        if "total_engagement" in account_data and "total_views" in account_data:
            engagement_rate = account_data["total_engagement"] / account_data["total_views"] if account_data["total_views"] > 0 else 0
            results["engagement_rate"] = MetricResult(
                name="互动率",
                value=engagement_rate * 100,
                unit="%",
                benchmark=self.BENCHMARKS.get(account_data.get("platform", ""), {}).get("engagement_rate", 0) * 100
            )
            results["engagement_rate"].gap = results["engagement_rate"].value - results["engagement_rate"].benchmark

        # 发布频次
        if "posts" in account_data and "days" in account_data:
            freq = account_data["posts"] / account_data["days"] * 7  # 每周发布
            results["posting_frequency"] = MetricResult(
                name="周发布频次",
                value=freq,
                unit="篇/周"
            )

        # 平均互动量
        if "total_engagement" in account_data and "posts" in account_data:
            avg_engagement = account_data["total_engagement"] / account_data["posts"] if account_data["posts"] > 0 else 0
            results["avg_engagement"] = MetricResult(
                name="平均互动量",
                value=avg_engagement,
                unit="次"
            )

        return results

    def calculate_platform_metrics(self, platform: str, account_data: Dict) -> Dict[str, MetricResult]:
        """计算平台特化指标"""
        results = {}

        if platform == "xiaohongshu":
            results = self._calculate_xiaohongshu_metrics(account_data)
        elif platform == "douyin":
            results = self._calculate_douyin_metrics(account_data)
        elif platform == "shipinhao":
            results = self._calculate_shipinhao_metrics(account_data)
        elif platform == "gongzhonghao":
            results = self._calculate_gongzhonghao_metrics(account_data)

        return results

    def _calculate_xiaohongshu_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """小红书特化指标"""
        results = {}

        if "saves" in data and "views" in data:
            save_rate = data["saves"] / data["views"] if data["views"] > 0 else 0
            results["save_rate"] = MetricResult(
                name="收藏率",
                value=save_rate * 100,
                unit="%",
                benchmark=self.BENCHMARKS["xiaohongshu"]["save_rate"] * 100,
                status=self._get_status(save_rate, 0.05, 0.03)
            )
            results["save_rate"].gap = results["save_rate"].value - results["save_rate"].benchmark

        if "comments" in data and "views" in data:
            comment_rate = data["comments"] / data["views"] if data["views"] > 0 else 0
            results["comment_rate"] = MetricResult(
                name="评论率",
                value=comment_rate * 100,
                unit="%",
                benchmark=self.BENCHMARKS["xiaohongshu"]["comment_rate"] * 100
            )

        return results

    def _calculate_douyin_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """抖音特化指标"""
        results = {}

        if "completion_rate" in data:
            results["completion_rate"] = MetricResult(
                name="完播率",
                value=data["completion_rate"] * 100,
                unit="%",
                benchmark=self.BENCHMARKS["douyin"]["completion_rate"] * 100,
                status=self._get_status(data["completion_rate"], 0.5, 0.35)
            )
            results["completion_rate"].gap = results["completion_rate"].value - results["completion_rate"].benchmark

        if "replays" in data and "views" in data:
            replay_rate = data["replays"] / data["views"] if data["views"] > 0 else 0
            results["replay_rate"] = MetricResult(
                name="复播率",
                value=replay_rate * 100,
                unit="%"
            )

        if "new_followers" in data and "views" in data:
            growth_rate = data["new_followers"] / data["views"] if data["views"] > 0 else 0
            results["follower_conversion"] = MetricResult(
                name="涨粉转化率",
                value=growth_rate * 100,
                unit="%"
            )

        return results

    def _calculate_shipinhao_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """视频号特化指标"""
        results = {}

        if "forwards" in data and "views" in data:
            forward_rate = data["forwards"] / data["views"] if data["views"] > 0 else 0
            results["forward_rate"] = MetricResult(
                name="转发率",
                value=forward_rate * 100,
                unit="%",
                benchmark=self.BENCHMARKS["shipinhao"]["forward_rate"] * 100
            )

        return results

    def _calculate_gongzhonghao_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """公众号特化指标"""
        results = {}

        if "reads" in data and "followers" in data:
            open_rate = data["reads"] / data["followers"] if data["followers"] > 0 else 0
            results["open_rate"] = MetricResult(
                name="打开率",
                value=open_rate * 100,
                unit="%",
                benchmark=self.BENCHMARKS["gongzhonghao"]["open_rate"] * 100,
                status=self._get_status(open_rate, 0.04, 0.02)
            )
            results["open_rate"].gap = results["open_rate"].value - results["open_rate"].benchmark

        if "shares" in data and "reads" in data:
            share_rate = data["shares"] / data["reads"] if data["reads"] > 0 else 0
            results["share_rate"] = MetricResult(
                name="分享率",
                value=share_rate * 100,
                unit="%"
            )

        return results

    def _get_status(self, value: float, good: float, warning: float) -> str:
        """根据值的状态判断"""
        if value >= good:
            return "normal"
        elif value >= warning:
            return "warning"
        return "critical"

    def compare_with_benchmark(self, metrics: Dict[str, MetricResult], platform: str) -> List[Dict]:
        """与行业基准对比"""
        comparison = []
        benchmark = self.BENCHMARKS.get(platform, {})

        for key, metric in metrics.items():
            if metric.benchmark > 0:
                diff = metric.value - metric.benchmark
                diff_pct = (diff / metric.benchmark) * 100 if metric.benchmark > 0 else 0
                comparison.append({
                    "metric": metric.name,
                    "current": metric.value,
                    "benchmark": metric.benchmark,
                    "diff": diff,
                    "diff_pct": diff_pct,
                    "status": metric.status
                })

        return comparison
