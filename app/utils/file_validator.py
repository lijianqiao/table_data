"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: file_validator.py
@DateTime: 2024-12-19
@Docs: 文件验证工具
"""

import os
from typing import Any

from config.file_config import FileConfig


class FileValidator:
    """文件验证器

    提供文件格式、大小、内容验证功能
    """

    def __init__(self, max_size: int = FileConfig.MAX_FILE_SIZE):
        """构造函数

        Args:
            max_size: 最大文件大小限制
        """
        self.max_size = max_size
        self.supported_formats = FileConfig.SUPPORTED_FORMATS

    def validate_file_format(self, file) -> bool:
        """验证文件格式

        Args:
            file: 上传的文件对象

        Returns:
            格式是否支持
        """
        filename = file.name.lower()
        return any(filename.endswith(fmt) for fmt in self.supported_formats)

    def validate_file_size(self, file) -> bool:
        """验证文件大小

        Args:
            file: 上传的文件对象

        Returns:
            大小是否符合要求
        """
        return file.size <= self.max_size

    def get_file_info(self, file) -> dict[str, Any]:
        """获取文件信息

        Args:
            file: 上传的文件对象

        Returns:
            文件信息字典
        """
        size_mb = file.size / 1024 / 1024

        return {
            "name": file.name,
            "size": f"{size_mb:.2f} MB",
            "size_bytes": file.size,
            "type": file.type if hasattr(file, "type") else "unknown",
            "extension": os.path.splitext(file.name)[1].lower(),
        }

    def validate_file_content(self, file) -> dict[str, Any]:
        """验证文件内容

        Args:
            file: 上传的文件对象

        Returns:
            验证结果字典
        """
        validation_result: dict[str, Any] = {"valid": True, "errors": [], "warnings": []}

        try:
            # 简单的内容检查
            file.seek(0)
            first_bytes = file.read(1024)
            file.seek(0)

            # 检查是否为空文件
            if len(first_bytes) == 0:
                validation_result["valid"] = False
                validation_result["errors"].append("文件为空")

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"文件内容验证失败: {str(e)}")

        return validation_result

    def validate_file(self, file) -> dict[str, Any]:
        """综合验证文件

        Args:
            file: 上传的文件对象

        Returns:
            完整的验证结果
        """
        result: dict[str, Any] = {"valid": True, "errors": [], "warnings": [], "file_info": self.get_file_info(file)}

        # 格式验证
        if not self.validate_file_format(file):
            result["valid"] = False
            result["errors"].append("不支持的文件格式")

        # 大小验证
        if not self.validate_file_size(file):
            result["valid"] = False
            result["errors"].append(f"文件大小超过限制 ({self.max_size / 1024 / 1024:.0f}MB)")

        # 内容验证
        content_result = self.validate_file_content(file)
        if not content_result["valid"]:
            result["valid"] = False
            result["errors"].extend(content_result["errors"])
        result["warnings"].extend(content_result["warnings"])

        return result
