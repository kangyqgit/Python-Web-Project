# UI组件
import tkinter as tk
from tkinter import ttk
from utils.logger import logger

class ProgressDialog(tk.Toplevel):
    def __init__(self,parent,title="下载进度"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x100")
        self.transient(parent)
        self.grab_set()

        self.progress_var = tk.IntVar(value=0)
        tk.Label(self,text="正在下载...").pack(pady=5)

        process_bar = ttk.Progressbar(
            self,variable=self.progress_var,maximum=100
        )
        process_bar.pack(fill=tk.X,padx=20,pady=5)

        self.status_label = tk.Label(self,text="0%")
        self.status_label.pack(pady=5)

        self.cancel_btn = tk.Button(self,text="取消",command=self.cancel)
        self.cancel_btn.pack(pady=5)

        self.cancelled = False


    def update_progress(self,value):
        """更新进度更新"""
        self.progress_var.set(value)
        self.status_label.config(text=f"{value}%")
        if value >=100:
            self.destroy()


    def cancel(self):
        """取消下载"""
        self.cancelled = True
        self.destroy()

class SongList(ttk.Treeview):
    """歌曲列表UI"""
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, columns=columns, show="headings", **kwargs)

        #设置列
        self.columns = columns
        for col in columns:
            self.heading(col, text=col)
            self.column(col, width=100, anchor=tk.W)

        #添加滚动条
        scroll_bar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.yview)
        self.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_song(self,song):
        """"""
        values = [song.get(col.lower(),"") for col in self.columns]
        self.insert("",tk.END,values=values,tags=(song.get('id')))


    def clear(self):
        for item in self.get_children():
            self.delete(item)


    def get_selected_song_id(self):
        """"""
        selected = self.selection()
        if selected:
            return self.item(selected[0], "tags")[0]
        return None

class NowPlayingPanel(tk.LabelFrame):
    """当前播放面板UI"""
    def __init__(self, parent,player,**kwargs):
        super().__init__(parent, **kwargs)
        self.player = player
        #专辑封面
        self.album_art = tk.Label(self, text="专辑封面",bg="gray",width=20,height=10)
        self.album_art.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        #歌曲信息
        info_frame = tk.Frame(self)
        info_frame.grid(row=0, column=1, sticky='w', padx=10, pady=5)

        tk.Label(info_frame, text=" 歌 曲 :",font=("Arial", 10)).grid(row=0, column=0,sticky='w')
        self.song_title = tk.Label(info_frame, text="",font=("Arial", 10,"bold"))
        self.song_title.grid(row=0, column=1,sticky='w')

        tk.Label(info_frame, text=" 歌 手 :",font=("Arial", 10)).grid(row=1, column=0,sticky='w')
        self.song_artist = tk.Label(info_frame, text="",font=("Arial", 10))
        self.song_artist.grid(row=1, column=1,sticky='w')

        tk.Label(info_frame, text=" 专 辑 :", font=("Arial", 10)).grid(row=2, column=0, sticky='w')
        self.song_album = tk.Label(info_frame, text="", font=("Arial", 10))
        self.song_album.grid(row=2, column=1, sticky='w')

        #时间显示
        time_frame = tk.Frame(self)
        time_frame.grid(row=1, column=1, sticky='e', padx=10, pady=5)

        self.current_time = tk.Label(time_frame, text="00:00")
        self.current_time.pack(side=tk.LEFT)
        tk.Label(time_frame, text="/").pack(side=tk.LEFT,padx=5)
        self.total_time = tk.Label(time_frame, text="00:00")
        self.total_time.pack(side=tk.LEFT)

    def update_song_info(self, song):
        """更新当前播放歌曲信息"""
        logger.info(f"更新当前播放歌曲信息：{song}")
        self.album_art.config(image=song['img_path'])
        self.song_title.config(text=song['title'])
        self.song_artist.config(text=song['artist'])
        self.song_album.config(text=song['album'])

        total_time = self.format_time(song['duration'])
        self.total_time.config(text=total_time)
        #通过当前播放进度转化为时间显示
        position  = self.player.position
        current = self.format_time(int(position*song['duration']/100))
        logger.info(f"当前播放进度时间：{current}")
        self.current_time.config(text=current)


    # 格式化时间显示
    def format_time(self,seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def update_time(self,current,total):
        """更新当前播放时间"""
        self.current_time.config(text=self.format_time(current))
        self.total_time.config(text=self.format_time(total))

class PlaybackControls(ttk.Treeview):
    """播放控制面板UI"""
    def __init__(self, parent, player, **kwargs):
        super().__init__(parent,  **kwargs)
        self.player = player

        #按钮控制
        self.prev_btn = ttk.Button(self, text="⏮", command=self.prev_song)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.play_btn = ttk.Button(self, text="▶", command=self.toggle_song)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn = ttk.Button(self, text="⏭", command=self.next_song)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        #进度条控制
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5)
        self.progress_bar.bind("<Button-1>", self.on_progress_click)

        #音量控制
        self.volume_var = tk.DoubleVar(value=self.player.volume)
        self.volume_scale = ttk.Scale(
            self, variable=self.volume_var, from_=0, to=1, orient=tk.HORIZONTAL,
            length=100
        )
        self.volume_scale.pack(side=tk.RIGHT, padx=5)
        tk.Label(self, text="音量").pack(side=tk.RIGHT)



    def prev_song(self):
        """上一首"""
        self.player.play_prev()


    def toggle_song(self):
        """播放/暂停"""
        if self.player.playing and not self.player.paused:
            self.player.pause()
            self.play_btn.config(text="▶")
        else:
            self.player.play()
            self.play_btn.config(text="⏸")


    def next_song(self):
        """下一首"""
        self.player.play_next()

    def on_progress_click(self, event):
        """进度条点击事件"""
        # 计算点击位置对应的百分比
        width = self.progress_bar.winfo_width()
        pos = event.x / width * 100
        self.player.set_position(pos)
        self.progress_var.set(pos)

    def update_progress(self, position):
        """更新进度"""
        self.progress_var.set(position)


