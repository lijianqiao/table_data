"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: merge.py
@DateTime: 2024-12-19
@Docs: 数据合并应用
"""

import polars as pl
import streamlit as st

from app.base.base_app import BaseApp
from app.components.column_selector import ColumnSelector
from app.components.data_preview import DataPreview
from app.components.error_handler import ErrorHandler
from app.components.export_panel import ExportPanel
from app.components.file_uploader import FileUploader
from app.handlers.data_processor import DataProcessor
from app.handlers.file_handler import FileHandler
from app.state.session_manager import SessionManager
from app.utils.file_validator import FileValidator
from app.utils.logger import log_function_calls, logger


class MergeApp(BaseApp):
    """数据合并应用

    合并多个数据表为一个统一的数据表
    """

    @log_function_calls()
    def __init__(self):
        """初始化应用"""
        logger.info("初始化数据合并应用")

        # 使用全局服务管理器获取服务，如果不可用则创建本地实例
        try:
            from app.core.service_manager import ServiceManager

            self.file_validator = ServiceManager.get_service("file_validator")
            self.file_uploader = ServiceManager.get_service("file_uploader")
            self.file_handler = ServiceManager.get_service("file_handler")
            self.data_processor = ServiceManager.get_service("data_processor")
            logger.debug("使用全局服务管理器获取服务")

        except (RuntimeError, ValueError):
            # 兜底：创建本地服务实例
            logger.warning("全局服务管理器不可用，创建本地服务实例")
            self.file_validator = FileValidator()
            self.file_uploader = FileUploader(self.file_validator)
            self.file_handler = FileHandler()
            self.data_processor = DataProcessor()

        logger.info("数据合并应用初始化完成")

    def get_name(self) -> str:
        """获取应用名称"""
        return "数据合并"

    def get_description(self) -> str:
        """获取应用描述"""
        return "合并多个数据表为一个统一的数据表"

    def validate_input(self, data: pl.DataFrame) -> bool:
        """验证输入数据

        Args:
            data: 待验证的数据

        Returns:
            验证是否通过
        """
        is_valid = data is not None and len(data) > 0
        logger.debug(
            f"输入数据验证: {'通过' if is_valid else '失败'} | 数据行数: {len(data) if data is not None else 0}"
        )
        return is_valid

    @log_function_calls()
    def render(self) -> None:
        """渲染应用界面"""
        logger.info("开始渲染数据合并应用界面")

        st.header("🔗 数据合并工具")
        st.markdown("将多个数据表合并为一个统一的数据表")

        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs(["📁 文件上传", "📋 数据预览", "🎯 字段选择", "📤 导出数据"])

        with tab1:
            self._render_file_upload_tab()

        with tab2:
            self._render_data_preview_tab()

        with tab3:
            self._render_column_selection_tab()

        with tab4:
            self._render_export_tab()

        logger.debug("数据合并应用界面渲染完成")

    @log_function_calls()
    def _render_file_upload_tab(self) -> None:
        """渲染文件上传标签页"""
        logger.debug("渲染文件上传标签页")

        st.subheader("📁 文件上传")

        # 添加功能说明
        st.markdown("""
        **数据合并工具说明：**
        - 支持 CSV、Excel 格式，可同时上传多个文件
        - 要求所有文件的字段结构完全一致
        - 自动添加"来源"列，记录每行数据的来源文件
        - 适用于需要合并多个相同结构数据表的场景
        """)

        # 文件上传
        uploaded_files = self.file_uploader.render()

        if uploaded_files:
            logger.info(f"用户上传了 {len(uploaded_files)} 个文件")
            SessionManager.set_state("uploaded_files", uploaded_files)

            # 处理文件并合并数据
            self._process_and_merge_files(uploaded_files)
        else:
            logger.debug("没有上传文件")
            st.info("请上传至少一个数据文件")

    @log_function_calls()
    def _process_and_merge_files(self, uploaded_files: list) -> None:
        """处理并合并文件

        Args:
            uploaded_files: 上传的文件列表
        """
        logger.info(f"开始处理和合并文件 | 文件数量: {len(uploaded_files)}")

        try:
            with st.spinner("正在读取和合并文件..."):
                all_dataframes = []
                source_names = []

                # 读取每个文件并准备来源信息
                for i, file in enumerate(uploaded_files):
                    logger.debug(f"处理文件 {i + 1}/{len(uploaded_files)}: {file.name}")

                    try:
                        dfs = self.file_handler.read_file(file)

                        # 提取文件名作为来源标识（去掉扩展名）
                        import os

                        source_name = os.path.splitext(file.name)[0]

                        # 为每个工作表添加来源信息
                        for j, df in enumerate(dfs):
                            all_dataframes.append(df)
                            # 如果有多个工作表，添加工作表标识
                            if len(dfs) > 1:
                                source_names.append(f"{source_name}_工作表{j + 1}")
                            else:
                                source_names.append(source_name)

                        logger.debug(f"文件 {file.name} 读取成功，包含 {len(dfs)} 个数据表")

                    except Exception as e:
                        error_msg = f"文件 {file.name} 读取失败: {str(e)}"
                        logger.error(error_msg)
                        ErrorHandler.show_error(error_msg)
                        continue

                if not all_dataframes:
                    error_msg = "没有成功读取任何数据"
                    logger.error(error_msg)
                    ErrorHandler.show_error(error_msg)
                    return

                # 使用新的合并方法，专门处理字段一致的场景
                logger.info(f"开始合并数据 | 总数据表数量: {len(all_dataframes)} | 来源数量: {len(source_names)}")
                merged_data = self.data_processor.merge_identical_dataframes(all_dataframes, source_names)

                # 保存到会话状态
                SessionManager.set_state("processed_data", merged_data)

                # 显示成功信息和来源统计
                success_msg = (
                    f"文件处理完成！合并后数据: {len(merged_data)} 行 x {len(merged_data.columns)} 列（包含来源列）"
                )
                logger.info(success_msg)
                ErrorHandler.show_success(success_msg)

                # 显示来源统计信息
                if "来源" in merged_data.columns:
                    source_stats = merged_data.group_by("来源").len().sort("len", descending=True)
                    st.subheader("📊 数据来源统计")
                    stats_data = []
                    for row in source_stats.iter_rows():
                        source, count = row
                        stats_data.append({"来源文件": source, "数据行数": count})

                    import polars as pl

                    stats_df = pl.DataFrame(stats_data)
                    st.dataframe(stats_df, use_container_width=True)

        except Exception as e:
            error_msg = f"文件处理失败: {str(e)}"
            logger.exception(error_msg)
            ErrorHandler.show_error("文件处理失败", str(e))

    @log_function_calls()
    def _render_data_preview_tab(self) -> None:
        """渲染数据预览标签页"""
        logger.debug("渲染数据预览标签页")

        processed_data = SessionManager.get_state("processed_data")

        if processed_data is None:
            st.info("请先在'文件上传'标签页中上传并处理文件")
            logger.debug("没有可预览的数据")
            return

        logger.debug(f"显示数据预览 | 行数: {len(processed_data)} | 列数: {len(processed_data.columns)}")

        preview = DataPreview()
        st.subheader("📊 合并结果预览")

        # 数据摘要
        with st.expander("📊 数据摘要", expanded=True):
            preview.render_summary(processed_data)

        # 详细数据预览
        with st.expander("📋 详细数据预览", expanded=False):
            preview.render_sample_data(processed_data)

        # 字段详情
        with st.expander("📊 字段详情", expanded=False):
            preview.render_column_info(processed_data)

    @log_function_calls()
    def _render_column_selection_tab(self) -> None:
        """渲染字段选择标签页"""
        logger.debug("渲染字段选择标签页")

        processed_data = SessionManager.get_state("processed_data")

        if processed_data is None:
            st.info("请先在'文件上传'标签页中上传并处理文件")
            logger.debug("没有可选择字段的数据")
            return

        logger.debug(f"显示字段选择 | 可选字段数: {len(processed_data.columns)}")

        selector = ColumnSelector()
        selected_columns, is_confirmed = selector.render_with_preview(processed_data)

        # 只有在确认后才保存选择的字段
        if is_confirmed and selected_columns:
            SessionManager.set_state("selected_columns", selected_columns)
            logger.info(f"用户确认选择了 {len(selected_columns)} 个字段")

            # 显示确认成功的提示
            st.balloons()  # 添加一个小的庆祝效果

        elif selected_columns and not is_confirmed:
            logger.debug(f"用户选择了 {len(selected_columns)} 个字段但尚未确认")
        else:
            logger.debug("用户未选择任何字段")

    @log_function_calls()
    def _render_export_tab(self) -> None:
        """渲染导出标签页"""
        logger.debug("渲染导出标签页")

        processed_data = SessionManager.get_state("processed_data")
        selected_columns = SessionManager.get_state("selected_columns")

        if processed_data is None:
            st.info("请先在'文件上传'标签页中上传并处理文件")
            logger.debug("没有可导出的数据")
            return

        if not selected_columns:
            st.info("请先在'字段选择'标签页中选择要导出的字段")
            logger.debug("没有选择要导出的字段")
            return

        logger.info(f"显示导出面板 | 数据行数: {len(processed_data)} | 选择字段数: {len(selected_columns)}")

        # 显示导出面板
        try:
            from app.core.service_manager import ServiceManager

            _ = ServiceManager.get_service("export_handler")
            logger.debug("使用全局服务获取导出处理器")
        except (RuntimeError, ValueError):
            from app.handlers.export_handler import ExportHandler

            _ = ExportHandler()
            logger.debug("创建本地导出处理器实例")

        export_panel = ExportPanel()
        export_panel.render(processed_data, selected_columns)
