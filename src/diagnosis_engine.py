"""
诊断分析引擎
整合指标计算和算法趋势，生成诊断结果
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from src.metrics_engine import MetricsEngine, MetricResult
from src.algorithm_trends import AlgorithmTrendAnalyzer

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
    overall_score: int  # 0-100
    basic_metrics: Dict[str, MetricResult]
    platform_metrics: Dict[str, MetricResult]
    issues: List[DiagnosisIssue]
    strengths: List[DiagnosisStrength]
    algorithm_trends: List[str]
    summary: str

    def to_dict(self) -> Dict:
        result = asdict(self)
        # 转换 MetricResult 为字典
        result["basic_metrics"] = {k: v.__dict__ for k, v in self.basic_metrics.items()}
        result["platform_metrics"] = {k: v.__dict__ for k, v in self.platform_metrics.items()}
        return result

class DiagnosisEngine:
    """诊断分析引擎"""

    def __init__(self):
        self.metrics_engine = MetricsEngine()
        self.trend_analyzer = AlgorithmTrendAnalyzer()

    def diagnose(self, platform: str, account_name: str, account_data: Dict, historical_data: Dict = None) -> DiagnosisResult:
        """执行诊断"""
        # 1. 计算基础指标
        basic_metrics = self.metrics_engine.calculate_basic_metrics(account_data)

        # 2. 计算平台特化指标
        platform_metrics = self.metrics_engine.calculate_platform_metrics(platform, account_data)

        # 3. 获取算法趋势
        algorithm_trends = self.trend_analyzer.get_trends(platform)
        recommendations = self.trend_analyzer.generate_recommendations(platform)

        # 4. 问题识别
        issues = self._identify_issues(platform, basic_metrics, platform_metrics)

        # 5. 优势识别
        strengths = self._identify_strengths(platform, basic_metrics, platform_metrics)

        # 6. 计算综合评分
        overall_score = self._calculate_score(platform, basic_metrics, platform_metrics)

        # 7. 生成摘要
        summary = self._generate_summary(account_name, platform, issues, strengths, overall_score)

        return DiagnosisResult(
            platform=platform,
            account_name=account_name,
            overall_score=overall_score,
            basic_metrics=basic_metrics,
            platform_metrics=platform_metrics,
            issues=issues,
            strengths=strengths,
            algorithm_trends=recommendations,
            summary=summary
        )

    def _identify_issues(self, platform: str, basic: Dict, platform_m: Dict) -> List[DiagnosisIssue]:
        """识别问题"""
        issues = []
        priority = 1

        # 检查基础指标
        for key, metric in basic.items():
            if metric.status in ["warning", "critical"]:
                severity_map = {"critical": "高", "high": "中", "medium": "低"}
                issues.append(DiagnosisIssue(
                    category="运营",
                    severity=metric.status,
                    title=f"基础指标{metric.name}低于基准",
                    description=f"当前{metric.name}为{metric.value:.1f}{metric.unit}，低于行业基准{metric.benchmark:.1f}{metric.unit}",
                    metric=key,
                    current_value=metric.value,
                    target_value=metric.benchmark * 1.1,  # 目标设为基准的110%
                    suggestion=self._get_metric_suggestion(platform, key, metric),
                    priority=priority,
                    expected_impact=severity_map.get(metric.status, "中"),
                    difficulty=self._get_difficulty(key)
                ))
                priority += 1

        # 检查平台特化指标
        for key, metric in platform_m.items():
            if metric.status in ["warning", "critical"]:
                severity_map = {"critical": "高", "high": "中", "medium": "低"}
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
                    expected_impact=severity_map.get(metric.status, "中"),
                    difficulty=self._get_difficulty(key)
                ))
                priority += 1

        # 按优先级排序
        issues.sort(key=lambda x: (["critical", "high", "medium", "low"].index(x.severity), x.priority))
        return issues[:10]  # 最多返回10个问题

    def _identify_strengths(self, platform: str, basic: Dict, platform_m: Dict) -> List[DiagnosisStrength]:
        """识别优势"""
        strengths = []

        for key, metric in {**basic, **platform_m}.items():
            if metric.status == "normal" and metric.gap > 0:
                strengths.append(DiagnosisStrength(
                    category="运营",
                    title=f"{metric.name}表现优秀",
                    description=f"高于行业基准{(metric.gap / metric.benchmark * 100):.1f}%",
                    metric=key,
                    value=metric.value
                ))

        return strengths[:5]  # 最多返回5个优势

    def _calculate_score(self, platform: str, basic: Dict, platform_m: Dict) -> int:
        """计算综合评分"""
        total = 0
        count = 0

        all_metrics = {**basic, **platform_m}
        for metric in all_metrics.values():
            if hasattr(metric, 'benchmark') and metric.benchmark > 0:
                # 评分公式: 基准为100分，每高于基准10%加5分，每低10%减5分
                ratio = metric.value / metric.benchmark
                if ratio >= 1:
                    score = min(100, 100 + (ratio - 1) * 50)  # 封顶100
                else:
                    score = max(0, 100 - (1 - ratio) * 50)  # 最低0
                total += score
                count += 1

        return int(total / count) if count > 0 else 50

    def _get_metric_suggestion(self, platform: str, metric_key: str, metric: MetricResult) -> str:
        """获取指标优化建议"""
        suggestions = {
            "engagement_rate": "优化内容选题，增加互动性元素",
            "follower_growth": "增加爆款内容产出，提升账号吸引力",
            "posting_frequency": "制定稳定的内容发布计划",
        }
        return suggestions.get(metric_key, "优化内容质量")

    def _get_platform_suggestion(self, platform: str, metric_key: str, metric: MetricResult) -> str:
        """获取平台特化指标建议"""
        # 具体建议根据平台和指标类型
        return "参考算法趋势建议优化内容"

    def _get_difficulty(self, metric_key: str) -> str:
        """获取执行难度"""
        difficulty_map = {
            "engagement_rate": "中",
            "follower_growth": "高",
            "posting_frequency": "低",
            "save_rate": "中",
            "comment_rate": "高",
            "completion_rate": "高",
        }
        return difficulty_map.get(metric_key, "中")

    def _generate_summary(self, account_name: str, platform: str, issues: List, strengths: List, score: int) -> str:
        """生成诊断摘要"""
        platform_name = {"xiaohongshu": "小红书", "douyin": "抖音", "shipinhao": "视频号", "gongzhonghao": "公众号"}.get(platform, platform)

        summary = f"{account_name}（{platform_name}）诊断完成。综合评分{score}分，"

        if score >= 80:
            summary += "整体表现优秀。"
        elif score >= 60:
            summary += "表现中等，存在提升空间。"
        else:
            summary += "表现较差，需要重点优化。"

        if issues:
            summary += f"发现{len(issues)}个问题，其中{sum(1 for i in issues if i.severity == 'critical')}个需要立即处理。"

        return summary
