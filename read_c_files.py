import os
import shutil

def get_files_from_directory(directory_path, file_extensions=None, recursive=True):
    """
    递归读取指定目录下所有指定扩展名的文件
    
    Args:
        directory_path: 要扫描的目录路径
        file_extensions: 文件扩展名列表，如['.c', '.h']，默认为None表示读取所有文件
        recursive: 是否递归扫描子目录，默认为True
    
    Returns:
        包含目录中匹配的所有文件的列表，返回的是相对于directory_path的路径
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"目录不存在: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"路径不是一个目录: {directory_path}")
    
    files_list = []
    
    # 遍历目录
    for item in os.listdir(directory_path):
        # 获取完整路径
        item_path = os.path.join(directory_path, item)
        
        # 如果是目录且开启了递归扫描
        if os.path.isdir(item_path) and recursive:
            # 递归获取子目录中的文件
            sub_files = get_files_from_directory(item_path, file_extensions, recursive)
            # 将子目录前缀添加到文件名中
            for sub_file in sub_files:
                # 构建相对于原始directory_path的路径
                relative_path = os.path.join(item, sub_file)
                files_list.append(relative_path)
        
        # 如果是文件
        elif os.path.isfile(item_path):
            # 如果没有指定扩展名或者文件扩展名匹配，则添加到列表
            if file_extensions is None:
                files_list.append(item)
            else:
                # 获取文件扩展名
                _, ext = os.path.splitext(item)
                if ext.lower() in file_extensions:
                    files_list.append(item)
    
    return files_list

def get_c_files_from_directory(directory_path, include_headers=True, recursive=True):
    """
    递归读取指定目录下所有的C语言相关文件
    
    Args:
        directory_path: 要扫描的目录路径
        include_headers: 是否包含头文件 (.h)，默认为True
        recursive: 是否递归扫描子目录，默认为True
    
    Returns:
        包含目录中所有C文件和头文件的列表
    """
    extensions = ['.c']
    if include_headers:
        extensions.append('.h')
    
    return get_files_from_directory(directory_path, extensions, recursive)

def sort_c_files(c_files):
    """
    对C文件列表进行排序，使main.c排在最前面，头文件排在相关实现文件前面
    
    Args:
        c_files: C文件列表
    
    Returns:
        排序后的C文件列表
    """
    # 提取纯文件名（不含路径）
    c_file_names = [os.path.basename(f) for f in c_files]
    
    # 创建文件名到完整路径的映射
    file_map = {os.path.basename(f): f for f in c_files}
    
    # 将main.c移到最前面
    main_files = [f for f in c_file_names if f.lower() == 'main.c']
    non_main_files = [f for f in c_file_names if f.lower() != 'main.c']
    
    # 将头文件排在实现文件前面
    h_files = [f for f in non_main_files if f.endswith('.h')]
    c_impl_files = [f for f in non_main_files if f.endswith('.c')]
    
    # 尝试将关联的头文件和实现文件放在一起
    processed_bases = set()
    paired_files = []
    
    # 首先处理有关联的文件
    for h_file in h_files:
        base_name = os.path.splitext(h_file)[0]
        impl_file = f"{base_name}.c"
        
        if impl_file in c_impl_files:
            paired_files.extend([h_file, impl_file])
            processed_bases.add(base_name)
    
    # 添加剩余的头文件
    remaining_h_files = [h_file for h_file in h_files 
                        if os.path.splitext(h_file)[0] not in processed_bases]
    
    # 添加剩余的实现文件
    remaining_c_files = [c_file for c_file in c_impl_files 
                        if os.path.splitext(c_file)[0] not in processed_bases]
    
    # 合并最终排序的文件列表
    sorted_file_names = main_files + paired_files + remaining_h_files + remaining_c_files
    
    # 将文件名转换回完整路径
    sorted_files = [file_map[name] for name in sorted_file_names]
    
    return sorted_files

def read_files(directory_path, file_extensions=None, recursive=True):
    """
    递归读取指定目录下的所有文件（可指定文件类型）
    
    Args:
        directory_path: 要扫描的目录路径
        file_extensions: 文件扩展名列表，如['.c', '.h', '.cpp']，默认为None表示读取所有文件
        recursive: 是否递归扫描子目录，默认为True
    
    Returns:
        包含目录中匹配的所有文件的列表和格式化字符串
    """
    try:
        # 获取文件
        files_list = get_files_from_directory(directory_path, file_extensions, recursive)
        
        # 如果是C文件，可以进行排序
        if file_extensions and all(ext in ['.c', '.h'] for ext in file_extensions):
            files_list = sort_c_files(files_list)
        
        print(f"找到的文件: {files_list}")
        
        # 输出符合代码格式的列表字符串
        files_str = "files_list = " + repr(files_list)
        print("\n生成的代码变量:")
        print(files_str)

        return files_list, files_str
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return [], ""

def read_C_file(directory_path, recursive=True):
    """
    递归读取目录下所有的C语言文件
    
    Args:
        directory_path: 要扫描的目录路径
        recursive: 是否递归扫描子目录，默认为True
    
    Returns:
        C文件列表和格式化字符串
    """
    try:
        # 获取所有C文件
        c_files = get_c_files_from_directory(directory_path, True, recursive)
        
        # 对C文件进行排序
        c_files = sort_c_files(c_files)
        
        print(f"找到的C文件: {c_files}")
        
        # 输出符合代码格式的列表字符串
        c_files_str = "c_files = " + repr(c_files)
        print("\n生成的代码变量:")
        print(c_files_str)
        return c_files, c_files_str
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return [], ""

def get_full_path(directory_path, file_list):
    """
    将相对路径文件列表转换为绝对路径
    
    Args:
        directory_path: 基础目录路径
        file_list: 相对路径文件列表
    
    Returns:
        绝对路径文件列表
    """
    return [os.path.join(directory_path, f) for f in file_list]



def get_output_path(output_dir, filename, c_files, directory_path):
    """生成适当的输出路径，确保不同类型的文件不会产生命名冲突，且保持正确的目录结构
    
    Args:
        output_dir: 输出目录
        filename: 原始文件名
        c_files: 所有代码文件列表
        directory_path: 源代码目录路径
        
    Returns:
        输出文件的完整路径
    """
    # 获取相对于源目录的相对路径
    rel_path = os.path.relpath(filename, start=directory_path) if os.path.isabs(filename) else filename
    
    # 提取文件名和扩展名
    base_dir = os.path.dirname(rel_path)
    base_name = os.path.basename(rel_path)
    name, ext = os.path.splitext(base_name)
    
    # 检查此文件是否有同名的配对文件(.h和.c)
    has_twin_file = False
    twin_ext = ".c" if ext.lower() == ".h" else ".h"
    twin_name = name + twin_ext
    
    # 检查同一目录下是否有配对文件
    for c_file in c_files:
        c_rel_path = os.path.relpath(c_file, start=directory_path) if os.path.isabs(c_file) else c_file
        c_dir = os.path.dirname(c_rel_path)
        c_base = os.path.basename(c_rel_path)
        
        if c_dir == base_dir and c_base == twin_name:
            has_twin_file = True
            break
    
    # 为不同类型的文件生成不同的输出名称
    if ext.lower() == ".h":
        if has_twin_file:
            output_name = f"{name}_header.rs"
        else:
            output_name = f"{name}.rs"
    elif ext.lower() == ".c":
        if has_twin_file:
            output_name = f"{name}_impl.rs"
        else:
            output_name = f"{name}.rs"
    else:
        # 对于其他类型文件
        output_name = f"{name}.rs"
    
    # 构建输出路径，保持与源目录相同的结构
    if base_dir:
        output_subdir = os.path.join(output_dir, base_dir)
        os.makedirs(output_subdir, exist_ok=True)
        return os.path.join(output_subdir, output_name)
    else:
        return os.path.join(output_dir, output_name)

def is_code_file(filename):
    """判断文件是否为需要转换的代码文件"""
    code_extensions = ['.c', '.h', '.cpp', '.hpp']
    _, ext = os.path.splitext(filename)
    return ext.lower() in code_extensions


def is_data_file(filename):
    """判断文件是否为数据文件（无需转换）"""
    data_extensions = ['.txt', '.csv', '.json', '.xml', '.dat', '.cfg', '.ini']
    _, ext = os.path.splitext(filename)
    return ext.lower() in data_extensions


def copy_file(src_dir, filename, dest_dir):
    """将文件从源目录复制到目标目录，保持正确的目录结构
    
    Args:
        src_dir: 源目录
        filename: 相对于src_dir的文件路径
        dest_dir: 目标目录
        
    Returns:
        是否复制成功
    """
    # 获取完整的源路径
    src_path = os.path.join(src_dir, filename)
    
    # 获取相对路径，保持目录结构
    rel_path = os.path.relpath(filename, start=src_dir) if os.path.isabs(filename) else filename
    dest_path = os.path.join(dest_dir, rel_path)
    
    # 确保目标目录存在
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        shutil.copy2(src_path, dest_path)
        print(f"已复制文件: {filename} -> {dest_path}")
        return True
    except Exception as e:
        print(f"复制文件 {filename} 失败: {str(e)}")
        return False


def read_cpp_file(directory_path, filenames):
    """读取多个C++文件内容并拼接"""
    combined_code = ""
    
    for filename in filenames:
        try:
            # 拼接完整路径
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                combined_code += f"\n// ---------- {filename} ----------\n\n"
                combined_code += file_content + "\n"
        except Exception as e:
            return f"读取文件 {filename} 出错: {str(e)}"
    
    return combined_code if combined_code else "没有找到任何文件内容"


# 使用示例
if __name__ == "__main__":
    try:
        # 指定目录路径
        directory_path = "./CODE_SRC"  # 修改为您的目录路径
        
        print("==== 读取所有文件（包括子目录） ====")
        all_files, _ = read_files(directory_path)
        
        print("\n==== 读取C和C++文件（包括子目录） ====")
        code_files, _ = read_files(directory_path, ['.c', '.h', '.cpp', '.hpp'])
        
        print("\n==== 只读取C文件（包括子目录） ====")
        c_files, c_files_str = read_C_file(directory_path)
        
        # 获取文件的完整路径
        full_paths = get_full_path(directory_path, c_files)
        print("\n完整路径：")
        for path in full_paths:
            print(path)
        
    except Exception as e:
        print(f"错误: {str(e)}")