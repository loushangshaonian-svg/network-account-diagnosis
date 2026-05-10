"""
诊断报告生成器
核心功能：生成诊断优化一体化表格
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class OptimizationAction:
    """优化行动项"""
    priority: str  # P0/P1/P2
    action: str
    expected_impact: str
    difficulty: str  # 低/中/高
    timeline: str  # 立即/本周/本月
    kpi_target: str


class DiagnosisReportGenerator:
    """诊断报告生成器"""

    def __init__(self):
        self.platform_names = {
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "shipinhao": "视频号",
            "gongzhonghao": "公众号"
        }

    def generate_diagnosis_table(self, diagnosis_results: List[Dict]) -> str:
        """
        生成诊断优化一体化总表
        核心输出：Markdown表格，包含诊断+优化一体化
        """
        if not diagnosis_results:
            return "暂无诊断数据"

        # 表头
        headers = [
            "平台", "账号名", "综合评分",
            "粉丝数", "粉丝增速", "内容数", "发布频次",
            "互动率", "平台特化指标1", "平台特化指标2",
            "核心问题", "问题等级", "优化策略", "预期效果", "执行难度"
        ]

        rows = []
        for result in diagnosis_results:
            row = self._build_row(result)
            rows.append(row)

        return self._format_markdown_table(headers, rows)

    def _build_row(self, result: Dict) -> List[str]:
        """构建单行数据"""
        platform = result.get("platform", "")
        metrics = result.get("basic_metrics", {})
        platform_metrics = result.get("platform_metrics", {})
        issues = result.get("issues", [])

        # 平台特化指标
        special_1 = ""
        special_2 = ""
        if platform_metrics:
            keys = list(platform_metrics.keys())
            if len(keys) > 0:
                special_1 = f"{keys[0]}: {platform_metrics[keys[0]].get('value', 0):.1f}%" if isinstance(platform_metrics[keys[0]], dict) else f"{keys[0]}: {platform_metrics[keys[0]]:.1f}%"
            if len(keys) > 1:
                special_2 = f"{keys[1]}: {platform_metrics[keys[1]].get('value', 0):.1f}%" if isinstance(platform_metrics[keys[1]], dict) else f"{keys[1]}: {platform_metrics[keys[1]]:.1f}%"

        # 问题汇总
        issue_summary = ""
        issue_level = ""
        if issues:
            top_issue = issues[0]
            issue_summary = top_issue.get("title", "")[:20]
            issue_level = top_issue.get("severity", "")

        # 优化策略
        optimization = ""
        if issues:
            optimization = issues[0].get("suggestion", "")[:30]

        return [
            self.platform_names.get(platform, platform),
            result.get("account_name", ""),
            f"{result.get('overall_score', 0)}/100",
            str(result.get("followers", "")),
            f"{metrics.get('follower_growth', {}).get('value', 0):.1f}%",
            str(result.get("posts", "")),
            f"{metrics.get('posting_frequency', {}).get('value', 0):.1f}篇/周",
            f"{metrics.get('engagement_rate', {}).get('value', 0):.1f}%",
            special_1,
            special_2,
            issue_summary,
            issue_level,
            optimization,
            issues[0].get("expected_impact", "") if issues else "",
            issues[0].get("difficulty", "") if issues else ""
        ]

    def _format_markdown_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """格式化Markdown表格"""
        lines = []

        # 表头
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # 数据行
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        return "\n".join(lines)

    def generate_time_comparison_table(self, current: Dict, previous: Dict) -> str:
        """
        生成时间序列对比表
        纵向对比：各平台同周期数据变化
        """
        headers = ["平台", "指标", "上周期", "本周期", "环比变化", "问题等级", "优化建议"]
        rows = []

        platforms = set(current.keys()) & set(previous.keys())
        for platform in platforms:
            current_metrics = current.get(platform, {}).get("metrics", {})
            previous_metrics = previous.get(platform, {}).get("metrics", {})

            for metric_key in current_metrics:
                if metric_key in previous_metrics:
                    curr_val = current_metrics[metric_key]
                    prev_val = previous_metrics[metric_key]
                    change = curr_val - prev_val
                    change_pct = (change / prev_val * 100) if prev_val > 0 else 0

                    # 判断问题等级
                    level = "正常"
                    if abs(change_pct) < -20:
                        level = "🔴 高"
                    elif abs(change_pct) < -10:
                        level = "⚠️ 中"

                    rows.append([
                        self.platform_names.get(platform, platform),
                        metric_key,
                        f"{prev_val:.1f}",
                        f"{curr_val:.1f}",
                        f"{change_pct:+.1f}%",
                        level,
                        ""  # 优化建议列
                    ])

        return self._format_markdown_table(headers, rows)

    def generate_comprehensive_plan(self, diagnosis_results: List[Dict]) -> str:
        """
        生成综合优化方案
        """
        all_issues = []
        all_kpi_targets = {}

        for result in diagnosis_results:
            platform = result.get("platform", "")
            issues = result.get("issues", [])

            for issue in issues:
                issue_copy = issue.copy()
                issue_copy["platform"] = platform
                all_issues.append(issue_copy)

        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_issues.sort(key=lambda x: (priority_order.get(x.get("severity", ""), 4), x.get("priority", 99)))

        # 生成方案
        plan = []
        plan.append("# 综合运营优化方案\n")
        plan.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        plan.append(f"诊断平台数: {len(diagnosis_results)}\n")
        plan.append("\n---\n")

        # P0 紧急行动
        p0_issues = [i for i in all_issues if i.get("severity") == "critical"]
        if p0_issues:
            plan.append("## 🔴 P0 紧急行动（立即执行）\n")
            for i, issue in enumerate(p0_issues[:3], 1):
                plan.append(f"{i}. **{issue.get('title', '')}** ({issue.get('platform', '')})")
                plan.append(f"   - 问题: {issue.get('description', '')}")
                plan.append(f"   - 建议: {issue.get('suggestion', '')}")
                plan.append("")

        # P1 本周行动
        p1_issues = [i for i in all_issues if i.get("severity") == "high"]
        if p1_issues:
            plan.append("## 🟠 P1 本周行动\n")
            for i, issue in enumerate(p1_issues[:5], 1):
                plan.append(f"{i}. **{issue.get('title', '')}** ({issue.get('platform', '')})")
                plan.append(f"   - 建议: {issue.get('suggestion', '')}")
                plan.append("")

        # P2 本月行动
        p2_issues = [i for i in all_issues if i.get("severity") in ["medium", "low"]]
        if p2_issues:
            plan.append("## 🟡 P2 本月行动\n")
            for i, issue in enumerate(p2_issues[:5], 1):
                plan.append(f"{i}. **{issue.get('title', '')}** ({issue.get('platform', '')})")
                plan.append(f"   - 建议: {issue.get('suggestion', '')}")
                plan.append("")

        # KPI目标
        plan.append("\n## 📊 KPI目标建议\n")
        plan.append("| 指标 | 目标值 | 达成时间 |")
        plan.append("|------|--------|----------|")
        plan.append("| 总粉丝增长 | +20% | 3个月 |")
        plan.append("| 平均互动率 | +2% | 1个月 |")
        plan.append("| 内容产出 | 稳定更新 | 持续 |")

        return "\n".join(plan)

    def generate_full_report(self, input_keyword: str, accounts: List[Dict], diagnosis_results: List[Dict]) -> str:
        """
        生成完整诊断报告
        """
        report = []

        # 执行摘要
        report.append(f"# 网络账号运营诊断报告\n")
        report.append(f"**诊断对象**: {input_keyword}\n")
        report.append(f"**诊断时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        report.append(f"**诊断平台**: {', '.join([self.platform_names.get(r.get('platform', ''), '') for r in diagnosis_results])}\n")
        report.append(f"**账号数量**: {len(accounts)}\n")
        report.append("\n---\n")

        # 综合评分
        scores = [r.get("overall_score", 0) for r in diagnosis_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        report.append(f"## 综合评分: **{avg_score:.0f}/100**\n")

        # 一体化表格
        report.append("## 诊断优化总表\n")
        report.append("（诊断数据与优化数据纵向对比）\n")
        report.append(self.generate_diagnosis_table(diagnosis_results))
        report.append("\n\n")

        # 分平台详情
        for result in diagnosis_results:
            platform = result.get("platform", "")
            report.append(f"\n### {self.platform_names.get(platform, platform)} 诊断详情\n")
            report.append(f"**账号**: {result.get('account_name', '')}\n")
            report.append(f"**评分**: {result.get('overall_score', 0)}/100\n")

            # 指标
            report.append("\n**核心指标**:\n")
            basic_metrics = result.get("basic_metrics", {})
            for key, metric in basic_metrics.items():
                # 处理metric可能是字典或对象的情况
                if isinstance(metric, dict):
                    status = metric.get("status", "normal")
                    name = metric.get("name", key)
                    value = metric.get("value", 0)
                    unit = metric.get("unit", "")
                    benchmark = metric.get("benchmark", 0)
                else:
                    status = getattr(metric, "status", "normal")
                    name = getattr(metric, "name", key)
                    value = getattr(metric, "value", 0)
                    unit = getattr(metric, "unit", "")
                    benchmark = getattr(metric, "benchmark", 0)

                status_icon = "✅" if status == "normal" else "⚠️" if status == "warning" else "❌"
                report.append(f"- {status_icon} {name}: {value:.1f}{unit}")
                if benchmark > 0:
                    report.append(f" (基准: {benchmark:.1f}{unit})")
                report.append("\n")

            # 问题
            if result.get("issues"):
                report.append("\n**发现的问题**:\n")
                for issue in result["issues"][:3]:
                    report.append(f"- 🔸 {issue.get('title', '')}")
                    report.append(f"  {issue.get('description', '')}\n")

            # 优势
            if result.get("strengths"):
                report.append("\n**优势**:\n")
                for strength in result["strengths"][:3]:
                    report.append(f"- ✨ {strength.get('title', '')}\n")

            # 算法趋势建议
            if result.get("algorithm_trends"):
                report.append("\n**算法趋势建议**:\n")
                for trend in result["algorithm_trends"][:2]:
                    report.append(f"- {trend}\n")

            report.append("\n---\n")

        # 综合优化方案
        report.append(self.generate_comprehensive_plan(diagnosis_results))

        return "".join(report)


# 便捷函数
def generate_report(input_keyword: str, accounts: List[Dict], diagnosis_results: List[Dict]) -> str:
    """生成诊断报告的便捷函数"""
    generator = DiagnosisReportGenerator()
    return generator.generate_full_report(input_keyword, accounts, diagnosis_results)


def generate_diagnosis_table(diagnosis_results: List[Dict]) -> str:
    """生成诊断优化一体化表格的便捷函数"""
    generator = DiagnosisReportGenerator()
    return generator.generate_diagnosis_table(diagnosis_results)


def generate_comprehensive_plan(diagnosis_results: List[Dict]) -> str:
    """生成综合优化方案的便捷函数"""
    generator = DiagnosisReportGenerator()
    return generator.generate_comprehensive_plan(diagnosis_results)
