import os
import zipfile
import shutil
from pathlib import Path
def pull_DBlog(local_base_path,remote_base_path):
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
        os.makedirs(local_base_path, exist_ok=True)
        
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
            size = parts[4]
            remote_file_path = ' '.join(parts[5:])
            relative_path = os.path.relpath(remote_file_path, remote_base_path)
            remote_files[relative_path] = size
        
        # 遍历远程文件列表，检查是否需要拉取
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
        self.rename_db_folders_with_timestamp(local_base_path)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Android日志拉取失败: {e}")
        return False
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        return False

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
        if os.path.isdir(item_path) and item.startswith("db."):
            # 构建新名称
            new_name = f"{item}_{timestamp}"
            new_path = os.path.join(base_path, new_name)
            
            try:
                # 重命名文件夹
                os.rename(item_path, new_path)
                print(f"已重命名文件夹: {item} -> {new_name}")
            except Exception as e:
                print(f"重命名文件夹 {item} 失败: {str(e)}")


