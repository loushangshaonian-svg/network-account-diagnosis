# 网络账号运营诊断报告

## 执行摘要
- 诊断对象: {{ keyword }}
- 诊断时间: {{ timestamp }}
- 诊断平台: {{ platforms }}
- 综合评分: {{ avg_score }}/100

## 诊断优化总表

{{ diagnosis_table }}

## 分平台诊断详情

{% for result in results %}
### {{ result.platform_name }} 诊断详情

**账号**: {{ result.account_name }}
**评分**: {{ result.overall_score }}/100

**核心指标**:
{% for metric in result.metrics %}
- {{ metric.icon }} {{ metric.name }}: {{ metric.value }}{{ metric.unit }}
{% endfor %}

**发现的问题**:
{% for issue in result.issues %}
- {{ issue.title }}
{% endfor %}

---
{% endfor %}

## 综合优化方案

{{ comprehensive_plan }}
