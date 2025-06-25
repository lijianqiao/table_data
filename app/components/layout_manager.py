"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: layout_manager.py
@DateTime: 2024-12-19
@Docs: 布局管理组件
"""

import streamlit as st


class LayoutManager:
    """布局管理器

    提供统一的页面布局管理功能
    """

    @staticmethod
    def create_main_layout():
        """创建主布局"""
        # 设置页面配置
        st.set_page_config(page_title="数据表处理系统", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

        # 主标题
        st.title("📊 数据表处理系统")
        st.markdown("---")

    @staticmethod
    def create_sidebar():
        """创建侧边栏

        Returns:
            侧边栏容器对象
        """
        with st.sidebar:
            st.header("🔧 系统控制")
            return st.container()

    @staticmethod
    def show_progress_bar(progress: float, text: str = "处理中...") -> None:
        """显示进度条

        Args:
            progress: 进度值（0-1之间）
            text: 进度文本
        """
        progress_bar = st.progress(0)
        status_text = st.empty()

        progress_bar.progress(progress)
        status_text.text(f"{text} {progress * 100:.1f}%")

    @staticmethod
    def create_collapsible_section(title: str, expanded: bool = True):
        """创建可折叠区域

        Args:
            title: 区域标题
            expanded: 是否默认展开

        Returns:
            可折叠区域对象
        """
        return st.expander(title, expanded=expanded)

    @staticmethod
    def create_columns(ratios: list[int]):
        """创建多列布局

        Args:
            ratios: 列宽比例列表

        Returns:
            列对象列表
        """
        return st.columns(ratios)

    @staticmethod
    def create_tabs(tab_names: list[str]):
        """创建标签页

        Args:
            tab_names: 标签页名称列表

        Returns:
            标签页对象列表
        """
        return st.tabs(tab_names)

    @staticmethod
    def show_metrics(metrics: dict) -> None:
        """显示指标卡片

        Args:
            metrics: 指标字典，格式为 {标题: 值}
        """
        cols = st.columns(len(metrics))
        for i, (title, value) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(title, value)

    @staticmethod
    def create_container():
        """创建容器

        Returns:
            容器对象
        """
        return st.container()

    @staticmethod
    def add_vertical_space(lines: int = 1) -> None:
        """添加垂直间距

        Args:
            lines: 空行数量
        """
        for _ in range(lines):
            st.write("")
