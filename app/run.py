"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: run.py
@DateTime: 2024-12-19
@Docs: 应用主编排器：管理依赖注入、应用注册
"""

from app.components.error_handler import ErrorHandler
from app.components.file_uploader import FileUploader
from app.core.container import Container
from app.core.registry import AppRegistry
from app.handlers.data_processor import DataProcessor
from app.handlers.export_handler import ExportHandler
from app.handlers.file_handler import FileHandler
from app.ui.ui import MainUI
from app.utils.file_validator import FileValidator
from app.utils.logger import log_function_calls, logger


class AppOrchestrator:
    """应用主编排器

    负责管理依赖注入、应用注册，UI渲染交给MainUI处理
    """

    @log_function_calls(include_args=False)
    def __init__(self):
        """初始化编排器"""
        logger.info("开始初始化应用编排器")

        self.container = Container()
        logger.debug("依赖注入容器创建完成")

        self.app_registry = AppRegistry()
        logger.debug("应用注册器创建完成")

        self._setup_dependencies()
        self._register_apps()

        # 初始化全局服务管理器
        from app.core.service_manager import ServiceManager

        ServiceManager.initialize(self.container)
        logger.info("全局服务管理器初始化完成")

        # 创建主UI
        self.main_ui = MainUI(self.app_registry)
        logger.info("主UI创建完成")
        logger.info("应用编排器初始化完成")

    @log_function_calls()
    def _setup_dependencies(self):
        """设置依赖注入"""
        logger.info("开始设置依赖注入")

        # 注册核心服务
        services = [
            ("file_handler", FileHandler),
            ("data_processor", DataProcessor),
            ("export_handler", ExportHandler),
            ("file_validator", FileValidator),
        ]

        for name, service_class in services:
            self.container.register(name, service_class, singleton=True)
            logger.debug(f"注册服务: {name}")

        # 注册UI组件
        self.container.register("file_uploader", lambda: FileUploader(self.container.get("file_validator")))
        logger.debug("注册服务: file_uploader")

        logger.info(f"依赖注入设置完成，共注册 {len(services) + 1} 个服务")

    @log_function_calls()
    def _register_apps(self):
        """注册应用"""
        logger.info("开始注册应用")

        try:
            # 注册欢迎页应用（默认应用）
            from app.welcome.welcome_app import WelcomeApp

            self.app_registry.register_app(WelcomeApp)
            logger.info("注册应用: WelcomeApp (默认)")

            # 注册数据合并应用
            from app.merge_extract.merge import MergeApp

            self.app_registry.register_app(MergeApp)
            logger.info("注册应用: MergeApp")

        except ImportError as e:
            error_msg = f"部分应用加载失败: {str(e)}"
            logger.error(error_msg)
            ErrorHandler.show_warning(error_msg)

        registered_apps = self.app_registry.get_app_names()
        logger.info(f"应用注册完成，共注册 {len(registered_apps)} 个应用: {', '.join(registered_apps)}")

    def get_service(self, name: str):
        """获取注册的服务

        Args:
            name: 服务名称

        Returns:
            服务实例
        """
        logger.debug(f"获取服务: {name}")
        try:
            service = self.container.get(name)
            logger.debug(f"服务获取成功: {name}")
            return service
        except Exception as e:
            logger.error(f"服务获取失败: {name} | 错误: {str(e)}")
            raise

    @log_function_calls()
    def run(self):
        """运行主应用"""
        logger.info("开始运行主应用UI")
        self.main_ui.render()
        logger.debug("主应用UI渲染完成")
