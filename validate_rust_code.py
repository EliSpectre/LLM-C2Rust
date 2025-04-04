import os
import subprocess
import tempfile
import re
import sys
from pathlib import Path

def analyze_module_structure(filename, file_list, output_dir):
    """
    分析Rust项目的模块结构，确定正确的mod引用方式
    
    Args:
        filename: 当前处理的文件名
        file_list: 所有源文件列表
        output_dir: 输出目录
    
    Returns:
        dict: 模块结构分析结果
    """
    result = {
        "is_main": False,             # 是否为main文件
        "mod_statements": [],         # 需要添加的mod语句
        "file_path": filename,        # 当前文件路径
        "base_name": "",              # 不含扩展名的文件名
        "directory": "",              # 文件所在目录
        "module_path": "",            # 模块路径
        "sibling_modules": [],        # 同级模块
        "nested_modules": {},         # 嵌套模块 {父模块: [子模块列表]}
        "child_modules": [],          # 子模块
        "parent_modules": []          # 父模块
    }
    
    # 获取基本文件信息
    file_path = Path(filename)
    result["base_name"] = file_path.stem
    result["directory"] = str(file_path.parent)
    result["is_main"] = result["base_name"] == "main"
    
    # 构建模块路径映射和目录结构
    module_map = {}  # 目录到模块的映射
    dir_modules = {}  # 目录结构映射: {父目录: [子模块列表]}
    
    for f in file_list:
        path = Path(f)
        module_name = path.stem
        parent_dir = str(path.parent)
        
        # 模块映射
        if parent_dir not in module_map:
            module_map[parent_dir] = []
        module_map[parent_dir].append(module_name)
        
        # 目录结构映射
        if parent_dir != path.parent.parent:  # 不是根目录
            parent_parent_dir = str(path.parent.parent)
            dir_name = path.parent.name
            if parent_parent_dir not in dir_modules:
                dir_modules[parent_parent_dir] = set()
            dir_modules[parent_parent_dir].add(dir_name)
    
    # 找出同级模块
    if result["directory"] in module_map:
        result["sibling_modules"] = [m for m in module_map[result["directory"]] if m != result["base_name"]]
    
    # 构建嵌套模块结构
    for parent_dir, children in dir_modules.items():
        if parent_dir == result["directory"]:
            # 当前目录的子模块
            for child_dir in children:
                child_path = os.path.join(parent_dir, child_dir)
                if child_path in module_map:
                    result["nested_modules"][child_dir] = module_map[child_path]
    
    # 找出子模块 (在子目录中的模块)
    dir_prefix = result["directory"] + os.path.sep
    for dir_path, modules in module_map.items():
        if dir_path.startswith(dir_prefix) and dir_path != result["directory"]:
            # 提取相对路径部分
            rel_path = os.path.relpath(dir_path, result["directory"])
            if rel_path == '.':
                continue
                
            # 只考虑直接子目录
            if os.path.sep not in rel_path:
                result["child_modules"].extend(modules)
    
    # 确定父模块
    parent_dir = os.path.dirname(result["directory"])
    while parent_dir:
        if parent_dir in module_map:
            result["parent_modules"].extend(module_map[parent_dir])
        parent_dir = os.path.dirname(parent_dir)
    
    # 为main文件生成mod语句
    if result["is_main"]:
        # 生成嵌套模块声明
        for dir_name, modules in result["nested_modules"].items():
            nested_mod = f"mod {dir_name} {{"
            for module in modules:
                nested_mod += f"\n    pub mod {module};"
            nested_mod += "\n}"
            result["mod_statements"].append(nested_mod)
        
        # 生成同级模块声明
        for module in result["sibling_modules"]:
            # 检查是否是目录而非单个文件
            is_dir_module = module in result["nested_modules"]
            
            if not is_dir_module:  # 避免重复声明
                result["mod_statements"].append(f"mod {module};")
    
    return result

def check_missing_libraries(rust_code):
    """
    检查Rust代码中可能缺少的常用库引用
    
    Args:
        rust_code: Rust代码
        
    Returns:
        list: 可能缺少的库引用列表
    """
    missing_libs = []
    
    # 检测IO操作但缺少IO库
    if (("File::" in rust_code or "stdin()" in rust_code or "stdout()" in rust_code) and
        "std::io" not in rust_code):
        missing_libs.append("std::io")
    
    # 检测文件系统操作但缺少fs库
    if ("fs::File" in rust_code or "fs::read" in rust_code) and "std::fs" not in rust_code:
        missing_libs.append("std::fs")
    
    # 检测路径操作但缺少path库
    if ("Path::" in rust_code or "PathBuf::" in rust_code) and "std::path" not in rust_code:
        missing_libs.append("std::path")
    
    # 检测常见的trait使用情况
    trait_patterns = {
        "lines()": "std::io::BufRead",
        "read_line": "std::io::BufRead",
        "flush()": "std::io::Write",
        "read_to_string": "std::io::Read",
        "write_all": "std::io::Write",
        "BufReader": "std::io::BufReader",
        "BufWriter": "std::io::BufWriter"
    }
    
    for pattern, lib in trait_patterns.items():
        if pattern in rust_code and lib not in rust_code:
            missing_libs.append(lib)
    
    # 检测CSV处理
    if "csv::" in rust_code and "csv =" not in rust_code:
        missing_libs.append("csv")
    
    return list(set(missing_libs))  # 去重

def add_missing_libraries(rust_code, missing_libs):
    """
    添加缺少的库引用到Rust代码中
    
    Args:
        rust_code: 原始Rust代码
        missing_libs: 缺少的库引用列表
        
    Returns:
        str: 添加库引用后的Rust代码
    """
    if not missing_libs:
        return rust_code
    
    # 分组库引用
    std_io_libs = []
    std_other_libs = []
    extern_libs = []
    
    for lib in missing_libs:
        if lib.startswith("std::io::"):
            std_io_libs.append(lib.split("::")[-1])
        elif lib.startswith("std::"):
            std_other_libs.append(lib)
        else:
            extern_libs.append(lib)
    
    # 构建导入语句
    import_statements = []
    
    # 添加标准IO库
    if std_io_libs:
        import_statements.append(f"use std::io::{{{', '.join(std_io_libs)}}};")
    
    # 添加其他标准库
    for lib in std_other_libs:
        import_statements.append(f"use {lib};")
    
    # 添加外部库
    for lib in extern_libs:
        import_statements.append(f"use {lib};")
    
    # 将导入语句插入到代码中
    if import_statements:
        # 查找已有的导入部分
        use_pattern = re.compile(r'^use\s+', re.MULTILINE)
        use_matches = list(use_pattern.finditer(rust_code))
        
        if use_matches:
            # 找到最后一个use语句
            last_use_pos = use_matches[-1].start()
            last_use_end = rust_code.find("\n", last_use_pos)
            if last_use_end == -1:
                last_use_end = len(rust_code)
            
            # 在最后一个use语句后插入新的导入
            return rust_code[:last_use_end+1] + "\n" + "\n".join(import_statements) + "\n" + rust_code[last_use_end+1:]
        else:
            # 在文件顶部添加导入（在注释之后）
            lines = rust_code.split("\n")
            insert_pos = 0
            
            for i, line in enumerate(lines):
                if not line.strip().startswith("//") and line.strip():
                    insert_pos = i
                    break
            
            return "\n".join(lines[:insert_pos]) + "\n" + "\n".join(import_statements) + "\n" + "\n".join(lines[insert_pos:])
    
    return rust_code

def fix_module_references(rust_code, module_info):
    """
    修复Rust代码中的模块引用
    
    Args:
        rust_code: Rust代码
        module_info: 模块结构信息
        
    Returns:
        str: 修复后的Rust代码
    """
    fixed_code = rust_code
    
    # 检查并添加必要的mod语句（主要针对main.rs）
    if module_info["is_main"]:
        # 分析当前代码中已有的模块声明
        existing_mods = []
        existing_nested_mods = {}
        
        # 查找简单的mod声明
        simple_mod_pattern = re.compile(r"mod\s+(\w+)\s*;")
        for match in simple_mod_pattern.finditer(fixed_code):
            existing_mods.append(match.group(1))
        
        # 查找嵌套的mod声明
        nested_mod_pattern = re.compile(r"mod\s+(\w+)\s*{([^}]*)}")
        for match in nested_mod_pattern.finditer(fixed_code):
            parent = match.group(1)
            content = match.group(2)
            existing_nested_mods[parent] = re.findall(r"pub\s+mod\s+(\w+)\s*;", content)
            existing_mods.append(parent)
        
        # 检查文件系统中的直接子目录，这些是可能的模块
        dirs_to_check = set()
        
        # 修复这里：正确处理file_path，确保它不为空
        file_path = module_info["file_path"]
        if ";" in file_path:
            file_paths = file_path.split(";")
        else:
            file_paths = [file_path]
            
        for file_path in file_paths:
            if not file_path:  # 跳过空路径
                continue
                
            file_dir = os.path.dirname(file_path)
            if not file_dir:  # 如果目录为空，使用当前目录
                file_dir = "."
                
            try:
                for item in os.listdir(file_dir):
                    item_path = os.path.join(file_dir, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        dirs_to_check.add(item)
            except FileNotFoundError:
                print(f"警告: 目录不存在 '{file_dir}'")
                continue
        
        # 构建模块声明
        needed_mods = {}
        
        # 对于每个子目录，确定是否需要声明为模块
        for dir_name in dirs_to_check:
            dir_path = os.path.join(os.path.dirname(module_info["file_path"]), dir_name)
            # 检查子目录中是否有rust文件或mod.rs
            has_rust_files = False
            for root, _, files in os.walk(dir_path):
                if any(f.endswith(".rs") for f in files):
                    has_rust_files = True
                    break
            
            if has_rust_files:
                # 这是一个需要声明的模块
                if dir_name not in existing_mods:
                    # 查找此目录中的rs文件
                    rs_files = []
                    for file in os.listdir(dir_path):
                        if file.endswith(".rs") and file != "mod.rs":
                            rs_files.append(os.path.splitext(file)[0])
                    
                    if rs_files:
                        needed_mods[dir_name] = rs_files
                    else:
                        needed_mods[dir_name] = None  # 简单声明
        
        # 生成缺失的mod语句
        new_mod_statements = []
        
        for mod_name, submods in needed_mods.items():
            if submods:
                # 嵌套模块声明
                stmt = f"mod {mod_name} {{"
                for submod in submods:
                    stmt += f"\n    pub mod {submod};"
                stmt += "\n}"
                new_mod_statements.append(stmt)
            else:
                # 简单模块声明
                new_mod_statements.append(f"mod {mod_name};")
        
        # 添加到代码中
        if new_mod_statements:
            # 查找适合插入位置
            use_matches = list(re.finditer(r"use\s+", fixed_code))
            if use_matches:
                # 在最后一个use后插入
                last_use = use_matches[-1].start()
                last_use_end = fixed_code.find(";", last_use)
                if last_use_end != -1:
                    fixed_code = fixed_code[:last_use_end+1] + "\n\n" + "\n".join(new_mod_statements) + "\n" + fixed_code[last_use_end+1:]
                else:
                    # 插入到代码开头
                    fixed_code = "\n".join(new_mod_statements) + "\n\n" + fixed_code
            else:
                # 没有use语句，插入到头部注释之后
                lines = fixed_code.split("\n")
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.strip().startswith("//"):
                        insert_pos = i
                        break
                
                lines.insert(insert_pos, "\n" + "\n".join(new_mod_statements))
                fixed_code = "\n".join(lines)
    
    # 修复非main文件中可能错误的mod语句
    elif not module_info["is_main"]:
        # 移除自引用
        self_mod_pattern = f"mod {module_info['base_name']};"
        fixed_code = fixed_code.replace(self_mod_pattern, "")
    
    return fixed_code

def fix_simple_to_nested_modules(rust_code, file_list):
    """
    将简单mod声明转换为嵌套形式
    
    Args:
        rust_code: 原始代码
        file_list: 文件列表
        
    Returns:
        str: 修复后的代码
    """
    # 分析模块结构
    module_map = {}
    for filepath in file_list:
        # 处理路径分隔符，支持Windows和Unix风格
        filepath = filepath.replace("\\", "/")
        parts = filepath.split("/")
        if len(parts) > 1:  # 有目录结构
            module = parts[-2]
            submodule = os.path.splitext(parts[-1])[0]
            
            if module not in module_map:
                module_map[module] = []
            if submodule not in module_map[module]:
                module_map[module].append(submodule)
    
    # 查找简单mod声明
    fixed_code = rust_code
    simple_mod_pattern = re.compile(r"mod\s+(\w+)\s*;")
    matches = list(simple_mod_pattern.finditer(rust_code))
    
    # 从后向前替换，以避免位置偏移
    for match in reversed(matches):
        mod_name = match.group(1)
        if mod_name in module_map and module_map[mod_name]:
            # 生成嵌套模块声明
            nested_mod = f"mod {mod_name} {{"
            for submod in module_map[mod_name]:
                nested_mod += f"\n    pub mod {submod};"
            nested_mod += "\n}"
            
            # 替换原来的简单声明
            start, end = match.span()
            fixed_code = fixed_code[:start] + nested_mod + fixed_code[end:]
            print(f"修复: 将 'mod {mod_name};' 转换为嵌套模块声明")
    
    return fixed_code

def check_rust_syntax(rust_code):
    """
    使用rustc检查Rust代码的语法错误
    
    Args:
        rust_code: 要检查的Rust代码
        
    Returns:
        (bool, str): (是否有错误, 错误消息)
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.rs', delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(rust_code.encode('utf-8'))
    
    try:
        # 调用rustc检查语法（使用--check选项只检查语法不生成可执行文件）
        result = subprocess.run(
            ['rustc', '--edition=2021', '--check', temp_filename],
            capture_output=True, 
            text=True
        )
        
        # 检查是否有错误
        if result.returncode != 0:
            return True, result.stderr
        return False, ""
    except Exception as e:
        return True, f"检查过程出错: {str(e)}"
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_filename)
        except:
            pass

def analyze_rust_errors(error_message):
    """
    分析Rust编译错误，识别缺少的traits和其他常见问题
    
    Args:
        error_message: rustc返回的错误消息
        
    Returns:
        dict: 包含错误分析和修复建议的字典
    """
    analysis = {
        "missing_traits": [],
        "undefined_functions": [],
        "type_mismatches": [],
        "module_errors": [],
        "path_errors": [],
        "other_errors": [],
        "suggested_fixes": []
    }
    
    # 识别缺少trait的错误
    trait_pattern = r"the method [`']([^'`]+)[`'] exists for[^,]+, but the following trait is not implemented: [`']([^'`]+)[`']"
    for method, trait in re.findall(trait_pattern, error_message):
        analysis["missing_traits"].append((method, trait))
        analysis["suggested_fixes"].append(f"需要添加 'use {trait};' 来使用 '{method}' 方法")
    
    # 识别未定义函数的错误
    undef_func_pattern = r"cannot find function [`']([^'`]+)[`']"
    for func in re.findall(undef_func_pattern, error_message):
        analysis["undefined_functions"].append(func)
    
    # 识别模块错误
    mod_pattern = r"cannot find (module|crate) [`']([^'`]+)[`']"
    for _, module in re.findall(mod_pattern, error_message):
        analysis["module_errors"].append(module)
        if not module.startswith("std::"):
            analysis["suggested_fixes"].append(f"需要添加 'mod {module};' 或检查模块路径")
    
    # 识别路径错误
    path_pattern = r"failed to resolve: (use of undeclared .+|maybe a missing crate)"
    path_errors = re.findall(path_pattern, error_message)
    if path_errors:
        analysis["path_errors"] = path_errors
    
    # 其他错误
    for line in error_message.split('\n'):
        if "error:" in line and not any(item for sublist in analysis.values() for item in sublist):
            analysis["other_errors"].append(line.strip())
    
    return analysis

def fix_common_rust_issues(rust_code, error_analysis, module_info=None):
    """
    根据错误分析修复常见的Rust代码问题
    
    Args:
        rust_code: 原始Rust代码
        error_analysis: 错误分析结果
        module_info: 模块结构信息
        
    Returns:
        str: 修复后的Rust代码
    """
    fixed_code = rust_code
    
    # 添加缺失的trait导入
    missing_imports = []
    
    for _, trait in error_analysis["missing_traits"]:
        # 标准库常见traits
        if trait == "std::io::Read" or trait == "Read":
            missing_imports.append("std::io::Read")
        elif trait == "std::io::Write" or trait == "Write":
            missing_imports.append("std::io::Write")
        elif trait == "std::io::BufRead" or trait == "BufRead":
            missing_imports.append("std::io::BufRead")
        elif trait == "std::io::BufReader" or trait == "BufReader":
            missing_imports.append("std::io::BufReader")
        elif trait == "std::io::BufWriter" or trait == "BufWriter":
            missing_imports.append("std::io::BufWriter")
        elif trait == "std::iter::Iterator" or trait == "Iterator":
            missing_imports.append("std::iter::Iterator")
        elif trait == "std::convert::From" or trait == "From":
            missing_imports.append("std::convert::From")
        elif trait == "std::convert::Into" or trait == "Into":
            missing_imports.append("std::convert::Into")
        elif trait.startswith("std::"):
            missing_imports.append(trait)
    
    # 检查模块错误，添加缺失的mod语句
    if module_info and module_info["is_main"]:
        for module in error_analysis["module_errors"]:
            if module in [m.split("::")[-1] for m in module_info["mod_statements"]]:
                continue
                
            if module in module_info["sibling_modules"]:
                # 如果是同级模块，直接添加mod语句
                missing_imports.append(f"mod {module};")
            elif module in module_info["child_modules"]:
                # 如果是子模块，添加子模块路径
                missing_imports.append(f"mod {module};")
    
    # 去重
    missing_imports = list(set(missing_imports))
    
    # 构造import语句
    if missing_imports:
        std_io_imports = [imp for imp in missing_imports if imp.startswith("std::io::")]
        mod_statements = [imp for imp in missing_imports if imp.startswith("mod ")]
        other_imports = [imp for imp in missing_imports if not imp.startswith("std::io::") and not imp.startswith("mod ")]
        
        import_statements = []
        
        # 合并std::io导入
        if std_io_imports:
            io_traits = [imp.split("::")[-1] for imp in std_io_imports]
            import_statements.append(f"use std::io::{{{', '.join(io_traits)}}}; // 添加缺少的IO traits")
        
        # 其他导入
        for imp in other_imports:
            if not imp.startswith("mod "):
                import_statements.append(f"use {imp}; // 添加缺少的trait")
        
        # mod语句应该放在use语句之后
        import_statements.extend(mod_statements)
        
        # 在文件顶部添加导入
        if import_statements:
            # 检查文件是否已有use语句
            first_use_idx = fixed_code.find("use ")
            if first_use_idx != -1:
                # 在最后一个use语句后添加
                last_use_idx = fixed_code.rfind("use ")
                last_use_end = fixed_code.find(";", last_use_idx)
                
                if last_use_end != -1:
                    fixed_code = fixed_code[:last_use_end+1] + "\n" + "\n".join(import_statements) + "\n" + fixed_code[last_use_end+1:]
                else:
                    # 如果没有找到分号，在文件开头添加
                    fixed_code = "\n".join(import_statements) + "\n" + fixed_code
            else:
                # 在第一行非注释后添加
                lines = fixed_code.split("\n")
                insert_idx = 0
                
                for i, line in enumerate(lines):
                    if not line.strip().startswith("//") and line.strip():
                        insert_idx = i
                        break
                
                lines.insert(insert_idx, "\n".join(import_statements))
                fixed_code = "\n".join(lines)
    
    return fixed_code

def use_ai_to_fix_rust_code(rust_code, error_message, module_info=None, api_key=None, base_url=None):
    """
    使用AI来修复复杂的Rust代码问题
    
    Args:
        rust_code: 有错误的Rust代码
        error_message: 编译器错误消息
        module_info: 模块结构信息
        api_key: API密钥
        base_url: API基础URL
        
    Returns:
        str: AI修复后的Rust代码
    """
    if not api_key:
        api_key = ""  # 默认API密钥
    
    if not base_url:
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 默认基础URL
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        module_context = ""
        if module_info:
            module_context = f"""
文件名: {module_info['base_name']}.rs
文件路径: {module_info['file_path']}
是主文件: {"是" if module_info['is_main'] else "否"}
同级模块: {", ".join(module_info['sibling_modules']) if module_info['sibling_modules'] else "无"}
子模块: {", ".join(module_info['child_modules']) if module_info['child_modules'] else "无"}
"""
        
        prompt = f"""我正在将C代码转换为Rust代码，但生成的Rust代码有编译错误。请帮我修复这些错误。

{module_context}

以下是出现错误的Rust代码:
```rust
{rust_code}
```

编译器报告的错误:
```
{error_message}
```

请分析这些错误，并提供修复后的完整Rust代码。特别注意:
1. 缺少的trait导入（如std::io::Read, Write, BufRead等）
2. 模块路径问题（正确引用其他模块）
3. 类型错误和未定义的函数
4. 修复代码时保持原有功能不变

你的输出应该是可以直接编译的完整Rust代码，不要包含任何解释或Markdown标记。
"""

        # 使用流式响应
        if True:  # 始终使用流式处理
            response = client.chat.completions.create(
                model="qwq-32b",
                messages=[
                    {"role": "system", "content": "你是一位Rust专家，擅长修复Rust代码中的编译错误。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=0.1,
            )
            
            # 收集流式响应的内容
            content_chunks = []
            print("正在接收AI响应: ", end="", flush=True)
            
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    if chunk.choices[0].delta.content:
                        content_chunks.append(chunk.choices[0].delta.content)
                        print(".", end="", flush=True)
            
            fixed_code = "".join(content_chunks)
            print(" 完成!")
        else:
            # 备用非流式方法
            response = client.chat.completions.create(
                model="qwq-32b",
                messages=[
                    {"role": "system", "content": "你是一位Rust专家，擅长修复Rust代码中的编译错误。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            fixed_code = response.choices[0].message.content
        
        # 移除Markdown代码块标记
        fixed_code = re.sub(r'```rust\s*', '', fixed_code)
        fixed_code = re.sub(r'```\s*', '', fixed_code)
        
        return fixed_code.strip()
    
    except Exception as e:
        print(f"AI修复代码时出错: {str(e)}")
        traceback.print_exc()  # 打印详细堆栈跟踪
        return rust_code  # 出错时返回原始代码

def validate_rust_code(filename, rust_code, file_list=None, fix_errors=True, use_ai=True, api_key=None, base_url=None, output_dir="./my_project/src"):
    """
    验证生成的Rust代码是否符合预期，并修复常见问题
    
    Args:
        filename: 原始C文件名
        rust_code: 生成的Rust代码
        file_list: 项目中的所有文件列表
        fix_errors: 是否自动修复检测到的错误
        use_ai: 对于复杂错误是否使用AI修复
        api_key: AI API密钥
        base_url: AI API基础URL
        output_dir: 输出目录
    
    Returns:
        str: 验证和可能修复后的Rust代码
    """
    name, ext = os.path.splitext(os.path.basename(filename))
    
    # 分析模块结构
    module_info = None
    if file_list:
        module_info = analyze_module_structure(filename, file_list, output_dir)
        print(f"\n分析模块结构: {name}.rs")
        print(f"- 同级模块: {', '.join(module_info['sibling_modules']) if module_info['sibling_modules'] else '无'}")
        print(f"- 子模块: {', '.join(module_info['child_modules']) if module_info['child_modules'] else '无'}")
        if module_info['mod_statements']:
            print(f"- 需要添加的mod语句: {', '.join(module_info['mod_statements'])}")
    
    # 1. 检查基本文件规则
    if name == "main":
        # main.rs 应该包含main函数
        if "fn main(" not in rust_code and "fn main() {" not in rust_code:
            print(f"警告: {name}.rs 中未找到main函数")
    else:
        # 非main.rs不应包含main函数
        if ("fn main(" in rust_code or "fn main() {" in rust_code) and ".c" in filename:
            print(f"警告: {name}.rs 不应包含main函数")
            # 移除main函数及其内容
            start = rust_code.find("fn main")
            if start != -1:
                end = rust_code.find("}", start)
                if end != -1:
                    rust_code = rust_code[:start].strip() + "\n" + rust_code[end+1:].strip()
        
        # 非main.rs不应包含对自己的mod引用
        if f"mod {name};" in rust_code:
            print(f"警告: {name}.rs 不应包含'mod {name};'声明")
            rust_code = rust_code.replace(f"mod {name};", "").strip()
    
    # 2. 检查常见的库引用缺失
    missing_libs = check_missing_libraries(rust_code)
    if missing_libs:
        print(f"检测到可能缺少的库引用: {', '.join(missing_libs)}")
        rust_code = add_missing_libraries(rust_code, missing_libs)
    
    # 3. 如果提供了file_list，修复模块引用
    if module_info:
        rust_code = fix_module_references(rust_code, module_info)
    
    # 4. 检查编译错误
    if fix_errors:
        has_error, error_message = check_rust_syntax(rust_code)
        if has_error:
            print(f"发现Rust编译错误，尝试修复...")
            error_analysis = analyze_rust_errors(error_message)
            
            # 输出错误分析
            if error_analysis["missing_traits"]:
                missing_traits = [trait for _, trait in error_analysis['missing_traits']]
                print(f"缺少的traits: {', '.join(missing_traits)}")
            
            if error_analysis["undefined_functions"]:
                print(f"未定义的函数: {', '.join(error_analysis['undefined_functions'])}")
            
            if error_analysis["module_errors"]:
                print(f"模块错误: {', '.join(error_analysis['module_errors'])}")
            
            if error_analysis["suggested_fixes"]:
                for fix in error_analysis["suggested_fixes"]:
                    print(f"- {fix}")
            
            # 先尝试自动修复常见问题
            fixed_code = fix_common_rust_issues(rust_code, error_analysis, module_info)
            
            # 再次检查修复后的代码
            still_has_error, new_error_message = check_rust_syntax(fixed_code)
            
            # 如果仍有错误且启用了AI修复，使用AI进一步修复
            if still_has_error and use_ai:
                print("常规修复未解决所有问题，尝试使用AI修复...")
                fixed_code = use_ai_to_fix_rust_code(
                    fixed_code, new_error_message, 
                    module_info, api_key, base_url
                )
                
                # 验证AI修复结果
                final_has_error, _ = check_rust_syntax(fixed_code)
                if not final_has_error:
                    print("AI成功修复了所有编译错误")
                else:
                    print("警告: 即使经过AI修复，代码仍有编译错误")
            
            return fixed_code
    
    return rust_code


# 测试代码
if __name__ == "__main__":
    # 测试一个有错误的Rust代码
    test_code = """
    // 错误的模块声明
    mod module;

    fn main() {
        module::stu::init();
        module::stu::show_all_stu();
        module::stu::find_stu_by_scores();
    }
    """
    
    # 模拟项目文件列表
    test_files = [
        "main.c",
        "module/stu.c",
        "module/data.c"
    ]
    
    print("原始代码:")
    print(test_code)
    print("\n验证并修复代码...")
    
    fixed_code = validate_rust_code("main.c", test_code, test_files)
    
    print("\n修复后的代码:")
    print(fixed_code)