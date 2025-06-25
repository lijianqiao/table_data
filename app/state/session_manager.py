"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: session_manager.py
@DateTime: 2024-12-19
@Docs: 会话状态管理器
"""

from typing import Any

import streamlit as st

from app.utils.logger import logger


class SessionManager:
    """会话状态管理器

    提供Streamlit会话状态的统一管理接口
    """

    # 缓存键命名规则
    CACHE_KEYS = {
        "uploaded_files": "files_{session_id}",
        "processed_data": "data_{file_hash}",
        "user_selections": "selections_{app_name}",
        "current_app": "current_app",
        "processing_status": "processing_status",
    }

    @staticmethod
    def init_session_state() -> None:
        """初始化会话状态"""
        logger.debug("初始化会话状态")

        default_states: dict[str, Any] = {
            "current_app": None,
            "uploaded_files": [],
            "processed_data": None,
            "selected_columns": [],
            "processing_status": "idle",
            "error_message": None,
        }

        initialized_count = 0
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value
                initialized_count += 1
                logger.debug(f"初始化状态: {key} = {value}")

        if initialized_count > 0:
            logger.info(f"会话状态初始化完成 | 新增状态数: {initialized_count}")
        else:
            logger.debug("会话状态已存在，无需初始化")

    @staticmethod
    def get_state(key: str) -> Any:
        """获取状态值

        Args:
            key: 状态键名

        Returns:
            状态值，不存在时返回None
        """
        value = st.session_state.get(key)
        logger.debug(f"获取状态: {key} = {type(value).__name__}")
        return value

    @staticmethod
    def set_state(key: str, value: Any) -> None:
        """设置状态值

        Args:
            key: 状态键名
            value: 状态值
        """
        old_value = st.session_state.get(key)
        st.session_state[key] = value

        # 安全的值比较，处理DataFrame等特殊类型
        values_changed = SessionManager._values_are_different(old_value, value)

        if values_changed:
            logger.info(f"状态更新: {key} | 类型: {type(value).__name__}")
            if hasattr(value, "shape") and hasattr(value, "columns"):
                # DataFrame类型，记录更简洁的信息
                logger.debug(f"状态详情: {key} | DataFrame形状: {getattr(value, 'shape', 'unknown')}")
            else:
                logger.debug(f"状态详情: {key} | 新值: {value}")
        else:
            logger.debug(f"状态未变化: {key}")

    @staticmethod
    def _values_are_different(old_value: Any, new_value: Any) -> bool:
        """安全比较两个值是否不同

        Args:
            old_value: 旧值
            new_value: 新值

        Returns:
            值是否不同
        """
        try:
            # 如果是相同的对象引用，直接返回False
            if old_value is new_value:
                return False

            # 如果类型不同，认为值不同
            if type(old_value) is not type(new_value):
                return True

            # 处理DataFrame类型的比较
            if hasattr(old_value, "shape") and hasattr(new_value, "shape"):
                # 比较DataFrame的形状和列名
                if hasattr(old_value, "columns") and hasattr(new_value, "columns"):
                    return old_value.shape != new_value.shape or list(old_value.columns) != list(new_value.columns)
                else:
                    return old_value.shape != new_value.shape

            # 处理None值
            if old_value is None or new_value is None:
                return old_value is not new_value

            # 尝试常规比较
            return old_value != new_value

        except (TypeError, ValueError):
            # 如果比较出错，假设值不同
            logger.debug(
                f"值比较出错，假设值已变化 | 旧值类型: {type(old_value).__name__} | 新值类型: {type(new_value).__name__}"
            )
            return True

    @staticmethod
    def clear_state(keys: list[str] | None = None) -> None:
        """清空指定状态或全部状态

        Args:
            keys: 要清空的状态键名列表，为None时清空全部状态
        """
        if keys:
            logger.info(f"清空指定状态 | 数量: {len(keys)} | 键名: {keys}")
            cleared_count = 0
            for key in keys:
                if key in st.session_state:
                    old_value = st.session_state[key]
                    del st.session_state[key]
                    cleared_count += 1
                    logger.debug(f"清空状态: {key} | 原值类型: {type(old_value).__name__}")

            logger.info(f"状态清空完成 | 实际清空: {cleared_count}/{len(keys)}")
        else:
            total_keys = len(st.session_state)
            st.session_state.clear()
            logger.info(f"全部状态已清空 | 清空数量: {total_keys}")

    @staticmethod
    def get_cache_key(template: str, **kwargs) -> str:
        """生成缓存键

        Args:
            template: 缓存键模板
            **kwargs: 模板参数

        Returns:
            生成的缓存键
        """
        cache_key = template.format(**kwargs)
        logger.debug(f"生成缓存键: {cache_key} | 模板: {template}")
        return cache_key

    @staticmethod
    def has_state(key: str) -> bool:
        """检查状态是否存在

        Args:
            key: 状态键名

        Returns:
            状态是否存在
        """
        exists = key in st.session_state
        logger.debug(f"状态存在检查: {key} = {exists}")
        return exists

    @staticmethod
    def get_all_states() -> dict[str, Any]:
        """获取所有状态

        Returns:
            所有状态的字典
        """
        states = {str(k): v for k, v in st.session_state.items()}
        logger.debug(f"获取所有状态 | 状态数量: {len(states)}")
        return states

    @staticmethod
    def get_state_summary() -> dict[str, Any]:
        """获取状态摘要

        Returns:
            状态摘要信息
        """
        states = st.session_state
        summary = {
            "total_states": len(states),
            "state_keys": list(states.keys()),
            "state_types": {key: type(value).__name__ for key, value in states.items()},
        }

        logger.debug(f"状态摘要 | 总数: {summary['total_states']} | 键名: {summary['state_keys']}")
        return summary
