import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
from ..utils.logger import logger

class DataValidator:
    def __init__(self):
        self.validation_rules = {
            '日期': self._validate_date,
            '商品编码': self._validate_product_code,
            '数量': self._validate_quantity,
            '单价': self._validate_price,
            '单位': self._validate_unit
        }

    def validate_delivery_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """验证送货明细数据"""
        errors = []
        
        try:
            # 检查必需字段
            required_fields = ['日期', '商品编码', '商品名称', '数量', '单位']
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                errors.append(f"缺少必需字段: {', '.join(missing_fields)}")
                return False, errors

            # 应用验证规则
            for field, validator in self.validation_rules.items():
                if field in df.columns:
                    field_errors = validator(df[field])
                    errors.extend(field_errors)

            # 检查数据完整性
            null_counts = df[required_fields].isnull().sum()
            for field, count in null_counts.items():
                if count > 0:
                    errors.append(f"{field}列有{count}个空值")

            is_valid = len(errors) == 0
            return is_valid, errors

        except Exception as e:
            logger.error(f"数据验证失败: {str(e)}")
            errors.append(f"验证过程发生错误: {str(e)}")
            return False, errors

    def validate_price_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """验证价格表数据"""
        errors = []
        
        try:
            # 检查必需字段
            required_fields = ['商品编码', '商品名称', '单价', '单位']
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                errors.append(f"缺少必需字段: {', '.join(missing_fields)}")
                return False, errors

            # 验证单价
            price_errors = self._validate_price(df['单价'])
            errors.extend(price_errors)

            # 验证商品编码
            code_errors = self._validate_product_code(df['商品编码'])
            errors.extend(code_errors)

            # 检查重复的商品编码
            duplicates = df[df['商品编码'].duplicated()]['商品编码'].unique()
            if len(duplicates) > 0:
                errors.append(f"发现重复的商品编码: {', '.join(duplicates)}")

            # 检查数据完整性
            null_counts = df[required_fields].isnull().sum()
            for field, count in null_counts.items():
                if count > 0:
                    errors.append(f"{field}列有{count}个空值")

            is_valid = len(errors) == 0
            return is_valid, errors

        except Exception as e:
            logger.error(f"价格表验证失败: {str(e)}")
            errors.append(f"验证过程发生错误: {str(e)}")
            return False, errors

    def _validate_date(self, series: pd.Series) -> List[str]:
        """验证日期格式"""
        errors = []
        try:
            pd.to_datetime(series, errors='raise')
        except Exception as e:
            errors.append(f"日期格式错误: {str(e)}")
        return errors

    def _validate_product_code(self, series: pd.Series) -> List[str]:
        """验证商品编码"""
        errors = []
        # 检查空值
        if series.isnull().any():
            errors.append("商品编码不能为空")
        # 检查格式（假设商品编码应该是字符串）
        if not series.apply(lambda x: isinstance(x, str) or isinstance(x, int)).all():
            errors.append("商品编码格式不正确")
        return errors

    def _validate_quantity(self, series: pd.Series) -> List[str]:
        """验证数量"""
        errors = []
        try:
            numeric_series = pd.to_numeric(series, errors='raise')
            if (numeric_series <= 0).any():
                errors.append("数量必须大于0")
        except Exception:
            errors.append("数量必须为数字")
        return errors

    def _validate_price(self, series: pd.Series) -> List[str]:
        """验证单价"""
        errors = []
        try:
            numeric_series = pd.to_numeric(series, errors='raise')
            if (numeric_series <= 0).any():
                errors.append("单价必须大于0")
        except Exception:
            errors.append("单价必须为数字")
        return errors

    def _validate_unit(self, series: pd.Series) -> List[str]:
        """验证单位"""
        errors = []
        if series.isnull().any():
            errors.append("单位不能为空")
        if not series.apply(lambda x: isinstance(x, str) if pd.notnull(x) else True).all():
            errors.append("单位必须为文本")
        return errors