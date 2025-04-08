from openai import OpenAI
import os
import shutil
from prompt import get_system_prompt
from read_c_files import read_files, get_output_path, is_data_file, is_code_file, read_cpp_file, copy_file
from validate_rust_code import validate_rust_code
from config import src_code_directory_path, api_key, big_model, document_path, code_output_dir, data_output_dir, base_url

def extract_rust_code(answer_content):
    """从回答内容中提取Rust代码"""
    rust_code = answer_content
    
    # 处理<rust>和</rust>标记
    if "<rust>" in rust_code:
        rust_code = rust_code.split("<rust>")[1].strip()
    
    if "</rust>" in rust_code:
        rust_code = rust_code.split("</rust>")[0].strip()
    
    # 处理```rust和'''rust标记
    for marker in ["```rust", "'''rust"]:
        if rust_code.startswith(marker):
            rust_code = rust_code.replace(marker, "", 1).strip()
            break
    
    # 处理结束标记
    for end_marker in ["```", "'''"]:
        if rust_code.endswith(end_marker):
            rust_code = rust_code[:-len(end_marker)].strip()
            break
    
    return rust_code



# 主程序开始
# 指定要读取的文件列表（包括所有类型文件）
# src_code_directory_path = "./CODE_SRC/src2"
all_files, _ = read_files(src_code_directory_path)  # 不限制扩展名，读取所有文件

# 过滤出需要处理的代码文件
c_files = [f for f in all_files if is_code_file(f)]


# 确保输出目录存在
os.makedirs(code_output_dir, exist_ok=True)
os.makedirs(data_output_dir, exist_ok=True)

# 先处理非代码文件（直接复制到上一级目录）
for filename in all_files:
    if is_data_file(filename):
        print(f"\n{'='*40}\n处理数据文件: {filename}\n{'='*40}")
        # 使用data_output_dir作为目标目录
        copy_file(src_code_directory_path, filename, data_output_dir)

# 如果有代码文件需要转换
if c_files:
    # 获取拼接后的C代码
    cpp_code = read_cpp_file(src_code_directory_path, c_files)
    if cpp_code.startswith("读取文件"):
        print(cpp_code)
        exit(1)

    # 初始化zhipuai客户端
    client = OpenAI(
        api_key = api_key,  # 请填写您自己的APIKey
        base_url=base_url,  # 
    )

    # 处理每个代码文件
    for filename in c_files:
        print(f"\n{'='*40}\n处理代码文件: {filename}\n{'='*40}")
        
        # 获取针对当前文件类型的系统提示
        system_prompt = get_system_prompt(filename,all_files, document_path)
        
        reasoning_content = ""  # 定义完整思考过程
        answer_content = ""     # 定义完整回复
        is_answering = False    # 判断是否结束思考过程并开始回复
        
        # 注意这里使用code_output_dir
        output_path = get_output_path(code_output_dir, filename, c_files, src_code_directory_path)
        
        system_prompt = ("\n\n这是文件的路径,你生成代码的时候,使用其他文件mod的时候需要注意一下!!!!!,特别是比如main文件时,直接mod某个文件名可能不行,同时转换子文件的时候也得注意一下" + str(all_files)+
        "注意这是数据的保存的路径,即:比我们转换完的代码的路径少一级,所以代码中遇到的读取数据的路径需要对应修改一下"+data_output_dir
        +"\n\n" + system_prompt)
        
        
        completion = client.chat.completions.create(
            model= big_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "这是c语言的代码/n" + cpp_code}
            ],
            stream=True,
        )

        print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

        for chunk in completion:
            if not chunk.choices:
                if hasattr(chunk, 'usage'):
                    print("\nUsage:")
                    print(chunk.usage)
            else:
                delta = chunk.choices[0].delta
                # 打印思考过程
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    print(delta.reasoning_content, end='', flush=True)
                    reasoning_content += delta.reasoning_content
                elif hasattr(delta, 'content') and delta.content is not None:
                    # 开始回复
                    if delta.content != "" and is_answering is False:
                        print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                        is_answering = True
                    # 打印回复过程
                    print(delta.content, end='', flush=True)
                    answer_content += delta.content

        # 检查是否应跳过此文件
        if "Skip this file".lower() in answer_content.lower():
            print(f"\n跳过文件 {filename}，不需要转换")
            continue
        
        # 提取Rust代码
        rust_code = extract_rust_code(answer_content)
        
        
        # 验证并修正Rust代码
        print("\n" + "=" * 20 + "验证Rust代码" + "=" * 20 + "\n")
        if filename == "main.c":
            # 对于main文件，直接使用cpp_code
            rust_code = validate_rust_code(filename, rust_code, all_files)
        # rust_code = validate_rust_code(filename, rust_code,all_files)
        
         # 提取Rust代码
        rust_code = extract_rust_code(answer_content)
        
        # 保存到文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rust_code)

        print(f"\n\n转换结果已保存到 {output_path}")

print("\n\n转换完成!!!!!")