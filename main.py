from openai import OpenAI
import os
from prompt import get_system_prompt
from read_c_files import read_files


def read_cpp_file(directory_path,filenames):
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

def validate_rust_code(filename, rust_code):
    """验证生成的Rust代码是否符合预期"""
    name, _ = os.path.splitext(filename)
    
    if name == "main":
        # main.rs 应该包含main函数且可能引用math模块
        if "fn main(" not in rust_code and "fn main() {" not in rust_code:
            print(f"警告: {name}.rs 中未找到main函数")
        
    elif name == "math":
        # math.rs 不应包含main函数
        if "fn main(" in rust_code or "fn main() {" in rust_code:
            print(f"警告: {name}.rs 不应包含main函数")
            # 移除main函数及其内容（简化处理）
            start = rust_code.find("fn main")
            if start != -1:
                end = rust_code.find("}", start)
                if end != -1:
                    rust_code = rust_code[:start].strip() + "\n" + rust_code[end+1:].strip()
        
        # math.rs 不应包含mod math;
        if "mod math;" in rust_code:
            print(f"警告: {name}.rs 不应包含'mod math;'声明")
            rust_code = rust_code.replace("mod math;", "").strip()
    
    return rust_code

# 指定要读取的C语言文件列表
# c_files = ["main.c","math.h","math.c"]
directory_path = "./CODE_SRC"
c_files, _ = read_files(directory_path, ['.c', '.h', '.cpp', '.hpp'])


# 获取拼接后的C代码
cpp_code = read_cpp_file(directory_path,c_files)
if cpp_code.startswith("读取文件"):
    print(cpp_code)
    exit(1)

# 确保输出目录存在
os.makedirs("./my_project/src", exist_ok=True)

# 初始化OpenAI客户端
client = OpenAI(
    api_key = "sk-99ff2f4f157d4fa6a54cafe3b4671aec",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

for filename in c_files:
    print(f"\n{'='*40}\n处理文件: {filename}\n{'='*40}")
    
    # 获取针对当前文件类型的系统提示
    system_prompt = get_system_prompt(filename)
    
    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""     # 定义完整回复
    is_answering = False    # 判断是否结束思考过程并开始回复
    
    completion = client.chat.completions.create(
        model="qwq-32b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": cpp_code}
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
    rust_code = validate_rust_code(filename, rust_code)
    
    # 创建新文件名
    name, _ = os.path.splitext(filename)
    
    # 保存到文件
    output_path = f"./my_project/src/{name}.rs"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rust_code)

    print(f"\n\n转换结果已保存到 {output_path}")

print("\n\n转换完成!!!!!")