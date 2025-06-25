"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base_app.py
@DateTime: 2024-12-19
@Docs: 应用基础接口定义
"""

from abc import ABC, abstractmethod

import polars as pl


class BaseApp(ABC):
    """应用基础接口

    定义所有应用必须实现的基础方法
    """

    @abstractmethod
    def get_name(self) -> str:
        """获取应用名称

        Returns:
            应用名称
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取应用描述

        Returns:
            应用描述信息
        """
        pass

    @abstractmethod
    def render(self) -> None:
        """渲染应用界面

        渲染应用的用户界面
        """
        pass

    @abstractmethod
    def validate_input(self, data: pl.DataFrame) -> bool:
        """验证输入数据

        Args:
            data: 待验证的数据

        Returns:
            验证是否通过
        """
        pass

    def get_config(self) -> dict:
        """获取应用配置

        Returns:
            应用配置字典
        """
        return {}
