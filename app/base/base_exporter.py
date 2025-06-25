"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base_exporter.py
@DateTime: 2024-12-19
@Docs: 导出器基础接口定义
"""

from abc import ABC, abstractmethod

import polars as pl


class BaseExporter(ABC):
    """导出器基础接口

    定义数据导出器必须实现的基础方法
    """

    @abstractmethod
    def export(self, df: pl.DataFrame, **kwargs) -> bytes:
        """导出数据

        Args:
            df: 待导出的数据
            **kwargs: 导出参数

        Returns:
            导出的字节数据
        """
        pass

    @abstractmethod
    def get_mime_type(self) -> str:
        """获取MIME类型

        Returns:
            MIME类型字符串
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """获取文件扩展名

        Returns:
            文件扩展名
        """
        pass
