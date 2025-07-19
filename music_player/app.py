# 主程序入口
from ui.main_windows import MainWindow
from utils.logger import logger

if __name__ == '__main__':
    logger.info('程序启动')

    try:
        app = MainWindow()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        logger.info("程序正常退出")
    except Exception as e:
        logger.error(f'程序启动失败：{e}')
