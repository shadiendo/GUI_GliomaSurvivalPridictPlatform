# -*- coding: utf-8 -*-
import subprocess
import time
import os
import configparser
class MRIRegistration:
    def __init__(self):
        self.MNI152 = r'tools\icbm_avg_152_t1_tal_nlin_symmetric_VI.nii.gz'
        self.antsRegistration = os.path.join(r'tools\ANTs', 'antsRegistration.exe')
        self.antsApplyTransforms = os.path.join(r'tools\ANTs', 'antsApplyTransforms.exe')
    def run_command(self, command, message=''):
        start_time = time.time()
        if message != '':
            print(message)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        end_time = time.time()
        duration = end_time - start_time
        # 检查命令的返回值
        if result.returncode == 0:
            print(f'命令执行完毕,耗时{duration:.2f}秒')
        else:
            print(f"命令执行失败,耗时{duration:.2f}秒")
    def find_which_first(self, all_files):
        # 设置导入的文件名，即文件名必须遵循设置文件中规定的规则
        config_path = 'config.ini'
        config = configparser.ConfigParser()
        def load_Multimodals():
            config.read(config_path)
            keywords = [
                config.get('ANTs_find_which_first', 't1ce'),
                config.get('ANTs_find_which_first', 't1'),
                config.get('ANTs_find_which_first', 't2'),
                config.get('ANTs_find_which_first', 't2flair'),
                config.get('ANTs_find_which_first', 'dwi'),
                config.get('ANTs_find_which_first', 'adc'),
            ]
            return keywords
        keywords = load_Multimodals()
        # 按顺序找到最好的序列
        def select_target_file(files_list):
            # priority = ['T1CE.nii.gz', 'T1.nii.gz', 'T2.nii.gz', 'T2Flair.nii.gz', 'fDWI_2.nii.gz', 'ADC.nii.gz',
            #             'ADC_manual.nii.gz']
            priority = keywords
            print(f'在ANTs选择优先配准序列时的顺序为 {priority}')
            for file in priority:
                if file in files_list:
                    return file
            return None
        target_file = ''
        target_file = select_target_file(all_files)
        remaining_files = []
        remaining_files = [file for file in all_files if file != target_file]
        print("先配准:", target_file)
        print("后配准:", remaining_files)
        # target_file是一个文件，里面必然有东西且只有一个；remaining_files是文件的列表，可以为空列表
        return [target_file, remaining_files]
    def find_which_best_patch(self, all_files, priority):
        # 按顺序找到最好的序列
        def select_target_file(files_list):
            # priority = ['T1CE.nii.gz', 'T1.nii.gz', 'T2.nii.gz', 'T2Flair.nii.gz', 'fDWI_2.nii.gz', 'ADC.nii.gz', 'ADC_manual.nii.gz']
            for file in priority:
                if file in files_list:
                    return file
            return None
        target_file = ''
        target_file = select_target_file(all_files)
        remaining_files = []
        remaining_files = [file for file in all_files if file != target_file]
        # target_file是一个文件，里面必然有东西且只有一个；remaining_files是文件的列表，可以为空列表
        return [target_file, remaining_files]
    def rigid_regisitration(self, template_file, input_file, output_file):
        # 相对路径
        work_dir = os.path.dirname(input_file)
        # 放射变换文件的前缀
        mat_prefix = os.path.join(work_dir, 'rigidTemp_')
        mat_name = mat_prefix + '0GenericAffine.mat'
        # 一阶段
        command_Rigid = ' '.join([
            self.antsRegistration, '-d 3',
            '-m', f'MI[{template_file},{input_file},1,32,Regular,0.25]', '-w [0.005, 0.995]', '--float', '-v',
            '-t', 'Rigid[0.1]',
            '-o', mat_prefix,
            '-c [1000x500x250x100x0,1e-6,10]', '-s 4x3x2x1x1vox', '-f 12x8x4x2x1',
        ])
        command_trans = ' '.join([
            self.antsApplyTransforms, '-d 3', '-n', 'Linear', '-v',
            '-i', input_file,
            '-r', template_file,
            '-t', mat_name,
            '-o', output_file,
        ])
        self.run_command(command_Rigid, f'Rigid: {input_file}→{template_file}\n→{output_file}')
        self.run_command(command_trans, '')
        # 删除临时的变换文件
        os.remove(mat_name)
    def one_click(self, folder):
        # 先分出先后批次
        aaaa = self.find_which_first(os.listdir(folder))
        forerunner = aaaa[0]
        latecomer = aaaa[1]
        # 完整路径
        forerunner_full_path = os.path.join(folder, forerunner)
        latecomer_full_path = []
        for i in latecomer:
            latecomer_full_path.append(os.path.join(folder, i))
        # ————————————————————————————————
        # 先将 forerunner 重采样以及刚体配准到MNI152上
        rsmp_forerunner = os.path.join(os.path.dirname(forerunner_full_path),
                                       '__rsmp_' + os.path.basename(forerunner_full_path))
        self.rigid_regisitration(self.MNI152, forerunner_full_path, rsmp_forerunner)  # template_file, input_file, output_file
        # ————————————————————————————————
        # 把其他所有序列都重采样到 rsmp_forerunner 上(互相配准，刚体)
        if len(latecomer_full_path) > 0:
            for input_file in latecomer_full_path:
                output_file = os.path.join(os.path.dirname(input_file),
                                           '__rsmp_' + os.path.basename(input_file))
                self.rigid_regisitration(rsmp_forerunner, input_file, output_file)  # template_file, input_file, output_file
# mri_reg = MRIRegistration()
# mri_reg.one_click('demo_data')
