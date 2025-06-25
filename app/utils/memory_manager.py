"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: memory_manager.py
@DateTime: 2024-12-19
@Docs: 内存管理工具
"""

import polars as pl
import psutil


class MemoryManager:
    """内存管理器

    提供内存监控和优化功能
    """

    @staticmethod
    def get_memory_usage() -> float:
        """获取当前内存使用率

        Returns:
            内存使用率（0-1之间）
        """
        return psutil.virtual_memory().percent / 100

    @staticmethod
    def check_memory_available(required_mb: float) -> bool:
        """检查是否有足够内存

        Args:
            required_mb: 需要的内存大小（MB）

        Returns:
            是否有足够内存
        """
        available_mb = psutil.virtual_memory().available / 1024 / 1024
        return available_mb > required_mb

    @staticmethod
    def optimize_dataframe(df: pl.DataFrame) -> pl.DataFrame:
        """优化DataFrame内存使用

        Args:
            df: 待优化的DataFrame

        Returns:
            优化后的DataFrame
        """
        # 转换数据类型以节省内存
        optimized_df = df

        for col in df.columns:
            if df[col].dtype == pl.Utf8:
                # 尝试转换为分类类型
                if len(df) > 0:  # 避免除零错误
                    unique_ratio = df[col].n_unique() / len(df)
                    if unique_ratio < 0.5:  # 如果唯一值比例小于50%
                        optimized_df = optimized_df.with_columns(pl.col(col).cast(pl.Categorical))

        return optimized_df

    @staticmethod
    def estimate_processing_memory(df: pl.DataFrame, factor: float = 2.0) -> float:
        """估算处理所需内存 (MB)

        Args:
            df: 待处理的DataFrame
            factor: 内存放大因子

        Returns:
            估算的内存需求（MB）
        """
        current_size = df.estimated_size() / 1024 / 1024
        return current_size * factor

    @staticmethod
    def get_memory_info() -> dict:
        """获取详细内存信息

        Returns:
            内存信息字典
        """
        memory = psutil.virtual_memory()
        return {
            "total_mb": memory.total / 1024 / 1024,
            "available_mb": memory.available / 1024 / 1024,
            "used_mb": memory.used / 1024 / 1024,
            "usage_percent": memory.percent,
        }
