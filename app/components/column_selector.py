"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: column_selector.py
@DateTime: 2024-12-19
@Docs: 字段选择组件
"""

import polars as pl
import streamlit as st


class ColumnSelector:
    """字段选择器

    提供数据字段选择功能
    """

    def render(self, available_columns: list[str], default_selected: list[str] | None = None) -> list[str]:
        """渲染字段选择界面

        Args:
            available_columns: 可用字段列表
            default_selected: 默认选中的字段列表

        Returns:
            选中的字段列表
        """
        st.subheader("🎯 选择导出字段")

        # 使用 st.checkbox 实现全选/取消全选
        select_all = st.checkbox("全选/取消全选", value=True)

        if select_all:
            default_selection = available_columns
        else:
            default_selection = default_selected or []

        # 字段选择
        selected_columns = st.multiselect(
            "选择要导出的字段：", options=available_columns, default=default_selection, help="选择需要导出的数据字段"
        )

        # 显示选择摘要
        if selected_columns:
            st.info(f"已选择 {len(selected_columns)} / {len(available_columns)} 个字段")
        else:
            st.warning("请至少选择一个字段")

        return selected_columns

    def render_with_preview(self, df: pl.DataFrame, max_preview_rows: int = 5) -> tuple[list[str], bool]:
        """带预览的字段选择

        Args:
            df: 数据DataFrame
            max_preview_rows: 最大预览行数

        Returns:
            元组：(选中的字段列表, 是否已确认)
        """
        # 使用 st.form 来防止每次选择都触发重新加载
        with st.form("column_selection_form"):
            st.subheader("🎯 选择导出字段")

            # 使用 st.checkbox 实现全选/取消全选
            select_all = st.checkbox("全选/取消全选", value=True)

            if select_all:
                default_selection = df.columns
            else:
                default_selection = []

            # 字段选择
            selected_columns = st.multiselect(
                "选择要导出的字段：", options=df.columns, default=default_selection, help="选择需要导出的数据字段"
            )

            # 显示选择摘要
            if selected_columns:
                st.info(f"已选择 {len(selected_columns)} / {len(df.columns)} 个字段")
            else:
                st.warning("请至少选择一个字段")

            # 添加确认按钮区域
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                # 确认按钮 - 使用 form_submit_button
                confirm_button = st.form_submit_button(
                    "🎯 确认选择的字段", type="primary", use_container_width=True, help="确认字段选择并显示预览"
                )

        # 只有在点击确认按钮后才显示预览
        if confirm_button and selected_columns:
            st.success(f"✅ 已确认选择 {len(selected_columns)} 个字段")

            # 显示字段预览
            st.subheader("👀 选择字段预览")
            preview_df = df.select(selected_columns).head(max_preview_rows)
            st.dataframe(preview_df, use_container_width=True)

            # 显示字段详细信息
            self.show_column_info(df, selected_columns)

            return selected_columns, True

        # 如果没有确认，返回空列表和False
        return [], False

    def show_column_info(self, df: pl.DataFrame, selected_columns: list[str]) -> None:
        """显示选中字段的详细信息

        Args:
            df: 数据DataFrame
            selected_columns: 选中的字段列表
        """
        if not selected_columns:
            return

        st.subheader("📊 字段详细信息")

        column_info = []
        for col in selected_columns:
            if col in df.columns:
                col_data = df[col]
                info = {
                    "字段名": col,
                    "数据类型": str(col_data.dtype),
                    "空值数": col_data.null_count(),
                    "唯一值数": col_data.n_unique(),
                    "空值比例": f"{col_data.null_count() / len(df) * 100:.1f}%" if len(df) > 0 else "0%",
                }
                column_info.append(info)

        if column_info:
            info_df = pl.DataFrame(column_info)
            st.dataframe(info_df, use_container_width=True)
