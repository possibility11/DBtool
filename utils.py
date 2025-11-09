import os
import zipfile
import shutil
from pathlib import Path
import traceback

# 启用长路径支持
def get_long_path(path):
    """
    将普通路径转换为Windows长路径格式（使用\\\\?\\前缀）
    用于处理超过260字符的路径限制问题

    参数:
    path: 原始路径字符串

    返回:
    处理后的长路径字符串
    """
    if os.name != 'nt':  # 非Windows系统直接返回原路径
        return path

    # 如果已经是长路径格式，直接返回
    if path.startswith('\\\\?\\'):
        return path

    # 将路径转换为绝对路径
    abs_path = os.path.abspath(path)

    # 检查是否是UNC路径（网络路径）
    if abs_path.startswith('\\\\'):
        # 对于UNC路径，使用格式: \\\\?\\UNC\\server\\share
        if not abs_path.startswith('\\\\?\\UNC\\'):
            return '\\\\?\\UNC\\' + abs_path[2:]
        return abs_path

    # 对于本地路径，使用格式: \\\\?\\C:\\path\\to\\file
    # 确保路径使用反斜杠
    abs_path = abs_path.replace('/', '\\')
    return '\\\\?\\' + abs_path

# 确保使用正确的路径分隔符
def normalize_path(path):
    if os.name == 'nt':  # Windows系统
        return path.replace('/', '\\')
    else:
        return path.replace('\\', '/')


def zip_and_move_folder(source_folder, target_directory):
    """
    完整打包多层文件夹结构并移动到目标目录
    
    参数:
    source_folder: 要打包的源文件夹名称
    target_directory: 目标目录路径
    """
    
    try:
        # 确保路径是绝对路径
        source_folder = os.path.abspath(source_folder)
        target_directory = os.path.abspath(target_directory)
        #source_folder1 = get_long_path(source_folder)
        #target_directory1 = get_long_path(target_directory)
        #source_folder = normalize_path(source_folder)
        #target_directory = normalize_path(target_directory)
        
        print(f"源文件夹绝对路径: {source_folder}")
        print(f"目标目录绝对路径: {target_directory}")
        
        # 检查源文件夹是否存在
        if not os.path.exists(source_folder):
            print(f"错误: 源文件夹 '{source_folder}' 不存在")
            return False
        
        # 检查是否是文件夹
        if not os.path.isdir(source_folder):
            print(f"错误: '{source_folder}' 不是一个文件夹")
            return False
        
        # 检查目标目录是否存在，如果不存在则创建
        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                print(f"创建目标目录: {target_directory}")
            except OSError as e:
                print(f"错误: 无法创建目标目录 '{target_directory}': {e}")
                return False
        
        # 创建zip文件名
        source_name = os.path.basename(source_folder)
        zip_filename = f"{source_name}.zip"
        temp_zip_path = get_long_path(os.path.join(os.getcwd(), zip_filename))
        
        # 删除已存在的同名zip文件
        if os.path.exists(temp_zip_path):
            try:
                os.remove(temp_zip_path)
                print(f"删除已存在的临时zip文件: {temp_zip_path}")
            except OSError as e:
                print(f"错误: 无法删除已存在的文件 '{temp_zip_path}': {e}")
                return False
        
        print(f"正在打包文件夹 '{source_folder}'...")
        
        # 创建zip文件
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 使用Path对象简化路径处理
            source_path = Path(source_folder)
            # 遍历所有文件和子文件夹
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    try:
                        # 计算在zip文件中的相对路径
                        arcname = file_path.relative_to(source_path.parent)
                        # 使用长路径格式访问文件
                        long_file_path = get_long_path(str(file_path))
                        # 将文件添加到zip中
                        #zipf.write(str(file_path), str(arcname))
                        zipf.write(long_file_path, str(arcname))
                        print(f"添加文件: {arcname}")
                    except Exception as e:
                        print(f"无法添加文件 {file_path}: {e}")
                        print(f"文件路径长度: {len(str(file_path))}")
                        if hasattr(e, 'winerror') and e.winerror:
                            print(f"Windows错误代码: {e.winerror}")
                        continue
        
        print(f"已创建zip文件: {temp_zip_path}")
        
        # 验证zip文件内容
        print("验证ZIP文件内容...")
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                print(f"ZIP文件中包含 {len(file_list)} 个文件/文件夹")
                
                # 按目录结构显示文件
                dir_structure = {}
                for file in file_list:
                    parts = file.split('/')
                    if len(parts) > 1:
                        dir_name = parts[0]
                        if dir_name not in dir_structure:
                            dir_structure[dir_name] = []
                        dir_structure[dir_name].append('/'.join(parts[1:]))
                    else:
                        if "根目录" not in dir_structure:
                            dir_structure["根目录"] = []
                        dir_structure["根目录"].append(file)
                
                for dir_name, files in dir_structure.items():
                    print(f"\n{dir_name} 目录下的文件 ({len(files)} 个):")
                    for f in sorted(files)[:10]:  # 只显示前10个文件
                        print(f"  {f}")
                    if len(files) > 10:
                        print(f"  ... 还有 {len(files) - 10} 个文件")
        except Exception as e:
            print(f"警告: 无法验证ZIP文件内容: {e}")
                    
        # 移动zip文件到目标目录
        target_zip_path = get_long_path(os.path.join(target_directory, zip_filename))
        print(f"准备移动文件到: {target_zip_path}")
        
        # 确保目标路径是有效的
        if not os.path.isabs(target_zip_path):
            target_zip_path = os.path.abspath(target_zip_path)
        
        # 检查目标路径是否已存在同名文件
        if os.path.exists(target_zip_path):
            try:
                os.remove(target_zip_path)
                print(f"删除已存在的目标文件: {target_zip_path}")
            except OSError as e:
                print(f"错误: 无法删除已存在的目标文件 '{target_zip_path}': {e}")
                return False
        
        # 移动文件
        shutil.move(temp_zip_path, target_zip_path)
        print(f"已移动zip文件到: {target_zip_path}")
        return True
        
    except Exception as e:
        print(f"错误: 操作过程中发生错误: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 设置源文件夹和目标目录
    source_folder = "DBfile"  # 要打包的文件夹
    
    # 请替换为你的目标目录路径
    # 注意: 使用正斜杠(/)而不是反斜杠(\)，或者在Windows上使用原始字符串(r"路径")
    target_directory = "D:/"
    
    # 如果目标目录是Windows路径，可以这样处理
    # target_directory = r"C:\path\to\your\target\directory"
    
    # 执行打包和移动操作
    success = zip_and_move_folder(source_folder, target_directory)
    
    if success:
        print("操作成功完成!")
    else:
        print("操作失败!")