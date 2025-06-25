"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: app_config.py
@DateTime: 2024-12-19
@Docs: 应用程序相关配置
"""


class AppConfig:
    """应用配置类"""

    # 应用元信息
    APP_NAME = "数据表处理系统"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "专业的数据表处理工具"

    # 性能配置
    MAX_MEMORY_USAGE = 0.8  # 最大内存使用率
    CHUNK_SIZE = 10000  # 批处理大小

    # 缓存配置
    CACHE_TTL = 3600  # 缓存生存时间（秒）
    MAX_CACHE_SIZE = 100  # 最大缓存项数

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
