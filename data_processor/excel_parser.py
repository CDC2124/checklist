import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from ..utils.logger import logger
from ..utils.config import config

class ExcelParser:
    def __init__(self):
        self.price_config = config.price_template_config
        self.delivery_config = config.delivery_template_config

    def parse_price_file(self, file_path: str) -> pd.DataFrame:
        """解析价格表文件"""
        try:
            sheet_name = self.price_config.get('sheet_name', '价格表')
            required_fields = self.price_config.get('required_fields', [])
            
            # 读取Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 验证必需字段
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                raise ValueError(f"价格表缺少必需字段: {', '.join(missing_fields)}")
            
            # 数据清洗
            df = df.dropna(subset=required_fields)
            
            # 确保数值类型正确
            df['单价'] = pd.to_numeric(df['单价'], errors='coerce')
            df = df.dropna(subset=['单价'])
            
            logger.info(f"成功解析价格表，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"解析价格表失败: {str(e)}")
            raise

    def parse_delivery_file(self, file_path: str) -> pd.DataFrame:
        """解析送货明细文件"""
        try:
            sheet_name = self.delivery_config.get('sheet_name', '送货明细')
            required_fields = self.delivery_config.get('required_fields', [])
            
            # 读取Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 验证必需字段
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                raise ValueError(f"送货明细缺少必需字段: {', '.join(missing_fields)}")
            
            # 数据清洗
            df = df.dropna(subset=required_fields)
            
            # 确保日期格式正确
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            df = df.dropna(subset=['日期'])
            
            # 确保数量为数值类型
            df['数量'] = pd.to_numeric(df['数量'], errors='coerce')
            df = df.dropna(subset=['数量'])
            
            logger.info(f"成功解析送货明细，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"解析送货明细失败: {str(e)}")
            raise

    def validate_data_compatibility(self, price_df: pd.DataFrame, delivery_df: pd.DataFrame) -> List[str]:
        """验证价格表和送货明细的数据兼容性"""
        warnings = []
        
        # 检查商品编码匹配情况
        delivery_codes = set(delivery_df['商品编码'].unique())
        price_codes = set(price_df['商品编码'].unique())
        
        unmatched_codes = delivery_codes - price_codes
        if unmatched_codes:
            warning = f"发现{len(unmatched_codes)}个商品编码在价格表中未找到匹配"
            warnings.append(warning)
            logger.warning(warning)
            
        # 检查单位匹配情况
        for code in delivery_codes & price_codes:
            delivery_unit = delivery_df[delivery_df['商品编码'] == code]['单位'].iloc[0]
            price_unit = price_df[price_df['商品编码'] == code]['单位'].iloc[0]
            
            if delivery_unit != price_unit:
                warning = f"商品编码 {code} 的单位不匹配: 送货单为{delivery_unit}，价格表为{price_unit}"
                warnings.append(warning)
                logger.warning(warning)
        
        return warnings