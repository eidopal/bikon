import logging
import sys


def setup_logging(level=logging.INFO):
    """配置全局日志"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def get_logger(name: str) -> logging.Logger:
    """获取指定模块的 logger"""
    return logging.getLogger(name)
