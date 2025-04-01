import requests
import os
import time
import concurrent.futures

# ✅ API配置
API_URL = "http://example.com/api/convert"  # 替换为实际API地址
MAX_WORKERS = 5  # 并发调用API的最大线程数
DELAY_BETWEEN_REQUESTS = 1  # 防止频繁调用API的延迟（秒）

# ✅ 将C语言文件转换为Rust语言
def convert_to_rust(file_name, file_content):
    """调用API，将C语言代码转换为Rust语言"""
    try:
        response = requests.post(
            API_URL,
            json={"file_name": file_name, "file_content": file_content},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ {file_name} 转换成功！")
            return response.text  # 返回Rust代码
        else:
            print(f"❌ 转换失败: {file_name} - 状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {file_name} - {str(e)}")
        return None


# ✅ 将C语言项目中的所有文件进行转换
def convert_files_in_project(project_dir):
    """将C语言项目批量转换为Rust项目"""

    # 1️⃣ 获取C语言项目中的所有C语言相关文件
    c_files = [f for f in os.listdir(project_dir) if f.endswith(('.c', '.h', '.S'))]
    
    # 2️⃣ 创建Rust项目目录
    rust_dir = os.path.join(project_dir, "rust_project")
    os.makedirs(rust_dir, exist_ok=True)

    # 3️⃣ 并行转换文件
    def process_file(c_file):
        c_file_path = os.path.join(project_dir, c_file)
        
        # 读取C语言文件内容
        with open(c_file_path, 'r', encoding='utf-8') as file:
            c_content = file.read()

        # 调用API将C语言代码转换为Rust语言代码
        rust_code = convert_to_rust(c_file, c_content)

        if rust_code:
            # 转换后的文件名
            rust_file = c_file.replace('.c', '.rs').replace('.h', '.rs').replace('.S', '.rs')
            rust_file_path = os.path.join(rust_dir, rust_file)
            
            # 保存Rust代码到文件
            with open(rust_file_path, 'w', encoding='utf-8') as rust_file:
                rust_file.write(rust_code)
            
            print(f"✅ 已保存：{rust_file_path}")
        else:
            print(f"⚠️ 转换失败：{c_file}")
        
        # 防止调用API过于频繁，延迟请求
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # 并行处理多个文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_file, c_files)

    print("\n🎉 全部文件已转换完成！")


# ✅ 执行转换
if __name__ == "__main__":
    # 指定C语言项目的路径
    project_dir = "path/to/your/c_project"  # 替换为实际路径
    convert_files_in_project(project_dir)
