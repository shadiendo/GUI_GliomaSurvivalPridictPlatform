# -*- coding: utf-8 -*-
import SimpleITK as sitk
import numpy as np
import os
class SkullStripe:
    # def __init__(self):
    #     # 完整路径
    #     self.T1 = '______regd_rsmp_T1.nii.gz'
    #     self.T1CE = '______regd_rsmp_T1CE.nii.gz'
    #     self.T2 = '______regd_rsmp_T2.nii.gz'
    #     self.T2Flair = '______regd_rsmp_T2Flair.nii.gz'
    #     self.fDWI_2 = '______regd_rsmp_fDWI_2.nii.gz'
    #     self.ADC = '______regd_rsmp_ADC.nii.gz'
    #     self.ADC_manual = '______regd_rsmp_ADC_manual.nii.gz'
    # 转换文件类型 比如从8-bit unsigned integer转为64-bit float
    def convert_nifti_datatype(self, input_file, output_file, target_dtype):
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
    # target_dtype = np.float64
    # convert_nifti_datatype(input_file, output_file, target_dtype)
    def apply_mask_to_nifti(self, nifti_file, mask_file, output_file):
        self.convert_nifti_datatype(mask_file, mask_file, np.float64)
        # 读取NIfTI文件和掩膜文件
        nifti_image = sitk.ReadImage(nifti_file)
        mask_image = sitk.ReadImage(mask_file)
        #     print("NIfTI image size: ", nifti_image.GetSize())
        #     print("NIfTI image spacing: ", nifti_image.GetSpacing())
        #     print("NIfTI image origin: ", nifti_image.GetOrigin())
        #     print("NIfTI image direction: ", nifti_image.GetDirection())
        #     print("NIfTI image pixel type: ", nifti_image.GetPixelIDTypeAsString())
        #     print("Mask image size: ", mask_image.GetSize())
        #     print("Mask image spacing: ", mask_image.GetSpacing())
        #     print("Mask image origin: ", mask_image.GetOrigin())
        #     print("Mask image direction: ", mask_image.GetDirection())
        #     print("Mask image pixel type: ", mask_image.GetPixelIDTypeAsString())
        # 确保掩膜是二值的
        mask_image = sitk.BinaryThreshold(mask_image, lowerThreshold=0.5, upperThreshold=1, insideValue=1, outsideValue=0)
        # 将掩膜应用到NIfTI文件上
        masked_image = sitk.Mask(nifti_image, mask_image)
        # 保存结果为新的NIfTI文件
        sitk.WriteImage(masked_image, output_file)
    # # 使用示例
    # nifti_file = r'F:\preOperationMRI_registered\s2\JSPH\X0899144\20161217-Pre\flair.nii.gz'
    # mask_file = r'F:\preOperationMRI_registered\s2\JSPH\X0899144\20161217-Pre\BRAIN_seg.nii.gz'
    # output_file = r'F:\preOperationMRI_registered\s2\JSPH\X0899144\20161217-Pre\BRAIN.nii.gz'
    # apply_mask_to_nifti(nifti_file, mask_file, output_file)
    def one_click(self, filePaths):
        # 输入的 filePaths 为一个存储了文件位置的列表
        for nifti_file in filePaths:
            basePath = os.path.dirname(nifti_file)  # 文件路径
            fileName = os.path.basename(nifti_file)   # 文件名
            mask_file = r'tools\____brain_mask.nii.gz'
            output_file = os.path.join(basePath, '________b_' + fileName[6:])
            if os.path.exists(nifti_file):
                self.apply_mask_to_nifti(nifti_file, mask_file, output_file)
# mri_reg = SkullStripe()
# mri_reg.one_click([r'D:\pythonProject\Full_pypline\result_data\__rsmp___rsmp_T1CE.nii.gz'])
