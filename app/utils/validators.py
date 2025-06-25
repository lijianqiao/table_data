"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: validators.py
@DateTime: 2024-12-19
@Docs: 数据验证工具
"""

from typing import Any

import polars as pl


class DataValidator:
    """数据验证器

    提供各种数据验证功能
    """

    @staticmethod
    def validate_dataframe(df: pl.DataFrame) -> dict[str, Any]:
        """验证DataFrame基本信息

        Args:
            df: 待验证的DataFrame

        Returns:
            验证结果字典
        """
        return {
            "is_valid": df is not None and len(df) > 0,
            "row_count": len(df) if df is not None else 0,
            "column_count": len(df.columns) if df is not None else 0,
            "has_data": df is not None and len(df) > 0 and len(df.columns) > 0,
        }

    @staticmethod
    def validate_columns(df: pl.DataFrame, required_columns: list[str]) -> dict[str, Any]:
        """验证必需列是否存在

        Args:
            df: 待验证的DataFrame
            required_columns: 必需的列名列表

        Returns:
            验证结果字典
        """
        if df is None:
            return {"is_valid": False, "missing_columns": required_columns, "existing_columns": []}

        existing_columns = df.columns
        missing_columns = [col for col in required_columns if col not in existing_columns]

        return {
            "is_valid": len(missing_columns) == 0,
            "missing_columns": missing_columns,
            "existing_columns": existing_columns,
        }

    @staticmethod
    def validate_data_types(df: pl.DataFrame, expected_types: dict[str, type]) -> dict[str, Any]:
        """验证数据类型

        Args:
            df: 待验证的DataFrame
            expected_types: 期望的数据类型字典

        Returns:
            验证结果字典
        """
        if df is None:
            return {"is_valid": False, "type_mismatches": list(expected_types.keys())}

        type_mismatches = []
        for column, expected_type in expected_types.items():
            if column in df.columns:
                actual_type = df[column].dtype
                # 这里可以添加更详细的类型检查逻辑
                if str(actual_type) != str(expected_type):
                    type_mismatches.append(
                        {"column": column, "expected": str(expected_type), "actual": str(actual_type)}
                    )

        return {"is_valid": len(type_mismatches) == 0, "type_mismatches": type_mismatches}
