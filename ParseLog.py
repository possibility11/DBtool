# -*- coding: utf-8 -*-
# ===========================================================================
# File:    ParseLog.py
# Author:  mark
# Time:    2025/8/15 21:23
# Email:   maky_cq@163.com
# Version： V2.0
# Description: xxx
# History:
# <author>    <version>      <time>         <desc>
#  mark          V1.0        2025/8/26   新增日志拉取功能函数
#  mark          V2.0        2025/8/27   新增DB日志解析，解析文件结构化函数
# ===========================================================================

import sys
import os, subprocess, pathlib, shlex
import time
import re
from datetime import datetime
import zipfile
import shutil
from pathlib import Path

def rename_db_folders_with_timestamp(base_path):
    """
    重命名以"db."开头的文件夹，添加时间戳后缀
    
    Args:
        base_path: 要搜索的基路径
    """
    # 生成当前时间戳，格式为YYYYMMDD_HHMMSS
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # 遍历基路径下的所有项
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        # 只处理文件夹且以"db."开头
        if os.path.isdir(item_path) and item.startswith("db.") and len(item) < 20:
            # 构建新名称
            new_name = f"{item}_{timestamp}"
            new_path = os.path.join(base_path, new_name)
            try:
                # 重命名文件夹
                os.rename(item_path, new_path)
                print(f"已重命名文件夹: {item} -> {new_name}")
            except Exception as e:
                print(f"重命名文件夹 {item} 失败: {str(e)}")


def pull_DBlog1(local_base_path, remote_base_path):
    try:
        # 获取当前设备id
        output = subprocess.check_output('adb devices').decode().splitlines()
        if len(output) < 2:
            print("未找到连接的Android设备")
            return False
        device_id = output[1].split('\t')[0]
        if not device_id:
            print("未找到连接的Android设备")
            return False

        # 确保本地目录存在
        if not os.path.exists(local_base_path):
            os.makedirs(local_base_path)
        # ADB root和remount
        subprocess.run('adb root', check=True, shell=True)
        time.sleep(1)
        subprocess.run('adb remount', check=True, shell=True)
        time.sleep(1)
        # 获取远程目录下所有db.开头的文件夹
        find_folder_cmd = f'adb -s {device_id} shell find {remote_base_path} -name "db.*" -type d'
        output = subprocess.check_output(find_folder_cmd, shell=True).decode().splitlines()
        remote_folders = {}
        for folder_path in output:
            folder_path = folder_path.strip()
            if not folder_path:
                continue
        # 获取文件夹的修改时间
        time_cmd = f'adb -s {device_id} shell stat -c %Y {folder_path}'
        try:
            modify_time = subprocess.check_output(time_cmd, shell=True).decode().strip()
            folder_name = os.path.basename(folder_path)
            remote_folders[folder_name] = {
                'path': folder_path,
                'modify_time': int(modify_time)
            }
        except:
            print(f"获取文件夹修改时间失败: {folder_path}")
            continue
        # 遍历远程文件夹，只拉取新增或修改过的文件夹
        for folder_name, folder_info in remote_folders.items():
            remote_modify_time = folder_info['modify_time']
            remote_path = folder_info['path']
            # 检查是否已经拉取过
            if folder_name in local_folders:
                local_modify_time = local_folders[folder_name]
                # 如果远程文件夹修改时间早于或等于本地记录的时间，跳过
                if remote_modify_time <= local_modify_time:
                    print(f"跳过已拉取的文件夹: {folder_name}")
                    continue



def pull_DBlog(local_base_path, remote_base_path):
    """
    通过ADB从Android设备拉取日志，只拉取新增或修改过的文件。
    拉取完成后，对本地以"db."开头的文件夹加上时间戳后缀进行重命名。
    """
    try:
        # 获取当前设备id
        output = subprocess.check_output('adb devices').decode().splitlines()
        if len(output) < 2:
            print("未找到连接的Android设备")
            return False
        device_id = output[1].split('\t')[0]
        if not device_id:
            print("未找到连接的Android设备")
            return False
        # cur_path = os.getcwd()
        # local_base_path = os.path.join(cur_path, 'DBfile/android')
        # remote_base_path = '/log/android/aee_exp'
        
        # 确保本地目录存在
        if not os.path.exists(local_base_path):
            os.makedirs(local_base_path)
        #os.makedirs(local_base_path, exist_ok=True) # 创建目录
        
        # ADB root和remount
        subprocess.run('adb root', check=True, shell=True)
        time.sleep(1)
        subprocess.run('adb remount', check=True, shell=True)
        time.sleep(1)
        # 获取远程目录下所有文件列表
        remote_files = {}
        # 使用adb shell find命令递归获取文件信息
        find_cmd = f'adb -s {device_id} shell find {remote_base_path} -type f -exec ls -l {{}} \\;'
        output = subprocess.check_output(find_cmd, shell=True).decode().splitlines()

        for line in output:
            parts = line.split()
            if len(parts) < 6:
                continue
            # 文件大小和路径
            size = parts[4] # 提取文件大小（第5个字段）
            #print(size)
            # remote_file_path = ' '.join(parts[5:])
            remote_file_path = ' '.join(parts[7:]) # 提取文件完整路径
            relative_path = os.path.relpath(remote_file_path, remote_base_path) # 计算相对于基路径的相对路径
            remote_files[relative_path] = size #将相对路径和文件大小存入字典
            #print(remote_files)

        # 遍历远程文件列表，检查本地是否存在对应文件,如果本地不存在或文件大小不同，则创建本地目录并拉取文件
        for relative_path, remote_size in remote_files.items():
            local_file_path = os.path.join(local_base_path, relative_path)
            remote_file_path = os.path.join(remote_base_path, relative_path)
            # 如果本地不存在该文件，或者文件大小不同，则拉取
            if not os.path.exists(local_file_path) or os.path.getsize(local_file_path) != int(remote_size):
                # 确保本地目录存在
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                # 拉取单个文件
                pull_cmd = f'adb -s {device_id} pull {remote_file_path} {local_file_path}'
                subprocess.run(pull_cmd, check=True, shell=True)
                print(f"拉取文件: {relative_path}")
        print("Android日志拉取完成!")
        # 重命名以"db."开头的文件夹，添加时间戳后缀
        rename_db_folders_with_timestamp(local_base_path)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Android日志拉取失败: {e}")
        return False
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        return False
def pull_logacat():
    cur_path = os.getcwd()  # 当前目录
    # 获取设备上的日志文件列表（包括完整路径）
    try:
        result = subprocess.run(
            ['adb', 'shell', f'cd /log && find . -type f'],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"执行ADB命令时出错: {e}")
        return
    files = result.stdout.strip().split('\n')
    # 遍历所有文件
    for file_rel_path in files:
        if not file_rel_path.strip():  # 跳过空行
            continue
        device_file = os.path.join("/log", file_rel_path.lstrip('./'))
        local_file = os.path.join(cur_path, 'DBfile/logcat', file_rel_path)
        # 创建本地目录（如果不存在）
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        # 检查设备上文件是否存在
        check_result = subprocess.run(
            ['adb', 'shell', f'test -f "{device_file}" && echo exists'],
            capture_output=True,
            text=True
        )
        if check_result.stdout.strip() != 'exists':
            print(f"文件不存在，跳过: {device_file}")
            continue
        # 执行adb pull
        print(f"正在导出: {device_file} -> {local_file}")
        pull_result = subprocess.run(
            ['adb', 'pull', device_file, local_file],
            capture_output=True,
            text=True
        )
        if pull_result.returncode != 0:
            print(f"导出失败: {device_file} - {pull_result.stderr}")
        else:
            print(f"导出成功: {device_file}")

def parse_DB():
    GAT_BIN = pathlib.Path('gat-win32-x86_64-4/modules/spsst/tools/aee_db_extract/aee_extract.exe').resolve() # GAT二进制文件
    print(GAT_BIN)
    cur_path = os.getcwd()  # 当前目录
    base_path = os.path.join(cur_path, 'DBfile') # DB文件存放目录
    base_path_obj = pathlib.Path(base_path) # 创建目录对象
    for dbg in base_path_obj.rglob('*.dbg'): # 遍历当前目录下的所有.dbg文件
        dec = dbg.with_suffix('.dbg.DEC') # .dbg.DEC文件
        if dec.exists(): # 如果.dbg.DEC文件已存在，则跳过
            continue
        cmd = [str(GAT_BIN), str(dbg)]
        print('>>>', shlex.join(cmd))
        subprocess.run(cmd)

def parse_exp_main(file_path):
    results = {
        "Exception Log Time": None,
        "Exception Class": None,
        "Exception Type": None,
        "Current Executing Process": None,
        "PID": None,
        "Subject": None,
        "System": None
    } 
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 检查路径中是否包含"android"
        if "android" in file_path:
            results["System"] = "Android"
        elif "tbox" in file_path:
            results["System"] = "TBox"
        elif "cluster" in file_path:
            results["System"] = "Cluster"
        # 提取Exception Log Time
        log_time_match = re.search(r"Exception Log Time:\[(.*?)\]", content)
        if log_time_match:
            log_time = datetime.strptime(log_time_match.group(1).strip(),'%a %b %d %H:%M:%S CST %Y')
            formatted_time = log_time.strftime("%Y-%m-%d %H:%M:%S")
            #results["Exception Log Time"] = log_time_match.group(1).strip()
            results["Exception Log Time"] = formatted_time
        # 提取Exception Class
        class_match = re.search(r"Exception Class:\s*(.*)", content)
        if class_match:
            results["Exception Class"] = class_match.group(1).strip()
        # 提取Exception Type
        type_match = re.search(r"Exception Type:\s*(.*)", content)
        if type_match:
            results["Exception Type"] = type_match.group(1).strip()
        # 提取Current Executing Process
        process_match = re.search(r"Current Executing Process:\s*\n\s*pid:.*\n\s*(.*)", content)
        if process_match:
            results["Current Executing Process"] = process_match.group(1).strip()
        # 如果Exception Class是Native，则提取第二行
        if results["Exception Class"] and "Native" in results["Exception Class"]:
            process_match = re.search(r"Current Executing Process:\s*\n\s*pid:[^\n]+\n\s*(.*)", content)
            if process_match:
                results["Current Executing Process"] = process_match.group(1).strip()
            pid_match = re.search(r"pid:\s*(\w+)", content)
            if pid_match:
                results["PID"] = pid_match.group(1).strip()
        else:
            process_match = re.search(r"Current Executing Process:\s*(.*)", content)
            if process_match:
                results["Current Executing Process"] = process_match.group(1).strip()
            PID_match = re.search(r"PID:\s*(\w+)", content)
            if PID_match:
                results["PID"] = PID_match.group(1).strip()
            subject_match = re.search(r"Subject:\s*(.*)", content)
            if subject_match:
                results["Subject"] = subject_match.group(1).strip()
    return results

    

if __name__ == '__main__':
    # path = r'D:\390tools\390DBTool\DBfile'
    #path = r'/log/android/aee_exp'
    #path = r'D:\390tools\390DBTool\DBfile\android\db.00.NE\db.00.NE.dbg.DEC\__exp_main.txt'
    #result1 = parse_exp_main(path)
    #DB = DBLogPpase(path)
    # local_base_path= r'D:\390tools\390DBTool\g'
    # remote_base_path = '/data/local/tmp'
    # pull_DBlog(local_base_path, remote_base_path)
    base_path = r"C:\Users\94713\Desktop\390_0630\aee_exp"
    rename_db_folders_with_timestamp(base_path)


