"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base_processor.py
@DateTime: 2024-12-19
@Docs: 处理器基础接口定义
"""

from abc import ABC, abstractmethod

import polars as pl


class BaseProcessor(ABC):
    """处理器基础接口

    定义数据处理器必须实现的基础方法
    """

    @abstractmethod
    def process(self, df: pl.DataFrame) -> pl.DataFrame:
        """处理数据

        Args:
            df: 待处理的数据

        Returns:
            处理后的数据
        """
        pass

    @abstractmethod
    def validate(self, df: pl.DataFrame) -> bool:
        """验证数据

        Args:
            df: 待验证的数据

        Returns:
            验证是否通过
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取处理器描述

        Returns:
            处理器描述信息
        """
        pass
