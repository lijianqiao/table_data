"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: container.py
@DateTime: 2024-12-19
@Docs: 依赖注入容器
"""

from typing import Any

from app.utils.logger import logger


class Container:
    """依赖注入容器

    提供服务注册和获取功能，支持单例模式
    """

    def __init__(self):
        """初始化容器"""
        self._services = {}
        self._singletons = {}
        logger.debug("依赖注入容器初始化完成")

    def register(self, name: str, service_class, singleton: bool = False) -> None:
        """注册服务

        Args:
            name: 服务名称
            service_class: 服务类
            singleton: 是否为单例模式
        """
        self._services[name] = (service_class, singleton)
        logger.debug(
            f"服务注册: {name} | 类型: {service_class.__name__ if hasattr(service_class, '__name__') else str(service_class)} | 单例: {singleton}"
        )

    def get(self, name: str) -> Any:
        """获取服务实例

        Args:
            name: 服务名称

        Returns:
            服务实例

        Raises:
            ValueError: 当服务未注册时
        """
        if name not in self._services:
            error_msg = f"服务未注册: {name}"
            logger.error(error_msg)
            raise ValueError(f"Service {name} not registered")

        service_class, is_singleton = self._services[name]

        try:
            if is_singleton:
                if name not in self._singletons:
                    logger.debug(f"创建单例服务实例: {name}")
                    self._singletons[name] = service_class()
                else:
                    logger.debug(f"获取已存在的单例服务: {name}")
                return self._singletons[name]

            logger.debug(f"创建新的服务实例: {name}")
            return service_class()

        except Exception as e:
            error_msg = f"服务实例化失败: {name} | 错误: {str(e)}"
            logger.exception(error_msg)
            raise

    def clear(self) -> None:
        """清空容器"""
        service_count = len(self._services)
        singleton_count = len(self._singletons)

        self._services.clear()
        self._singletons.clear()

        logger.info(f"容器已清空 | 清除服务: {service_count} | 清除单例: {singleton_count}")

    def get_registered_services(self) -> list[str]:
        """获取已注册的服务列表

        Returns:
            服务名称列表
        """
        return list(self._services.keys())

    def is_singleton(self, name: str) -> bool:
        """检查服务是否为单例

        Args:
            name: 服务名称

        Returns:
            是否为单例
        """
        if name not in self._services:
            return False
        _, is_singleton = self._services[name]
        return is_singleton
