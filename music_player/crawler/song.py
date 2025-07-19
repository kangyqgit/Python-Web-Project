class Song:
    """ 歌曲实体"""


    # 构造函数
    def __init__(self):
        self.song_id = 0
        self.title = "" #歌名
        self.artist = "" #演唱者
        self.album = "" # 专辑
        self.classify = "" # 分类
        self.style = "" # 风格
        self.language = "" # 语言
        """后续可以将歌词对象化"""
        self.lyric = "" # 歌词
        self.duration = 0 # 歌曲时间（秒）int类型
        self.file_path = "" # 歌曲文件路径
        self.source = "" # 歌曲来源
        self.add_time = 0 # 歌曲添加时间
        self.img_path = "" # 歌曲图片路径


    #创建歌曲对象字典
    def to_dict(self):
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "classify": self.classify,
            "style": self.style,
            "language": self.language,
            "lyric": self.lyric,
            "duration": self.duration,
            "file_path": self.file_path,
            "source": self.source,
            "add_time": self.add_time,
            "img_path": self.img_path
        }


    def __del__(self):
        pass
