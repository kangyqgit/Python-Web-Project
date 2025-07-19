# 音乐播放器
import pygame
from pygame import mixer
import os
import time
import threading
from config import CONFIG
from utils.logger import logger

class AudioPlayer:

    #初始化音乐播放器
    def __init__(self):
         try:
             mixer.init()
             #当前歌曲
             self.current_song = None
             #是否暂停
             self.paused = False
             # 是否正在播放
             self.playing = False
             #播放列表
             self.playlist = []
             #当前播放列表索引
             self.current_index = -1
             #音量
             self.volume = CONFIG['player']['default_volume']
             #设置音乐播放器音量
             mixer.music.set_volume(self.volume)
             #当前播放进度
             self.position = 0
             #歌曲时长
             self.duration = 0
             #更新播放列表线程
             self.update_thread = None
             #暂停播放标志
             self.stop_flag = False
             logger.info("初始化音频播放器成功")
         except Exception as e:
             logger.critical(f"初始化音频播放器失败：{e}")
             raise e

    #加载歌曲
    def load_song(self,song_path):
        logger.info(f"加载歌曲：{song_path}")
        try:
            if not os.path.exists(song_path):
                logger.error(f"音乐文件{song_path}不存在")
                return False
            mixer.music.load(song_path)
            self.playing = False
            self.stop_flag = False
            self.duration = 180 #获取歌曲时间（默认3分钟）
            self.position = 0 #

            logger.info(f"加载音乐文件{song_path}成功")
            return True
        except pygame.error as e :
            logger.error(f"加载音乐文件{song_path}失败：{e}")
            return False
        except Exception as e:
            logger.critical(f"加载音乐文件发生未知错误{song_path}失败：{e}")
            return False

    #播放歌曲
    def play(self):
        if not self.current_song :
            logger.warning("当前没有歌曲选中，无法播放")
            return False

        try:
            #暂停歌曲恢复播放
            if self.paused :
                mixer.music.unpause()
                self.paused = False
                logger.info("恢复播放")
            else:
                #加载当前歌曲
                mixer.music.play()
                self.playing = True
                self.start_position_update()
                logger.info(f"开始播放：{self.current_song.get('title','未知歌曲')}")
            return True
        except pygame.error as e:
            logger.error(f"播放音乐失败：{e}")
            return False
        except Exception as e:
            logger.critical(f"播放音乐发生未知错误：{e}")
            return False

    #暂停播放
    def pause(self):
        if self.playing and not self.paused:
            mixer.music.pause()
            self.paused = True
            logger.info("暂停播放")
            return True
        logger.warning("当前没有正在播放的音乐，无法暂停")
        return False

    #停止播放
    def stop(self):
        if self.playing:
            mixer.music.stop()
            self.playing = False
            self.paused = False
            self.position = 0
            self.stop_flag = True
            logger.info("停止播放")
            return True
        logger.warning("当前没有正在播放的音乐，无法停止")
        return False

    #设置音量
    def set_volume(self,volume):
        self.volume = max(0.0,min(1.0,volume)) #设置音量范围为0-1
        mixer.music.set_volume(self.volume)
        logger.info(f"设置音量为{self.volume}")
        return True

    #设置播放位置
    def set_position(self,position):
        """设置播放位置（百分比）"""

        if not self.playing:
            logger.warning("当前没有正在播放的音乐，无法设置播放位置")
            return False
        pos_sec = int(position * self.duration/100)
        try:
            mixer.music.set_pos(pos_sec)
            self.position = position
            logger.info(f"设置播放位置为{position}%")
            return True
        except pygame.error as e:
            logger.error(f"设置播放位置失败：{e}")
            return False
        except Exception as e:
            logger.critical(f"设置播放位置发生未知错误：{e}")
            return False

    #下一首
    def play_next(self):

        if not  self.playlist :
            logger.warning("当前没有播放列表，无法播放下一首")
            return False

        if self.current_index < len(self.playlist)-1:
            self.current_index += 1
        else:
            #播放列表播放完毕，回到第一首
            self.current_index = 0

        self.current_song =self.playlist[self.current_index]
        logger.info(f"下一首：{self.current_song.get('title','未知歌曲')}")

        if self.load_song(self.current_song['file_path']):
            self.play()
            return True
        return False

    #上一首
    def play_prev(self):
        if not  self.playlist :
            logger.warning("当前没有播放列表，无法播放上一首")
            return False

        if self.current_index > 0:
            self.current_index -= 1
        else:
            #播放列表播放完毕，回到最后一首
            self.current_index = len(self.playlist)-1

        self.current_song =self.playlist[self.current_index]
        logger.info(f"上一首：{self.current_song.get('title','未知歌曲')}")

        if self.load_song(self.current_song['file_path']):
            self.play()
            return True
        return False

    #启动播放位置更新线程
    def start_position_update(self):
        self.stop_flag = False
        self.update_thread = threading.Thread(target=self.update_position)
        self.update_thread.daemon = True # 守护线程
        self.update_thread.start()
        logger.debug("启动播放位置更新线程")

    #停止播放位置更新线程
    def stop_position_update(self):
        self.stop_flag = True
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
            logger.debug("停止播放位置更新线程")

    #播放位置更新线程启动
    def update_position(self):
        logger.debug("播放位置更新线程启动")
        while not self.stop_flag and self.playing:
            if not self.paused:
                #更新播放进度
                self.position += 1
                #判断是否播放完毕
                if self.position >= self.duration:
                    self.position = self.duration
                    self.stop()
                    logger.info(f"播放完毕：{self.current_song.get('title','未知歌曲')}")
                    #播放下一首
                    self.play_next()
            time.sleep(1)
        logger.debug("播放位置更新线程结束")

        pass

    #获取当前播放进度(百分比)
    def get_position_percent(self):
        if self.duration == 0:
            return 0
        return int((self.position / self.duration )* 100)

    #添加歌曲至播放列表
    def add_to_playlist(self,song):
        self.playlist.append(song)

        if self.current_index == -1:
            self.current_index = 0
        logger.info(f"添加歌曲至播放列表：{song.get('title','未知歌曲')}")


