"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: ui_config.py
@DateTime: 2024-12-19
@Docs: UI界面相关配置
"""


class UIConfig:
    """UI配置类"""

    # 数据预览配置
    PREVIEW_ROWS = 100
    MAX_PREVIEW_ROWS = 1000

    # 布局配置
    SIDEBAR_WIDTH = 300
    MAIN_CONTENT_WIDTH = 800

    # 组件配置
    PROGRESS_BAR_HEIGHT = 20
    ERROR_MESSAGE_DURATION = 5000

    # 导出配置
    DEFAULT_EXPORT_FORMAT = "xlsx"
    EXPORT_FORMATS = ["xlsx"]

    # 颜色主题
    COLORS = {"primary": "#1f77b4", "success": "#2ca02c", "warning": "#ff7f0e", "danger": "#d62728", "info": "#17a2b8"}
