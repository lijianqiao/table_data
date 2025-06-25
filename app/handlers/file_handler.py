"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: file_handler.py
@DateTime: 2024-12-19
@Docs: 文件处理器
"""

import polars as pl

from app.utils.logger import log_function_calls, logger


class FileHandler:
    """文件处理器

    提供文件读取和格式转换功能
    """

    def __init__(self):
        """初始化文件处理器"""
        self.supported_formats = [".csv", ".xlsx", ".xls"]
        logger.info(f"文件处理器初始化完成 | 支持格式: {', '.join(self.supported_formats)}")

    @log_function_calls(include_args=True)
    def detect_file_type(self, file) -> str:
        """检测文件类型

        Args:
            file: 文件对象

        Returns:
            文件类型

        Raises:
            ValueError: 不支持的文件格式
        """
        filename = file.name.lower()
        logger.debug(f"检测文件类型: {filename}")

        for fmt in self.supported_formats:
            if filename.endswith(fmt):
                logger.debug(f"文件类型检测成功: {filename} -> {fmt}")
                return fmt

        error_msg = f"不支持的文件格式: {filename}"
        logger.error(error_msg)
        raise ValueError(f"Unsupported file format: {filename}")

    @log_function_calls(include_result=True)
    def read_csv(self, file) -> pl.DataFrame:
        """读取CSV文件

        Args:
            file: CSV文件对象

        Returns:
            DataFrame对象

        Raises:
            ValueError: 读取失败时
        """
        filename = getattr(file, "name", "unknown")
        logger.info(f"开始读取CSV文件: {filename}")

        try:
            df = pl.read_csv(file)
            logger.info(f"CSV文件读取成功: {filename} | 行数: {len(df)} | 列数: {len(df.columns)}")
            return df
        except Exception as e:
            error_msg = f"CSV文件读取失败: {filename} | 错误: {str(e)}"
            logger.exception(error_msg)
            raise ValueError(f"Error reading CSV file: {str(e)}") from e

    @log_function_calls(include_result=True)
    def read_excel(self, file) -> list[pl.DataFrame]:
        """读取Excel文件，支持多工作表

        Args:
            file: Excel文件对象

        Returns:
            DataFrame列表

        Raises:
            ValueError: 读取失败时
        """
        filename = getattr(file, "name", "unknown")
        logger.info(f"开始读取Excel文件: {filename}")

        try:
            # 读取所有工作表
            excel_data = pl.read_excel(file, sheet_id=None)

            if isinstance(excel_data, dict):
                dataframes = list(excel_data.values())
                sheet_count = len(dataframes)
                total_rows = sum(len(df) for df in dataframes)
                total_cols = sum(len(df.columns) for df in dataframes)
                logger.info(
                    f"Excel文件读取成功: {filename} | 工作表数: {sheet_count} | 总行数: {total_rows} | 总列数: {total_cols}"
                )
                return dataframes
            else:
                logger.info(
                    f"Excel文件读取成功: {filename} | 行数: {len(excel_data)} | 列数: {len(excel_data.columns)}"
                )
                return [excel_data]

        except Exception as e:
            error_msg = f"Excel文件读取失败: {filename} | 错误: {str(e)}"
            logger.exception(error_msg)
            raise ValueError(f"Error reading Excel file: {str(e)}") from e

    @log_function_calls(include_result=True)
    def read_file(self, file) -> list[pl.DataFrame]:
        """统一文件读取接口

        Args:
            file: 文件对象

        Returns:
            DataFrame列表

        Raises:
            ValueError: 读取失败时
        """
        filename = getattr(file, "name", "unknown")
        logger.info(f"开始读取文件: {filename}")

        try:
            file_type = self.detect_file_type(file)

            if file_type == ".csv":
                result = [self.read_csv(file)]
            elif file_type in [".xlsx", ".xls"]:
                result = self.read_excel(file)
            else:
                error_msg = f"不支持的文件类型: {file_type}"
                logger.error(error_msg)
                raise ValueError(f"Unsupported file type: {file_type}")

            total_dataframes = len(result)
            total_rows = sum(len(df) for df in result)
            logger.info(f"文件读取完成: {filename} | DataFrame数: {total_dataframes} | 总行数: {total_rows}")
            return result

        except Exception:
            logger.exception(f"文件读取失败: {filename}")
            raise

    @log_function_calls()
    def get_file_summary(self, file) -> dict:
        """获取文件摘要信息

        Args:
            file: 文件对象

        Returns:
            文件摘要字典
        """
        filename = getattr(file, "name", "unknown")
        logger.debug(f"获取文件摘要: {filename}")

        try:
            dataframes = self.read_file(file)
            total_rows = sum(len(df) for df in dataframes)
            total_columns = sum(len(df.columns) for df in dataframes)

            summary = {
                "file_name": filename,
                "file_type": self.detect_file_type(file),
                "sheets_count": len(dataframes),
                "total_rows": total_rows,
                "total_columns": total_columns,
                "success": True,
            }

            logger.info(
                f"文件摘要生成成功: {filename} | 工作表: {len(dataframes)} | 行: {total_rows} | 列: {total_columns}"
            )
            return summary

        except Exception as e:
            error_summary = {"file_name": filename, "error": str(e), "success": False}
            logger.error(f"文件摘要生成失败: {filename} | 错误: {str(e)}")
            return error_summary
