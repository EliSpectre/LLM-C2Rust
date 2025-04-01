import os

def get_files_from_directory(directory_path, file_extensions=None):
    """
    读取指定目录下所有指定扩展名的文件
    
    Args:
        directory_path: 要扫描的目录路径
        file_extensions: 文件扩展名列表，如['.c', '.h']，默认为None表示读取所有文件
    
    Returns:
        包含目录中匹配的所有文件的列表
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"目录不存在: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"路径不是一个目录: {directory_path}")
    
    files_list = []
    
    # 遍历目录
    for file in os.listdir(directory_path):
        # 获取完整路径
        file_path = os.path.join(directory_path, file)
        
        # 检查是否是文件
        if os.path.isfile(file_path):
            # 如果没有指定扩展名或者文件扩展名匹配，则添加到列表
            if file_extensions is None:
                files_list.append(file)
            else:
                # 获取文件扩展名
                _, ext = os.path.splitext(file)
                if ext.lower() in file_extensions:
                    files_list.append(file)
    
    return files_list

def get_c_files_from_directory(directory_path, include_headers=True):
    """
    读取指定目录下所有的C语言相关文件
    
    Args:
        directory_path: 要扫描的目录路径
        include_headers: 是否包含头文件 (.h)，默认为True
    
    Returns:
        包含目录中所有C文件和头文件的列表
    """
    extensions = ['.c']
    if include_headers:
        extensions.append('.h')
    
    return get_files_from_directory(directory_path, extensions)

def sort_c_files(c_files):
    """
    对C文件列表进行排序，使main.c排在最前面，头文件排在相关实现文件前面
    
    Args:
        c_files: C文件列表
    
    Returns:
        排序后的C文件列表
    """
    # 将main.c移到最前面
    if 'main.c' in c_files:
        c_files.remove('main.c')
        c_files.insert(0, 'main.c')
    
    # 将头文件排在实现文件前面
    h_files = [f for f in c_files if f.endswith('.h')]
    c_impl_files = [f for f in c_files if f.endswith('.c') and f != 'main.c']
    
    # 尝试将关联的头文件和实现文件放在一起
    sorted_files = ['main.c'] if 'main.c' in c_files else []
    
    # 添加其他头文件和实现文件
    processed_bases = set()
    
    # 首先处理有关联的文件
    for h_file in h_files:
        base_name = os.path.splitext(h_file)[0]
        impl_file = f"{base_name}.c"
        
        if impl_file in c_impl_files:
            sorted_files.append(h_file)
            sorted_files.append(impl_file)
            processed_bases.add(base_name)
    
    # 添加剩余的头文件
    for h_file in h_files:
        base_name = os.path.splitext(h_file)[0]
        if base_name not in processed_bases:
            sorted_files.append(h_file)
    
    # 添加剩余的实现文件
    for c_file in c_impl_files:
        base_name = os.path.splitext(c_file)[0]
        if base_name not in processed_bases:
            sorted_files.append(c_file)
    
    return sorted_files

def read_files(directory_path, file_extensions=None):
    """
    读取指定目录下的所有文件（可指定文件类型）
    
    Args:
        directory_path: 要扫描的目录路径
        file_extensions: 文件扩展名列表，如['.c', '.h', '.cpp']，默认为None表示读取所有文件
    
    Returns:
        包含目录中匹配的所有文件的列表和格式化字符串
    """
    try:
        # 获取文件
        files_list = get_files_from_directory(directory_path, file_extensions)
        
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

def read_C_file(directory_path):
    """
    读取目录下所有的C语言文件
    
    Args:
        directory_path: 要扫描的目录路径
    
    Returns:
        C文件列表和格式化字符串
    """
    try:
        # 获取所有C文件
        c_files = get_c_files_from_directory(directory_path)
        
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

# 使用示例
if __name__ == "__main__":
    try:
        # 指定目录路径
        directory_path = ".\CODE_SRC"  # 修改为您的目录路径
        
        print("==== 读取所有文件 ====")
        all_files, _ = read_files(directory_path)
        
        print("\n==== 读取C和C++文件 ====")
        code_files, _ = read_files(directory_path, ['.c', '.h', '.cpp', '.hpp'])
        # print(code_files)

        print("\n==== 只读取C文件 ====")
        c_files, c_files_str = read_C_file(directory_path)
        
    except Exception as e:
        print(f"错误: {str(e)}")