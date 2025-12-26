import os
from datetime import datetime
from loguru import logger
from .config import config

def setup_logger():
    """配置日志系统"""
    log_dir = config.log_dir
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = config.logging_config.get('format')
    log_level = config.logging_config.get('level', 'INFO')
    file_pattern = config.logging_config.get('file_pattern')

    # 生成日志文件名
    current_date = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, file_pattern.format(date=current_date))

    # 移除默认的处理器
    logger.remove()

    # 添加文件处理器
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="00:00",  # 每天轮换
        retention="30 days",  # 保留30天
        encoding="utf-8"
    )

    # 添加控制台处理器
    logger.add(
        lambda msg: print(msg),
        format=log_format,
        level=log_level,
        colorize=True
    )

    return logger

# 初始化日志系统
logger = setup_logger()