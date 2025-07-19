"""歌曲爬取器"""
from winreg import EnumValue

import requests
from bs4 import BeautifulSoup
from enum import Enum
import os
import re
import time
from utils.logger import logger
from crawler.song import Song
from config import CONFIG
from urllib.parse import urljoin
import lxml
from modules.source_enum import SourceEnum

class SpiderSong:


    def __init__(self):
        self.config = CONFIG["database"]
        self.base_url = CONFIG["spider"]['base_url']
        self.login_url =  CONFIG["spider"]['login_url']
        self.session = requests.Session()
        self.session.headers.update(CONFIG["spider"]["headers"])
        #设置最大重试次数
        self.retries = CONFIG["spider"]["max_retries"]
        #设置请求延迟
        self.delay = CONFIG["spider"]["request_delay"]
        pass


    def fetch_page(self, url):
        """获取页面内容"""

        logger.info(f"获取页面内容，地址为: {url}")

        #在重试次数内，尝试获取页面内容
        for attempt in range(self.retries):
            try:
                response  = self.session.get(url)
                response.raise_for_status()
                logger.info(f"获取页面内容成功,可以进行下一步了")
                return response.text
            except requests.RequestException as e:
                logger.error(f"获取页面内容失败，内容地址{url}: {e}")
                time.sleep(2 ** attempt)
        logger.error(f"获取页面内容失败，超过最大重试次数，内容地址{url}")
        return None


    def parse_song_list(self,url):
        """解析歌曲列表"""
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, 'lxml')
        song_list = []

        #获取新歌首发列表
        for item in  soup.select('.song-item'):
            song = Song()
            #解析歌名
            song_name = item.select_one('.name')
            song.name = song_name.get_text(strip=True) if song_name else ""
            #歌曲来源
            song.source = SourceEnum.WEB.value
            #解析演唱者
            song_artist = item.select_one('.author')
            song.artist = song_artist.get_text(strip=True) if song_artist else ""
            #解析歌曲背景图片
            song_img = item.select_one('img')
            song.img = song_img['src'] if song_img else ""

            #获取歌曲详情页地址
            link_elem = item.select_one('a') #只会获取到第一个a标签
            if link_elem:
                detail_url = link_elem['href']
                #解析歌曲详情页
                time.sleep(self.delay) #延迟防止被封
                #解析歌曲详情页
                self.parse_song_detail(detail_url, song)

            song_list.append(song)


        logger.info(f"获取歌曲列表成功,共获取到{len(song_list)}首歌曲")
        return song_list



    def parse_song_detail(self, url, song):
        """解析歌曲详情页"""

        html = self.fetch_page(url)

        soup = BeautifulSoup(html, 'lxml')

        #解析详情歌曲信息列表
        for item in soup.select('.view_info'):

            #获取到详情页面的头部列表获取基本信息
            li_list = item.select('li')
            #解析歌曲分类
            song_classify = li_list[5].select_one('a').get_text(strip=True)
            song.classify = song_classify if song_classify else ""

            #解析歌曲语种 -
            languages = li_list[6].get_text().split('：')
            song.language = languages[-1] if languages else ""

            #解析歌曲风格
            styles = li_list[7].get_text(strip=True).split('：')
            song.style = styles[-1] if styles else ""

            #解析歌曲发布时间
            time_without_deal =li_list[0].selecy_one('em').dind_next_sibling(string=True)
            # 将字符串时间转换为时间戳
            timestamp = 0.0
            if len(time_without_deal) >1:
                time_str  = time_without_deal.strip()
                time_tuple  = time.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                timestamp = time.mktime(time_tuple)
            song.add_time  = timestamp


            # 解析歌词并格式化歌词
            song_lyric_without_deal = soup.select_one(".lrc-tab-content").get_text(strip=True)
            if song_lyric_without_deal:
                song_lyric = re.sub(r'\[.*?]', '', song_lyric_without_deal)  # 去除歌词中[xxx]标签
                song.lyric = song_lyric_without_deal

            # 解析歌曲地址
            try:
                song_url = soup.audio['src']
                song_data_url = soup.audio['data-src']
                song.file_path = song_url if song_url else song_data_url if song_data_url else ""
            except Exception as e:
                print(e)



        pass



