import subprocess
class RunAutoSeg:
    def __init__(self, python_path='D:\\Full_Radiomics_Pipline\\venv\\Scripts\\python.exe'):
        self.python_path = python_path
    def run_script(self, script_path="main.py", dataset_folder="dataset", folder_depth=2):
        # 通过subprocess 执行Python脚本命令
        cmd = [
            self.python_path,
            script_path,
            "--dataset-folder", dataset_folder,
            "--folder-depth", str(folder_depth)
        ]
        # 实际的运行命令为：
        # D:\Full_Radiomics_Pipline\venv\Scripts\python.exe  main.py --dataset-folder "dataset" --folder-depth 2
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
mri_reg = RunAutoSeg()
mri_reg.run_script()
