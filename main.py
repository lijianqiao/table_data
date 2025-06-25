"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: main.py
@DateTime: 2024-12-19
@Docs: 数据表处理系统主入口
"""

import streamlit as st

from app.run import AppOrchestrator
from app.utils.logger import logger


def main():
    """主函数"""
    logger.info("系统启动中...")

    try:
        # 创建并运行应用编排器
        logger.info("初始化应用编排器")
        orchestrator = AppOrchestrator()

        logger.info("开始运行应用")
        orchestrator.run()

        logger.info("应用运行完成")

    except Exception as e:
        error_msg = f"系统启动失败: {str(e)}"
        logger.exception(error_msg)
        st.error(error_msg)
        st.exception(e)


if __name__ == "__main__":
    main()
