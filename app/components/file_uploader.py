"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: file_uploader.py
@DateTime: 2024-12-19
@Docs: 文件上传组件
"""

import streamlit as st

from app.utils.file_validator import FileValidator
from app.utils.logger import log_function_calls, logger


class FileUploader:
    """文件上传器

    提供文件上传和验证功能
    """

    def __init__(self, file_validator: FileValidator):
        """初始化文件上传器

        Args:
            file_validator: 文件验证器实例
        """
        self.file_validator = file_validator
        logger.debug("文件上传器初始化完成")

    @log_function_calls()
    def render(self) -> list:
        """渲染文件上传界面

        Returns:
            验证通过的文件列表
        """
        logger.debug("开始渲染文件上传界面")

        uploaded_files = st.file_uploader(
            "📁 选择文件",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            help="支持 CSV、Excel 格式，可多选",
        )

        if uploaded_files:
            logger.info(f"用户上传了 {len(uploaded_files)} 个文件")

            # 记录文件信息
            for file in uploaded_files:
                file_info = self.file_validator.get_file_info(file)
                logger.debug(
                    f"上传文件: {file_info['name']} | 大小: {file_info['size']} | 类型: {file_info['extension']}"
                )

            validation_results = self.validate_files(uploaded_files)
            self.show_upload_status(uploaded_files, validation_results)

            # 只返回验证通过的文件
            valid_files = [f for f, result in zip(uploaded_files, validation_results, strict=False) if result["valid"]]
            logger.info(f"验证通过的文件数量: {len(valid_files)}/{len(uploaded_files)}")
            return valid_files

        logger.debug("没有文件上传")
        return []

    @log_function_calls()
    def validate_files(self, files: list) -> list[dict]:
        """验证文件

        Args:
            files: 文件列表

        Returns:
            验证结果列表
        """
        logger.debug(f"开始验证文件 | 文件数量: {len(files)}")

        results = []
        for i, file in enumerate(files):
            logger.debug(f"验证文件 {i + 1}/{len(files)}: {file.name}")

            result = {"valid": True, "errors": [], "warnings": []}

            try:
                # 文件格式验证
                if not self.file_validator.validate_file_format(file):
                    result["valid"] = False
                    result["errors"].append("不支持的文件格式")
                    logger.warning(f"文件格式验证失败: {file.name}")

                # 文件大小验证
                if not self.file_validator.validate_file_size(file):
                    result["valid"] = False
                    result["errors"].append("文件大小超过限制")
                    logger.warning(f"文件大小验证失败: {file.name}")

                if result["valid"]:
                    logger.debug(f"文件验证通过: {file.name}")
                else:
                    logger.warning(f"文件验证失败: {file.name} | 错误: {result['errors']}")

            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"验证过程出错: {str(e)}")
                logger.exception(f"文件验证异常: {file.name} | 错误: {str(e)}")

            results.append(result)

        valid_count = sum(1 for r in results if r["valid"])
        logger.info(f"文件验证完成 | 通过: {valid_count}/{len(files)}")
        return results

    def show_upload_status(self, files: list, validation_results: list[dict]) -> None:
        """显示上传状态

        Args:
            files: 文件列表
            validation_results: 验证结果列表
        """
        logger.debug("显示文件上传状态")

        for file, result in zip(files, validation_results, strict=False):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.text(f"📄 {file.name}")

            with col2:
                if result["valid"]:
                    st.success("✅")
                else:
                    st.error("❌")

            with col3:
                try:
                    file_info = self.file_validator.get_file_info(file)
                    st.caption(f"{file_info['size']}")
                except Exception as e:
                    logger.warning(f"获取文件信息失败: {file.name} | 错误: {str(e)}")
                    st.caption("未知大小")

            # 显示错误信息
            if result["errors"]:
                for error in result["errors"]:
                    st.error(f"  • {error}")
                    logger.debug(f"显示文件错误: {file.name} | {error}")

            # 显示警告信息
            if result["warnings"]:
                for warning in result["warnings"]:
                    st.warning(f"  • {warning}")
                    logger.debug(f"显示文件警告: {file.name} | {warning}")
