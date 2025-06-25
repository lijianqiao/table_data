"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: data_processor.py
@DateTime: 2024-12-19
@Docs: 数据处理器
"""

import polars as pl

from app.utils.logger import log_function_calls, logger


class DataProcessor:
    """数据处理器

    提供数据合并、清理、验证等功能
    """

    def __init__(self):
        """初始化数据处理器"""
        self.processing_steps = []
        logger.info("数据处理器初始化完成")

    @log_function_calls(include_result=True)
    def merge_dataframes(self, dfs: list[pl.DataFrame]) -> pl.DataFrame:
        """合并多个DataFrame

        当前策略: 基于共同列进行纵向合并(concat)
        未来可扩展: 支持基于key的横向合并(join)等多种策略

        Args:
            dfs: DataFrame列表

        Returns:
            合并后的DataFrame

        Raises:
            ValueError: 没有数据可合并时
        """
        logger.info(f"开始合并数据 | DataFrame数量: {len(dfs)}")

        if not dfs:
            error_msg = "没有提供要合并的DataFrame"
            logger.error(error_msg)
            raise ValueError("No dataframes to merge")

        if len(dfs) == 1:
            logger.info("只有一个DataFrame，直接返回")
            return dfs[0]

        try:
            # 获取共同列
            common_columns = self.get_common_columns(dfs)
            logger.info(f"共同列数量: {len(common_columns)} | 列名: {common_columns}")

            # 标准化列名并合并
            standardized_dfs = []
            for i, df in enumerate(dfs):
                logger.debug(f"标准化DataFrame {i + 1}/{len(dfs)} | 原始列数: {len(df.columns)}")
                std_df = self.standardize_columns(df)
                # 只保留共同列
                std_df = std_df.select(common_columns)
                standardized_dfs.append(std_df)
                logger.debug(f"DataFrame {i + 1} 标准化完成 | 保留列数: {len(std_df.columns)}")

            merged_df = pl.concat(standardized_dfs)
            logger.info(f"数据合并完成 | 合并后行数: {len(merged_df)} | 列数: {len(merged_df.columns)}")
            return merged_df

        except Exception as e:
            logger.exception(f"数据合并失败: {str(e)}")
            raise

    @log_function_calls(include_result=True)
    def get_common_columns(self, dfs: list[pl.DataFrame]) -> list[str]:
        """获取共同列

        Args:
            dfs: DataFrame列表

        Returns:
            共同列名列表
        """
        if not dfs:
            logger.warning("没有DataFrame提供，返回空列表")
            return []

        logger.debug(f"计算共同列 | DataFrame数量: {len(dfs)}")

        common_cols = set(dfs[0].columns)
        original_count = len(common_cols)

        for i, df in enumerate(dfs[1:], 1):
            common_cols &= set(df.columns)
            logger.debug(f"与DataFrame {i + 1} 比较后，共同列数量: {len(common_cols)}")

        result = list(common_cols)
        logger.info(f"共同列计算完成 | 原始列数: {original_count} | 共同列数: {len(result)}")
        return result

    @log_function_calls(include_result=True)
    def standardize_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """标准化列名

        Args:
            df: 待标准化的DataFrame

        Returns:
            标准化后的DataFrame
        """
        logger.debug(f"开始标准化列名 | 原始列数: {len(df.columns)}")

        # 去除空格，转换为小写
        column_mapping = {col: col.strip().lower().replace(" ", "_") for col in df.columns}

        # 记录列名变化
        changed_columns = [(old, new) for old, new in column_mapping.items() if old != new]
        if changed_columns:
            logger.debug(f"列名标准化变更 | 变更数量: {len(changed_columns)}")
            for old, new in changed_columns:
                logger.debug(f"列名变更: '{old}' -> '{new}'")
        else:
            logger.debug("列名无需变更")

        result = df.rename(column_mapping)
        logger.debug("列名标准化完成")
        return result

    @log_function_calls(include_result=True)
    def validate_data(self, df: pl.DataFrame) -> dict:
        """验证数据质量

        Args:
            df: 待验证的DataFrame

        Returns:
            数据质量报告
        """
        logger.info(f"开始数据质量验证 | 行数: {len(df)} | 列数: {len(df.columns)}")

        try:
            validation_result = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "null_counts": df.null_count().to_dict(),
                "data_types": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes, strict=False)},
                "memory_usage": df.estimated_size(),
            }

            # 统计空值情况
            null_counts_dict = validation_result["null_counts"]
            if isinstance(null_counts_dict, dict):
                null_counts = list(null_counts_dict.values())
            else:
                # 如果不是字典，尝试转换为列表
                null_counts = list(null_counts_dict) if hasattr(null_counts_dict, "__iter__") else [0]
            total_nulls = sum(null_counts)
            null_percentage = (total_nulls / (len(df) * len(df.columns))) * 100 if len(df) > 0 else 0

            logger.info(
                f"数据质量验证完成 | 总空值: {total_nulls} | 空值比例: {null_percentage:.2f}% | 内存使用: {validation_result['memory_usage']} bytes"
            )
            return validation_result

        except Exception as e:
            logger.exception(f"数据质量验证失败: {str(e)}")
            raise

    @log_function_calls(include_result=True)
    def deduplicate(self, df: pl.DataFrame) -> pl.DataFrame:
        """去重

        Args:
            df: 待去重的DataFrame

        Returns:
            去重后的DataFrame
        """
        original_count = len(df)
        logger.info(f"开始去重处理 | 原始行数: {original_count}")

        try:
            result = df.unique()
            final_count = len(result)
            removed_count = original_count - final_count

            logger.info(f"去重处理完成 | 去重后行数: {final_count} | 移除重复行: {removed_count}")
            return result

        except Exception as e:
            logger.exception(f"去重处理失败: {str(e)}")
            raise

    @log_function_calls(include_result=True)
    def clean_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """数据清理

        Args:
            df: 待清理的DataFrame

        Returns:
            清理后的DataFrame
        """
        original_count = len(df)
        logger.info(f"开始数据清理 | 原始行数: {original_count}")

        try:
            # 移除全空行
            df_cleaned = df.filter(~pl.all_horizontal(pl.all().is_null()))
            empty_rows_removed = original_count - len(df_cleaned)

            if empty_rows_removed > 0:
                logger.info(f"移除空行: {empty_rows_removed} 行")

            # 字符串列去除前后空格
            string_cols = [
                col for col, dtype in zip(df_cleaned.columns, df_cleaned.dtypes, strict=False) if dtype == pl.Utf8
            ]
            logger.debug(f"检测到字符串列: {len(string_cols)} 个 | 列名: {string_cols}")

            for col in string_cols:
                df_cleaned = df_cleaned.with_columns(pl.col(col).str.strip_chars())
                logger.debug(f"字符串列清理完成: {col}")

            final_count = len(df_cleaned)
            logger.info(f"数据清理完成 | 清理后行数: {final_count} | 总共移除: {original_count - final_count} 行")
            return df_cleaned

        except Exception as e:
            logger.exception(f"数据清理失败: {str(e)}")
            raise

    @log_function_calls(include_result=True)
    def merge_identical_dataframes(
        self, dfs: list[pl.DataFrame], source_names: list[str], source_column_name: str = "来源"
    ) -> pl.DataFrame:
        """合并字段完全一致的DataFrame，并添加来源列

        专门用于数据合并工具，假设所有DataFrame字段完全一致

        Args:
            dfs: DataFrame列表
            source_names: 每个DataFrame对应的来源文件名
            source_column_name: 来源列的名称，默认为"来源"

        Returns:
            合并后的DataFrame，包含来源列

        Raises:
            ValueError: 当输入参数不匹配或DataFrame字段不一致时
        """
        logger.info(f"开始合并一致字段的数据 | DataFrame数量: {len(dfs)} | 来源数量: {len(source_names)}")

        if not dfs:
            error_msg = "没有提供要合并的DataFrame"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if len(dfs) != len(source_names):
            error_msg = f"DataFrame数量({len(dfs)})与来源名称数量({len(source_names)})不匹配"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # 验证所有DataFrame字段是否一致
            first_columns = dfs[0].columns
            logger.info(f"参考列结构 | 列数: {len(first_columns)}")

            for i, df in enumerate(dfs[1:], 1):
                if df.columns != first_columns:
                    # 详细报告字段差异
                    missing_in_current = set(first_columns) - set(df.columns)
                    extra_in_current = set(df.columns) - set(first_columns)

                    error_details = []
                    if missing_in_current:
                        error_details.append(f"缺少字段: {list(missing_in_current)}")
                    if extra_in_current:
                        error_details.append(f"多余字段: {list(extra_in_current)}")

                    error_msg = f"第{i + 1}个DataFrame与第1个DataFrame字段不一致 | {' | '.join(error_details)}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            logger.info("所有DataFrame字段验证通过")

            # 为每个DataFrame添加来源列并合并
            dfs_with_source = []
            total_rows = 0

            for i, (df, source_name) in enumerate(zip(dfs, source_names, strict=False)):
                # 添加来源列
                df_with_source = df.with_columns(pl.lit(source_name).alias(source_column_name))
                dfs_with_source.append(df_with_source)

                rows_count = len(df)
                total_rows += rows_count
                logger.debug(f"处理文件 {i + 1}/{len(dfs)} | 来源: {source_name} | 行数: {rows_count}")

            # 直接合并，不进行任何列名处理
            merged_df = pl.concat(dfs_with_source)

            # 统计来源分布
            source_stats = merged_df.group_by(source_column_name).len().sort("len", descending=True)
            logger.info(f"合并完成 | 总行数: {len(merged_df)} | 总列数: {len(merged_df.columns)} (包含来源列)")

            # 记录每个来源的数据量
            for row in source_stats.iter_rows():
                source, count = row
                logger.info(f"来源统计 | {source}: {count} 行")

            return merged_df

        except Exception as e:
            logger.exception(f"一致字段数据合并失败: {str(e)}")
            raise

    def get_column_statistics(self, df: pl.DataFrame) -> dict:
        """获取列统计信息

        Args:
            df: 待分析的DataFrame

        Returns:
            列统计信息字典
        """
        stats = {}
        for col in df.columns:
            col_data = df[col]
            stats[col] = {
                "dtype": str(col_data.dtype),
                "null_count": col_data.null_count(),
                "unique_count": col_data.n_unique(),
                "null_percentage": (col_data.null_count() / len(df)) * 100 if len(df) > 0 else 0,
            }

            # 对数值列添加更多统计信息
            if col_data.dtype.is_numeric():
                stats[col].update(
                    {"min": col_data.min(), "max": col_data.max(), "mean": col_data.mean(), "median": col_data.median()}
                )

        return stats
