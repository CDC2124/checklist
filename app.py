import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data_processor.excel_parser import ExcelParser
from src.data_processor.price_matcher import PriceMatcher
from src.data_processor.validator import DataValidator
from src.export.excel_exporter import ExcelExporter
from src.utils.logger import logger
from src.utils.config import config

def main():
    st.set_page_config(page_title="对账单生成器", layout="wide")
    st.title("对账单生成器")

    # 初始化处理器
    parser = ExcelParser()
    matcher = PriceMatcher()
    validator = DataValidator()
    exporter = ExcelExporter()

    # 文件上传区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("上传送货明细")
        delivery_file = st.file_uploader("选择送货明细Excel文件", type=['xlsx', 'xls'])

    with col2:
        st.subheader("上传价格表")
        price_file = st.file_uploader("选择价格表Excel文件", type=['xlsx', 'xls'])

    if delivery_file is not None and price_file is not None:
        try:
            # 解析文件
            with st.spinner("正在解析文件..."):
                # 保存上传的文件
                delivery_path = os.path.join("temp", delivery_file.name)
                price_path = os.path.join("temp", price_file.name)
                
                os.makedirs("temp", exist_ok=True)
                
                with open(delivery_path, "wb") as f:
                    f.write(delivery_file.getvalue())
                with open(price_path, "wb") as f:
                    f.write(price_file.getvalue())

                # 解析文件
                delivery_df = parser.parse_delivery_file(delivery_path)
                price_df = parser.parse_price_file(price_path)

                # 验证数据
                delivery_valid, delivery_errors = validator.validate_delivery_data(delivery_df)
                price_valid, price_errors = validator.validate_price_data(price_df)

                if not delivery_valid:
                    st.error("送货明细数据验证失败：")
                    for error in delivery_errors:
                        st.error(error)
                    return

                if not price_valid:
                    st.error("价格表数据验证失败：")
                    for error in price_errors:
                        st.error(error)
                    return

                # 验证数据兼容性
                warnings = parser.validate_data_compatibility(price_df, delivery_df)
                if warnings:
                    st.warning("数据兼容性警告：")
                    for warning in warnings:
                        st.warning(warning)

                # 匹配价格
                result_df, stats = matcher.match_prices(delivery_df, price_df)
                match_report = matcher.generate_match_report(result_df)

                # 显示匹配统计
                st.subheader("价格匹配结果")
                col1, col2, col3 = st.columns(3)
                col1.metric("总记录数", stats['total_items'])
                col2.metric("匹配成功", stats['matched_items'])
                col3.metric("匹配失败", stats['unmatched_items'])

                # 日期筛选
                st.subheader("选择导出月份")
                min_date = result_df['日期'].min()
                max_date = result_df['日期'].max()
                selected_month = st.selectbox(
                    "选择月份",
                    options=pd.date_range(start=min_date, end=max_date, freq='M').strftime("%Y%m"),
                    format_func=lambda x: f"{x[:4]}年{x[4:]}月"
                )

                # 客户名称输入
                customer = st.text_input("客户名称", value="恩龙")

                # 数据预览
                st.subheader("数据预览")
                month_mask = result_df['日期'].dt.strftime("%Y%m") == selected_month
                preview_df = result_df[month_mask].copy()
                
                # 显示数据表格
                edited_df = st.data_editor(
                    preview_df,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "日期": st.column_config.DateColumn("日期", format="YYYY-MM-DD"),
                        "数量": st.column_config.NumberColumn("数量", format="%.2f"),
                        "单价": st.column_config.NumberColumn("单价", format="%.2f"),
                        "金额": st.column_config.NumberColumn("金额", format="%.2f"),
                    }
                )

                # 导出按钮
                if st.button("生成对账单"):
                    try:
                        with st.spinner("正在生成对账单..."):
                            # 导出文件
                            export_path = exporter.export_statement(edited_df, selected_month, customer)
                            st.success(f"对账单已生成: {export_path}")
                    except Exception as e:
                        st.error(f"生成对账单失败: {str(e)}")
                        logger.error(f"生成对账单失败: {str(e)}")

        except Exception as e:
            st.error(f"处理文件时发生错误: {str(e)}")
            logger.error(f"处理文件时发生错误: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists("temp"):
                for file in os.listdir("temp"):
                    os.remove(os.path.join("temp", file))
                os.rmdir("temp")

if __name__ == "__main__":
    main()