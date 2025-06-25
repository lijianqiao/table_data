"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: service_manager.py
@DateTime: 2024-12-19
@Docs: 全局服务管理器
"""

from typing import Any

from app.core.container import Container


class ServiceManager:
    """全局服务管理器

    提供应用访问注册服务的统一接口
    """

    _instance: "ServiceManager | None" = None
    _container: Container | None = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, container: Container) -> None:
        """初始化服务管理器

        Args:
            container: 依赖注入容器
        """
        cls._container = container

    @classmethod
    def get_service(cls, name: str) -> Any:
        """获取服务实例

        Args:
            name: 服务名称

        Returns:
            服务实例

        Raises:
            RuntimeError: 服务管理器未初始化
            ValueError: 服务未注册
        """
        if cls._container is None:
            raise RuntimeError("服务管理器未初始化")

        return cls._container.get(name)

    @classmethod
    def is_initialized(cls) -> bool:
        """检查是否已初始化

        Returns:
            是否已初始化
        """
        return cls._container is not None
