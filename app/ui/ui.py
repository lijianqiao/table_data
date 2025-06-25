"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: ui.py
@DateTime: 2024-12-19
@Docs: 主UI界面
"""

import streamlit as st

from app.core.registry import AppRegistry
from app.state.session_manager import SessionManager
from app.utils.logger import log_function_calls, logger


class MainUI:
    """主UI界面类

    负责整体布局和页面渲染
    """

    def __init__(self, app_registry: AppRegistry):
        """初始化主UI

        Args:
            app_registry: 应用注册器
        """
        self.app_registry = app_registry
        logger.info("主UI初始化完成")

    @log_function_calls()
    def render(self) -> None:
        """渲染主界面"""
        logger.info("开始渲染主界面")

        # 初始化会话状态
        SessionManager.init_session_state()
        logger.debug("会话状态初始化完成")

        # 设置页面配置
        self._setup_page_config()

        # 创建布局
        self._create_main_layout()

        # 渲染侧边栏
        self._render_sidebar()

        # 渲染主内容区
        self._render_main_content()

        logger.debug("主界面渲染完成")

    def _setup_page_config(self) -> None:
        """设置页面配置"""
        logger.debug("设置页面配置")

        st.set_page_config(page_title="数据表处理系统", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

    def _create_main_layout(self) -> None:
        """创建主布局"""
        logger.debug("创建主页面布局")

        st.title("📊 数据表处理系统")
        st.markdown("---")

    @log_function_calls()
    def _render_sidebar(self) -> None:
        """渲染侧边栏"""
        logger.debug("开始渲染侧边栏")

        with st.sidebar:
            st.header("🔧 应用控制")

            # 应用选择器
            self._render_app_selector()

            st.markdown("---")

            # 项目信息
            self._render_project_info()

    @log_function_calls()
    def _render_app_selector(self) -> None:
        """渲染应用选择器"""
        logger.debug("渲染应用选择器")

        st.subheader("🎯 选择应用")

        try:
            available_apps = self.app_registry.get_available_apps()
            app_names = list(available_apps.keys())

            if not app_names:
                st.error("没有可用的应用")
                logger.warning("没有可用的应用")
                return

            logger.debug(f"可用应用: {app_names}")

            selected_app_name = st.selectbox(
                "选择要使用的应用：",
                options=app_names,
                format_func=lambda x: f"{x} - {available_apps[x]}",
                key="selected_app_name",
            )

            # 只有当选择的应用发生变化时，才更新状态并清空相关数据
            current_app = SessionManager.get_state("current_app")
            if selected_app_name != current_app:
                logger.info(f"应用切换: {current_app} -> {selected_app_name}")
                SessionManager.set_state("current_app", selected_app_name)
                # 清空相关状态，但保留处理后的数据
                SessionManager.clear_state(["selected_columns"])

        except Exception as e:
            error_msg = f"应用选择器渲染失败: {str(e)}"
            logger.exception(error_msg)
            st.error(error_msg)

    def _render_project_info(self) -> None:
        """渲染项目信息"""
        logger.debug("渲染项目信息")

        st.subheader("📋 项目信息")

        project_info = """
        **数据表处理系统**

        **版本**: 1.0.0
        **作者**: lijianqiao

        #### 🔗 相关链接
        - [GitHub](https://github.com)
        - [文档](https://docs.github.com)
        """

        st.markdown(project_info)

    @log_function_calls()
    def _render_main_content(self) -> None:
        """渲染主内容区"""
        logger.debug("开始渲染主内容区")

        current_app_name = SessionManager.get_state("current_app")

        if not current_app_name:
            # 显示欢迎页面
            self._render_welcome_page()
        else:
            # 渲染选中的应用
            self._render_selected_app(current_app_name)

    def _render_welcome_page(self) -> None:
        """渲染欢迎页面"""
        logger.debug("渲染欢迎页面")

        st.markdown("""
        ## 👋 欢迎使用数据表处理系统

        ### 🚀 快速开始
        1. **选择应用**: 在左侧边栏选择您需要的数据处理应用
        2. **上传文件**: 根据应用指引上传您的数据文件
        3. **处理数据**: 按照应用流程处理您的数据
        4. **导出结果**: 下载处理后的数据文件

        ### 💡 功能特色
        - 📁 **多格式支持**: 支持 CSV、Excel 等常见格式
        - 🔗 **智能合并**: 自动识别和合并多个数据表
        - ⚙️ **数据预处理**: 提供清理、去重等数据预处理功能
        - 📤 **高效导出**: 优化的数据导出，支持大文件处理

        ### 📊 系统状态
        """)

        # 显示系统状态
        try:
            available_apps = self.app_registry.get_available_apps()
            col1, col2 = st.columns(2)

            with col1:
                st.metric("可用应用", len(available_apps))

            with col2:
                session_status = "活跃" if SessionManager.get_state("current_app") else "待选择"
                st.metric("会话状态", session_status)

            logger.debug(f"系统状态显示完成 | 可用应用: {len(available_apps)}")

        except Exception as e:
            logger.exception(f"系统状态显示失败: {str(e)}")
            st.error("系统状态获取失败")

    @log_function_calls()
    def _render_selected_app(self, app_name: str) -> None:
        """渲染选中的应用

        Args:
            app_name: 应用名称
        """
        logger.info(f"开始渲染应用: {app_name}")

        try:
            # 加载应用实例
            app_instance = self.app_registry.load_app(app_name)
            logger.debug(f"应用实例加载成功: {app_name}")

            # 渲染应用界面
            app_instance.render()
            logger.debug(f"应用界面渲染完成: {app_name}")

        except Exception as e:
            error_msg = f"应用渲染失败: {app_name} | 错误: {str(e)}"
            logger.exception(error_msg)
            st.error(f"应用加载失败: {str(e)}")

            # 显示错误详情
            with st.expander("错误详情"):
                st.code(str(e))

    def get_current_app(self) -> str | None:
        """获取当前选中的应用

        Returns:
            当前应用名称，未选择时返回None
        """
        current_app = SessionManager.get_state("current_app")
        logger.debug(f"获取当前应用: {current_app}")
        return current_app
