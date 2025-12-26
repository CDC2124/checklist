import pandas as pd
from typing import Dict, Tuple
from ..utils.logger import logger

class PriceMatcher:
    def __init__(self):
        pass

    def match_prices(self, delivery_df: pd.DataFrame, price_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """匹配送货明细和价格表数据"""
        try:
            # 创建结果DataFrame
            result_df = delivery_df.copy()
            
            # 创建价格查找字典
            price_dict = price_df.set_index('商品编码')['单价'].to_dict()
            
            # 添加单价列
            result_df['单价'] = result_df['商品编码'].map(price_dict)
            
            # 计算金额
            result_df['金额'] = result_df['数量'] * result_df['单价']
            
            # 统计匹配结果
            total_items = len(result_df)
            matched_items = result_df['单价'].notna().sum()
            unmatched_items = total_items - matched_items
            
            stats = {
                'total_items': total_items,
                'matched_items': matched_items,
                'unmatched_items': unmatched_items,
                'match_rate': matched_items / total_items if total_items > 0 else 0
            }
            
            logger.info(f"价格匹配完成: 总数{total_items}, 匹配成功{matched_items}, 未匹配{unmatched_items}")
            
            return result_df, stats
            
        except Exception as e:
            logger.error(f"价格匹配失败: {str(e)}")
            raise

    def generate_match_report(self, result_df: pd.DataFrame) -> Dict:
        """生成价格匹配报告"""
        try:
            # 获取未匹配的记录
            unmatched = result_df[result_df['单价'].isna()]
            
            # 按商品分组统计未匹配数量
            unmatched_stats = unmatched.groupby(['商品编码', '商品名称']).size().reset_index()
            unmatched_stats.columns = ['商品编码', '商品名称', '未匹配数量']
            
            # 计算汇总信息
            total_amount = result_df['金额'].sum()
            matched_count = result_df['单价'].notna().sum()
            unmatched_count = result_df['单价'].isna().sum()
            
            report = {
                'summary': {
                    'total_amount': total_amount,
                    'matched_count': matched_count,
                    'unmatched_count': unmatched_count,
                    'match_rate': matched_count / len(result_df) if len(result_df) > 0 else 0
                },
                'unmatched_items': unmatched_stats.to_dict('records')
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成匹配报告失败: {str(e)}")
            raise