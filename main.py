# -*- coding: utf-8 -*-
import configparser
import os
import shutil
import threading
from utils import Nifti2ArrayFrame, LianDong_ShowTheImage_with_3D_array
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox
from RUN3_Registration import MRIRegistration
from RUN4_Skull_Stripe import SkullStripe
class fourfourfour(tk.Frame):
    def __init__(self, master, array_6lists):
        super().__init__(master)
        # 创建主Frame
        self.Main_Frame = tk.Frame(master, bg='black')
        self.Main_Frame.pack(fill="both", expand=True)
        # 添加滑动条按钮
        self.slider = tk.Scale(self.Main_Frame, from_=0, to=200, orient=tk.HORIZONTAL,
                               showvalue=False, highlightthickness=0, command=self.update_image,
                               bg='black', troughcolor='#3d3d3d',
                               sliderrelief='flat', activebackground='red')
        self.slider.pack(fill="x", anchor="center")
        # 创建可滑动显示的 Canvas 和 滑动条
        self.canvas_drag = tk.Canvas(self.Main_Frame, borderwidth=0, width=240, bg='black')
        self.canvas_drag.pack(side="left", fill="both", expand=True)
        self.vsb = tk.Scrollbar(self.Main_Frame, orient="vertical", command=self.canvas_drag.yview)
        self.vsb.pack(side="left", fill="y")
        self.canvas_drag.configure(yscrollcommand=self.vsb.set)
        # 创建Canvas内的frame以及设定，最后的所有东西都放置在 self.frame_drag 中
        def onFrameConfigure(canvas):
            # 当frame大小改变时，重设canvas的滚动区域
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.frame_drag = tk.Frame(self.canvas_drag, bg='black')
        self.canvas_drag.create_window((0, 0), window=self.frame_drag, anchor="nw")
        self.frame_drag.bind("<Configure>", lambda event, canvas=self.canvas_drag: onFrameConfigure(canvas))
        #  ------------------------------------------
        # Create the instances
        self.instances = []
        for sequence_name,file_name in array_6lists.items():
            self.instances.append(
                LianDong_ShowTheImage_with_3D_array(self.frame_drag, Nifti2ArrayFrame(file_name).load_nifti(), sequence_name)
            )
        for i in range(len(self.instances)):
            instance = self.instances[i]
            instance.pack(fill='x', expand=True)
    def update_image(self, slice_index):
        slice_index = int(slice_index)         # 操作可以丝滑，但是数值得是整数
        self.slider.set(slice_index)        # 初始化滑动条的位置
        print(slice_index)
        for instance in self.instances:
            instance.on_scroll(slice_index)
    def reset(self, array_6lists):
        # 销毁self.frame_drag中的所有子组件
        for child in self.frame_drag.winfo_children():
            child.destroy()
        # 清空self.instances
        self.instances = []
        # 重新创建和展示新的实例
        for sequence_name, file_name in array_6lists.items():
            self.instances.append(
                LianDong_ShowTheImage_with_3D_array(self.frame_drag, Nifti2ArrayFrame(file_name).load_nifti(), sequence_name)
            )
        for i in range(len(self.instances)):
            instance = self.instances[i]
            instance.pack(fill='x', expand=True)
class MAIN_DIV(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config_path = 'config.ini'
        self.config = configparser.ConfigParser()
        self.last_open_path = self.load_last_open_path()
        # --------------------------------------------------------------------
        # 左边的两侧图像显示
        # --------------------------------------------------------------------
        # 第一栏 原始图像
        self.Frame_LEFT = tk.Frame(root)
        self.Frame_LEFT.pack(side='left', anchor=tk.NW, fill="y")
        # 第二栏 对比图像
        self.Frame_LEFT_2 = tk.Frame(root)
        self.Frame_LEFT_2.pack(side='left', anchor=tk.NW, fill="y")
        # ---------------------------------------------
        self.Inpot_button = tk.Button(self.Frame_LEFT,text='Multimodal (max=6)',fg='#abe338',bg='black',font=("Helvetica", 16, "bold"))
        self.Inpot_button.pack(fill="x")
        # 默认打开
        import_dict = {
            'T1': r'tools/defualt_show/t1.nii.gz',
            'T1CE': r'tools/defualt_show/t1ce.nii.gz',
            'T2': r'tools/defualt_show/t2.nii.gz',
            'T2Flair': r'tools/defualt_show/Flair.nii.gz',
            'DWI': r'tools/defualt_show/DWI.nii.gz',
            'ADC': r'tools/defualt_show/ADC.nii.gz',
        }
        self.f = fourfourfour(self.Frame_LEFT, import_dict)
        # ---------------------------------------------
        self.Inpot_button = tk.Button(self.Frame_LEFT_2,text='Comparisons',fg='#abe338',bg='black',font=("Helvetica", 16, "bold"))
        self.Inpot_button.pack(fill="x")
        # 默认打开
        compare_import_dict = {}
        self.ff = fourfourfour(self.Frame_LEFT_2, compare_import_dict)
        # --------------------------------------------------------------------
        # 右边的大界面 分成上中下 上边分成三列
        # --------------------------------------------------------------------
        self.Frame_RIGHT = tk.Frame(root, bg='#2b2b2b')
        self.Frame_RIGHT.pack(side='left', fill='x', anchor=tk.NW, padx=10, expand=True)
        # 第一行
        first_line = tk.Frame(self.Frame_RIGHT, bg='#2b2b2b')
        first_line.pack(anchor='w',fill='x', expand=True)
        # 第二行
        second_line = tk.Frame(self.Frame_RIGHT, bg='#2b2b2b')
        second_line.pack(fill='x',anchor='w', expand=True)
        sep = ttk.Separator(second_line, orient='horizontal', style='red.TSeparator')
        sep.pack(padx=0, pady=20, fill='x', expand=True)
        # 第三行
        third_line = tk.Frame(self.Frame_RIGHT, bg='#2b2b2b')
        third_line.pack(fill='x',anchor='center', expand=True)
        sep = ttk.Separator(third_line, orient='horizontal', style='red.TSeparator')
        sep.pack(padx=0, pady=20, fill='x', expand=True)
        # 第二行的第1列
        first_col = tk.Frame(second_line, bg='#2b2b2b')
        first_col.pack(side='left',anchor='w')
        # 第二行的第2列
        second_col = tk.Frame(second_line, bg='#2b2b2b')
        second_col.pack(side='left',anchor='w',padx=10)
        # 第二行 第2 3列之间空隙
        tk.Frame(second_line, bg='#2b2b2b',width=30).pack(side='left', anchor='w')
        # 第二行的第3列
        third_col = tk.Frame(second_line, bg='#2b2b2b')
        third_col.pack(fill='x', side='left', expand=True, anchor='w')
        # --------------------------------------------------------------------
        # 第一行
        # --------------------------------------------------------------------
        first_line_content = tk.Frame(first_line, bg='#2b2b2b')
        first_line_content.pack( fill='x', expand=True,anchor='w')
        tk.Button(first_line_content, text='Rec and Import',
                  fg='red', bg='black', font=("Helvetica", 15, "bold"),
                  command=self.select_files).pack(side='left')
        tk.Label(first_line_content,
                 text='← NIFTI files:  t1  t1ce  t2  flair  DWI(b1000)  ADC',
                 bg='#2b2b2b', fg='white', font=("Helvetica", 12)
                 ).pack(side='left')
        # --------------------------------------------------------------------
        # 第二行 第一列
        # --------------------------------------------------------------------
        modules_div_style = {'anchor': 'w', 'justify': 'left','fg':'#afb1b3','bg':'#3c3f41',
                             'width':13, 'font':("Helvetica", 15, "bold")}
        modules_div_star_style = {'anchor': 'w', 'justify': 'left','fg':'#e9f2f8','bg':'#304a6b',
                             'width':2, 'font':("Helvetica", 9)}
        modules_div_label_style = {'anchor': 'w', 'justify': 'left','fg':'white','bg':'#2b2b2b',
                             'width':15, 'font':("Helvetica", 12)}
        # 存储所有按钮的状态
        self.buttons = {}
        # 存储所有按钮对应的函数
        self.functions = {
            "Denoising": self.RUN_Denoising,
            "N4bias": self.RUN_N4bias,
            "Registration": self.RUN_Registration,
            "Skull Stripe": self.RUN_Skull_Stripe,
            "Normalization": self.RUN_Normalization,
            "Auto Seg": self.RUN_Auto_Seg,
            "Radiomics": self.RUN_Radiomics,
            "Select Model": self.RUN_Select_Model
        }
        for i, text in enumerate(['Denoising', 'N4bias', 'Registration', 'Skull Stripe','Normalization', 'Auto Seg', 'Radiomics', 'Select Model']):
            self.buttons[text] = tk.Button(first_col, text='  ' + text, **modules_div_style,command=lambda text=text: self.toggle_button(text))
            self.buttons[text].grid(row=i, column=0, padx=0, sticky='w')
        self.wuJiaoXing_buttons = {}  # 存储所有按钮的状态
        for i, text in enumerate(['★', '★', '★', '★','★', '★', '★', '★']):
            self.wuJiaoXing_buttons[text] = tk.Button(first_col, text=text, **modules_div_star_style)
            self.wuJiaoXing_buttons[text].grid(row=i, column=1, padx=0, sticky='wns')
        self.labels_buttons = {}  # 存储所有按钮的状态
        for i, text in enumerate(['ADF', 'simpleITK', 'ANTs', 'brain mask','WhiteStripe', 'CDK-module', 'pyradiomics v1.4', 'main']):
            self.wuJiaoXing_buttons[text] = tk.Label(first_col, text=' ' + text, **modules_div_label_style)
            self.wuJiaoXing_buttons[text].grid(row=i, column=2, padx=0, sticky='w')
        # --------------------------------------------------------------------
        # 第二行 第二列
        # --------------------------------------------------------------------
        tk.Button(second_col, text='RUN',width=8,
                  fg='#abe338', bg='black', font=("Helvetica", 20, "bold"),
                  command=self.threading_print_buttons).grid(row=1, column=0, padx=0,rowspan=2, sticky='nswe')
        # tk.Button(second_col, text='STOP',width=12,
        #           fg='#abe338', bg='black', font=("Helvetica", 20, "bold"),
        #           command=self.empty).grid(row=1, column=1, padx=0, sticky='w')
        # tk.Button(second_col, text='CONTINUE',width=12,
        #           fg='#abe338', bg='black', font=("Helvetica", 20, "bold"),
        #           command=self.empty).grid(row=2, column=1, padx=0, sticky='w')
        # --------------------------------------------------------------------
        # 第二行 第三列 third_col
        # --------------------------------------------------------------------
        # --------------------------------------------------------------------
        # 第三行 third_line
        # --------------------------------------------------------------------
        with open('what2say.txt', 'r', encoding='utf-8') as f:
            file_content = f.read()
        file_lines = file_content.splitlines()
        # 创建一个框架来容纳Listbox和滚动条
        frame = tk.Frame(third_line)
        frame.pack(side="right", expand=True, fill="both")
        # 创建垂直滚动条并放置
        sb_y = tk.Scrollbar(frame)
        sb_y.pack(side="right", fill="y")
        # 创建水平滚动条并放置
        sb_x = tk.Scrollbar(frame, orient="horizontal")
        sb_x.pack(side="bottom", fill="x")
        # 创建下拉文字框并放置
        var1 = tk.StringVar()
        var1.set(file_lines)  # 这里没问题的
        self.lb = tk.Listbox(frame, listvariable=var1, yscrollcommand=sb_y.set, xscrollcommand=sb_x.set,
                        bg='#323232', fg='white', font=("Helvetica", 12), height=100)
        self.lb.pack(side="left", expand=True, fill="both")
        # 将两者联动
        sb_y.config(command=self.lb.yview)
        sb_x.config(command=self.lb.xview)
    def toggle_button(self, text):
        # 检查按钮的颜色并切换它
        if self.buttons[text].cget('bg') == '#3c3f41':
            self.buttons[text].config(bg='#094eda')  # 改变颜色
            self.buttons[text].config(fg='#f4e27a')  # 改变颜色
        else:
            self.buttons[text].config(bg='#3c3f41')  # 恢复颜色
            self.buttons[text].config(fg='#afb1b3')  # 改变颜色
    def print_buttons(self):
        # 打印出所有变色的按钮
        for text, button in self.buttons.items():
            if button.cget('bg') == '#094eda':
                function = self.functions.get(text)
                if function:
                    self.lb.insert(tk.END, f"{'#' * 60}")
                    self.lb.insert(tk.END, f"{' ' * 50} {text} {' ' * 30}")
                    self.lb.insert(tk.END, f"{'#' * 60}")
                    function()  # 执行对应的函数
    def threading_print_buttons(self):
        threading.Thread(target=self.print_buttons).start()
    def empty(self):
        pass
    # ----------------------- 功能按钮 --------------------------------
    def RUN_Denoising(self):
        print("RUN_Denoising")
        self.lb.insert(tk.END, f"预计2分钟")
    def RUN_N4bias(self):
        print("RUN_N4bias")
        self.lb.insert(tk.END, f"预计2分钟")
    # 配准
    def RUN_Registration(self):
        print("RUN_Registration")
        self.lb.insert(tk.END, f"预计3-5分钟")
        mri_reg = MRIRegistration()
        mri_reg.one_click('result_data')
    def RUN_Skull_Stripe(self):
        print("RUN_Skull_Stripe")
        self.lb.insert(tk.END, f"预计<1分钟")
        mri_b = SkullStripe()
        mri_b.one_click([])
    def RUN_Normalization(self):
        print("RUN_Normalization")
        self.lb.insert(tk.END, f"预计2分钟")
    def RUN_Auto_Seg(self):
        print("RUN_Auto_Seg")
        self.lb.insert(tk.END, f"预计5分钟")
    def RUN_Radiomics(self):
        print("RUN_Radiomics")
        self.lb.insert(tk.END, f"预计<1分钟")
    def RUN_Select_Model(self):
        print("RUN_Select_Model")
        self.lb.insert(tk.END, f"预计<1分钟")
    # 设置导入的文件名，即文件名必须遵循设置文件中规定的规则
    def load_Multimodals(self):
        self.config.read(self.config_path)
        keywords = [
            self.config.get('Multimodals', 't1wi'),
            self.config.get('Multimodals', 't2wi'),
            self.config.get('Multimodals', 't1ce'),
            self.config.get('Multimodals', 't2flair'),
            self.config.get('Multimodals', 'dwi'),
            self.config.get('Multimodals', 'adc'),
        ]
        return keywords
    def load_last_open_path(self):
        self.config.read(self.config_path)
        return self.config.get('DEFAULT', 'last_open_path', fallback='D:/')
    def save_last_open_path(self, path):
        self.config['DEFAULT']['last_open_path'] = path
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
    # 导入按钮
    def select_files(self):
        # 一次性打开多个文件
        filenames = filedialog.askopenfilenames(title='Select files', filetypes=[('All Files', '*.*')], initialdir=self.last_open_path)
        if filenames:
            self.last_open_path = os.path.dirname(filenames[0])
            self.save_last_open_path(self.last_open_path)
        file_list = list(root.tk.splitlist(filenames))  # 将元组转换为列表
        # 构建一种匹配机制，将文件名的列表转换成字典，每个关键词只能出现一次
        # 设置识别顺序为 T1CE、Flair、T2、T1、DWI、ADC
        def match_files(file_list):
            keywords = self.load_Multimodals()
            matched_files = {}
            for keyword in keywords:
                for file in file_list:
                    file_name = os.path.basename(file)
                    if keyword.lower() == file_name.lower():
                        matched_files[keyword] = file
                        file_list.remove(file)  # 从file_list中移除已匹配的文件名
                        # 新增：复制文件一份到 result_data 文件夹
                        result_dir = 'result_data'
                        os.makedirs(result_dir, exist_ok=True)  # 确保 result_data 目录存在
                        try:
                            shutil.copy(file, os.path.join(result_dir, file_name))  # 复制文件
                        except:
                            pass
                        break  # 如果找到了，就跳出内部循环
            return matched_files
        import_dict = match_files(file_list)
        print(import_dict)
        # 清空原来的，并展示新的
        self.f.reset(import_dict)
        tkinter.messagebox.showinfo(title='Hi', message=f'成功导入{len(import_dict)}个文件')
def on_close(root, config):
    if root.state() == 'zoomed':  # Check if the window is fullscreen
        config['DEFAULT']['geometry'] = 'zoomed'
    else:
        config['DEFAULT']['geometry'] = root.geometry()
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    root.destroy()
if __name__ == "__main__":
    root = tk.Tk()
    root.config(bg='#2b2b2b')
    # -----------------------------------------
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=filemenu)
    filemenu.add_command(label='Save')
    filemenu.add_command(label='Exit')
    editmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Help', menu=editmenu)
    editmenu.add_command(label='About')
    root.config(menu=menubar)
    # -----------------------------------------
    config = configparser.ConfigParser()
    config.read('config.ini')
    geometry = config.get('DEFAULT', 'geometry', fallback='1280x960+140+20')
    if geometry == 'zoomed':
        root.state('zoomed')  # Use state method to set the window state
    else:
        root.geometry(geometry)
    root.protocol('WM_DELETE_WINDOW', lambda: on_close(root, config))
    MAIN_DIV(root)
    root.mainloop()
