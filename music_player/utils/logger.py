# 日志模块
import logging
import logging.handlers
import os
from config import CONFIG
from datetime import  datetime
import sys


def setup_logger():
    """
    设置日志模块
    :return:
    """
    #创建日志目录
    log_dir = os.path.join(os.path.dirname(__file__), '..','logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    #创建日志文件名（按日期）
    log_file = os.path.join(log_dir,f"music_player_{datetime.now().strftime('%Y-%m-%d')}.log")

    #创建日志记录器
    logger = logging.getLogger("music_player")
    logger.setLevel(logging.DEBUG)

    #创建格式化器
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(module)s.%(funcName)s]-%(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    #文件处理器（按天滚动，保存7天）
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=7,encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    #控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if CONFIG.get('log_level',
                                                        'info').lower() == 'info' else logging.DEBUG)
    console_handler.setFormatter(formatter)

    #添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    #捕获未处理异常
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            #不记录键盘中断
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))


    sys.excepthook = handle_exception

    return logger

#全局日志记录器
logger = setup_logger()