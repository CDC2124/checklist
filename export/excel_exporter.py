import os
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from ..utils.logger import logger
from ..utils.config import config

class ExcelExporter:
    def __init__(self):
        self.export_config = config.export_config
        self.export_dir = config.export_dir

    def export_statement(self, df: pd.DataFrame, month: str, customer: str) -> str:
        """导出对账单"""
        try:
            # 确保导出目录存在
            if not os.path.exists(self.export_dir):
                os.makedirs(self.export_dir)

            # 生成文件名
            filename = self.export_config['filename_pattern'].format(
                year=month[:4],
                month=month[4:],
                customer=customer
            )
            
            # 构建完整的文件路径
            file_path = os.path.join(self.export_dir, filename)

            # 准备导出数据
            export_df = self._prepare_export_data(df)

            # 导出到Excel
            self._write_to_excel(export_df, file_path)

            logger.info(f"对账单已导出到: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"导出对账单失败: {str(e)}")
            raise

    def _prepare_export_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备导出数据"""
        # 复制数据，避免修改原始数据
        export_df = df.copy()

        # 格式化日期
        export_df['日期'] = export_df['日期'].dt.strftime('%Y-%m-%d')

        # 格式化数值
        export_df['数量'] = export_df['数量'].round(2)
        export_df['单价'] = export_df['单价'].round(2)
        export_df['金额'] = export_df['金额'].round(2)

        # 按日期排序
        export_df = export_df.sort_values('日期')

        # 添加合计行
        total_row = pd.DataFrame([{
            '日期': '合计',
            '商品编码': '',
            '商品名称': '',
            '数量': export_df['数量'].sum(),
            '单位': '',
            '单价': '',
            '金额': export_df['金额'].sum()
        }])
        
        export_df = pd.concat([export_df, total_row], ignore_index=True)

        return export_df

    def _write_to_excel(self, df: pd.DataFrame, file_path: str) -> None:
        """写入Excel文件"""
        # 创建Excel写入器
        writer = pd.ExcelWriter(file_path, engine='openpyxl')

        # 获取配置的sheet名称
        sheet_name = self.export_config.get('sheet_name', '对账单')

        # 写入数据
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # 获取工作表
        worksheet = writer.sheets[sheet_name]

        # 设置列宽
        column_widths = {
            'A': 12,  # 日期
            'B': 15,  # 商品编码
            'C': 30,  # 商品名称
            'D': 10,  # 数量
            'E': 8,   # 单位
            'F': 10,  # 单价
            'G': 12   # 金额
        }

        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width

        # 设置合计行样式
        last_row = len(df)
        for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            cell = worksheet[f"{col}{last_row}"]
            cell.font = cell.font.copy(bold=True)

        # 保存文件
        writer.close()

    def get_export_path(self, month: str, customer: str) -> str:
        """获取导出文件路径"""
        filename = self.export_config['filename_pattern'].format(
            year=month[:4],
            month=month[4:],
            customer=customer
        )
        return os.path.join(self.export_dir, filename)