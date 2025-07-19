#工具函数
import requests

class HttpUtils:

    def __init__(self):
        """网络请求工具类"""
        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://www.kugou.com/",
            # 音频文件相关头信息
            "Accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5",
            "Accept-Encoding": "identity;q=1, *;q=0",  # 禁用压缩确保音频完整
            "Connection": "keep-alive",
            "Range": "bytes=0-"
        })
        self.session.cookies.set("kg_dfid", '0R6lIG2T95Nq2gYNip2aAOYG')


    def get(self,url):
        """GET请求"""
        return  self.session.get(url, stream = True,timeout=10)

