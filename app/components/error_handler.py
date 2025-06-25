"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: error_handler.py
@DateTime: 2024-12-19
@Docs: 错误处理组件
"""

from collections.abc import Callable
from typing import Any

import streamlit as st

from app.utils.logger import logger


class ErrorHandler:
    """错误处理器

    提供统一的错误显示和处理功能，并记录日志
    """

    @staticmethod
    def show_error(message: str, details: str | None = None) -> None:
        """显示错误信息

        Args:
            message: 错误消息
            details: 错误详情（可选）
        """
        # 记录错误日志
        if details:
            logger.error(f"错误: {message} | 详情: {details}")
        else:
            logger.error(f"错误: {message}")

        # 显示错误信息
        st.error(f"❌ {message}")
        if details:
            with st.expander("错误详情"):
                st.code(details)

    @staticmethod
    def show_warning(message: str) -> None:
        """显示警告信息

        Args:
            message: 警告消息
        """
        logger.warning(f"警告: {message}")
        st.warning(f"⚠️ {message}")

    @staticmethod
    def show_success(message: str) -> None:
        """显示成功信息

        Args:
            message: 成功消息
        """
        logger.info(f"成功: {message}")
        st.success(f"✅ {message}")

    @staticmethod
    def show_info(message: str) -> None:
        """显示信息提示

        Args:
            message: 信息内容
        """
        logger.info(f"信息: {message}")
        st.info(f"ℹ️ {message}")

    @staticmethod
    def validate_and_execute(func: Callable, *args, **kwargs) -> Any:
        """安全执行函数并处理错误

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果，失败时返回None
        """
        func_name = getattr(func, "__name__", str(func))
        logger.debug(f"开始执行函数: {func_name}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数执行成功: {func_name}")
            return result
        except Exception as e:
            error_msg = f"函数执行失败: {func_name} | 错误: {str(e)}"
            logger.exception(error_msg)
            ErrorHandler.show_error("操作失败", str(e))
            return None

    @staticmethod
    def handle_exception(e: Exception, context: str = "操作") -> None:
        """处理异常并显示友好的错误信息

        Args:
            e: 异常对象
            context: 操作上下文描述
        """
        error_message = f"{context}失败"
        error_details = f"{type(e).__name__}: {str(e)}"

        # 记录详细的异常信息
        logger.exception(f"异常处理 - 上下文: {context} | 异常类型: {type(e).__name__} | 异常信息: {str(e)}")

        ErrorHandler.show_error(error_message, error_details)
