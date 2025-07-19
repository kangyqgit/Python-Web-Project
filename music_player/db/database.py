#数据库模块

import pymysql
from pymysql.cursors import DictCursor
from utils.logger import logger
from config import CONFIG

class Database:
    def __init__(self):
        self.config = CONFIG['database']
        self.connection = None
        self.connect()
        self.create_tables()
        logger.info("数据库初始化完成")


    #数据库连接
    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                ssl={'disabled':True},
                cursorclass=DictCursor

            )
            logger.info("数据库连接成功")
        except pymysql.Error as  e:
            logger.error(f"数据库连接失败：{e}")
            #如果数据库不存在，尝试创建
            if 'Unknown database' in str(e):
                self.create_database()
        pass


    #创建数据库
    def create_database(self):
        try:
            logger.info("尝试创建数据库...")
            conn =  pymysql.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {self.config['database']}")
            conn.commit()
            #关闭连接
            cursor.close()
            conn.close()
            logger.info(f"数据库{self.config['database']}创建成功")
            #重新连接
            self.connect()
        except pymysql.Error as e:
            logger.critical(f"创建数据库失败：{e}")


    #创建表
    def create_tables(self):
        if not self.connection:
            return
        try:
            cursor = self.connection.cursor()

            #创建音乐表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS songs(
                    song_id INT PRIMARY KEY AUTO_INCREMENT,
                    title VARCHAR(100) NOT NULL,
                    artist VARCHAR(100) NOT NULL,
                    album VARCHAR(100),
                    duration INT,
                    file_path VARCHAR(255) NOT NULL, 
                    source INT NOT NULL,
                    add_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    img_path VARCHAR(255)
                )
             """)

            #创建播放列表表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists(
                    playlist_id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP 
                )
             """)

            #创建播放列表歌曲关联表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_songs(
                    playlist_id INT NOT NULL,
                    song_id INT NOT NULL,
                    order_num INT NOT NULL,
                    PRIMARY KEY (playlist_id, song_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),
                    FOREIGN KEY (song_id) REFERENCES songs(song_id)
                )
             """)

            self.set_default_playlists("默认播放列表")

            #提交事务
            self.connection.commit()
            logger.info("数据库表创建成功")

        except pymysql.Error as e:
            logger.error(f"创建表失败：{e}")


    #添加歌曲
    def add_song(self,title,artist,album,duration,file_path,source):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                INSERT INTO songs(title,artist,album,duration,file_path,source)
                VALUES('{title}','{artist}','{album}',{duration},'{file_path}','{source}')
            """)
            self.connection.commit()
            logger.info(f"歌曲{title}添加成功")
        except pymysql.Error as e:
            logger.error(f"添加歌曲失败：{e}")


    #删除歌曲
    def delete_song(self,song_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                DELETE FROM songs WHERE song_id={song_id}
            """)
            self.connection.commit()
            logger.info(f"歌曲{song_id}删除成功")
        except pymysql.Error as e:
            logger.error(f"删除歌曲失败：{e}")


    #更新歌曲信息
    def update_song(self,song_id,title,artist,album,duration,file_path,source):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                UPDATE songs SET title='{title}',artist='{artist}',album='{album}',duration={duration},file_path='{file_path}',source='{source}' WHERE song_id={song_id}
            """)
            self.connection.commit()
            logger.info(f"歌曲{song_id}信息更新成功")
        except pymysql.Error as e:
            logger.error(f"更新歌曲信息失败：{e}")

    #通过歌名或歌手获取歌曲
    def get_song_by_title_or_Artist(self,param):
        try:
            cursor = self.connection.cursor()
            query = """SELECT * FROM songs """
            params = ()
            if param:
                query += """WHERE title LIKE %s OR artist LIKE %s"""
                params = (f"%{param}%",f"%{param}%")
            cursor.execute(query,params)
            return cursor.fetchall()
        except Exception as e :
            logger.error(f"通过歌名或歌手获取歌曲失败：{e}")

    #获取所有歌曲或指定歌曲源的歌曲
    def get_all_songs(self,source=None):
        try:
            cursor = self.connection.cursor()
            query = """SELECT * FROM songs"""
            params = ()
            if source:
                query += " WHERE source='%s'"
                params = (source,)
            cursor.execute(query,params)
            return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"获取所有歌曲失败：{e}")


    #获取歌曲 by playlist_id
    def get_song_by_id(self,playlist_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT * FROM songs WHERE song_id in (
                    SELECT song_id FROM playlist_songs WHERE playlist_id = {playlist_id} )
            """)
            return  cursor.fetchone()
        except pymysql.Error as e:
            logger.error(f"获取歌曲{playlist_id}失败：{e}")
            return

    def get_song_by_song_id(self,song_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT * FROM songs WHERE song_id = {song_id}
            """)
            return  cursor.fetchone()
        except pymysql.Error as e:
            logger.error(f"获取歌曲{song_id}失败：{e}")
            return

    #获取默认播放列表 获取本地音乐列表
    def get_playlist(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT * FROM playlists
            """)
            return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"获取播放列表失败：{e}")
            return []

    #添加{name}的播放列表（默认有一个默认播放列表）
    def set_default_playlists(self,name):
        try:
            cursor = self.connection.cursor()
            if name:
                cursor.execute(f"""
                    SELECT playlist_id FROM playlists WHERE name = '{name}'
                """)

                result = cursor.fetchall()

                if not result:
                    cursor.execute(f"""
                        INSERT INTO playlists(name) VALUES('{name}')
                    """)
                    logger.info(f"创建播放列表{name}成功")
                logger.info(f"播放列表{name}已存在，无需创建")
        except pymysql.Error as e:
            logger.error(f"设置默认播放列表失败：{e}")

    #关闭数据库连接
    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("数据库连接关闭")

    def get_songs_by_playlist_id(self,playlist_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT song_id FROM songs,playlist_songs WHERE songs.song_id = playlist_songs.song_id AND playlist_songs.playlist_id = {playlist_id} ORDER BY playlist_songs.order_num
            """)
            return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"获取播放列表{playlist_id}歌曲失败：{e}")
            return []




#全局数据库对象
db = Database()






