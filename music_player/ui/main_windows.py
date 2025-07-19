#主窗口
import os.path
from utils.logger import logger
import tkinter as tk
from tkinter import ttk as ttk, filedialog,messagebox
from player.audio_player import AudioPlayer
from player.downloader import MusicDownloader
from .components import NowPlayingPanel ,SongList ,PlaybackControls,ProgressDialog
from db.database import db
import threading

class MainWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("小康的个人音乐播放器")
        self.geometry("900x600")
        self.minsize(800,500)
        logger.info("音乐播放器启动，可以使用免费的音乐资源了！")

        try:
            #初始化播放器和下载器
            self.player = AudioPlayer()
            self.downloader = MusicDownloader()

            #创建界面
            self.create_widgets()
            #加载本地音乐
            self.load_local_music()
            #设置播放列表
            self.set_default_playlist()
            #更新ui
            self.update_ui()
            logger.info("音乐播放器初始化完成")
        except Exception as e:
            logger.error("初始化播放器和下载器失败：%s",e)
            messagebox.showerror("错误", "初始化播放器和下载器失败：%s" % e)
            self.destroy()

    def create_widgets(self):
        #创建界面
        try:
            #创建主框架
            main_frame = ttk.Frame()
            main_frame.pack(fill=tk.BOTH,expand=True,padx=10,pady=10)
            #顶部控制栏
            control_fram = ttk.Frame(main_frame)
            control_fram.pack(fill=tk.X, pady=(0,10))

            #创建搜索框
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(control_fram,textvariable=self.search_var,width=30)
            search_entry.pack(side=tk.LEFT,padx=5)
            #为搜索框绑定事件
            search_entry.bind("<Return>",lambda event:self.search_music_online())
            #创建搜索按钮
            search_btn = ttk.Button(control_fram,text=" 搜  索 ",command=self.search_music_online)
            search_btn.pack(side=tk.LEFT,padx=5)
            #创建添加本地音乐按钮
            add_local_btn = ttk.Button(control_fram,text=" 添加本地音乐 ",command=self.add_local_music)
            add_local_btn.pack(side=tk.LEFT,padx=5)

            #主内容区间
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True)

            #左边面板
            left_panel = ttk.Frame(content_frame,width=200)
            left_panel.pack(side=tk.LEFT,fill=tk.Y,padx=(0,10))

            #播放列表
            player_list_frame = ttk.LabelFrame(left_panel,text="播放列表")
            player_list_frame.pack(fill=tk.X,pady=(0,10))
            #播放列表内容
            self.playlist_listbox = tk.Listbox(player_list_frame,height = 10)
            self.playlist_listbox.pack(fill=tk.BOTH,padx =5,pady = 5)
            #为列表绑定查询音乐列表事件
            self.playlist_listbox.bind("<<ListboxSelect>>",self.on_playlist_select)

            #本地音乐
            local_music_frame = ttk.LabelFrame(left_panel,text="本地音乐")
            local_music_frame.pack(fill=tk.BOTH,expand=True)
            columns = ("ID","歌名","歌手","")
            self.local_music_list = SongList(local_music_frame,columns,height=15)
            self.local_music_list.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)
            self.local_music_list.bind("<Double-1>",self.on_music_double_click)

            #右侧面板
            right_panel = ttk.Frame(content_frame)
            right_panel.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)

            #当前播放面板
            self.now_playing_panel = NowPlayingPanel(right_panel,self.player)
            self.now_playing_panel.pack(fill=tk.X,pady=(0,10))

            #播放控制
            self.playback_controls = PlaybackControls(right_panel,self.player)
            self.playback_controls.pack(fill=tk.X,pady=5)

            #在线音乐模块
            search_result_frame = ttk.LabelFrame(right_panel,text="在线音乐")
            search_result_frame.pack(fill=tk.BOTH,expand=True)
            columns = ("ID","歌名","歌手","")
            self.search_result_list = SongList(search_result_frame,columns,height=8)
            self.search_result_list.pack(fill=tk.BOTH,expand=True,padx=5,pady=5)

            #下载按钮
            download_frame = ttk.Frame(search_result_frame)
            download_frame.pack(fill=tk.X,pady=5)

            download_btn = ttk.Button(download_frame,text="下载选中歌曲",command=self.download_selected)
            download_btn.pack(pady=5)

            logger.info("创建界面成功")


        except Exception as e:
            logger.error("创建菜单栏失败：%s",e)
            raise
        pass

    def load_local_music(self):
        """加载本地音乐"""
        logger.info("加载本地音乐")
        try:
            songs = db.get_all_songs(0)
            #本地音乐列表清空
            self.local_music_list.clear()
            #加载新的本地音乐列表
            for song in songs:
                self.local_music_list.add_song({
                    "id": song['song_id'],
                    "歌名": song['title'],
                    "歌手": song['artist'],
                     "": "播放" if song['file_path'] else "下载"
                })
                self.search_result_list.add_song({
                    "id": song['song_id'],
                    "歌名": song['title'],
                    "歌手": song['artist'],
                    "": "播放" if song['file_path'] else "下载"
                })
            logger.info(f"加载本地音乐成功,共加载{len(songs)}首歌曲！")
        except Exception as e:
            logger.error(f"加载本地音乐失败：{e}")
        pass

    def set_default_playlist(self):
        """设置默认播放列表"""
        logger.info("设置默认播放列表")
        try:
            playlists = db.get_playlist()
            self.playlist_listbox.delete(0,tk.END)
            for playlist in playlists:
                self.playlist_listbox.insert(tk.END,playlist['name'])

                #添加播放列表里面的歌曲
                playlist_id = playlist['playlist_id']
                if playlist_id:
                    song = db.get_song_by_id(playlist_id)
                    if song:
                        self.player.playlist.append(song)
            logger.info(f"设置默认播放列表成功,共加载{len(playlists)}首歌曲！")

        except Exception as e:
            logger.error(f"设置默认播放列表失败：{e}")

    def on_playlist_select(self,event):
        """播放列表选择事件"""
        self.set_default_playlist()

    def on_music_double_click(self,event):
        """双击播放音乐"""
        song_id = self.local_music_list.get_selected_song_id()
        if song_id:
            try:
                song = db.get_song_by_song_id(song_id)
                if song:
                    self.player.current_song = song
                    if self.player.load_song(song['file_path']):
                        self.player.play()
                        self.now_playing_panel.update_song_info(song)
                        self.playback_controls.play_btn.config(text="暂停")
            except Exception as e:
                logger.error(f"播放歌曲失败，ID={song_id},错误信息：{e}")
                messagebox.showerror("播放音乐错误", f"播放歌曲失败，ID={song_id},错误信息：{e}")

    def add_local_music(self):
        """添加本地音乐"""
        logger.info("添加本地音乐")
        try:
            files = filedialog.askopenfilenames(
                title="选择音乐文件",
                filetypes=[("音乐文件","*.mp3;*.wav;*.ogg;*.flac")]
            )
            if not files:
                logger.info(f"用户取消了添加本地音乐")
                return

            logger.info(f"用户添加了{len(files)}首歌曲")
            for file_path in files:
                filename = os.path.basename(file_path)
                title,_ = os.path.splitext(filename)
                artist = "未知"
                album = "未知"

                #保存到数据库
                db.add_song(title,artist,album,0,file_path,0)
                #添加到列表
            self.load_local_music()
            logger.info(f"本地音乐添加成功")

        except Exception as e:
            logger.error(f"添加本地音乐失败：{e}")
            messagebox.showerror("错误", f"添加本地音乐失败：{e}")

    def search_music_online(self):
        """搜索在线音乐"""
        query = self.search_var.get().strip()
        if not query:
            logger.info(f"搜索在线音乐失败，搜索内容为空")
            messagebox.showerror("错误", "搜索内容不能为空！")
            return

        logger.info(f"搜索在线音乐：{query}")
        self.search_result_list.clear()

        #显示加载状态s
        self.search_result_list.insert("",tk.END,values=("正在搜索...","",""))

        #新开辟线程执行搜索
        def search_thread():
            logger.info(f"开辟线程搜索在线音乐：{query}")
            try:
                results = self.downloader.search(query,self.update_search_results)
                if not results:
                    self.after(0,lambda : messagebox.showinfo("提示", "没有找到相关的音乐！",args=None))
                return results
            except Exception as e:
                logger.error(f"搜索在线音乐失败：{e}")
                messagebox.showerror("错误", f"搜索在线音乐失败：{e}")

        result = threading.Thread(target=search_thread,daemon=True).start()
        self.player.playlist = result

    def update_search_results(self,results):
        """更新搜索结果到ui"""
        logger.info(f"更新搜索结果到ui：{len(results)}")
        self.search_result_list.clear()
        for song in results:
            self.search_result_list.add_song({
                "id": song['song_id'],
                "歌名": song['title'],
                "歌手": song['artist'],
                "时长": song['duration']
            })

    def download_selected(self):
        """下载选中的音乐"""
        logger.info(f"下载选中的音乐")
        song_id = self.search_result_list.get_selected_song_id()
        if not song_id:
            logger.info(f"下载选中的音乐失败，未选择歌曲")
            messagebox.showerror("错误", "请先选择要下载的歌曲！")
            return

        song_info =  None
        for item in self.search_result_list.get_children():
            if self.search_result_list.item(item,"tags")[0] == str(song_id):
                values = self.search_result_list.item(item,"values")
                song_info = {
                    "id": values[0],
                    "歌名": values[1],
                    "歌手": values[2],
                }
                break
            if not song_info:
                logger.info(f"下载选中的音乐失败，歌曲ID={song_id}不存在")
                messagebox.showerror("错误", f"歌曲ID={song_id}不存在！")
                return

        #下载歌曲

        logger.info(f"开始下载歌曲：{song_info['title']}")
        #显示进度框
        progress_dialog = ProgressDialog(self,title=f"正在下载{song_info['title']}...")

        def progress_callback(value):
            if progress_dialog.winfo_exists():
                progress_dialog.update_progress(value)

        def complete_callback(song,file_path):
            self.load_local_music()
            logger.info(f"下载歌曲完成回调，重新加载本地音乐：{song['title']}")
            messagebox.showinfo("提示", f"下载歌曲完成：{song['title']}")


        #开始下载
        try:
            self.downloader.download_music(
                song_info,
                progress_callback=progress_callback,
                complete_callback=complete_callback
            )
        except Exception as e:
            logger.error(f"下载歌曲失败：{e}")
            messagebox.showerror("错误", f"下载歌曲失败：{e}")

    def update_ui(self):
        """定期更新ui状态"""
        try:
            #更新播放进度
            if self.player.playing:
                position = self.player.get_position_percent()
                self.playback_controls.update_progress(position)
                #更新时间显示
                self.now_playing_panel.update_time(
                    self.player.position,
                    self.player.duration
                )
                #每100ms更新一次ui
                self.after(100,self.update_ui)

        except Exception as e:
            logger.error(f"更新ui失败：{e}")
        pass

    def on_closing(self):
        """关闭窗口"""
        logger.info("程序关闭")
        try:
            self.player.stop()
            db.close()
            self.destroy()
        except Exception as e:
            logger.error(f"程序关闭失败：{e}")







