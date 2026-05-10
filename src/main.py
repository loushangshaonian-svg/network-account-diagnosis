"""
主程序入口 - 诊断执行器
管理完整的诊断流程：搜索 → 诊断 → 报告
"""

import asyncio
import logging
import sys
import argparse
from typing import List, Optional, Dict
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入核心模块
from src.data_layer import DataFetcher, AccountData
from src.diagnosis_engine import DiagnosisEngine
from src.report_generator import DiagnosisReportGenerator


class DiagnosisSkillExecutor:
    """诊断技能执行器 - 管理完整诊断流程"""
    
    def __init__(self):
        """初始化执行器"""
        self.data_fetcher = DataFetcher()
        self.diagnosis_engine = DiagnosisEngine()
        self.report_generator = DiagnosisReportGenerator()
        logger.info("诊断执行器初始化完成")
    
    async def execute(self, 
                     input_keyword: str, 
                     platforms: Optional[List[str]] = None,
                     is_url: bool = False) -> str:
        """
        执行完整诊断流程
        
        Args:
            input_keyword: 品牌名或URL
            platforms: 诊断平台列表，None 表示所有平台
            is_url: 是否为URL输入
            
        Returns:
            诊断报告（Markdown格式）
        """
        
        logger.info(f"开始诊断: {input_keyword[:50]}{'...' if len(input_keyword) > 50 else ''}")
        
        try:
            # 步骤1: 获取账号信息
            logger.info("步骤1: 获取账号信息...")
            accounts = await self._fetch_accounts(input_keyword, platforms, is_url)
            
            if not accounts:
                logger.warning("未找到任何账号数据")
                return f"❌ 诊断失败：未找到 '{input_keyword}' 的相关账号"
            
            logger.info(f"✓ 成功获取 {len(accounts)} 个账号")
            
            # 步骤2: 执行诊断分析
            logger.info("步骤2: 执行诊断分析...")
            diagnosis_results = await self._diagnose_accounts(accounts)
            
            if not diagnosis_results:
                logger.warning("诊断分析结果为空")
                return f"❌ 诊断失败：无法分析账号数据"
            
            logger.info(f"✓ 完成 {len(diagnosis_results)} 个账号的诊断")
            
            # 步骤3: 生成报告
            logger.info("步骤3: 生成诊断报告...")
            report = self.report_generator.generate_full_report(
                input_keyword,
                accounts,
                diagnosis_results
            )
            
            logger.info("✓ 诊断报告生成完成")
            return report
            
        except Exception as e:
            logger.error(f"诊断执行失败: {str(e)}", exc_info=True)
            return f"❌ 诊断执行失败: {str(e)}"
    
    async def _fetch_accounts(self, 
                             input_keyword: str, 
                             platforms: Optional[List[str]] = None,
                             is_url: bool = False) -> List[Dict]:
        """
        获取账号信息
        
        Returns:
            账号数据列表
        """
        accounts = []
        
        try:
            if is_url:
                # 直接从URL抓取
                logger.debug(f"从URL抓取: {input_keyword}")
                account = await self.data_fetcher.fetch_by_url(input_keyword)
                if account:
                    accounts.append({
                        'platform': account.platform,
                        'account_name': account.account_name,
                        'account_id': account.account_id,
                        'followers': account.followers,
                        'following': account.following,
                        'posts': account.posts,
                        'total_likes': account.total_likes,
                        'total_views': account.total_views,
                        'engagement_rate': account.engagement_rate
                    })
                    logger.info(f"✓ 从URL成功抓取账号: {account.account_name}")
            else:
                # 关键词搜索
                logger.debug(f"搜索账号: {input_keyword}")
                search_results = await self.data_fetcher.fetch_by_keyword(
                    input_keyword, 
                    platforms
                )
                
                for account in search_results:
                    accounts.append({
                        'platform': account.platform,
                        'account_name': account.account_name,
                        'account_id': account.account_id,
                        'followers': account.followers,
                        'following': account.following,
                        'posts': account.posts,
                        'total_likes': account.total_likes,
                        'total_views': account.total_views,
                        'engagement_rate': account.engagement_rate
                    })
                    logger.info(f"✓ 找到账号: {account.platform}/{account.account_name}")
            
        except Exception as e:
            logger.error(f"账号获取失败: {str(e)}", exc_info=True)
        
        return accounts
    
    async def _diagnose_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """
        诊断账号
        
        Args:
            accounts: 账号列表
            
        Returns:
            诊断结果列表
        """
        diagnosis_results = []
        
        for account in accounts:
            try:
                platform = account['platform']
                account_name = account['account_name']
                
                logger.debug(f"诊断: {platform}/{account_name}")
                
                # 执行诊断
                diagnosis = self.diagnosis_engine.diagnose(
                    platform=platform,
                    account_name=account_name,
                    account_data=account
                )
                
                # 转换为字典
                result_dict = diagnosis.to_dict()
                
                # 添加原始账号信息
                result_dict.update(account)
                
                diagnosis_results.append(result_dict)
                
                logger.info(f"✓ 诊断完成: {platform}/{account_name} (评分: {result_dict.get('overall_score', 0)}/100)")
                
            except Exception as e:
                logger.error(f"账号诊断失败 ({account.get('platform')}/{account.get('account_name')}): {str(e)}", 
                           exc_info=True)
        
        return diagnosis_results


# 全局执行器实例
_executor = None


async def diagnose_account(input_keyword: str,
                          platforms: Optional[List[str]] = None,
                          is_url: bool = False) -> str:
    """
    便捷函数 - 诊断账号
    
    使用示例:
        # 诊断所有平台
        report = await diagnose_account("予茉女装")
        
        # 诊断指定平台
        report = await diagnose_account("予茉女装", platforms=["xiaohongshu"])
        
        # 诊断URL
        report = await diagnose_account("https://www.xiaohongshu.com/user/profile/xxx", is_url=True)
    
    Args:
        input_keyword: 品牌名或URL
        platforms: 诊断平台列表 (可选)
        is_url: 是否为URL输入 (默认: False)
        
    Returns:
        诊断报告 (Markdown格式)
    """
    global _executor
    
    if _executor is None:
        _executor = DiagnosisSkillExecutor()
    
    return await _executor.execute(input_keyword, platforms, is_url)


def main():
    """命令行入口"""
    
    parser = argparse.ArgumentParser(
        description='网络账号运营诊断专家',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 诊断所有平台
  python -m src.main "予茉女装"
  
  # 指定平台诊断
  python -m src.main "予茉女装" --platforms xiaohongshu,douyin
  
  # 诊断URL
  python -m src.main "https://www.xiaohongshu.com/user/profile/xxx"
  
  # 输出到文件
  python -m src.main "予茉女装" --output report.md
        '''
    )
    
    parser.add_argument('keyword', help='品牌名或账号URL')
    parser.add_argument(
        '--platforms', 
        help='诊断平台 (逗号分隔，默认为所有平台)',
        default=None
    )
    parser.add_argument(
        '--output',
        help='输出文件路径 (默认打印到控制台)',
        default=None
    )
    
    args = parser.parse_args()
    
    # 解析平台参数
    platforms = None
    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(',')]
    
    # 判断是否为URL
    is_url = args.keyword.startswith('http://') or args.keyword.startswith('https://')
    
    # 执行诊断
    logger.info(f"诊断对象: {args.keyword}")
    if platforms:
        logger.info(f"诊断平台: {', '.join(platforms)}")
    
    report = asyncio.run(diagnose_account(args.keyword, platforms, is_url))
    
    # 输出结果
    if args.output:
        try:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            logger.info(f"✓ 报告已保存到: {args.output}")
            print(f"\n✓ 报告已保存到: {args.output}")
        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")
            print(report)
    else:
        print(report)


if __name__ == '__main__':
    main()
