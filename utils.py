# 工具函数
# -*- coding: utf-8 -*-
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import time
import SimpleITK as sitk
class MouseTracker:
    def __init__(self, canvas, callback):
        self.canvas = canvas
        self.callback = callback
        self.canvas.bind('<Motion>', self.mouse_move)
    def mouse_move(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        relative_coordinates = (x, y)
        self.callback(relative_coordinates)
"""
canvas: 要识别的canvas
on_drag_callback: 回调函数
on_double_click_callback： 回调函数
用于右键向上拖拽时将  self.right_click_start_y  数值变化
"""
class RightClickHandler:
    def __init__(self, canvas, on_drag_callback=None, on_double_click_callback=None):
        self.canvas = canvas
        self.right_click_start_y = 0
        self.on_drag_callback = on_drag_callback
        self.on_double_click_callback = on_double_click_callback
        self.bind_events()
    def bind_events(self):
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_click_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_click_release)
        self.canvas.bind("<Double-Button-3>", self.on_double_click)
    def on_right_click(self, event):
        self.right_click_start_y = event.y
    def on_right_click_drag(self, event):
        delta_y = event.y - self.right_click_start_y
        self.right_click_start_y = event.y
        if self.on_drag_callback:
            self.on_drag_callback(delta_y)
    def on_right_click_release(self, event):
        pass
    def on_double_click(self, event):
        if self.on_double_click_callback:
            self.on_double_click_callback()
class MiddleClickHandler:
    def __init__(self, canvas, on_drag_callback=None, on_double_click_callback=None):
        self.canvas = canvas
        self.middle_click_start_x = 0
        self.middle_click_start_y = 0
        self.on_drag_callback = on_drag_callback
        self.on_double_click_callback = on_double_click_callback
        self.bind_events()
    def bind_events(self):
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<B2-Motion>", self.on_middle_click_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_click_release)
        self.canvas.bind("<Double-Button-2>", self.on_double_click)
    def on_middle_click(self, event):
        self.middle_click_start_x = event.x
        self.middle_click_start_y = event.y
    def on_middle_click_drag(self, event):
        delta_x = event.x - self.middle_click_start_x
        delta_y = event.y - self.middle_click_start_y
        self.middle_click_start_x = event.x
        self.middle_click_start_y = event.y
        if self.on_drag_callback:
            self.on_drag_callback([delta_x, delta_y])
    def on_middle_click_release(self, event):
        pass
    def on_double_click(self, event):
        if self.on_double_click_callback:
            self.on_double_click_callback()
class LeftClickHandler:
    def __init__(self, canvas, on_drag_callback=None, on_double_click_callback=None):
        self.canvas = canvas
        self.left_click_start_x = 0
        self.left_click_start_y = 0
        self.on_drag_callback = on_drag_callback
        self.on_double_click_callback = on_double_click_callback
        self.bind_events()
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_left_click_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_click_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
    def on_left_click(self, event):
        self.left_click_start_x = event.x
        self.left_click_start_y = event.y
    def on_left_click_drag(self, event):
        delta_x = event.x - self.left_click_start_x
        delta_y = event.y - self.left_click_start_y
        self.left_click_start_x = event.x
        self.left_click_start_y = event.y
        if self.on_drag_callback:
            self.on_drag_callback([delta_x, delta_y])
    def on_left_click_release(self, event):
        pass
    def on_double_click(self, event):
        if self.on_double_click_callback:
            self.on_double_click_callback()
'''
描述：一个可以触发点击效果的按钮
parent:父级构建，可以是frame等
your_function：自己定义的点击触发函数
**kwargs：输入按钮相关的参数，可以设置为这种
        label_options = {"text": 'btn_text', 'bg': '#b0b1b3','relief': 'raised'}
用法：ClickableLabel(root,your_function, **button_options).pack()
'''
class ClickableLabel(tk.Label):
    def __init__(self, frame, your_function, **kwargs):
        super().__init__(frame,**kwargs)
        self.your_function = your_function
        # 绑定鼠标事件
        self.bind("<Button-1>", self.toggle_active)
        self.bind("<ButtonRelease-1>", self.toggle_active)
    def toggle_active(self, event):
        if event.type == tk.EventType.ButtonPress:
            self["fg"] = 'red'
            self.your_function()
        elif event.type == tk.EventType.ButtonRelease:
            self["fg"] = self["fg"] if self["fg"] != 'red' else "#abe338"
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', lambda _: self.show_tip())
        self.widget.bind('<Leave>', lambda _: self.hide_tip())
    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() -20
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        tw.attributes("-topmost", True)  # 置顶
        tw.lift()  # 窗口置顶等级再提升
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                              background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                              font=("宋体", "10", "normal"))
        label.pack(ipadx=1)
    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
class SignalHistogram(tk.Toplevel):
    def __init__(self, array):
        super().__init__()
        self.title("Signal Histogram")
        # self.geometry("600x400")  # Optionally set a default size
        # -------------窗口居中---------------
        # 设置窗口大小
        winWidth = 600
        winHeight = 400
        # 获取屏幕分辨率
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        # 中间位置坐标
        x = int((screenWidth - winWidth) / 2)
        y = int((screenHeight - winHeight) / 2)
        # 设置窗口初始位置在屏幕居中
        self.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
        # -------------设置窗口置顶---------------
        self.wm_attributes('-topmost', 1)
        min_signal = np.min(array)
        # 将三维数组转换为一维数组
        flattened_array = array.flatten()
        # 排除信号值为0的数据
        flattened_array = flattened_array[flattened_array > min_signal]
        # 创建Figure和Axes对象
        fig, ax = plt.subplots()
        # 绘制直方图
        ax.hist(flattened_array, bins=100)
        ax.set_title("Signal Histogram")
        ax.set_xlabel("Signal Value")
        ax.set_ylabel("Frequency")
        # 设置坐标轴的文字大小
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.tick_params(axis='both', which='minor', labelsize=6)
        # 创建一个Frame来承载FigureCanvasTkAgg，以便它可以随窗口大小变化
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        # 创建FigureCanvasTkAgg对象，并将其嵌入到Tkinter窗口中
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        # 将绘图区域放置在Tkinter窗口中
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
"""
用于读取nifti文件，获取array
"""
class Nifti2ArrayFrame():
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = sitk.ReadImage(self.file_path)
        # 放射变换的方向矩阵
        self.direction = np.array(self.image.GetDirection()).reshape((3, 3))
    def load_nifti(self):
        array = sitk.GetArrayFromImage(self.image)
        """
        放射变换矩阵
        [[1. 0. 0.]
        [0. -1. 0.]
        [0. 0. 1.]]
        通过什么样的运算可以实现了三维数组所代表的图像的翻转？
        在放射变换矩阵中，你提供的是一个单位矩阵，其中第二行的值是-1，这意味着在y轴方向上应用了一个镜像翻转。你可以通过numpy的索引语法来实现这个翻转。
        在使用numpy来处理多维数组时，你可以使用::-1来反转数组的维度。
        例如，对于一个二维数组，array[::-1]将翻转第一个维度（即行），array[:, ::-1]将翻转第二个维度（即列）。对于三维数组，array[:, ::-1, :]将翻转第二个维度。
        """
        # print(self.direction)
        array = array[::int(self.direction[0][0]), ::int(self.direction[1][1]), ::int(self.direction[2][2])]
        return array
"""
简单版，供测试用，有中键、左键、右键
"""
class Simple_ShowTheImage_with_3D_array(tk.Frame):
    def __init__(self, master, array):
        super().__init__(master)
        self.array = array
        self.current_slice = self.array.shape[0] // 2   # 设置初始的显示位置为中间
        self.photo = None
        self.current_scale = 1.0
        self.right_click_start_x = 0
        self.right_click_start_y = 0
        self.middle_click_start_x = 0
        self.middle_click_start_y = 0
        self.pan_offset_x = None
        self.pan_offset_y = None
        self.last_update_time = 0
        self.update_interval = 1 / 90  # Update at most 30 times per second
        # 主背景建立在一个frame上
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)
        # Canvas建立在主背景上
        self.canvas_width = 200
        self.canvas_height = 200
        self.canvas = tk.Canvas(self.frame, bg='black', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill="both", expand=True)
        # 添加滑动条按钮
        self.slider = tk.Scale(self.frame, from_=0, to=self.array.shape[0] - 1, orient=tk.HORIZONTAL,command=self.update_image, showvalue=False)
        self.slider.pack(fill="x")
        self.slice_label = tk.Label(self.frame, text="Slice: 0")
        self.slice_label.pack()
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_click_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_click_release)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<B2-Motion>", self.on_middle_click_drag)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_click_release)
        self.update_image(self.current_slice)
    def reset_canvas(self):
        # 将Canvas的大小和位置还原到初始值
        self.canvas.delete("image")
        self.pan_offset_x = None
        self.pan_offset_y = None
        self.update_image(self.current_slice)
    def array_to_photoimage(self, array):
        array_normalized = (array - array.min()) / (array.max() - array.min())
        img = Image.fromarray((array_normalized * 255).astype('uint8'), mode='L')
        img_resized = img.resize((int(img.width * self.current_scale), int(img.height * self.current_scale)), Image.NEAREST)
        return ImageTk.PhotoImage(img_resized)
    def update_image(self, slice_index):
        slice_index = int(slice_index)         # 操作可以丝滑，但是数值得是整数
        self.slider.set(slice_index)        # 初始化滑动条的位置
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            # self.photo = self.array_to_photoimage(np.flipud(self.array[slice_index, :, :]))
            self.photo = self.array_to_photoimage(self.array[slice_index, :, :])
            # 设定图像的初始位置
            if self.pan_offset_x is None:
                self.pan_offset_x = self.canvas_width // 2
            if self.pan_offset_y is None:
                self.pan_offset_y = self.canvas_height // 2
            self.canvas.delete("image")  # 删除之前的图像
            self.canvas.create_image(self.pan_offset_x, self.pan_offset_y, image=self.photo, anchor="c", tags="image")
            self.last_update_time = current_time
            # Update the slice label
            self.slice_label.config(text=f"Slice: {slice_index}")
    def on_scroll(self, event):
        if event.delta > 0:
            self.current_slice = max(0, self.current_slice - 1)
        else:
            self.current_slice = min(self.array.shape[0] - 1, self.current_slice + 1)
        self.update_image(self.current_slice)
    def on_right_click(self, event):
        self.right_click_start_x = event.x
        self.right_click_start_y = event.y
    def on_right_click_drag(self, event):
        delta_y = event.y - self.right_click_start_y
        self.current_scale += delta_y * 0.01
        self.current_scale = max(0.1, self.current_scale)
        self.right_click_start_y = event.y
        self.update_image(self.current_slice)
    def on_right_click_release(self, event):
        pass
    def on_middle_click(self, event):
        self.middle_click_start_x = event.x
        self.middle_click_start_y = event.y
    def on_middle_click_drag(self, event):
        delta_x = event.x - self.middle_click_start_x
        delta_y = event.y - self.middle_click_start_y
        self.pan_offset_x += delta_x
        self.pan_offset_y += delta_y
        self.middle_click_start_x = event.x
        self.middle_click_start_y = event.y
        self.update_image(self.current_slice)
    def on_middle_click_release(self, event):
        pass
class LianDong_ShowTheImage_with_3D_array(tk.Frame):
    def __init__(self, master, array, tabs):
        super().__init__(master)
        self.array = array
        self.tabs = tabs
        self.canvas_width = 240
        self.canvas_height = 240
        self.alpha = 100  # 透明度
        self.current_scale = 1.3  # 放大倍率
        self.current_slice = self.array.shape[0] // 2   # 设置初始的显示位置为中间
        self.last_update_time = 0
        self.update_interval = 1 / 90  # Update at most 30 times per second
        self.photo = None
        # 主背景建立在一个frame上
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)
        # Canvas建立在主背景上
        self.canvas = tk.Canvas(self.frame, bg='black', width=self.canvas_width, height=self.canvas_height, highlightthickness=1)
        self.canvas.pack(fill="both", expand=True)
        # 创建LeftClickHandler的实例
        self.scale_label = self.canvas.create_text(5, 10, text=self.tabs, fill="white", tags='canvas_lable', anchor=tk.W,
                                                    font=("Helvetica", 12))
        # 创建LeftClickHandler的实例
        self.min_signal = round(np.amin(array),1)     # 最小的信号值
        self.max_signal = round(np.amax(array),1)   # 最大的信号值
        self.window_width = self.max_signal-self.min_signal
        self.window_level = (self.max_signal-self.min_signal)/2
        self.left_click_handler = LeftClickHandler(self.canvas, self.on_drag_left_click, self.on_double_left_click)
        self.update_image(self.current_slice)
    # ————————————————————————————————————————————————————————
    # 左键相关事件
    def on_drag_left_click(self, delta):
        delta_x, delta_y = delta
        self.window_width = int(self.window_width) + delta_x
        self.window_level = int(self.window_level) + delta_y
        minMax = f"{self.window_level - (self.window_width / 2)},{self.window_level + (self.window_width / 2)}"
        self.update_label(self.canvas, minMax)
        self.update_image(self.current_slice)
    def on_double_left_click(self):
        self.window_width = self.max_signal - self.min_signal
        self.window_level = (self.max_signal - self.min_signal) / 2
        minMax = f"{self.window_level - (self.window_width / 2)},{self.window_level + (self.window_width / 2)}"
        self.update_label(self.canvas, minMax)
        self.update_image(self.current_slice)
    # #############
    def array_to_normalized_alpha(self, array, window_width, window_level):
        orig_min_signal = np.amin(array)
        window_width = int(window_width)
        window_level = int(window_level)
        min_signal_strength = window_level - window_width // 2
        max_signal_strength = window_level + window_width // 2
        # 创建掩码，将最小值部分设为 True，其他部分设为 False
        mask = array <= orig_min_signal
        # 创建副本以确保不修改原始数组
        array_copy = array.copy()
        # 将掩码部分设为最小信号强度
        array_copy[mask] = min_signal_strength
        array_clipped = np.clip(array_copy, min_signal_strength, max_signal_strength)
        array_normalized = np.interp(array_clipped, (min_signal_strength, max_signal_strength), (0, 255))
        array_normalized_alpha = array_normalized * self.alpha//100
        return array_normalized_alpha
    def update_image(self, slice_index):
        slice_index = int(slice_index)         # 操作可以丝滑，但是数值得是整数
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            array_normalized_alpha_2D = self.array_to_normalized_alpha(self.array[slice_index, :, :], self.window_width, self.window_level)
            img = Image.fromarray(array_normalized_alpha_2D.astype('uint8'), mode='L')
            img_resized = img.resize((int(img.width * self.current_scale), int(img.height * self.current_scale)),
                                     Image.NEAREST)
            self.photo = ImageTk.PhotoImage(img_resized)
            # 设定图像的初始位置
            self.canvas.delete("image")  # 删除之前的图像
            self.canvas.create_image(self.canvas_width// 2, self.canvas_height// 2, image=self.photo, anchor="c", tags="image")
            self.canvas.tag_lower('image', 'canvas_lable')  # 将 'image' 置于 'canvas_lable' 之下
            self.last_update_time = current_time
    def update_label(self, canvas, coordinates):
        canvas.itemconfig(self.scale_label, text=f"Hi: {coordinates}")
    def on_scroll(self, slice_index):
        self.current_slice = slice_index
        self.update_image(self.current_slice)
    def alpha_change(self, alpha):
        print(f'调整透明度为{alpha}')
        self.alpha = alpha
        self.update_image(self.current_slice)
    def out_put_data(self):
        array_normalized_alpha_3D = self.array_to_normalized_alpha(self.array, self.window_width, self.window_level)
        return array_normalized_alpha_3D
class justShowTheImage_with_3D_array(tk.Frame):
    def __init__(self, master, array, plane):
        super().__init__(master)
        self.plane = plane  # 选择什么层面
        self.array = array  # 输入数组
        self.photo = None
        if self.plane == 'Axial':
            self.current_slice = self.array.shape[0] // 2  # 设置初始的显示位置为中间
            self.max_slice = self.array.shape[0] - 1
            self.canvas_width = 540
            self.canvas_height = 540
        elif self.plane == 'Sagittal':
            self.current_slice = self.array.shape[1] // 2  # 设置初始的显示位置为中间
            self.max_slice = self.array.shape[1] - 1
            self.canvas_width = 270
            self.canvas_height = 180
        elif self.plane == 'Coronal':
            self.current_slice = self.array.shape[2] // 2  # 设置初始的显示位置为中间
            self.max_slice = self.array.shape[2] - 1
            self.canvas_width = 270
            self.canvas_height = 180
        else:
            print('参数错误')
        # 设置初始放大倍率
        # self.canvas_width = 500
        # self.canvas_height = 500
        # print(f'先找到三维数组中最长的维度，'
        #       f'比如{array.shape}中最长的是{np.max(array.shape)}，'
        #       f'框架大小为({self.canvas_width},{self.canvas_height}),最长的边为{np.max((self.canvas_width, self.canvas_height))}'
        #       f'那么初始放大倍率为  np.max((self.canvas_width,self.canvas_height)) / np.max(array.shape)')
        # self.orig_scale = 1.0   # 初始放大比率
        self.orig_scale = round(np.min((self.canvas_width, self.canvas_height)) / np.min(array.shape), 1)
        # 下面的
        self.min_signal = 0  # 最小的信号值
        self.max_signal = round(np.amax(array), 1)  # 最大的信号值
        self.last_update_time = 0  # 用于限制刷新率
        self.update_interval = 1 / 90  # 每秒最大刷新90次
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # _____________________________________
        self.selfeee = tk.Frame(self, bg='black')
        self.selfeee.grid(row=0, column=0, sticky="nsew")
        def show_box():
            # 切换self.entry_box的可见性
            if self.entry_box.winfo_viewable():
                self.entry_box.grid_forget()  # 隐藏
            else:
                self.entry_box.grid(row=1, column=0, sticky="nsew")
                SignalHistogram(self.array)
        def select_plane(plane):
            if plane == 'Axial':
                self.plane = 'Axial'
            elif plane == 'Sagittal':
                self.plane = 'Sagittal'
            elif plane == 'Coronal':
                self.plane = 'Coronal'
            else:
                print('error')
            self.update_image(self.current_slice)
        # 添加复位按钮
        button_options_small = {'bg': '#2b2b2b', 'fg': '#abe338', 'relief': 'groove', 'font': ("Helvetica", 7, "bold"),
                                'width': 2, 'height': 1, 'anchor': 'center'}
        ClickableLabel(self.selfeee, lambda: select_plane('Axial'), text='Ax', **button_options_small).pack(
            anchor="center", side='left')
        ClickableLabel(self.selfeee, lambda: select_plane('Sagittal'), text='Sa', **button_options_small).pack(
            anchor="center", side='left')
        ClickableLabel(self.selfeee, lambda: select_plane('Coronal'), text='Co', **button_options_small).pack(
            anchor="center", side='left')
        # 添加滑动条按钮
        self.slider = tk.Scale(self.selfeee, from_=0, to=self.max_slice, orient=tk.HORIZONTAL,
                               showvalue=False, highlightthickness=0, command=self.update_image,
                               bg='black', troughcolor='#3d3d3d',
                               sliderrelief='flat', activebackground='red')
        self.slider.pack(fill="x", expand=True, anchor="center", side='left')
        # 添加复位按钮
        button_options = {'bg': '#2b2b2b', 'fg': '#abe338', 'relief': 'groove', 'font': ("Helvetica", 7, "bold"),
                          'width': 4, 'height': 1, 'anchor': 'center'}
        self.info_button = ClickableLabel(self.selfeee, show_box, text='info', **button_options)
        self.info_button.pack(anchor="center", side='left')
        Tooltip(self.info_button, 'sss')
        # __________________________
        self.entry_box = tk.Frame(self)
        # self.entry_box.grid(row=2, column=0, sticky="nsew")
        self.entry_box.pack_forget()
        # 信息显示标签
        self.slice_label = tk.Label(self.entry_box, text="Slice: 0", width=8, anchor=tk.W, justify='left',
                                    font=("Helvetica", 8))
        self.slice_label.pack(side='left')
        # 窗宽窗位
        self.min_sss = tk.Variable()
        self.min_sss.set(self.min_signal)  # 设置初始值为最小信号值
        tk.Label(self.entry_box, text='min', font=("Helvetica", 8)).pack(side='left')
        tk.Entry(self.entry_box, textvariable=self.min_sss, width=5, font=("Helvetica", 8)).pack(side='left')
        self.max_sss = tk.Variable()
        self.max_sss.set(self.max_signal)  # 设置初始值为最大信号值
        tk.Label(self.entry_box, text='max', font=("Helvetica", 8)).pack(side='left')
        tk.Entry(self.entry_box, textvariable=self.max_sss, width=5, font=("Helvetica", 8)).pack(side='left')
        # __________________________
        self.selfeeessss = tk.Frame(self)
        self.selfeeessss.grid(row=2, column=0, sticky="nsew")
        # Canvas建立在主背景上
        self.canvas = tk.Canvas(self.selfeeessss, bg='black', width=self.canvas_width, height=self.canvas_height,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        MouseTracker(self.canvas, self.update_label)
        # ——————————————————————————————
        # 创建RightClickHandler的实例
        self.current_scale = self.orig_scale
        self.right_click_handler = RightClickHandler(self.canvas, self.on_drag_right_click, self.on_double_right_click)
        # 创建MiddleClickHandler的实例
        self.pan_offset_x = None
        self.pan_offset_y = None
        self.middle_click_handler = MiddleClickHandler(self.canvas, self.on_drag_middle_click,
                                                       self.on_double_middle_click)
        # 创建LeftClickHandler的实例
        self.window_width = self.max_signal - self.min_signal
        self.window_level = (self.max_signal - self.min_signal) / 2
        self.left_click_handler = LeftClickHandler(self.canvas, self.on_drag_left_click, self.on_double_left_click)
        self.scale_label = self.canvas.create_text(5, 10, text="Hi!", fill="white",
                                                   tags='text__scale_label', anchor=tk.W, font=("Helvetica", 7))
        self.canvas.tag_raise('text__scale_label')
        self.update_image(self.current_slice)
    def update_label(self, coordinates):
        self.canvas.itemconfig(self.scale_label, text=f"Hi: {coordinates}")
    # ————————————————————————————————————————————————————————
    # 右键相关事件
    def on_drag_right_click(self, delta_y):
        self.current_scale += delta_y * 0.01
        self.current_scale = round(max(0.1, self.current_scale), 2)
        self.update_image(self.current_slice)
    def on_double_right_click(self):
        self.current_scale = self.orig_scale
        self.update_image(self.current_slice)
    # ————————————————————————————————————————————————————————
    # 中键相关事件
    def on_drag_middle_click(self, delta):
        delta_x, delta_y = delta
        self.pan_offset_x += delta_x
        self.pan_offset_y += delta_y
        self.update_image(self.current_slice)
    def on_double_middle_click(self):
        self.current_scale = self.orig_scale
        self.pan_offset_x = None
        self.pan_offset_y = None
        self.update_image(self.current_slice)
    # ————————————————————————————————————————————————————————
    # 左键相关事件
    def on_drag_left_click(self, delta):
        delta_x, delta_y = delta
        self.window_width = int(self.window_width) + delta_x
        self.window_level = int(self.window_level) + delta_y
        countMinMaxSignal = self.count_min_max_signal()
        self.min_sss.set(countMinMaxSignal[0])
        self.max_sss.set(countMinMaxSignal[1])
        self.update_image(self.current_slice)
    def on_double_left_click(self):
        self.window_width = self.max_signal - self.min_signal
        self.window_level = (self.max_signal - self.min_signal) / 2
        countMinMaxSignal = self.count_min_max_signal()
        self.min_sss.set(countMinMaxSignal[0])
        self.max_sss.set(countMinMaxSignal[1])
        self.update_image(self.current_slice)
    # ————————————————————————————————————————————————————————
    def on_canvas_resize(self, event):
        # 在整体窗口大小发生变化时，更新图像偏移值以将其保持在canvas的中心
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.pan_offset_x = self.canvas_width // 2
        self.pan_offset_y = self.canvas_height // 2
        self.update_image(self.current_slice)
    def count_min_max_signal(self):
        self.window_width = int(self.window_width)
        self.window_level = int(self.window_level)
        min_signal_strength = self.window_level - self.window_width // 2
        max_signal_strength = self.window_level + self.window_width // 2
        return [min_signal_strength, max_signal_strength]
    def array_to_photoimage(self, array):
        countMinMaxSignal = self.count_min_max_signal()
        min_signal_strength = countMinMaxSignal[0]
        max_signal_strength = countMinMaxSignal[1]
        array_clipped = np.clip(array, min_signal_strength, max_signal_strength)
        array_normalized = np.interp(array_clipped, (min_signal_strength, max_signal_strength), (0, 255))
        img = Image.fromarray(array_normalized.astype('uint8'), mode='L')
        img_resized = img.resize((int(img.width * self.current_scale), int(img.height * self.current_scale)),
                                 Image.NEAREST)
        return ImageTk.PhotoImage(img_resized)
    def update_image(self, slice_index):
        slice_index = int(slice_index)  # 操作可以丝滑，但是数值得是整数
        self.slider.set(slice_index)  # 初始化滑动条的位置
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            if self.plane == 'Axial':
                # self.photo = self.array_to_photoimage(np.flipud(self.array[slice_index, :, :]))
                self.photo = self.array_to_photoimage(self.array[slice_index, :, :])
            elif self.plane == 'Sagittal':
                self.photo = self.array_to_photoimage(np.flipud(self.array[:, :, slice_index]))
                # self.photo = self.array_to_photoimage(self.array[:, :, slice_index])
            elif self.plane == 'Coronal':
                self.photo = self.array_to_photoimage(np.flipud(self.array[:, slice_index, :]))
                # self.photo = self.array_to_photoimage(self.array[:, slice_index, :])
            else:
                print('参数错误')
            # 设定图像的初始位置
            if self.pan_offset_x is None:
                self.pan_offset_x = self.canvas_width // 2
            if self.pan_offset_y is None:
                self.pan_offset_y = self.canvas_height // 2
            self.canvas.delete("image")  # 删除之前的图像
            self.canvas.create_image(self.pan_offset_x, self.pan_offset_y, image=self.photo, anchor="c", tags="image")
            self.canvas.tag_lower('image', 'text__scale_label')  # 将 'image' 置于 'text__scale_label' 之下
            self.last_update_time = current_time
            # Update the slice label
            self.slice_label.config(text=f"Slice: {slice_index}")
            self.current_slice = slice_index
    def on_scroll(self, event):
        if event.delta > 0:
            self.current_slice = max(0, self.current_slice - 1)
        else:
            self.current_slice = min(self.array.shape[0] - 1, self.current_slice + 1)
        self.update_image(self.current_slice)
