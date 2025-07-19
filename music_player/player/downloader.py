#音乐下载器
import os
import time
from requests import HTTPError

from config import CONFIG
from db.database import db
from utils.logger import logger
from utils.utils import  HttpUtils
from  crawler.spider import SpiderSong



class MusicDownloader:

    #音乐下载器初始化，主要初始化下载目录
    def __init__(self):
        self.download_dir = CONFIG['paths']['download_dir']
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logger.info(f"创建下载目录{self.download_dir}")

    # app 1.0.0 版本 从本地数据库搜索音乐
    def search(self,query,callback=None):
        """搜索音乐"""
        #获取本地音乐
        songs = db.get_song_by_title_or_Artist(param=query)
        if  songs:
            logger.info(f"搜索到本地音乐{len(songs)}条")
            return songs

        logger.info(f"未搜索到本地音乐: {query}")


    #app 1.2.0 版本 从网络爬取音乐列表
    def crawler_music(self,query,callback= None):
        """爬取音乐并添加至列表  添加值本地数据库"""
        #本次本地下载歌曲数目
        local_songs_count = 0
        crawler_url = CONFIG['spider']['base_url']
        logger.info(f"开始爬取音乐列表,爬取地址为：{crawler_url}")
        song_list = SpiderSong.parse_song_list(url=crawler_url)
        logger.info(f"从目标地址爬取音乐完成，请等待音乐下载")
        result = []  # 存放音乐路径列表，后续实现在线听歌
        if song_list :
            logger.info("通过爬取到音乐列表中的歌曲路径下载音乐")
            for song in song_list:
                song_path = song['file_path']
                if song_path:
                    result.append(song_path)
                    file_name = song_path.split('/')[-1]

                    #将.mp3文件存储在本地下载目录下
                    song_file_name  = CONFIG['paths']['download_dir'].join(file_name)
                    if os.path.exists(song_file_name):
                        #文件名已存在，重命名文件
                        song_file_name = song_file_name.replace('.mp3','') + str(int(time.time())) + '.mp3'

                    try:
                        response = HttpUtils.get(song_path)
                        if response.status_code == 206:
                            logger.info(f"开始下载音乐{song['title']}本地目录")
                             #流式写入文件
                            with open(song_file_name, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=1024*1024):
                                    if chunk:
                                        f.write(chunk)
                                        local_songs_count +=1

                        response.raise_for_status() #
                    except HTTPError as e:
                        logger.error(f"获取音乐 {song['title']} 失败：{e}")
                    except PermissionError as  e:
                        logger.error(f"权限错误：{e}")
                    except Exception as e:
                        logger.error(f"下载音乐 {song['title']} 失败：{e}")
        else:
            logger.info(f"为爬取到任何音乐")


        logger.info(f"爬取音乐结束，下一步是添加至本地数据库并添加到播放列表（摘取部分数据）")
        logger.info(f"添加{local_songs_count}首歌曲至本地数据库")

        if callback:
            callback(result)

        return result # 返回爬取到的音乐路径列表 前10条

    # 下载音乐 
    def download_music(self,song_info,progress_callback=None,complete_callback=None):
        """下载音乐"""
        logger.info(f"开始下载音乐{song_info['title']}")




