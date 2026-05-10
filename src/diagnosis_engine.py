"""
诊断分析引擎
整合指标计算和算法趋势，生成诊断结果
修复数据结构不匹配问题
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import logging
from src.metrics_engine import MetricsEngine, MetricResult
from src.algorithm_trends import AlgorithmTrendAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class DiagnosisIssue:
    """诊断问题"""
    category: str  # 内容/运营/粉丝/互动
    severity: str  # critical/high/medium/low
    title: str
    description: str
    metric: str
    current_value: float
    target_value: float
    suggestion: str
    priority: int  # 1-5, 1最高
    expected_impact: str = ""  # 预期效果
    difficulty: str = ""  # 执行难度


@dataclass
class DiagnosisStrength:
    """账号优势"""
    category: str
    title: str
    description: str
    metric: str
    value: float


@dataclass
class DiagnosisResult:
    """诊断结果"""
    platform: str
    account_name: str
    account_id: str = ""
    followers: int = 0
    following: int = 0
    posts: int = 0
    total_likes: int = 0
    total_views: int = 0
    engagement_rate: float = 0.0
    overall_score: int = 0
    basic_metrics: Dict[str, MetricResult] = field(default_factory=dict)
    platform_metrics: Dict[str, MetricResult] = field(default_factory=dict)
    issues: List[DiagnosisIssue] = field(default_factory=list)
    strengths: List[DiagnosisStrength] = field(default_factory=list)
    algorithm_trends: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict:
        """转换为字典，保证顶级字段可直接访问"""
        result = {
            "platform": self.platform,
            "account_name": self.account_name,
            "account_id": self.account_id,
            "followers": self.followers,
            "following": self.following,
            "posts": self.posts,
            "total_likes": self.total_likes,
            "total_views": self.total_views,
            "engagement_rate": self.engagement_rate,
            "overall_score": self.overall_score,
            "summary": self.summary,
            "basic_metrics": {k: v.__dict__ for k, v in self.basic_metrics.items()},
            "platform_metrics": {k: v.__dict__ for k, v in self.platform_metrics.items()},
            "issues": [asdict(issue) for issue in self.issues],
            "strengths": [asdict(strength) for strength in self.strengths],
            "algorithm_trends": self.algorithm_trends
        }
        return result


class DiagnosisEngine:
    """诊断分析引擎"""

    def __init__(self):
        """初始化诊断引擎"""
        self.metrics_engine = MetricsEngine()
        self.trend_analyzer = AlgorithmTrendAnalyzer()
        logger.info("诊断引擎初始化完成")

    def diagnose(self, platform: str, account_name: str, account_data: Dict, historical_data: Dict = None) -> DiagnosisResult:
        """
        执行诊断
        
        Args:
            platform: 平台名称
            account_name: 账号名称
            account_data: 账号数据
            historical_data: 历史数据（可选）
            
        Returns:
            诊断结果
        """
        logger.info(f"开始诊断: {platform}/{account_name}")
        
        try:
            # 1. 计算基础指标
            logger.debug("计算基础指标...")
            basic_metrics = self.metrics_engine.calculate_basic_metrics(account_data)
            logger.debug(f"✓ 基础指标计算完成: {len(basic_metrics)} 个")

            # 2. 计算平台特化指标
            logger.debug("计算平台特化指标...")
            platform_metrics = self.metrics_engine.calculate_platform_metrics(platform, account_data)
            logger.debug(f"✓ 平台特化指标计算完成: {len(platform_metrics)} 个")

            # 3. 获取算法趋势
            logger.debug("获取算法趋势...")
            algorithm_trends = self.trend_analyzer.get_trends(platform)
            recommendations = self.trend_analyzer.generate_recommendations(platform)
            logger.debug(f"✓ 获取算法趋势: {len(recommendations)} 条建议")

            # 4. 问题识别
            logger.debug("识别问题...")
            issues = self._identify_issues(platform, basic_metrics, platform_metrics)
            logger.info(f"✓ 识别问题: {len(issues)} 个")

            # 5. 优势识别
            logger.debug("识别优势...")
            strengths = self._identify_strengths(platform, basic_metrics, platform_metrics)
            logger.debug(f"✓ 识别优势: {len(strengths)} 个")

            # 6. 计算综合评分
            logger.debug("计算综合评分...")
            overall_score = self._calculate_score(platform, basic_metrics, platform_metrics)
            logger.info(f"✓ 综合评分: {overall_score}/100")

            # 7. 生成摘要
            logger.debug("生成诊断摘要...")
            summary = self._generate_summary(account_name, platform, issues, strengths, overall_score)

            result = DiagnosisResult(
                platform=platform,
                account_name=account_name,
                account_id=account_data.get("account_id", ""),
                followers=account_data.get("followers", 0),
                following=account_data.get("following", 0),
                posts=account_data.get("posts", 0),
                total_likes=account_data.get("total_likes", 0),
                total_views=account_data.get("total_views", 0),
                engagement_rate=account_data.get("engagement_rate", 0.0),
                overall_score=overall_score,
                basic_metrics=basic_metrics,
                platform_metrics=platform_metrics,
                issues=issues,
                strengths=strengths,
                algorithm_trends=recommendations,
                summary=summary
            )
            
            logger.info(f"✓ {platform}/{account_name} 诊断完成")
            return result
            
        except Exception as e:
            logger.error(f"诊断执行异常: {str(e)}", exc_info=True)
            return DiagnosisResult(
                platform=platform,
                account_name=account_name,
                overall_score=0,
                summary=f"诊断失败: {str(e)}"
            )

    def _identify_issues(self, platform: str, basic: Dict, platform_m: Dict) -> List[DiagnosisIssue]:
        """
        识别问题
        
        Args:
            platform: 平台名称
            basic: 基础指标字典
            platform_m: 平台特化指标字典
            
        Returns:
            问题列表
        """
        issues = []
        priority = 1

        try:
            # 检查基础指标
            for key, metric in basic.items():
                if metric.status in ["warning", "critical"]:
                    severity_map = {"critical": "critical", "warning": "high", "medium": "medium"}
                    issues.append(DiagnosisIssue(
                        category="运营",
                        severity=metric.status,
                        title=f"{metric.name}表现不佳",
                        description=f"当前{metric.name}为{metric.value:.1f}{metric.unit}，低于行业基准{metric.benchmark:.1f}{metric.unit}",
                        metric=key,
                        current_value=metric.value,
                        target_value=metric.benchmark * 1.1,
                        suggestion=self._get_metric_suggestion(platform, key, metric),
                        priority=priority,
                        expected_impact="中",
                        difficulty=self._get_difficulty(key)
                    ))
                    priority += 1

            # 检查平台特化指标
            for key, metric in platform_m.items():
                if metric.status in ["warning", "critical"]:
                    issues.append(DiagnosisIssue(
                        category="平台特化",
                        severity=metric.status,
                        title=f"{metric.name}表现不佳",
                        description=f"当前{metric.name}为{metric.value:.1f}{metric.unit}，低于行业基准{metric.benchmark:.1f}{metric.unit}",
                        metric=key,
                        current_value=metric.value,
                        target_value=metric.benchmark * 1.1,
                        suggestion=self._get_platform_suggestion(platform, key, metric),
                        priority=priority,
                        expected_impact="中",
                        difficulty=self._get_difficulty(key)
                    ))
                    priority += 1

            # 按优先级排序
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            issues.sort(key=lambda x: (severity_order.get(x.severity, 4), x.priority))
            
            logger.debug(f"识别到 {len(issues)} 个问题")
            
        except Exception as e:
            logger.error(f"问题识别异常: {str(e)}", exc_info=True)

        return issues[:10]  # 最多返回10个问题

    def _identify_strengths(self, platform: str, basic: Dict, platform_m: Dict) -> List[DiagnosisStrength]:
        """
        识别优势
        
        Args:
            platform: 平台名称
            basic: 基础指标字典
            platform_m: 平台特化指标字典
            
        Returns:
            优势列表
        """
        strengths = []

        try:
            for key, metric in {**basic, **platform_m}.items():
                if metric.status == "normal" and metric.gap > 0:
                    strengths.append(DiagnosisStrength(
                        category="运营",
                        title=f"{metric.name}表现优秀",
                        description=f"高于行业基准{(metric.gap / metric.benchmark * 100):.1f}%",
                        metric=key,
                        value=metric.value
                    ))
            
            logger.debug(f"识别到 {len(strengths)} 个优势")
            
        except Exception as e:
            logger.error(f"优势识别异常: {str(e)}", exc_info=True)

        return strengths[:5]  # 最多返回5个优势

    def _calculate_score(self, platform: str, basic: Dict, platform_m: Dict) -> int:
        """
        计算综合评分
        
        Args:
            platform: 平台名称
            basic: 基础指标
            platform_m: 平台特化指标
            
        Returns:
            综合评分 (0-100)
        """
        total = 0
        count = 0

        try:
            all_metrics = {**basic, **platform_m}
            for metric in all_metrics.values():
                if hasattr(metric, 'benchmark') and metric.benchmark > 0:
                    # 评分公式: 基准为100分，每高于基准10%加5分，每低10%减5分
                    ratio = metric.value / metric.benchmark
                    if ratio >= 1:
                        score = min(100, 100 + (ratio - 1) * 50)
                    else:
                        score = max(0, 100 - (1 - ratio) * 50)
                    total += score
                    count += 1

            if count > 0:
                final_score = int(total / count)
                logger.debug(f"综合评分计算: {total}/{count} = {final_score}")
                return final_score
            else:
                logger.warning("无法计算综合评分：没有可用指标")
                return 50
            
        except Exception as e:
            logger.error(f"评分计算异常: {str(e)}", exc_info=True)
            return 50

    def _get_metric_suggestion(self, platform: str, metric_key: str, metric: MetricResult) -> str:
        """获取指标优化建议"""
        suggestions = {
            "engagement_rate": "优化内容选题，增加互动性元素，引导用户参与评论和分享",
            "follower_growth": "增加爆款内容产出，提升账号吸引力，关注平台热点话题",
            "posting_frequency": "制定稳定的内容发布计划，建立粉丝期待感",
        }
        return suggestions.get(metric_key, "优化内容质量")

    def _get_platform_suggestion(self, platform: str, metric_key: str, metric: MetricResult) -> str:
        """获取平台特化指标建议"""
        platform_suggestions = {
            "xiaohongshu": {
                "save_rate": "增加实用性和可收藏价值，提升笔记的教程类内容",
                "comment_rate": "增加互动性提问，引导用户评论互动"
            },
            "douyin": {
                "completion_rate": "优化视频开头吸引力，控制视频时长在15秒内",
                "follower_conversion": "在视频末尾增加引导关注，优化账号简介"
            },
            "shipinhao": {
                "forward_rate": "提升内容的分享价值，增加互动性"
            },
            "gongzhonghao": {
                "open_rate": "优化标题和封面设计，增加视觉冲击力",
                "share_rate": "提升内容分享价值，优化内容结构"
            }
        }
        
        platform_map = platform_suggestions.get(platform, {})
        return platform_map.get(metric_key, "参考算法趋势建议优化内容")

    def _get_difficulty(self, metric_key: str) -> str:
        """获取执行难度"""
        difficulty_map = {
            "engagement_rate": "中",
            "follower_growth": "高",
            "posting_frequency": "低",
            "save_rate": "中",
            "comment_rate": "高",
            "completion_rate": "高",
            "open_rate": "中",
            "share_rate": "高",
        }
        return difficulty_map.get(metric_key, "中")

    def _generate_summary(self, account_name: str, platform: str, issues: List, strengths: List, score: int) -> str:
        """生成诊断摘要"""
        platform_name = {
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "shipinhao": "视频号",
            "gongzhonghao": "公众号"
        }.get(platform, platform)

        summary = f"{account_name}（{platform_name}）诊断完成。综合评分{score}分，"

        if score >= 80:
            summary += "整体表现优秀！"
        elif score >= 60:
            summary += "表现中等，存在提升空间。"
        else:
            summary += "表现较弱，需要重点优化。"

        if issues:
            critical_count = sum(1 for i in issues if i.severity == 'critical')
            summary += f"发现{len(issues)}个问题，其中{critical_count}个需要立即处理。"
        
        if strengths:
            summary += f"发现{len(strengths)}个优势。"

        return summary
