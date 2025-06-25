"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: welcome_app.py
@DateTime: 2024-12-19
@Docs: 欢迎页应用
"""

import polars as pl
import streamlit as st

from app.base.base_app import BaseApp
from app.state.session_manager import SessionManager
from app.utils.logger import log_function_calls, logger


class WelcomeApp(BaseApp):
    """欢迎页应用

    提供系统介绍、功能说明、快速开始指南等内容
    """

    @log_function_calls(include_args=False)
    def __init__(self):
        """初始化欢迎页应用"""
        logger.info("初始化欢迎页应用")

        # 尝试从全局服务管理器获取应用注册器
        try:
            # 这里我们需要通过其他方式获取应用注册器
            self.app_registry = None
            logger.debug("全局服务管理器不可用，将在渲染时获取注册器")
        except Exception as e:
            logger.warning(f"无法获取应用注册器: {str(e)}")
            self.app_registry = None

        logger.info("欢迎页应用初始化完成")

    def get_name(self) -> str:
        """获取应用名称"""
        return "欢迎页"

    def get_description(self) -> str:
        """获取应用描述"""
        return "系统介绍和快速开始指南"

    def validate_input(self, data: pl.DataFrame) -> bool:
        """验证输入数据

        欢迎页不需要输入数据，始终返回True

        Args:
            data: 输入数据

        Returns:
            始终返回True
        """
        return True

    @log_function_calls()
    def render(self) -> None:
        """渲染欢迎页界面"""
        logger.info("开始渲染欢迎页")

        # # 页面标题和LOGO
        # self._render_header()

        # 快速开始指南和功能特色
        self._render_main_content()

        # 系统状态
        self._render_system_status()

        # 应用预览
        self._render_app_preview()

        # 帮助信息
        self._render_help_section()

        logger.debug("欢迎页渲染完成")

    # def _render_header(self) -> None:
    #     """渲染页面头部"""
    #     logger.debug("渲染页面头部")

    #     col1, col2, col3 = st.columns([1, 2, 1])
    #     with col2:
    #         st.markdown(
    #             """
    #         <div style="text-align: center;">
    #             <h2>📊 数据表处理系统</h2>
    #             <p style="font-size: 18px; color: #666;">专业的数据表处理与分析工具</p>
    #         </div>
    #         """,
    #             unsafe_allow_html=True,
    #         )

    #     st.markdown("---")

    def _render_main_content(self) -> None:
        """渲染主要内容"""
        logger.debug("渲染主要内容")

        # 简化为仪表盘样式，不显示详细的使用说明
        pass

    def _render_system_status(self) -> None:
        """渲染系统状态"""
        logger.debug("渲染系统状态")

        st.markdown("## 📊 系统状态")

        try:
            # 尝试获取应用注册器
            app_registry = self._get_app_registry()

            if app_registry:
                available_apps = app_registry.get_available_apps()
            else:
                available_apps = {}

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="🎯 可用应用", value=len(available_apps), help="系统中注册的数据处理应用数量")

            with col2:
                current_app = SessionManager.get_state("current_app")
                session_status = "活跃" if current_app and current_app != "欢迎页" else "待选择"
                status_color = "🟢" if session_status == "活跃" else "🟡"
                st.metric(label="🔄 会话状态", value=f"{status_color} {session_status}", help="当前会话的状态")

            with col3:
                uploaded_files = SessionManager.get_state("uploaded_files") or []
                st.metric(label="📁 已上传文件", value=len(uploaded_files), help="当前会话中已上传的文件数量")

            with col4:
                processed_data = SessionManager.get_state("processed_data")
                data_status = "已处理" if processed_data is not None else "无数据"
                data_color = "🟢" if processed_data is not None else "⚪"
                st.metric(label="📊 数据状态", value=f"{data_color} {data_status}", help="当前处理的数据状态")

            logger.debug(f"系统状态显示完成 | 可用应用: {len(available_apps)}")

        except Exception as e:
            logger.exception(f"系统状态显示失败: {str(e)}")
            st.error("系统状态获取失败")

        st.markdown("---")

    def _render_app_preview(self) -> None:
        """渲染可用应用"""
        logger.debug("渲染可用应用")

        try:
            app_registry = self._get_app_registry()

            if not app_registry:
                st.warning("无法获取应用列表")
                return

            available_apps = app_registry.get_available_apps()

            # 过滤掉欢迎页本身
            filtered_apps = {k: v for k, v in available_apps.items() if k != "欢迎页"}

            if not filtered_apps:
                st.info("暂无其他可用的应用")
                return

            st.markdown("## 🎯 可用应用")

            # 使用卡片样式显示应用
            cols = st.columns(min(len(filtered_apps), 3))  # 最多3列

            for i, (app_name, app_description) in enumerate(filtered_apps.items()):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 8px 0;">
                            <h4>{app_name}</h4>
                            <p style="color: #666; font-size: 14px;">{app_description}</p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        if st.button(f"使用 {app_name}", key=f"select_{app_name}", use_container_width=True):
                            SessionManager.set_state("current_app", app_name)
                            logger.info(f"从欢迎页选择应用: {app_name}")
                            st.rerun()

        except Exception as e:
            logger.exception(f"可用应用渲染失败: {str(e)}")
            st.error("应用列表加载失败")

        st.markdown("---")

    def _render_help_section(self) -> None:
        """渲染帮助部分"""
        logger.debug("渲染帮助部分")

        col1, col2 = st.columns(2)

        with col1:
            with st.expander("❓ 常见问题", expanded=False):
                st.markdown("""
                **Q: 支持哪些文件格式？**
                A: CSV 和 Excel 文件（.csv, .xlsx, .xls）

                **Q: 文件大小限制？**
                A: 单个文件最大 100MB

                **Q: 数据是否会保存？**
                A: 仅在浏览器会话中处理，不保存到服务器
                """)

        with col2:
            with st.expander("📞 帮助与支持", expanded=False):
                st.markdown("""
                **技术支持**
                📧 lijianqiao2906@live.com

                **系统信息**
                - 版本: 1.0.0
                - 技术栈: Streamlit + Polars
                """)

    def _get_app_registry(self):
        """获取应用注册器

        Returns:
            应用注册器实例，获取失败时返回None
        """
        try:
            # 从 session_state 中获取，这需要在主应用中设置
            if hasattr(st.session_state, "_app_registry"):
                return st.session_state._app_registry

            # 或者尝试从全局导入（需要确保已初始化）
            # 这里返回None，让调用方处理
            return None

        except Exception as e:
            logger.debug(f"获取应用注册器失败: {str(e)}")
            return None
