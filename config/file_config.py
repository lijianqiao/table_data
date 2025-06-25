"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: file_config.py
@DateTime: 2024-12-19
@Docs: 文件处理相关配置
"""


class FileConfig:
    """文件配置类"""

    # 支持的文件格式
    SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls"]

    # 文件大小限制 (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024

    # CSV读取配置
    CSV_CONFIG = {
        "encoding": "utf-8",
        "separator": ",",
        "has_header": True,
        "null_values": ["", "NULL", "null", "NA", "na"],
    }

    # Excel读取配置
    EXCEL_CONFIG = {"read_all_sheets": True, "header_row": 0}
