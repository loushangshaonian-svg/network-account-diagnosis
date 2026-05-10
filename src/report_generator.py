"""
诊断报告生成器
核心功能：生成诊断优化一体化表格
完整的数据处理和错误处理
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


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
        """初始化报告生成器"""
        self.platform_names = {
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "shipinhao": "视频号",
            "gongzhonghao": "公众号"
        }
        logger.info("报告生成器初始化完成")
    
    def generate_diagnosis_table(self, diagnosis_results: List[Dict]) -> str:
        """
        生成诊断优化一体化总表
        
        Args:
            diagnosis_results: 诊断结果列表
            
        Returns:
            Markdown格式的表格
        """
        if not diagnosis_results:
            logger.warning("诊断结果为空，无法生成表格")
            return "暂无诊断数据"
        
        logger.info(f"生成诊断表格，共 {len(diagnosis_results)} 个结果")
        
        # 表头
        headers = [
            "平台", "账号名", "综合评分",
            "粉丝数", "粉丝增速", "内容数", "发布频次",
            "互动率", "平台特化指标1", "平台特化指标2",
            "核心问题", "问题等级", "优化策略", "预期效果", "执行难度"
        ]
        
        rows = []
        for result in diagnosis_results:
            try:
                row = self._build_row(result)
                rows.append(row)
            except Exception as e:
                logger.error(f"行数据构建失败: {str(e)}", exc_info=True)
                continue
        
        table = self._format_markdown_table(headers, rows)
        logger.debug(f"✓ 生成 {len(rows)} 行数据")
        return table
    
    def _build_row(self, result: Dict) -> List[str]:
        """
        构建单行数据
        
        Args:
            result: 诊断结果字典
            
        Returns:
            行数据列表
        """
        try:
            platform = result.get("platform", "")
            account_name = result.get("account_name", "")
            score = result.get("overall_score", 0)
            followers = result.get("followers", "")
            posts = result.get("posts", "")
            
            # 基础指标
            metrics = result.get("basic_metrics", {})
            follower_growth = self._safe_get_metric_value(metrics, "follower_growth", 0)
            posting_freq = self._safe_get_metric_value(metrics, "posting_frequency", 0)
            engagement_rate = self._safe_get_metric_value(metrics, "engagement_rate", 0)
            
            # 平台特化指标
            platform_metrics = result.get("platform_metrics", {})
            special_1 = ""
            special_2 = ""
            
            if platform_metrics:
                keys = list(platform_metrics.keys())
                if len(keys) > 0:
                    val1 = platform_metrics[keys[0]]
                    special_1 = f"{keys[0]}: {self._safe_get_metric_value(val1, 'value', 0):.1f}%"
                if len(keys) > 1:
                    val2 = platform_metrics[keys[1]]
                    special_2 = f"{keys[1]}: {self._safe_get_metric_value(val2, 'value', 0):.1f}%"
            
            # 问题汇总
            issues = result.get("issues", [])
            issue_summary = ""
            issue_level = ""
            optimization = ""
            expected_impact = ""
            difficulty = ""
            
            if issues:
                top_issue = issues[0] if isinstance(issues[0], dict) else asdict(issues[0])
                issue_summary = top_issue.get("title", "")[:20]
                issue_level = top_issue.get("severity", "")
                optimization = top_issue.get("suggestion", "")[:30]
                expected_impact = top_issue.get("expected_impact", "")
                difficulty = top_issue.get("difficulty", "")
            
            row = [
                self.platform_names.get(platform, platform),
                str(account_name),
                f"{score}/100",
                str(followers),
                f"{follower_growth:.1f}%",
                str(posts),
                f"{posting_freq:.1f}篇/周",
                f"{engagement_rate:.1f}%",
                special_1,
                special_2,
                issue_summary,
                issue_level,
                optimization,
                expected_impact,
                difficulty
            ]
            
            return row
            
        except Exception as e:
            logger.error(f"行数据构建异常: {str(e)}", exc_info=True)
            return [""] * 15
    
    def _safe_get_metric_value(self, metric_data: Any, key: str, default: float = 0.0) -> float:
        """
        安全获取指标值
        支持字典和对象两种格式
        
        Args:
            metric_data: 指标数据（可能是dict或dataclass）
            key: 要获取的键
            default: 默认值
            
        Returns:
            float数值
        """
        try:
            if isinstance(metric_data, dict):
                val = metric_data.get(key, default)
                # 如果val本身是dict（比如 {value: 3.5, benchmark: 2.0}），尝试提取value
                if isinstance(val, dict):
                    return val.get("value", default)
                return float(val) if val is not None else default
            else:
                # 对象模式：尝试getattr
                val = getattr(metric_data, key, default)
                return float(val) if val is not None else default
        except:
            return default
    
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
        
        Args:
            current: 当前数据
            previous: 历史数据
            
        Returns:
            Markdown表格
        """
        headers = ["平台", "指标", "上周期", "本周期", "环比变化", "问题等级", "优化建议"]
        rows = []
        
        try:
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
                        if change_pct < -20:
                            level = "🔴 高"
                        elif change_pct < -10:
                            level = "⚠️ 中"
                        
                        rows.append([
                            self.platform_names.get(platform, platform),
                            metric_key,
                            f"{prev_val:.1f}",
                            f"{curr_val:.1f}",
                            f"{change_pct:+.1f}%",
                            level,
                            ""
                        ])
            
            logger.info(f"时间序列对比表生成完成: {len(rows)} 行")
            
        except Exception as e:
            logger.error(f"时间序列对比异常: {str(e)}", exc_info=True)
        
        return self._format_markdown_table(headers, rows)
    
    def generate_comprehensive_plan(self, diagnosis_results: List[Dict]) -> str:
        """
        生成综合优化方案
        
        Args:
            diagnosis_results: 诊断结果列表
            
        Returns:
            优化方案（Markdown格式）
        """
        all_issues = []
        
        try:
            for result in diagnosis_results:
                platform = result.get("platform", "")
                issues = result.get("issues", [])
                
                for issue in issues:
                    issue_copy = issue if isinstance(issue, dict) else asdict(issue)
                    issue_copy["platform"] = platform
                    all_issues.append(issue_copy)
            
            # 按优先级排序
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            all_issues.sort(key=lambda x: (priority_order.get(x.get("severity", ""), 4), x.get("priority", 99)))
            
            logger.info(f"生成优化方案: {len(all_issues)} 个行动项")
            
            # 生成方案
            plan = []
            plan.append("# 综合运营优化方案\n")
            plan.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            plan.append(f"诊断平台数: {len(diagnosis_results)}\n")
            plan.append(f"识别问题数: {len(all_issues)}\n")
            plan.append("\n---\n")
            
            # P0 紧急行动
            p0_issues = [i for i in all_issues if i.get("severity") == "critical"]
            if p0_issues:
                plan.append("## 🔴 P0 紧急行动（立即执行）\n")
                for i, issue in enumerate(p0_issues[:3], 1):
                    plan.append(f"{i}. **{issue.get('title', '')}** ({issue.get('platform', '')})\n")
                    plan.append(f"   - 问题: {issue.get('description', '')}\n")
                    plan.append(f"   - 建议: {issue.get('suggestion', '')}\n")
                    plan.append(f"   - 预期效果: {issue.get('expected_impact', '')}\n")
                    plan.append(f"   - 执行难度: {issue.get('difficulty', '')}\n")
                    plan.append("\n")
            
            # P1 本周行动
            p1_issues = [i for i in all_issues if i.get("severity") == "high"]
            if p1_issues:
                plan.append("## 🟠 P1 本周行动\n")
                for i, issue in enumerate(p1_issues[:5], 1):
                    plan.append(f"{i}. **{issue.get('title', '')}** ({issue.get('platform', '')})\n")
                    plan.append(f"   - 建议: {issue.get('suggestion', '')}\n")
                    plan.append("\n")
            
            # P2 本月行动
            p2_issues = [i for i in all_issues if i.get("severity") in ["medium", "low"]]
            if p2_issues:
                plan.append("## 🟡 P2 本月行动\n")
                for i, issue in enumerate(p2_issues[:5], 1):
                    plan.append(f"{i}. **{issue.get('title', '')}** ({issue.get('platform', '')})\n")
                    plan.append(f"   - 建议: {issue.get('suggestion', '')}\n")
                    plan.append("\n")
            
            # KPI目标
            plan.append("\n## 📊 KPI目标建议\n\n")
            plan.append("| 指标 | 目标值 | 达成时间 |\n")
            plan.append("|------|--------|----------|\n")
            plan.append("| 总粉丝增长 | +20% | 3个月 |\n")
            plan.append("| 平均互动率 | +2% | 1个月 |\n")
            plan.append("| 内容产出 | 稳定更新 | 持续 |\n")
            
            return "\n".join(plan)
            
        except Exception as e:
            logger.error(f"优化方案生成异常: {str(e)}", exc_info=True)
            return "❌ 优化方案生成失败"
    
    def generate_full_report(self, input_keyword: str, accounts: List[Dict], diagnosis_results: List[Dict]) -> str:
        """
        生成完整诊断报告
        
        Args:
            input_keyword: 诊断对象
            accounts: 账号数据列表
            diagnosis_results: 诊断结果列表
            
        Returns:
            完整报告（Markdown格式）
        """
        report = []
        
        try:
            logger.info(f"开始生成完整报告: {input_keyword}")
            
            # 执行摘要
            report.append(f"# 网络账号运营诊断报告\n\n")
            report.append(f"**诊断对象**: {input_keyword}\n\n")
            report.append(f"**诊断时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            report.append(f"**诊断平台**: {', '.join([self.platform_names.get(r.get('platform', ''), '') for r in diagnosis_results])}\n\n")
            report.append(f"**账号数量**: {len(accounts)}\n\n")
            report.append("\n---\n\n")
            
            # 综合评分
            scores = [r.get("overall_score", 0) for r in diagnosis_results]
            avg_score = sum(scores) / len(scores) if scores else 0
            report.append(f"## 📊 综合评分: **{avg_score:.0f}/100**\n\n")
            
            if avg_score >= 80:
                report.append("✅ 整体表现优秀，继续保持。\n\n")
            elif avg_score >= 60:
                report.append("⚠️ 表现中等，存在提升空间。\n\n")
            else:
                report.append("❌ 表现较弱，需要重点优化。\n\n")
            
            # 一体化表格
            report.append("## 📋 诊断优化总表\n\n")
            report.append("（包含账号基本数据、核心指标、问题与优化方案对应关系）\n\n")
            report.append(self.generate_diagnosis_table(diagnosis_results))
            report.append("\n\n")
            
            # 分平台详情
            report.append("## 📱 分平台诊断详情\n\n")
            for result in diagnosis_results:
                try:
                    platform = result.get("platform", "")
                    platform_name = self.platform_names.get(platform, platform)
                    report.append(f"### {platform_name}\n\n")
                    report.append(f"**账号**: {result.get('account_name', '')}\n\n")
                    report.append(f"**评分**: {result.get('overall_score', 0)}/100\n\n")
                    
                    # 基本信息
                    report.append("**基本信息**:\n")
                    report.append(f"- 粉丝数: {result.get('followers', ''):,}\n")
                    report.append(f"- 内容数: {result.get('posts', '')}\n")
                    report.append(f"- 互动率: {result.get('engagement_rate', 0):.2%}\n\n")
                    
                    # 核心指标
                    basic_metrics = result.get("basic_metrics", {})
                    if basic_metrics:
                        report.append("**核心指标**:\n")
                        for key, metric in basic_metrics.items():
                            status = metric.get("status", "normal")
                            value = metric.get("value", 0)
                            unit = metric.get("unit", "")
                            benchmark = metric.get("benchmark", 0)
                            
                            status_icon = "✅" if status == "normal" else "⚠️" if status == "warning" else "❌"
                            report.append(f"- {status_icon} {metric.get('name', key)}: {value:.1f}{unit}")
                            if benchmark > 0:
                                report.append(f" (基准: {benchmark:.1f}{unit})")
                            report.append("\n")
                        report.append("\n")
                    
                    # 问题
                    issues = result.get("issues", [])
                    if issues:
                        report.append("**发现的问题**:\n")
                        for issue in issues[:3]:
                            issue_dict = issue if isinstance(issue, dict) else asdict(issue)
                            report.append(f"- 🔸 {issue_dict.get('title', '')}\n")
                            report.append(f"  {issue_dict.get('description', '')}\n\n")
                    
                    # 优势
                    strengths = result.get("strengths", [])
                    if strengths:
                        report.append("**账号优势**:\n")
                        for strength in strengths[:3]:
                            strength_dict = strength if isinstance(strength, dict) else asdict(strength)
                            report.append(f"- ✨ {strength_dict.get('title', '')}\n")
                        report.append("\n")
                    
                    # 算法趋势建议
                    trends = result.get("algorithm_trends", [])
                    if trends:
                        report.append("**算法趋势建议**:\n")
                        for trend in trends[:2]:
                            report.append(f"- {trend}\n")
                        report.append("\n")
                    
                    report.append("\n---\n\n")
                    
                except Exception as e:
                    logger.error(f"分平台详情生成异常: {str(e)}", exc_info=True)
                    continue
            
            # 综合优化方案
            report.append("## 🎯 综合优化方案\n\n")
            report.append(self.generate_comprehensive_plan(diagnosis_results))
            
            logger.info("✓ 完整报告生成完成")
            return "".join(report)
            
        except Exception as e:
            logger.error(f"报告生成异常: {str(e)}", exc_info=True)
            return "❌ 报告生成失败"


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
