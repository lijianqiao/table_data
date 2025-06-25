"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: data_preview.py
@DateTime: 2024-12-19
@Docs: 数据预览组件
"""

import polars as pl
import streamlit as st


class DataPreview:
    """数据预览组件

    提供数据摘要、样本数据和列信息的展示
    """

    def __init__(self, max_rows: int = 100):
        """初始化数据预览组件

        Args:
            max_rows: 最大显示行数
        """
        self.max_rows = max_rows

    def render_summary(self, df: pl.DataFrame) -> None:
        """渲染数据摘要

        Args:
            df: 要预览的数据框
        """
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("总行数", f"{len(df):,}")

        with col2:
            st.metric("总列数", len(df.columns))

        with col3:
            st.metric("内存使用", f"{df.estimated_size() / 1024 / 1024:.2f} MB")

        with col4:
            null_count = df.null_count().sum_horizontal().item()
            st.metric("空值数量", f"{null_count:,}")

    def render_sample_data(self, df: pl.DataFrame, rows: int | None = None) -> None:
        """渲染样本数据

        Args:
            df: 要预览的数据框
            rows: 显示行数
        """
        display_rows = rows or self.max_rows

        st.subheader("📋 数据预览")

        if len(df) > display_rows:
            st.info(f"显示前 {display_rows} 行数据，共 {len(df)} 行")
            st.dataframe(df.head(display_rows), use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

    def render_column_info(self, df: pl.DataFrame) -> None:
        """渲染列信息

        Args:
            df: 要分析的数据框
        """
        st.subheader("📊 列信息")

        column_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].null_count()
            unique_count = df[col].n_unique()

            column_info.append(
                {
                    "列名": col,
                    "数据类型": dtype,
                    "空值数": null_count,
                    "唯一值数": unique_count,
                    "空值比例": f"{null_count / len(df) * 100:.1f}%",
                }
            )

        info_df = pl.DataFrame(column_info)
        st.dataframe(info_df, use_container_width=True)
