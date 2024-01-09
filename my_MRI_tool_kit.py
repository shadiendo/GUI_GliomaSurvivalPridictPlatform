# 工具函数
import SimpleITK as sitk
import numpy as np
import os
from collections import defaultdict
# ████████████████████████████
# 超强目录工具
# ████████████████████████████
'''
root_path：根目录
max_depth：最大深度
get_files：返回文件列表
'''
class DirectoryReader_dict:
    def __init__(self, root_path, max_depth):
        self.root_path = root_path
        self.max_depth = max_depth
        self.folder_path = []
        self.file_path = []
        self.file_dict = defaultdict(list)
    def _traverse_directory(self, path, depth):
        if depth > self.max_depth:
            return
        try:
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    self.folder_path.append(entry_path)
                    self._traverse_directory(entry_path, depth + 1)
                elif os.path.isfile(entry_path):
                    self.file_dict[path].append(entry)
                    self.file_path.append(entry_path)
        except FileNotFoundError as e:
            print(f"Error: {e}")
    
    # 返回指定深度的所有文件夹，包括之前的
    def get_directories(self):
        self._traverse_directory(self.root_path, 1)
        return self.folder_path
    # 返回指定深度的文件夹
    def get_aim_directories(self):
        self._traverse_directory(self.root_path, 1)
        cleared_path = []
        for i in self.folder_path:
            split_list = i.replace(self.root_path,'').split('\\')
            split_list_noneSpace = list(filter(None,split_list))
            if len(split_list_noneSpace) == self.max_depth:
                cleared_path.append(i)
        return cleared_path
    # 返回列表形式的所有指定深度的文件夹
    def get_files_list(self):
        self._traverse_directory(self.root_path, 1)
        return self.file_path    
    # 返回字典形式的所有指定深度的文件夹
    def get_files_dict(self):
        self._traverse_directory(self.root_path, 1)
        return dict(self.file_dict)
# root_path = r"J:\20230602\nifti_needed\REMBRANDT"
# max_depth = 2
# directory_reader = DirectoryReader_dict(root_path, max_depth)
# file_dict = directory_reader.get_aim_directories()
# file_dict
# ████████████████████████████
# 超强目录工具
# ████████████████████████████
def convert_nifti_datatype(input_file, output_file, target_dtype):
    # 读取输入 NIfTI 文件
    input_image = sitk.ReadImage(input_file)
    # 获取 NumPy 数组
    input_array = sitk.GetArrayFromImage(input_image)
    # 转换 NumPy 数组的数据类型
    converted_array = input_array.astype(target_dtype)
    # 将转换后的 NumPy 数组转回 SimpleITK 图像
    converted_image = sitk.GetImageFromArray(converted_array)
    converted_image.CopyInformation(input_image)
    # 保存转换后的图像为新的 NIfTI 文件
    sitk.WriteImage(converted_image, output_file)
# # 使用示例
# input_file = r'F:\preOperationMRI_registered\s2\JSPH\X0899144\20161217-Pre\BRAIN_seg.nii.gz'
# output_file = r'F:\preOperationMRI_registered\s2\JSPH\X0899144\20161217-Pre\BRAIN_seg.nii.gz'
# target_dtype = np.float64   # 转换文件类型为8-bit unsigned
# target_dtype = np.int8   # 转换文件类型为8-bit unsigned
# target_dtype = np.uint8   # 转换文件类型为8-bit unsigned
# convert_nifti_datatype(input_file, output_file, target_dtype)
# ████████████████████████████
# N4偏置场矫正 - 阈值法
# ████████████████████████████
def N4BiasFieldCorrection(imagePath, output_path, saveMaskOrNot):
    # 读nifty
    input_image = sitk.ReadImage(imagePath)
    # 设置蒙版，只对蒙版内的部分操作
    mask_image = sitk.OtsuThreshold(input_image,0,1,200)    
    input_image = sitk.Cast(input_image, sitk.sitkFloat32)
    # 主运行
    corrector = sitk.N4BiasFieldCorrectionImageFilter() # N4偏置场
    output_image = corrector.Execute(input_image,mask_image)
    output_image = sitk.Cast(output_image, sitk.sitkInt16)
    if saveMaskOrNot:
        sitk.WriteImage(mask_image, output_mask_path)
    sitk.WriteImage(output_image, output_path)
        
    print(f'【N4 processed successfully】{imagePath}')
