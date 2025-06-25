"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: registry.py
@DateTime: 2024-12-19
@Docs: 应用注册管理器
"""

from app.base.base_app import BaseApp
from app.utils.logger import logger


class AppRegistry:
    """应用注册管理器

    管理系统中所有可用应用的注册和加载
    """

    def __init__(self):
        """初始化注册器"""
        self._apps = {}
        logger.debug("应用注册器初始化完成")

    def register_app(self, app_class: type[BaseApp]) -> None:
        """注册应用

        Args:
            app_class: 应用类
        """
        try:
            app_instance = app_class()
            app_name = app_instance.get_name()
            self._apps[app_name] = app_class
            logger.info(f"应用注册成功: {app_name} | 类: {app_class.__name__}")
        except Exception as e:
            logger.exception(f"应用注册失败: {app_class.__name__} | 错误: {str(e)}")
            raise

    def get_available_apps(self) -> dict:
        """获取可用应用列表

        Returns:
            应用名称到描述的映射字典
        """
        logger.debug(f"获取可用应用列表，共 {len(self._apps)} 个应用")
        try:
            apps_info = {name: cls().get_description() for name, cls in self._apps.items()}
            logger.debug(f"应用信息获取成功: {list(apps_info.keys())}")
            return apps_info
        except Exception as e:
            logger.exception(f"获取应用信息失败: {str(e)}")
            return {}

    def load_app(self, name: str) -> BaseApp:
        """加载应用实例

        Args:
            name: 应用名称

        Returns:
            应用实例

        Raises:
            ValueError: 当应用未注册时
        """
        logger.debug(f"尝试加载应用: {name}")

        if name not in self._apps:
            error_msg = f"应用未注册: {name}"
            logger.error(error_msg)
            raise ValueError(f"App {name} not registered")

        try:
            app_instance = self._apps[name]()
            logger.info(f"应用加载成功: {name}")
            return app_instance
        except Exception as e:
            error_msg = f"应用加载失败: {name} | 错误: {str(e)}"
            logger.exception(error_msg)
            raise

    def get_app_names(self) -> list[str]:
        """获取应用名称列表

        Returns:
            应用名称列表
        """
        app_names = list(self._apps.keys())
        logger.debug(f"获取应用名称列表: {app_names}")
        return app_names

    def is_app_registered(self, name: str) -> bool:
        """检查应用是否已注册

        Args:
            name: 应用名称

        Returns:
            是否已注册
        """
        is_registered = name in self._apps
        logger.debug(f"检查应用注册状态: {name} | 已注册: {is_registered}")
        return is_registered

    def unregister_app(self, name: str) -> bool:
        """注销应用

        Args:
            name: 应用名称

        Returns:
            是否成功注销
        """
        if name in self._apps:
            del self._apps[name]
            logger.info(f"应用注销成功: {name}")
            return True
        else:
            logger.warning(f"尝试注销未注册的应用: {name}")
            return False
