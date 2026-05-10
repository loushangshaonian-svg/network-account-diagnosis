"""
指标计算引擎
包含基础指标、特化指标、对比分析
完整的状态判断和日志记录
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


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
        """
        计算基础指标
        
        Args:
            account_data: 账号数据字典
            
        Returns:
            基础指标字典
        """
        results = {}
        platform = account_data.get("platform", "")

        try:
            # 粉丝增长率
            if "prev_followers" in account_data and account_data["prev_followers"] > 0:
                growth = account_data["followers"] - account_data["prev_followers"]
                growth_rate = growth / account_data["prev_followers"]
                
                benchmark = self.BENCHMARKS.get(platform, {}).get("follower_growth_rate", 0.01)
                status = self._get_status_by_value(growth_rate, benchmark, good=benchmark*1.5, warning=benchmark*0.5)
                
                results["follower_growth"] = MetricResult(
                    name="粉丝增长率",
                    value=growth_rate * 100,
                    unit="%",
                    change=growth,
                    change_rate=growth_rate * 100,
                    benchmark=benchmark * 100,
                    status=status
                )
                results["follower_growth"].gap = results["follower_growth"].value - results["follower_growth"].benchmark
                logger.debug(f"粉丝增长率: {results['follower_growth'].value:.2f}% (基准: {results['follower_growth'].benchmark:.2f}%)")

            # 互动率 = (点赞 + 评论 + 收藏) / 总曝光
            total_engagement = account_data.get("total_likes", 0) + account_data.get("comments", 0) + account_data.get("saves", 0)
            total_views = account_data.get("total_views", 0)
            
            if total_views > 0:
                engagement_rate = total_engagement / total_views
                
                benchmark = self.BENCHMARKS.get(platform, {}).get("engagement_rate", 0.03)
                status = self._get_status_by_value(engagement_rate, benchmark, good=benchmark*1.2, warning=benchmark*0.8)
                
                results["engagement_rate"] = MetricResult(
                    name="互动率",
                    value=engagement_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["engagement_rate"].gap = results["engagement_rate"].value - results["engagement_rate"].benchmark
                logger.debug(f"互动率: {results['engagement_rate'].value:.2f}% (基准: {results['engagement_rate'].benchmark:.2f}%)")

            # 发布频次 = 内容数 / 天数 * 7 (转换为周频次)
            posts = account_data.get("posts", 0)
            days = account_data.get("days", 30)  # 默认30天
            
            if posts > 0 and days > 0:
                freq = posts / days * 7  # 每周发布数
                
                results["posting_frequency"] = MetricResult(
                    name="周发布频次",
                    value=freq,
                    unit="篇/周",
                    status="normal"
                )
                logger.debug(f"发布频次: {freq:.1f}篇/周")

            # 平均互动量 = 总互动 / 内容数
            if posts > 0:
                avg_engagement = total_engagement / posts
                
                results["avg_engagement"] = MetricResult(
                    name="平均互动量",
                    value=avg_engagement,
                    unit="次",
                    status="normal"
                )
                logger.debug(f"平均互动量: {avg_engagement:.0f}次")

        except Exception as e:
            logger.error(f"基础指标计算异常: {str(e)}", exc_info=True)

        return results

    def calculate_platform_metrics(self, platform: str, account_data: Dict) -> Dict[str, MetricResult]:
        """
        计算平台特化指标
        
        Args:
            platform: 平台名称
            account_data: 账号数据
            
        Returns:
            平台特化指标字典
        """
        results = {}

        try:
            if platform == "xiaohongshu":
                results = self._calculate_xiaohongshu_metrics(account_data)
            elif platform == "douyin":
                results = self._calculate_douyin_metrics(account_data)
            elif platform == "shipinhao":
                results = self._calculate_shipinhao_metrics(account_data)
            elif platform == "gongzhonghao":
                results = self._calculate_gongzhonghao_metrics(account_data)
            else:
                logger.warning(f"未知平台: {platform}")

        except Exception as e:
            logger.error(f"平台特化指标计算失败 ({platform}): {str(e)}", exc_info=True)

        return results

    def _calculate_xiaohongshu_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """小红书特化指标"""
        results = {}

        try:
            # 收藏率
            saves = data.get("saves", 0)
            views = data.get("total_views", 0)
            
            if views > 0:
                save_rate = saves / views
                benchmark = self.BENCHMARKS["xiaohongshu"]["save_rate"]
                status = self._get_status_by_value(save_rate, benchmark, good=benchmark*1.2, warning=benchmark*0.8)
                
                results["save_rate"] = MetricResult(
                    name="收藏率",
                    value=save_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["save_rate"].gap = results["save_rate"].value - results["save_rate"].benchmark
                logger.debug(f"收藏率: {results['save_rate'].value:.2f}% (基准: {results['save_rate'].benchmark:.2f}%)")

            # 评论率
            comments = data.get("comments", 0)
            if views > 0:
                comment_rate = comments / views
                benchmark = self.BENCHMARKS["xiaohongshu"]["comment_rate"]
                status = self._get_status_by_value(comment_rate, benchmark, good=benchmark*1.2, warning=benchmark*0.8)
                
                results["comment_rate"] = MetricResult(
                    name="评论率",
                    value=comment_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["comment_rate"].gap = results["comment_rate"].value - results["comment_rate"].benchmark
                logger.debug(f"评论率: {results['comment_rate'].value:.2f}% (基准: {results['comment_rate'].benchmark:.2f}%)")

        except Exception as e:
            logger.error(f"小红书指标计算异常: {str(e)}", exc_info=True)

        return results

    def _calculate_douyin_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """抖音特化指标"""
        results = {}

        try:
            # 完播率
            completion_rate = data.get("completion_rate", 0)
            if completion_rate > 0:
                benchmark = self.BENCHMARKS["douyin"]["completion_rate"]
                status = self._get_status_by_value(completion_rate, benchmark, good=benchmark*1.1, warning=benchmark*0.7)
                
                results["completion_rate"] = MetricResult(
                    name="完播率",
                    value=completion_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["completion_rate"].gap = results["completion_rate"].value - results["completion_rate"].benchmark
                logger.debug(f"完播率: {results['completion_rate'].value:.2f}% (基准: {results['completion_rate'].benchmark:.2f}%)")

            # 复播率
            replays = data.get("replays", 0)
            views = data.get("total_views", 0)
            if views > 0:
                replay_rate = replays / views
                results["replay_rate"] = MetricResult(
                    name="复播率",
                    value=replay_rate * 100,
                    unit="%",
                    status="normal"
                )
                logger.debug(f"复播率: {results['replay_rate'].value:.2f}%")

            # 涨粉转化率
            new_followers = data.get("new_followers", 0)
            if views > 0:
                growth_rate = new_followers / views
                results["follower_conversion"] = MetricResult(
                    name="涨粉转化率",
                    value=growth_rate * 100,
                    unit="%",
                    status="normal"
                )
                logger.debug(f"涨粉转化率: {results['follower_conversion'].value:.2f}%")

        except Exception as e:
            logger.error(f"抖音指标计算异常: {str(e)}", exc_info=True)

        return results

    def _calculate_shipinhao_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """视频号特化指标"""
        results = {}

        try:
            # 转发率
            forwards = data.get("forwards", 0)
            views = data.get("total_views", 0)
            
            if views > 0:
                forward_rate = forwards / views
                benchmark = self.BENCHMARKS["shipinhao"]["forward_rate"]
                status = self._get_status_by_value(forward_rate, benchmark, good=benchmark*1.2, warning=benchmark*0.8)
                
                results["forward_rate"] = MetricResult(
                    name="转发率",
                    value=forward_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["forward_rate"].gap = results["forward_rate"].value - results["forward_rate"].benchmark
                logger.debug(f"转发率: {results['forward_rate'].value:.2f}% (基准: {results['forward_rate'].benchmark:.2f}%)")

        except Exception as e:
            logger.error(f"视频号指标计算异常: {str(e)}", exc_info=True)

        return results

    def _calculate_gongzhonghao_metrics(self, data: Dict) -> Dict[str, MetricResult]:
        """公众号特化指标"""
        results = {}

        try:
            # 打开率
            reads = data.get("reads", 0)
            followers = data.get("followers", 0)
            
            if followers > 0:
                open_rate = reads / followers
                benchmark = self.BENCHMARKS["gongzhonghao"]["open_rate"]
                status = self._get_status_by_value(open_rate, benchmark, good=benchmark*1.2, warning=benchmark*0.8)
                
                results["open_rate"] = MetricResult(
                    name="打开率",
                    value=open_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["open_rate"].gap = results["open_rate"].value - results["open_rate"].benchmark
                logger.debug(f"打开率: {results['open_rate'].value:.2f}% (基准: {results['open_rate'].benchmark:.2f}%)")

            # 分享率
            shares = data.get("shares", 0)
            if reads > 0:
                share_rate = shares / reads
                benchmark = self.BENCHMARKS["gongzhonghao"]["share_rate"]
                status = self._get_status_by_value(share_rate, benchmark, good=benchmark*1.5, warning=benchmark*0.5)
                
                results["share_rate"] = MetricResult(
                    name="分享率",
                    value=share_rate * 100,
                    unit="%",
                    benchmark=benchmark * 100,
                    status=status
                )
                results["share_rate"].gap = results["share_rate"].value - results["share_rate"].benchmark
                logger.debug(f"分享率: {results['share_rate'].value:.2f}% (基准: {results['share_rate'].benchmark:.2f}%)")

        except Exception as e:
            logger.error(f"公众号指标计算异常: {str(e)}", exc_info=True)

        return results

    def _get_status_by_value(self, 
                            value: float, 
                            benchmark: float, 
                            good: Optional[float] = None,
                            warning: Optional[float] = None) -> str:
        """
        根据值与基准的关系判断状态
        
        Args:
            value: 实际值
            benchmark: 基准值
            good: 好状态的阈值 (默认: benchmark * 1.2)
            warning: 警告状态的阈值 (默认: benchmark * 0.8)
            
        Returns:
            状态字符串: normal/warning/critical
        """
        if benchmark == 0:
            return "normal"
        
        if good is None:
            good = benchmark * 1.2
        if warning is None:
            warning = benchmark * 0.8
        
        if value >= good:
            return "normal"
        elif value >= warning:
            return "warning"
        else:
            return "critical"

    def compare_with_benchmark(self, metrics: Dict[str, MetricResult], platform: str) -> List[Dict]:
        """
        与行业基准对比
        
        Args:
            metrics: 指标字典
            platform: 平台名称
            
        Returns:
            对比结果列表
        """
        comparison = []
        benchmark = self.BENCHMARKS.get(platform, {})

        try:
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
                    logger.debug(f"对比: {metric.name} = {metric.value:.2f}{metric.unit} (基准: {metric.benchmark:.2f}{metric.unit}, 差异: {diff_pct:+.1f}%)")

        except Exception as e:
            logger.error(f"基准对比异常: {str(e)}", exc_info=True)

        return comparison
