from openai import OpenAI
import os

def read_cpp_file(filenames):
    """读取多个C++文件内容并拼接"""
    combined_code = ""
    
    for filename in filenames:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                file_content = file.read()
                combined_code += f"\n// ---------- {filename} ----------\n\n"
                combined_code += file_content + "\n"
        except Exception as e:
            return f"读取文件 {filename} 出错: {str(e)}"
    
    return combined_code if combined_code else "没有找到任何文件内容"

# 指定要读取的C语言文件列表
c_files = ["main.c", "math.h","math.c"]

# 获取拼接后的C代码
cpp_code = read_cpp_file(c_files)
if cpp_code.startswith("读取文件"):
    print(cpp_code)
    exit(1)

# 初始化OpenAI客户端
client = OpenAI(
    # 如果没有配置环境变量，请用百炼API Key替换：api_key="sk-xxx"
    api_key = "sk-99ff2f4f157d4fa6a54cafe3b4671aec",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

reasoning_content = ""  # 定义完整思考过程
answer_content = ""     # 定义完整回复
is_answering = False   # 判断是否结束思考过程并开始回复

# 创建聊天完成请求
completion = client.chat.completions.create(
    model="qwq-32b",  # 此处以 qwq-32b 为例，可按需更换模型名称
    messages=[
        {"role":"system","content":"""你是一位精通 C 和 Rust 的专家。请将以下 C 代码转换为地道的 Rust 代码，确保遵循 Rust 的所有最佳实践、内存安全原则和惯用表达方式。

首先，分析 C 代码的核心功能、数据结构、算法和内存管理方式。然后，使用 <rust> 标记后换行直接提供完整的 Rust 实现，不要在代码部分包含任何解释或注释，输出结果时也不要使用markdown格式。Rust 代码应该尽可能保持原始程序的功能，同时利用 Rust 特有的优势。"""},
        {"role": "user", "content": cpp_code}
    ],
    stream=True,
)

print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

for chunk in completion:
    # 如果chunk.choices为空，则打印usage
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
    else:
        delta = chunk.choices[0].delta
        # 打印思考过程
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
            print(delta.reasoning_content, end='', flush=True)
            reasoning_content += delta.reasoning_content
        else:
            # 开始回复
            if delta.content != "" and is_answering is False:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True
            # 打印回复过程
            print(delta.content, end='', flush=True)
            answer_content += delta.content

# 可选：将结果保存到文件
with open(".\my_project\src\main.rs", "w", encoding="utf-8") as f:
    # 首先尝试提取<rust>标记后的代码
    if "<rust>" in answer_content:
        rust_code = answer_content.split("<rust>")[1].strip()
        
        # 进一步处理：如果包含'''rust或```rust标记，去除它们
        if rust_code.startswith("```rust"):
            # 移除开头的```rust
            rust_code = rust_code.replace("```rust", "", 1).strip()
            # 移除结尾的```
            if rust_code.endswith("```"):
                rust_code = rust_code[:-3].strip()
        
        # 处理可能的三引号变体
        if rust_code.startswith("'''rust"):
            # 移除开头的'''rust
            rust_code = rust_code.replace("'''rust", "", 1).strip()
            # 移除结尾的'''
            if rust_code.endswith("'''"):
                rust_code = rust_code[:-3].strip()
                
        f.write(rust_code)
    else:
        # 如果没有<rust>标记，尝试直接提取代码块
        if "```rust" in answer_content:
            # 提取```rust和```之间的内容
            start_index = answer_content.find("```rust") + 7  # 7是```rust的长度
            end_index = answer_content.find("```", start_index)
            if end_index != -1:
                rust_code = answer_content[start_index:end_index].strip()
                f.write(rust_code)
            else:
                f.write(answer_content)
        elif "'''rust" in answer_content:
            # 提取'''rust和'''之间的内容
            start_index = answer_content.find("'''rust") + 7  # 7是'''rust的长度
            end_index = answer_content.find("'''", start_index)
            if end_index != -1:
                rust_code = answer_content[start_index:end_index].strip()
                f.write(rust_code)
            else:
                f.write(answer_content)
        else:
            f.write(answer_content)

print("\n\n转换结果已保存到 main.rs")