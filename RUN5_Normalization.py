# -*- coding: utf-8 -*-
import os
import configparser
import rpy2.robjects as robjects
import subprocess
class RunWhiteStripe:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.r_home = None
    def load_r_environment(self):
        # 读取配置文件中的R环境
        self.config.read(self.config_file)
        self.r_home = self.config.get('DEFAULT', 'r_home', fallback='none')
        # 如果 r_home 值为none，那么通过rpy2包来获取一下R的安装路径
        if self.r_home == 'none':
            self.r_home = robjects.r('''R.home()''')[0]
            # 更新 DEFAULT section
            self.config['DEFAULT']['r_home'] = self.r_home
            # 写回配置文件
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
        # 设置运行环境并测试
        os.environ['R_HOME'] = self.r_home
        robjects.r('''
        aaa <- 1+1
        cat('1+1=2')''')
        print()
    def run_r_script(self, script_path=".\\RUN5_Normalization.R"):
        # 通过subprocess 执行R语言命令
        cmd = [
            os.path.normpath(
                os.path.join(self.r_home, 'bin', 'x64', 'Rscript.exe')),
            script_path]
        # 实际的运行命令为【& "C:\Program Files\R\R-4.2.3\bin\x64\Rscript.exe" .\RUN5_Normalization.R】
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
mri_reg = RunWhiteStripe()
mri_reg.load_r_environment()
mri_reg.run_r_script()
"""
# ===================================
# WhiteStripe代码留档，文件名为 RUN5_Normalization.R
# ===================================
rm(list=ls())
library(this.path);setwd(this.path::this.dir());cat('running path: ',getwd());
library(RNifti)
library(oro.nifti)
library(WhiteStripe)
library(neuroim2)
save_folder = "result_data/whiteStriped"
if (!dir.exists(save_folder)) {
  dir.create(save_folder)
}
df <- read.table('temp.txt',quote = "",sep = "")
for (line in 1:nrow(df)){
  file_name <- paste0(df[line,1])
  # Create the save_name with the "whiteStriped" directory
  save_name <- file.path(save_folder, basename(file_name))
  cat(file_name,'\n')
  cat(save_name,'\n')
  img = oro.nifti::readNIfTI(file_name, reorient = FALSE);
  img <- read_vol(file_name)
  # processe
  ws = whitestripe(img = img, type = "MD", stripped = TRUE)
  norm = whitestripe_norm(img = img, indices = ws$whitestripe.ind)
  # save
  write_vol(norm, save_name)
  cat('whiteStripe succeed!\n')
  rm(file_name,save_name,img,ws,norm)
}
"""
