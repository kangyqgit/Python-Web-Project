#配置文件加载模块
import os
import configparser

def load_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__),'config.ini')

    #检查配置文件是否存在
    if not os.path.exists(config_path):
        #创建默认配置文件
        return create_default_config()
    try:
        config.read(config_path, encoding='utf-8')
    # 获取配置并处理路径扩展
        config_dict ={
             'database':dict(config['database']),
             'paths': {
                'music_dir': os.path.expanduser(config.get('paths','music_dir')),
                'download_dir': os.path.expanduser(config.get('paths','download_dir'))
             },
             'player': {
                 'default_volume': config.getfloat('player', 'default_volume')
             },
             'logging': {
                 'log_level': config.get('logging', 'log_level', fallback='INFO')
             }
        }
        return config_dict
    except Exception as e:
        return create_default_config()




def create_default_config():
    """默认配置"""
    return {
        'database':{
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'root123',
            'database': 'music_player_db'
        },
        'paths':{
            'music_dir': os.path.expanduser('~/Music'),
            'download_dir': os.path.expanduser('~/Downloads/Music')
        },
        'player':{
            'default_volume ': 0.7
        },
        'logging':{
            'log_level': 'INFO'
        }
    }

#全局配置
CONFIG = load_config()
