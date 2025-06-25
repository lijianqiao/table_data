"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: export_panel.py
@DateTime: 2024-12-19
@Docs: 导出面板组件
"""

from datetime import datetime

import polars as pl
import streamlit as st

from app.components.error_handler import ErrorHandler
from app.handlers.export_handler import ExportHandler
from app.utils.logger import log_function_calls, logger


class ExportPanel:
    """导出面板

    提供数据导出功能界面
    """

    def __init__(self):
        """初始化导出面板"""
        self.export_handler = ExportHandler()
        logger.debug("导出面板初始化完成")

    @log_function_calls()
    def render(self, df: pl.DataFrame, selected_columns: list[str]):
        """渲染导出面板

        Args:
            df: 数据DataFrame
            selected_columns: 选中的字段列表
        """
        logger.info(f"渲染导出面板 | 数据行数: {len(df)} | 选择字段数: {len(selected_columns)}")

        st.subheader("📤 导出数据")

        default_filename = f"export_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = st.text_input("文件名：", value=default_filename, help="不需要包含文件扩展名")

        # 导出格式固定为xlsx
        export_format = "xlsx"

        try:
            export_summary = self.export_handler.get_export_summary(df, selected_columns)
            logger.debug(
                f"导出摘要生成 | 行数: {export_summary['total_rows']} | 预估大小: {export_summary['estimated_size']}"
            )

            st.info(f"""
            **导出摘要：**
            - 总行数: {export_summary["total_rows"]:,}
            - 总列数: {export_summary["total_columns"]}
            - 预估大小: {export_summary["estimated_size"]}
            """)

            with st.expander("📋 导出字段列表"):
                st.write(selected_columns)

            if st.button("🚀 生成导出文件", type="primary", use_container_width=True):
                logger.info(f"用户点击导出按钮 | 文件名: {filename} | 格式: {export_format}")
                self._handle_export(df, selected_columns, filename, export_format)

        except Exception as e:
            logger.exception(f"导出面板渲染失败: {str(e)}")
            ErrorHandler.show_error("导出面板显示失败", str(e))

    @log_function_calls()
    def _handle_export(self, df: pl.DataFrame, columns: list[str], filename: str, file_format: str):
        """处理导出操作

        Args:
            df: 数据DataFrame
            columns: 要导出的字段列表
            filename: 文件名
            file_format: 文件格式
        """
        logger.info(
            f"开始处理导出 | 文件名: {filename} | 格式: {file_format} | 数据行数: {len(df)} | 导出字段数: {len(columns)}"
        )

        with st.spinner("正在生成导出文件..."):
            try:
                # 导出数据
                export_data = self.export_handler.export_excel(df, columns)
                download_filename = f"{filename}.{file_format}"

                logger.info(f"文件导出成功 | 文件名: {download_filename} | 文件大小: {len(export_data)} bytes")

                # 直接显示下载按钮
                st.download_button(
                    label="💾 下载文件",
                    data=export_data,
                    file_name=download_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_button",
                )

                success_msg = f"文件已生成：{download_filename}"
                logger.info(success_msg)
                ErrorHandler.show_success("文件已生成，请点击上方按钮下载。")

            except Exception as e:
                error_msg = f"导出失败: {str(e)}"
                logger.exception(error_msg)
                ErrorHandler.show_error("导出失败", str(e))
