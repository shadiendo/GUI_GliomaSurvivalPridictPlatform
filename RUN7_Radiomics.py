import os
import pandas as pd
import numpy as np
import subprocess
from my_MRI_tool_kit import  DirectoryReader_dict
import SimpleITK as sitk
# 1.数据表准备
# 找到对应文件夹里所有文件
root_path = r"result_data\whiteStriped"
max_depth = 1
directory_reader = DirectoryReader_dict(root_path, max_depth)
directories = directory_reader.get_files_dict()
print(f'共找到{len(directories)}个文件夹')
# 形式应该如下：
# directories = {'G:\\Aim\\JSPH\\X0575009\\20180123-Pre': ['ADCm.nii.gz',
#   'ADCo.nii.gz',
#   'fDWI_2.nii.gz',
#   'T1.nii.gz',
#   'T1CE.nii.gz',
#   'T2.nii.gz',
#   'T2Flair.nii.gz',
#   '________ws_b_regd_rsmp_ADC.nii.gz',
#   '________ws_b_regd_rsmp_fDWI_2.nii.gz',
#   '________ws_b_regd_rsmp_T1.nii.gz',
#   '________ws_b_regd_rsmp_T1CE.nii.gz',
#   '________ws_b_regd_rsmp_T2.nii.gz',
#   '________ws_b_regd_rsmp_T2Flair.nii.gz']}
# Dictionary of patterns
patterns = {
    'path': None,
    'database': None,
    'ID': None,
    'seg': '__________CDK2m_seg.nii.gz',
    'ADCf': '________ws_b_regd_rsmp_ADC.nii.gz',  # 最终的ADC, ADC final
    'fDWI': '________ws_b_regd_rsmp_fDWI_2.nii.gz',
    'T1WI': '________ws_b_regd_rsmp_T1.nii.gz',
    'T1CE': '________ws_b_regd_rsmp_T1CE.nii.gz',
    'T2WI': '________ws_b_regd_rsmp_T2.nii.gz',
    'Flar': '________ws_b_regd_rsmp_T2Flair.nii.gz'
}
column_names = list(patterns.keys())
df_summary = pd.DataFrame(columns=column_names)
# Iterate over the dictionary items
for path, files in directories.items():
    # Initialize a new row with all values set to None
    row = {col: None for col in column_names}
    row['path'] = path
    row['database'] = path.split("\\")[-3]
    row['ID'] = path.split("\\")[-2]
    # Iterate over the files
    for file in files:
        # Only process files that match the patterns
        if file in patterns.values():
            # Get the column name for the file by looking up its value in the pattern dictionary
            col = [k for k, v in patterns.items() if v == file][0]
            row[col] = file
    # Add the row to the DataFrame
    df_summary = pd.concat([df_summary, pd.DataFrame(row, index=[0])], ignore_index=True)
df_summary = df_summary.drop_duplicates()
df_summary.to_csv(r'G:\\序列情况汇总.csv')
# 创建一个新的DataFrame，包含原始的`ID`列
new_df_summary = pd.DataFrame()
# 为每一个seq列生成一个新的路径列
seq_cols = ['seg', 'ADCf','ADCo', 'ADCm', 'fDWI', 'T1WI', 'T1CE', 'T2WI', 'Flar']
for col in seq_cols:
    new_col_name = f'{col}_path'  # 生成新的列名
    new_df_summary[new_col_name] = df_summary.apply(
        lambda row: os.path.join(row['path'], row[col]) if pd.notna(row[col]) else None, axis=1
    )
# 2.做好子区mask的函数准备
"""
检测输入mask文件的信号值的分布，输出如 (0, 1, 2, 4)
"""
def get_unique_signal_values(input_file):
    # 读取nifti文件
    image = sitk.ReadImage(input_file)
    # 将SimpleITK图像转换为NumPy数组
    image_array = sitk.GetArrayFromImage(image)
    # 获取NumPy数组中的唯一值并将其转换为整数元组
    # unique_values = set(image_array.flatten())
    unique_values = tuple(map(int, set(image_array.flatten())))
    return unique_values
"""
读取两个mask文件然后合并成一个
"""
def merge_masks(mask1_file, mask2_file, output_file):
    # 读取两个mask文件
    mask1 = sitk.ReadImage(mask1_file)
    mask2 = sitk.ReadImage(mask2_file)
    # 将两个mask相加
    merged_mask = sitk.Add(mask1, mask2)
    # 将信号值大于0的像素设置为1
    merged_mask = sitk.BinaryThreshold(merged_mask, lowerThreshold=1, upperThreshold=255, insideValue=1, outsideValue=0)
    # 将合并后的mask写入输出文件
    sitk.WriteImage(merged_mask, output_file)
# # 示例用法
# mask1_file = '________CDK1__seg.nii.gz'
# mask2_file = '________CDK4__seg.nii.gz'
# output_file = '________CDK14__seg.nii.gz'
# merge_masks(mask1_file, mask2_file, output_file)
"""
输入一个多值的mask然后分割之
如果是（0，1，2，4），那么输出
    ________CDK1__NCR__seg.nii.gz
    ________CDK2__ED__seg.nii.gz
    ________CDK4__ET__seg.nii.gz
如果是（0，1，2），那么输出存在的1和2，把4用全0值补齐，最后也是
    ________CDK1__NCR__seg.nii.gz
    ________CDK2__ED__seg.nii.gz
    ________CDK4__ET__seg.nii.gz
其他同理
"""
def split_masks(input_file, unique_signal_values):
    # 输入路径
    folder = os.path.dirname(input_file)
    # 读取nifti文件
    image = sitk.ReadImage(input_file)
    # 预定义的信号值列表
    predefined_signal_values = (0, 1, 2, 4)
    # 根据信号值分割mask并保存
    for value in predefined_signal_values:
        if value == 0:
            continue  # 忽略背景值（信号值为0的部分）
        if value in unique_signal_values:
            mask = sitk.BinaryThreshold(image, lowerThreshold=value, upperThreshold=value, insideValue=1,
                                        outsideValue=0)
        else:
            # 对于缺失的信号值，创建一个全零的mask
            mask_shape = sitk.GetArrayFromImage(image).shape
            mask_array = np.zeros(mask_shape, dtype=np.uint8)
            mask = sitk.GetImageFromArray(mask_array)
        # 复制输入图像的元数据到输出mask
        mask.CopyInformation(image)
        if value == 1:
            output_file = f"____________CDK_001NCR_seg.nii.gz"
        elif value == 2:
            output_file = f"____________CDK_0002ED_seg.nii.gz"
        elif value == 4:
            output_file = f"____________CDK_0004ET_seg.nii.gz"
        else:
            print('有问题？')
        print(os.path.join(folder, output_file))
        sitk.WriteImage(mask, os.path.join(folder, output_file))
# input_file = r'E:\Rigistration\________CDK_seg.nii.gz'
# unique_signal_values = get_unique_signal_values(input_file)
# print('#'*40,'\n',input_file,'\n',unique_signal_values)
# split_masks(input_file, unique_signal_values)
"""
输入一个多值的mask的文件位置，然后根据两种模式，若为 add_mode 则输出5个文件，若为 del_mode 则删除这五个文件
____________CDK__0001NCR__seg.nii.gz
____________CDK__0002ED__seg.nii.gz
____________CDK__0004ET__seg.nii.gz
____________CDK__0014TC__seg.nii.gz
____________CDK__0124WT__seg.nii.gz
"""
def one2five(input_seg, mode):
    folder = os.path.dirname(input_seg)
    if mode == 'add_mode':
        # 显示信号分布
        unique_signal_values = get_unique_signal_values(input_seg)
        print(unique_signal_values)
        # 先分割出三个文件
        split_masks(input_seg, unique_signal_values)
        print('分割成功！')
        # 融合出另外两个
        merge_masks(
            os.path.join(folder, '____________CDK_001NCR_seg.nii.gz'),  # mask1_file
            os.path.join(folder, '____________CDK_0004ET_seg.nii.gz'),  # mask2_file
            os.path.join(folder, '____________CDK_0014TC_seg.nii.gz')  # output_file
        )
        merge_masks(
            os.path.join(folder, '____________CDK_0002ED_seg.nii.gz'),  # mask1_file
            os.path.join(folder, '____________CDK_0014TC_seg.nii.gz'),  # mask2_file
            os.path.join(folder, '____________CDK_0124WT_seg.nii.gz')  # output_file
        )
        print('TC和WT融合成功！')
    elif mode == 'del_mode':
        fileToBeDelete = [
            '____________CDK_001NCR_seg.nii.gz',
            '____________CDK_0002ED_seg.nii.gz',
            '____________CDK_0004ET_seg.nii.gz',
            '____________CDK_0014TC_seg.nii.gz',
            '____________CDK_0124WT_seg.nii.gz'
        ]
        for i in fileToBeDelete:
            file = os.path.join(folder, i)
            if not os.path.exists(file):
                print(file)
            else:
                os.remove(file)
    else:
        print('模式选择错误')
# file = 'G:\\Aim\\JSPH\\X0800419\\20141030-Pre\\__________CDK1m_seg.nii.gz'
# one2five(file,'add_mode')   # add_mode   del_mode
# 2.1 批量处理生成五个子区
# 将新列转换为列表
path_seq_list = new_df_summary['seg_path'].tolist()
print(len(path_seq_list))
for i in path_seq_list:
    print(f"{'#'*50}")
    print(i)
    one2five(i,'add_mode')   # add_mode   del_mode
# 3.对特征提取的函数准备
import os
import pandas as pd
import SimpleITK as sitk
from radiomics import featureextractor
"""
提取一行 1 rows × 1911 columns 的影像组学数据
"""
def radiomics_feature_extraction(main_file, seg_file):
    # -------------------------------------------------------------
    # 提取特征前定义提取器
    settings = {}
    settings['binWidth'] = 25  # 25
    settings['sigma'] = [3, 5]
    # 标准化
    settings['normalize'] = True
    settings['normalizeScale'] = 100
    # 重采样
    settings['resampledPixelSpacing'] = [1, 1, 1]
    settings['interpolator'] = sitk.sitkBSpline
    extractor = featureextractor.RadiomicsFeatureExtractor()
    extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
    extractor.enableAllImageTypes()
    extractor.enableAllFeatures()
    # parameter force2D must be set to True to enable shape2D extraction
    # settings['force2D'] = True
    # ## 其他滤波
    # extractor.enableImageTypeByName('LoG')
    # extractor.enableImageTypeByName('Wavelet')
    # # # 文献里的手动加入的影像组学因子
    # extractor.enableFeaturesByName(firstorder=['Energy', 'TotalEnergy', 'Entropy', 'Minimum', '10Percentile', '90Percentile', 'Maximum', 'Mean', 'Median', 'InterquartileRange', 'Range', 'MeanAbsoluteDeviation', 'RobustMeanAbsoluteDeviation', 'RootMeanSquared', 'Skewness', 'Kurtosis', 'Variance', 'Uniformity'])
    # extractor.enableFeaturesByName(shape=['VoxelVolume', 'MeshVolume', 'SurfaceArea', 'SurfaceVolumeRatio', 'Sphericity','Maximum3DDiameter','Maximum2DDiameterSlice','Maximum2DDiameterColumn','Maximum2DDiameterRow', 'MajorAxisLength', 'MinorAxisLength', 'LeastAxisLength', 'Elongation', 'Flatness'])
    df = pd.DataFrame()
    try:
        featureVector = extractor.execute(main_file, seg_file)
        df_add = pd.DataFrame.from_dict(featureVector.values()).T
        df_add.columns = featureVector.keys()
        df = pd.concat([df, df_add]).T
    except:
        print('无法提取特征，可能是因为掩膜文件为空')
        df = 'error'
    return df
# 测试个
main_file = r'G:\Aim\JSPH\X0767803\20140208-Pre\________ws_b_regd_rsmp_fDWI_2.nii.gz'
seg_file = r'G:\Aim\JSPH\X0767803\20140208-Pre\____________CDK_0124WT_seg.nii.gz'  # 0014TC    0124WT
cc = radiomics_feature_extraction(main_file,seg_file)
"""
# 在某个序列上提取   0014TC 和  0124WT  的特征
subject_name: X0012345
sequence_name: ADCo
input_file：'G:\\Aim\\JSPH\\X0800419\\20141030-Pre\\________ws_b_regd_rsmp_T1CE.nii.gz'   这种
"""
def main_extract(subject_name, sequence_name, input_file):
    folder = os.path.dirname(input_file)
    # 001NCR 0002ED 0004ET 0014TC 0124WT
    # 注意这里要先提取 0124WT 的特征
    seg_dict = {
        sequence_name + '_0124WT__': os.path.join(folder, '____________CDK_0124WT_seg.nii.gz'),
        sequence_name + '_0014TC__': os.path.join(folder, '____________CDK_0014TC_seg.nii.gz'),
    }
    # 创建一个空列表来存储所有的结果数据框
    all_features = []
    empty_df = pd.DataFrame()
    for key, value in seg_dict.items():
        prefix = key
        features = radiomics_feature_extraction(input_file, value)
        # ######################################################
        # 这里判断一步，如果 features 正儿八经是个数据框，那么没问题，只要是先提取的 0124WT 都不怕
        if type(features) != str:
            print(f'在 {key} 上能提取到特征')
            # --------------------------------
            # 取后1874个特征，其开头应该是 original_shape_Elongation，结尾为 wavelet-LLL_ngtdm_Strength
            features_1874 = features.iloc[37:, :]
            empty_df = features_1874.copy()  # 深度拷贝一份
        # 如果 features 是空，即比如提取 0014TC 的时候它是个空掩膜，那么把 all_features[0] 复制一份，修改列名，然后把第二列内容删掉
        else:
            print(f'在 {key} 上无法提取特征')
            features_1874 = empty_df
        # ######################################################
        # 将行名转换为列
        features_1874.reset_index(inplace=True)
        # 为这个新列添加前缀
        features_1874.loc[:, 'index'] = prefix + features_1874['index']
        # 再将这个新列设为行名
        features_1874.set_index('index', inplace=True)
        # 记得修改列名
        features_1874 = features_1874.rename(columns={0: subject_name})
        # ######################################################
        if type(features) == str:
            # 记得删除内容
            features_1874.loc[:, subject_name] = None
        # ######################################################
        all_features.append(features_1874)
    # 使用 pd.concat 将所有的结果数据框堆叠起来
    all_features_df = pd.concat(all_features)
    return all_features_df
# 测试一个
input_file = r'G:\Aim\JSPH\X0575009\20180123-Pre\________ws_b_regd_rsmp_ADC.nii.gz'
rerr = main_extract('X124455', 'ADCf',input_file)
# 4.正式提取特征
def final_extract(sequence_name, input_file_list, output_file):
    all_features_list = []
    error = []
    for input_file in tqdm(input_file_list):
        print(f"{'#' * 50}")
        print(input_file)
        subject = input_file.split('\\')[-3]
        try:
            features_df = main_extract(subject, sequence_name, input_file)
            all_features_list.append(features_df)
        except:
            error.append(input_file)
    # 将列汇总
    all_features = pd.concat(all_features_list, axis=1)
    # 保存
    all_features.to_csv(output_file)
    return error
# 将新列转换为列表
T1WI_path_list = new_df_summary['T1WI_path'].tolist()
T1WI_path_list = [x for x in T1WI_path_list if x is not None]  # 去除空值
print(len(T1WI_path_list))
