''''
'"LLM辅助项目文档自动化编写功能" 
**"LLM-assisted Automated Project Documentation Writing Feature"**
这个文件是基于LLM将C语言的文件自动化编写文档,生成对应的prompt。
'''
import os
import re
import argparse
from openai import OpenAI
import time

class CProjectDocGenerator:
    """
    C语言项目文档自动化生成工具
    
    该工具可以分析整个C项目，并使用LLM生成语义化的项目文档
    """
    
    def __init__(self, api_key=None, base_url=None, model="qwq-32b"):
        """
        初始化文档生成器
        
        Args:
            api_key: API密钥
            base_url: API基础URL (如果使用非默认端点)
            model: 要使用的模型名称
        """
        self.model = model
        
        # 初始化OpenAI客户端
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)
        
        # 文档的各个部分
        self.doc_sections = {
            "project_overview": "项目概述",
            "architecture": "架构设计",
            "modules": "模块说明",
            "data_structures": "数据结构",
            "algorithms": "算法说明",
            "api_reference": "API参考",
            "usage_examples": "使用示例",
        }

    def generate_project_documentation(self, project_path):
        """
        为整个项目生成文档
        
        Args:
            project_path: C项目的根目录路径
            
        Returns:
            生成的项目文档字符串
        """
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"项目路径不存在: {project_path}")
        
        print(f"开始分析项目: {project_path}")
        
        # 扫描项目文件
        c_files, h_files = self._scan_project_files(project_path)
        print(f"发现 {len(c_files)} 个C文件和 {len(h_files)} 个头文件")
        
        # 读取所有文件内容
        project_code = self._read_project_files(c_files, h_files)
        
        # 生成项目概述
        overview = self._generate_project_overview(project_path, c_files, h_files, project_code)
        
        # 生成架构设计
        architecture = self._generate_architecture_docs(project_path, project_code)
        
        # 生成模块说明
        modules = self._generate_modules_docs(project_path, c_files, h_files)
        
        # 生成数据结构说明
        data_structures = self._generate_data_structures_docs(project_code)
        
        # 生成API参考
        api_reference = self._generate_api_reference(project_code)
        
        # 合并所有部分
        documentation = self._compile_documentation(
            project_path,
            overview,
            architecture,
            modules,
            data_structures,
            api_reference
        )
        
        return documentation
    
    def _scan_project_files(self, project_path):
        """
        扫描项目中所有的C文件和头文件
        
        Args:
            project_path: 项目根目录
            
        Returns:
            c_files列表和h_files列表
        """
        c_files = []
        h_files = []
        
        # 递归遍历目录
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.c'):
                    c_files.append(file_path)
                elif file.endswith('.h'):
                    h_files.append(file_path)
        
        return c_files, h_files
    
    def _read_project_files(self, c_files, h_files):
        """
        读取项目中所有文件的内容
        
        Args:
            c_files: C文件路径列表
            h_files: 头文件路径列表
            
        Returns:
            所有文件内容的字典，键为文件路径
        """
        project_code = {}
        
        # 读取所有C文件
        for file_path in c_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_code[file_path] = f.read()
            except UnicodeDecodeError:
                try:
                    # 尝试其他编码
                    with open(file_path, 'r', encoding='gbk') as f:
                        project_code[file_path] = f.read()
                except:
                    print(f"警告: 无法读取文件 {file_path}")
                    project_code[file_path] = "/* 无法读取文件内容 */"
        
        # 读取所有头文件
        for file_path in h_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_code[file_path] = f.read()
            except UnicodeDecodeError:
                try:
                    # 尝试其他编码
                    with open(file_path, 'r', encoding='gbk') as f:
                        project_code[file_path] = f.read()
                except:
                    print(f"警告: 无法读取文件 {file_path}")
                    project_code[file_path] = "/* 无法读取文件内容 */"
        
        return project_code
    
    def _generate_project_overview(self, project_path, c_files, h_files, project_code):
        """生成项目概述"""
        print("正在生成项目概述...")
        
        # 准备项目文件的摘要
        files_summary = []
        for file_path in sorted(c_files + h_files):
            rel_path = os.path.relpath(file_path, project_path)
            files_summary.append(f"- {rel_path}")
        
        files_summary_str = "\n".join(files_summary)
        
        # 选择主要文件进行分析
        main_files = []
        for file_path in c_files:
            if "main.c" in file_path.lower() or "app.c" in file_path.lower():
                main_files.append(file_path)
        
        # 如果没有找到主文件，选择几个最大的文件
        if not main_files and c_files:
            c_files_with_size = [(f, len(project_code[f])) for f in c_files]
            c_files_with_size.sort(key=lambda x: x[1], reverse=True)
            main_files = [f for f, _ in c_files_with_size[:min(3, len(c_files))]]
        
        # 准备主文件内容
        main_content = ""
        for file_path in main_files:
            rel_path = os.path.relpath(file_path, project_path)
            main_content += f"\n--- {rel_path} ---\n"
            # 取文件内容的前1000个字符作为样本
            content_sample = project_code[file_path][:1000] + "..." if len(project_code[file_path]) > 1000 else project_code[file_path]
            main_content += content_sample + "\n"
        
        # 使用LLM生成项目概述
        prompt = f"""你是一位专业的软件文档编写专家。请根据以下C项目的信息，生成一份项目概述文档。

项目名称: {os.path.basename(project_path)}
项目文件结构:
{files_summary_str}

以下是项目中的一些关键文件内容示例:
{main_content}

请提供以下内容:
1. 项目简介：项目的主要功能和用途
2. 项目背景：该项目解决的问题或满足的需求
3. 技术栈：项目使用的主要技术和库
4. 项目特点：项目的主要特点和优势

请用markdown格式编写。不要在回复中包含"根据提供的信息"或类似的提示词。直接开始编写文档内容。
"""

        response = self._get_completion(prompt)
        return response
    
    def _generate_architecture_docs(self, project_path, project_code):
        """生成架构设计文档"""
        print("正在生成架构设计文档...")
        
        # 准备所有文件的依赖关系分析
        dependencies = {}
        for file_path, content in project_code.items():
            rel_path = os.path.relpath(file_path, project_path)
            includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
            dependencies[rel_path] = includes
        
        # 转换为可读格式
        deps_str = ""
        for file, includes in dependencies.items():
            if includes:
                deps_str += f"{file} 依赖: {', '.join(includes)}\n"
        
        # 使用LLM生成架构设计文档
        prompt = f"""你是一位专业的软件架构师。请根据以下C项目的文件依赖关系，生成一份架构设计文档。

项目名称: {os.path.basename(project_path)}

文件依赖关系:
{deps_str}

请提供以下内容:
1. 架构概述：描述项目的整体架构设计
2. 组件划分：主要组件及其职责
3. 模块关系：模块之间的依赖关系
4. 数据流：系统中的主要数据流向

请用markdown格式编写，必要时可以使用ASCII图表示架构关系。不要在回复中包含"根据提供的信息"或类似的提示词。直接开始编写文档内容。
"""

        response = self._get_completion(prompt)
        return response
    
    def _generate_modules_docs(self, project_path, c_files, h_files):
        """生成模块说明文档"""
        print("正在生成模块说明文档...")
        
        # 根据目录结构分析模块
        modules = {}
        all_files = c_files + h_files
        
        for file_path in all_files:
            # 获取相对于项目根目录的路径
            rel_path = os.path.relpath(file_path, project_path)
            
            # 获取目录部分
            dir_path = os.path.dirname(rel_path)
            
            if dir_path not in modules:
                modules[dir_path] = []
            
            modules[dir_path].append(os.path.basename(file_path))
        
        # 将模块信息转换为字符串
        modules_str = ""
        for dir_path, files in modules.items():
            if dir_path == '.':
                modules_str += f"根目录: {', '.join(files)}\n"
            else:
                modules_str += f"{dir_path}: {', '.join(files)}\n"
        
        # 使用LLM生成模块说明文档
        prompt = f"""你是一位专业的软件文档编写专家。请根据以下C项目的模块结构，生成一份模块说明文档。

项目名称: {os.path.basename(project_path)}

模块结构:
{modules_str}

请提供以下内容:
1. 模块概述：项目的模块划分思路
2. 各模块功能：每个模块的主要功能和职责
3. 模块间关系：模块之间的交互和依赖关系

请用markdown格式编写。不要在回复中包含"根据提供的信息"或类似的提示词。直接开始编写文档内容。
"""

        response = self._get_completion(prompt)
        return response
    
    def _generate_data_structures_docs(self, project_code):
        """生成数据结构说明文档"""
        print("正在生成数据结构说明文档...")
        
        # 提取所有结构体和枚举定义
        struct_enum_definitions = []
        
        for file_path, content in project_code.items():
            # 提取结构体定义
            structs = re.findall(r'typedef\s+struct\s+\w*\s*{[^}]*}\s*(\w+);', content, re.DOTALL)
            structs += re.findall(r'struct\s+(\w+)\s*{[^}]*}', content, re.DOTALL)
            
            # 提取枚举定义
            enums = re.findall(r'typedef\s+enum\s+\w*\s*{[^}]*}\s*(\w+);', content, re.DOTALL)
            enums += re.findall(r'enum\s+(\w+)\s*{[^}]*}', content, re.DOTALL)
            
            if structs or enums:
                file_name = os.path.basename(file_path)
                struct_enum_definitions.append(f"文件 {file_name}:")
                
                if structs:
                    struct_enum_definitions.append("  结构体: " + ", ".join(structs))
                
                if enums:
                    struct_enum_definitions.append("  枚举: " + ", ".join(enums))
        
        # 寻找有代表性的结构体定义
        detailed_structs = []
        for file_path, content in project_code.items():
            # 详细提取几个结构体定义
            struct_matches = re.finditer(r'(typedef\s+struct\s+\w*\s*{[^}]*}\s*\w+;|struct\s+\w+\s*{[^}]*})', content, re.DOTALL)
            
            for i, match in enumerate(struct_matches):
                if i >= 3:  # 每个文件最多提取3个结构体
                    break
                detailed_structs.append(match.group(1).strip())
        
        # 构建数据结构概览
        data_structures_summary = "\n".join(struct_enum_definitions)
        
        # 添加详细结构体定义样本
        data_structures_samples = "\n\n详细结构体定义样本:\n" + "\n\n".join(detailed_structs[:5]) if detailed_structs else ""
        
        # 使用LLM生成数据结构说明文档
        prompt = f"""你是一位专业的软件文档编写专家。请根据以下C项目的数据结构定义，生成一份数据结构说明文档。

数据结构概览:
{data_structures_summary}

{data_structures_samples}

请提供以下内容:
1. 数据结构概述：项目中主要数据结构的设计思路
2. 关键结构体：关键结构体的功能和字段说明
3. 枚举类型：主要枚举类型及其用途
4. 数据关系：主要数据结构之间的关系

请用markdown格式编写。不要在回复中包含"根据提供的信息"或类似的提示词。直接开始编写文档内容。对于示例中没有的结构体，不要编造内容。
"""

        response = self._get_completion(prompt)
        return response
    
    def _generate_api_reference(self, project_code):
        """生成API参考文档"""
        print("正在生成API参考文档...")
        
        # 提取函数声明
        function_declarations = []
        
        for file_path, content in project_code.items():
            file_name = os.path.basename(file_path)
            
            # 寻找函数声明(这只是一个简单的方法，不能捕获所有类型的函数声明)
            declarations = re.findall(r'(\w+\s+\w+\s*\([^;{]*\))\s*[;{]', content)
            
            if declarations:
                file_functions = []
                for decl in declarations:
                    # 跳过一些常见的非函数模式
                    if decl.startswith('return ') or decl.startswith('if ') or decl.startswith('while ') or decl.startswith('for '):
                        continue
                    file_functions.append(decl)
                
                if file_functions:
                    function_declarations.append(f"文件 {file_name}:")
                    for func in file_functions[:10]:  # 每个文件最多显示10个函数
                        function_declarations.append(f"  {func}")
        
        # 构建API概览
        api_summary = "\n".join(function_declarations)
        
        # 使用LLM生成API参考文档
        prompt = f"""你是一位专业的软件文档编写专家。请根据以下C项目的函数声明，生成一份API参考文档。

API函数概览:
{api_summary}

请提供以下内容:
1. API分类：将函数按功能或模块分类
2. 关键函数：关键函数的详细说明，包括：
   - 函数名称
   - 参数说明
   - 返回值
   - 功能描述
   - 使用注意事项
3. 调用流程：主要API的调用流程和顺序

请用markdown格式编写，并使用表格等方式提高可读性。不要在回复中包含"根据提供的信息"或类似的提示词。直接开始编写文档内容。对于示例中没有的函数，不要编造内容。
"""

        response = self._get_completion(prompt)
        return response
    
    def _compile_documentation(self, project_path, overview, architecture, modules, data_structures, api_reference):
        """
        编译所有文档部分为一个完整的项目文档
        
        Args:
            project_path: 项目路径
            overview: 项目概述
            architecture: 架构设计
            modules: 模块说明
            data_structures: 数据结构说明
            api_reference: API参考
            
        Returns:
            完整的项目文档字符串
        """
        project_name = os.path.basename(project_path)
        
        documentation = f"""# {project_name} 项目文档

## 目录
- [项目概述](#项目概述)
- [架构设计](#架构设计)
- [模块说明](#模块说明)
- [数据结构](#数据结构)
- [API参考](#api参考)

## 项目概述
{overview}

## 架构设计
{architecture}

## 模块说明
{modules}

## 数据结构
{data_structures}

## API参考
{api_reference}

---
*此文档由 CProjectDocGenerator 自动生成 - {time.strftime("%Y-%m-%d %H:%M")}*
"""
        
        return documentation
    
    def _get_completion(self, prompt):
        """
        使用LLM获取文本生成（支持流式处理）
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        try:
            # 启用流式响应
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的软件文档专家，擅长将C语言代码转换为清晰的文档。请以专业、清晰的风格编写文档。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True  # 启用流式处理
            )
            
            # 收集所有响应片段
            content = ""
            print("接收文档生成流：", end="", flush=True)
            
            for chunk in response_stream:
                if hasattr(chunk.choices[0].delta, 'content'):
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content:
                        content += chunk_content
                        # 打印进度指示器
                        print(".", end="", flush=True)
            
            print(" 完成")
            return content
            
        except Exception as e:
            print(f"API调用出错: {str(e)}")
            return f"*内容生成失败: {str(e)}*"
    
    def save_documentation(self, documentation, output_path):
        """
        将生成的文档保存到文件
        
        Args:
            documentation: 文档内容
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            print(f"文档已保存到: {output_path}")
        except Exception as e:
            print(f"保存文档时出错: {str(e)}")


class CFileDocGenerator:
    """
    C文件文档生成器
    
    该工具可以为单个C文件生成详细的文档说明，并将文档保存为同名的md文件
    """
    
    def __init__(self, api_key=None, base_url=None, model="qwq-32b"):
        """
        初始化文档生成器
        
        Args:
            api_key: API密钥
            base_url: API基础URL (如果使用非默认端点)
            model: 要使用的模型名称
        """
        self.model = model
        
        # 初始化OpenAI客户端
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)
    
    def generate_file_documentation(self, file_path, include_related_files=False, project_path=None):
        """
        为单个C文件生成文档
        
        Args:
            file_path: 要生成文档的C文件路径
            include_related_files: 是否包含相关文件的信息（如对应的头文件）
            project_path: 项目根目录路径，用于确定相关文件
            
        Returns:
            生成的文件文档字符串
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not (file_path.endswith('.c') or file_path.endswith('.h')):
            raise ValueError(f"不支持的文件类型: {file_path}")
        
        print(f"开始分析文件: {file_path}")
        
        # 读取主文件内容
        file_content = self._read_file(file_path)
        
        # 尝试找到关联文件（如果需要）
        related_files_content = {}
        if include_related_files:
            related_files = self._find_related_files(file_path, project_path)
            
            for related_file in related_files:
                if os.path.exists(related_file):
                    related_files_content[related_file] = self._read_file(related_file)
        
        # 生成文件文档
        documentation = self._generate_documentation_for_file(file_path, file_content, related_files_content)
        
        return documentation
    
    def _read_file(self, file_path):
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # 尝试其他编码
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except:
                print(f"警告: 无法读取文件 {file_path}")
                return "/* 无法读取文件内容 */"
    
    def _find_related_files(self, file_path, project_path=None):
        """查找与文件相关的其他文件（如.c文件对应的.h文件）"""
        related_files = []
        
        basename = os.path.basename(file_path)
        name, ext = os.path.splitext(basename)
        
        # 确定查找目录
        search_dirs = []
        if project_path:
            search_dirs.append(project_path)
        
        file_dir = os.path.dirname(file_path)
        search_dirs.append(file_dir)
        
        # 如果是.c文件，查找对应的.h文件
        if ext == '.c':
            for search_dir in search_dirs:
                h_file = os.path.join(search_dir, f"{name}.h")
                if os.path.exists(h_file):
                    related_files.append(h_file)
                    break
        
        # 如果是.h文件，查找对应的.c文件
        elif ext == '.h':
            for search_dir in search_dirs:
                c_file = os.path.join(search_dir, f"{name}.c")
                if os.path.exists(c_file):
                    related_files.append(c_file)
                    break
        
        return related_files
    
    def _generate_documentation_for_file(self, file_path, file_content, related_files_content=None):
        """为单个文件生成文档"""
        file_name = os.path.basename(file_path)
        file_type = "头文件" if file_path.endswith('.h') else "实现文件"
        
        # 提取文件中的函数
        functions = self._extract_functions(file_content)
        function_str = "\n".join([f"- {func}" for func in functions])
        
        # 提取结构体和枚举
        structs = self._extract_structs(file_content)
        struct_str = "\n".join([f"- {struct}" for struct in structs])
        
        # 提取包含的头文件
        includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', file_content)
        include_str = "\n".join([f"- {inc}" for inc in includes])
        
        # 准备相关文件信息
        related_files_str = ""
        if related_files_content:
            related_files_str = "\n\n相关文件:\n"
            for rel_path, _ in related_files_content.items():
                related_files_str += f"- {os.path.basename(rel_path)}\n"
        
        # 使用LLM生成文件文档
        prompt = f"""你是一位专业的软件文档编写专家，擅长为C语言代码编写清晰详细的文档。请为以下C语言文件生成详细文档。

文件名: {file_name}
文件类型: {file_type}

引用的头文件:
{include_str if include_str else "无"}

定义的结构体/枚举:
{struct_str if struct_str else "无"}

函数列表:
{function_str if function_str else "无"}

{related_files_str}

文件内容:
```c
{file_content}
```

请提供以下内容:
1. 文件概述：该文件的主要功能和作用
2. 函数说明：分析文件中的每个函数，说明其功能、参数、返回值和注意事项
3. 数据结构：解释重要的结构体、枚举和类型定义
4. 使用示例：提供如何使用该文件中主要功能的示例（如适用）
5. 依赖关系：说明该文件依赖哪些其他文件或被哪些文件依赖

请使用Markdown格式编写，保持清晰、专业的风格。不要在回复中包含"根据提供的信息"或类似的提示词，直接开始编写文档内容。
"""

        # 调用API生成文档
        documentation = self._get_completion(prompt)
        
        # 添加标题和页脚
        file_basename = os.path.splitext(os.path.basename(file_path))[0]
        full_documentation = f"# {file_basename} 文件文档\n\n{documentation}\n\n---\n*此文档由 CFileDocGenerator 自动生成 - {time.strftime('%Y-%m-%d %H:%M')}*"
        
        return full_documentation
    
    def _extract_functions(self, content):
        """提取文件中的函数声明/定义"""
        # 这只是一个简单的提取方法，可能无法捕获所有函数
        functions = re.findall(r'(\w+\s+\w+\s*\([^;{]*\))\s*[;{]', content)
        
        # 过滤掉一些常见的非函数模式
        filtered_functions = []
        for func in functions:
            if not (func.startswith('return ') or func.startswith('if ') or 
                    func.startswith('while ') or func.startswith('for ')):
                filtered_functions.append(func)
        
        return filtered_functions
    
    def _extract_structs(self, content):
        """提取文件中的结构体和枚举定义"""
        # 提取结构体定义
        structs = re.findall(r'typedef\s+struct\s+\w*\s*{[^}]*}\s*(\w+);', content, re.DOTALL)
        structs += re.findall(r'struct\s+(\w+)\s*{[^}]*}', content, re.DOTALL)
        
        # 提取枚举定义
        enums = re.findall(r'typedef\s+enum\s+\w*\s*{[^}]*}\s*(\w+);', content, re.DOTALL)
        enums += re.findall(r'enum\s+(\w+)\s*{[^}]*}', content, re.DOTALL)
        
        return structs + enums
    
    def _get_completion(self, prompt):
        """
        使用LLM获取文本生成（支持流式处理）
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        try:
            # 启用流式响应
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的软件文档专家，擅长将C语言代码转换为清晰的文档。请以专业、清晰的风格编写文档。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True  # 启用流式处理
            )
            
            # 收集所有响应片段
            content = ""
            print("接收文档生成流：", end="", flush=True)
            
            for chunk in response_stream:
                if hasattr(chunk.choices[0].delta, 'content'):
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content:
                        content += chunk_content
                        # 打印进度指示器
                        print(".", end="", flush=True)
            
            print(" 完成")
            return content
            
        except Exception as e:
            print(f"API调用出错: {str(e)}")
            return f"*内容生成失败: {str(e)}*"

    def save_documentation(self, file_path, documentation, output_dir):
        """
        将生成的文档保存到指定的输出目录，保持与原文件相似的命名
        
        Args:
            file_path: 源代码文件路径
            documentation: 文档内容
            output_dir: 文档输出目录路径
            
        Returns:
            保存的文档路径或None（如果保存失败）
        """
        # 保留原始相对路径结构
        rel_dir = os.path.relpath(os.path.dirname(file_path), os.path.dirname(output_dir))
        target_dir = os.path.join(output_dir, rel_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取文件基本信息
        file_basename = os.path.splitext(os.path.basename(file_path))[0]
        file_ext = os.path.splitext(file_path)[1]
        
        # 创建包含文件类型的Markdown文件名
        if file_ext == '.h':
            output_filename = f"{file_basename}_header.md"
        elif file_ext == '.c':
            output_filename = f"{file_basename}_impl.md"
        else:
            # 对于其他类型的文件，使用扩展名作为标识符（去掉前面的点）
            ext_identifier = file_ext[1:] if file_ext.startswith('.') else file_ext
            output_filename = f"{file_basename}_{ext_identifier}.md"
        
        # 完整输出路径
        output_path = os.path.join(target_dir, output_filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            print(f"文档已保存到: {output_path}")
            return output_path
        except Exception as e:
            print(f"保存文档时出错: {str(e)}")
            return None


def process_directory_with_custom_output(directory_path, output_dir, api_key=None, base_url=None, model="qwq-32b", include_related=False):
    """
    处理目录中的所有C文件，为每个文件生成文档并保存到指定的输出目录
    
    Args:
        directory_path: 包含C文件的目录路径
        output_dir: 文档输出目录路径
        api_key: API密钥
        base_url: API基础URL
        model: 模型名称
        include_related: 是否包含相关文件信息
        
    Returns:
        生成的文档文件列表
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"目录不存在: {directory_path}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"文档将保存到: {output_dir}")
    
    # 初始化文档生成器
    doc_generator = CFileDocGenerator(api_key=api_key, base_url=base_url, model=model)
    
    # 扫描目录
    c_files = []
    h_files = []
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.c'):
                c_files.append(file_path)
            elif file.endswith('.h'):
                h_files.append(file_path)
    
    print(f"发现 {len(c_files)} 个C文件和 {len(h_files)} 个头文件")
    
    # 为每个文件生成文档
    generated_docs = []
    all_files = c_files + h_files
    
    for idx, file_path in enumerate(all_files):
        print(f"\n[{idx+1}/{len(all_files)}] 处理文件: {file_path}")
        
        try:
            documentation = doc_generator.generate_file_documentation(
                file_path, 
                include_related_files=include_related,
                project_path=directory_path
            )
            
            output_path = doc_generator.save_documentation(file_path, documentation, output_dir)
            
            if output_path:
                generated_docs.append(output_path)
            
            # 避免API限制
            if idx < len(all_files) - 1:
                print("等待1秒以避免API速率限制...")
                time.sleep(1)
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    print(f"\n文档生成完成，共生成 {len(generated_docs)} 个文档文件")
    print(f"所有文档已保存到: {output_dir} 目录下")
    return generated_docs


def save_single_file_documentation(file_path, documentation, output_dir):
    """
    将单个文件的文档保存到指定的输出目录
    
    Args:
        file_path: 源代码文件路径
        documentation: 文档内容
        output_dir: 文档输出目录路径
    """
    doc_generator = CFileDocGenerator()
    doc_generator.save_documentation(file_path, documentation, output_dir)


def main():
    parser = argparse.ArgumentParser(description='C文件文档生成工具')
    parser.add_argument('--path', type=str, default="./CODE_SRC/src2", help='要处理的C文件路径或目录路径')
    parser.add_argument('--output', type=str, default="./document", help='文档输出目录路径')
    parser.add_argument('--api_key', type=str, default="", help='API密钥')
    parser.add_argument('--base_url', type=str, default="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        help='API基础URL')
    parser.add_argument('--model', type=str, default='qwq-32b', help='要使用的模型')
    parser.add_argument('--include-related', action='store_true', help='包含相关文件信息')
    
    args = parser.parse_args()
    
    path = args.path
    output_dir = args.output
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 检查路径是文件还是目录
        if os.path.isfile(path):
            # 处理单个文件
            doc_generator = CFileDocGenerator(
                api_key=args.api_key,
                base_url=args.base_url,
                model=args.model
            )
            
            documentation = doc_generator.generate_file_documentation(
                path, 
                include_related_files=args.include_related
            )
            
            # 使用指定的输出目录保存文档
            save_single_file_documentation(path, documentation, output_dir)
            
        elif os.path.isdir(path):
            # 处理整个目录
            process_directory_with_custom_output(
                path,
                output_dir, 
                api_key=args.api_key, 
                base_url=args.base_url, 
                model=args.model,
                include_related=args.include_related
            )
            
        else:
            print(f"错误: 无效的路径 {path}")
            return 1
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)




