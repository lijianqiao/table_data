"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: export_handler.py
@DateTime: 2024-12-19
@Docs: 导出处理器
"""

from io import BytesIO
from typing import Any

import polars as pl

from app.utils.logger import log_function_calls, logger


class ExportHandler:
    """导出处理器

    提供数据导出功能，支持多种格式
    """

    def __init__(self):
        """初始化导出处理器"""
        self.supported_formats = [".xlsx"]  # 简化为只支持xlsx以获得更好性能
        logger.info(f"导出处理器初始化完成 | 支持格式: {', '.join(self.supported_formats)}")

    @log_function_calls(include_args=True)
    def export_excel(self, df: pl.DataFrame, columns: list[str] | None = None) -> bytes:
        """使用Polars直接导出Excel格式，避免Pandas转换，提升性能

        Args:
            df: 要导出的DataFrame
            columns: 要导出的列名列表，为None时导出所有列

        Returns:
            Excel文件的字节数据

        Raises:
            ValueError: 导出失败时
        """
        logger.info(f"开始导出Excel | 原始行数: {len(df)} | 原始列数: {len(df.columns)}")

        try:
            if columns:
                # 验证列名是否存在
                missing_columns = [col for col in columns if col not in df.columns]
                if missing_columns:
                    error_msg = f"指定的列不存在: {missing_columns}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                df_to_export = df.select(columns)
                logger.info(f"选择指定列导出 | 选择列数: {len(columns)} | 导出行数: {len(df_to_export)}")
            else:
                df_to_export = df
                logger.info("导出所有列")

            # 创建字节流
            output = BytesIO()

            # 使用Polars写入Excel
            df_to_export.write_excel(output)

            # 获取字节数据
            excel_data = output.getvalue()
            file_size = len(excel_data)

            logger.info(
                f"Excel导出成功 | 导出行数: {len(df_to_export)} | 导出列数: {len(df_to_export.columns)} | 文件大小: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)"
            )
            return excel_data

        except Exception as e:
            logger.exception(f"Excel导出失败: {str(e)}")
            raise ValueError(f"导出Excel失败: {str(e)}") from e
        finally:
            if "output" in locals():
                output.close()

    @log_function_calls()
    def get_export_summary(self, df: pl.DataFrame, selected_columns: list[str] | None = None) -> dict[str, Any]:
        """获取导出摘要信息

        Args:
            df: 要导出的DataFrame
            selected_columns: 选择的列名列表

        Returns:
            导出摘要信息字典
        """
        logger.debug(f"生成导出摘要 | 原始行数: {len(df)} | 原始列数: {len(df.columns)}")

        try:
            export_df = df.select(selected_columns) if selected_columns else df
            estimated_size_bytes = export_df.estimated_size()
            estimated_size_mb = estimated_size_bytes / 1024 / 1024

            summary = {
                "total_rows": len(export_df),
                "total_columns": len(export_df.columns),
                "selected_columns": selected_columns or df.columns,
                "estimated_size": f"{estimated_size_mb:.2f} MB",
                "estimated_size_bytes": estimated_size_bytes,
            }

            logger.debug(
                f"导出摘要生成完成 | 导出行数: {summary['total_rows']} | 导出列数: {summary['total_columns']} | 预估大小: {summary['estimated_size']}"
            )
            return summary

        except Exception as e:
            logger.exception(f"生成导出摘要失败: {str(e)}")
            raise

    def get_supported_formats(self) -> list[str]:
        """获取支持的导出格式

        Returns:
            支持的格式列表
        """
        logger.debug(f"获取支持的导出格式: {self.supported_formats}")
        return self.supported_formats.copy()

    def validate_export_data(self, df: pl.DataFrame, columns: list[str] | None = None) -> dict[str, Any]:
        """验证导出数据

        Args:
            df: 要验证的DataFrame
            columns: 要验证的列名列表

        Returns:
            验证结果字典
        """
        logger.debug("开始验证导出数据")

        validation_result: dict[str, Any] = {"valid": True, "warnings": [], "errors": []}

        try:
            # 检查DataFrame是否为空
            if len(df) == 0:
                validation_result["warnings"].append("DataFrame为空")
                logger.warning("DataFrame为空")

            # 检查指定的列是否存在
            if columns:
                missing_columns = [col for col in columns if col not in df.columns]
                if missing_columns:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"列不存在: {missing_columns}")
                    logger.error(f"指定的列不存在: {missing_columns}")

            # 检查数据大小
            if columns:
                export_df = df.select(columns)
            else:
                export_df = df

            size_mb = export_df.estimated_size() / 1024 / 1024
            if size_mb > 100:  # 大于100MB警告
                validation_result["warnings"].append(f"文件较大: {size_mb:.2f} MB")
                logger.warning(f"导出文件较大: {size_mb:.2f} MB")

            logger.debug(
                f"导出数据验证完成 | 有效: {validation_result['valid']} | 警告数: {len(validation_result['warnings'])} | 错误数: {len(validation_result['errors'])}"
            )
            return validation_result

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"验证过程出错: {str(e)}")
            logger.exception(f"导出数据验证失败: {str(e)}")
            return validation_result
