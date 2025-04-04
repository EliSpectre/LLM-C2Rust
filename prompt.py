import os
import re

class C2RustPromptGenerator:
    """
    C语言到Rust的转换Prompt生成器
    
    该类用于为C代码文件生成专门的转换提示，帮助AI将C代码转换为Rust代码。
    可以处理不同类型的C文件（主程序、头文件、实现文件等）。
    """
    
    def __init__(self, project_path=None, document_path=None):
        """
        初始化Prompt生成器
        
        Args:
            project_path: C项目的根目录路径，用于自动发现文件
            document_path: 文档目录路径，用于读取文档文件
        """
        self.project_path = project_path
        self.document_path = document_path
        self.file_info = {}
        self.special_files = {
            "main.c": "主程序文件",
            "main.h": "主程序头文件",
        }
        
        # 如果提供了项目路径，自动扫描项目文件
        if project_path:
            self.scan_project()
    
    def scan_project(self):
        """扫描项目目录，识别C文件"""
        if not os.path.exists(self.project_path):
            raise FileNotFoundError(f"项目路径不存在: {self.project_path}")
        
        c_files = []
        h_files = []
        
        # 递归遍历目录
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.c'):
                    c_files.append(os.path.join(root, file))
                elif file.endswith('.h'):
                    h_files.append(os.path.join(root, file))
        
        # 存储文件信息
        for h_file in h_files:
            basename = os.path.basename(h_file)
            self.file_info[basename] = {
                "path": h_file,
                "type": "header",
                "module_name": os.path.splitext(basename)[0]
            }
            
        for c_file in c_files:
            basename = os.path.basename(c_file)
            # 确定文件类型
            if basename == "main.c":
                file_type = "main"
            else:
                file_type = "implementation"
                
            self.file_info[basename] = {
                "path": c_file,
                "type": file_type,
                "module_name": os.path.splitext(basename)[0],
                "associated_header": self._find_associated_header(basename, h_files)
            }
        
        print(f"扫描完成: 发现 {len(c_files)} 个C文件和 {len(h_files)} 个头文件")
        
    def _find_associated_header(self, c_file, h_files):
        """查找与C文件关联的头文件"""
        base_name = os.path.splitext(c_file)[0]
        for h_file in h_files:
            h_basename = os.path.basename(h_file)
            if os.path.splitext(h_basename)[0] == base_name:
                return h_basename
        return None
    
    def read_file_content(self, file_path):
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容字符串，如果读取失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {str(e)}")
            return None
    
    def find_document_file(self, filename):
        """
        在文档目录中查找与源文件对应的文档文件
        
        Args:
            filename: 源文件名(如 main.c)
            
        Returns:
            文档文件路径，如果不存在则返回None
        """
        if not self.document_path or not os.path.exists(self.document_path):
            return None
            
        base_name = os.path.splitext(os.path.basename(filename))[0]
        ext = os.path.splitext(os.path.basename(filename))[1]
        
        # 可能的文档文件名模式
        possible_names = []
        if ext == '.c':
            possible_names = [f"{base_name}_impl.md", f"{base_name}.md"]
        elif ext == '.h':
            possible_names = [f"{base_name}_header.md", f"{base_name}.md"]
        else:
            possible_names = [f"{base_name}_{ext[1:]}.md", f"{base_name}.md"]
            
        # 首先尝试在主文档目录查找
        for doc_name in possible_names:
            doc_path = os.path.join(self.document_path, doc_name)
            if os.path.exists(doc_path):
                return doc_path
                
        # 如果在根目录没找到，递归查找子目录
        for root, _, files in os.walk(self.document_path):
            for file in files:
                if file in possible_names:
                    return os.path.join(root, file)
                    
        return None
    
    def get_file_prompt(self, filename, all_filenames=None, include_content=True):
        """
        为特定文件生成转换提示，可选择包含文件内容和相关文档
        
        Args:
            filename: 要转换的C文件名或路径
            all_filenames: 所有相关文件名列表，用于提供上下文
            include_content: 是否包含文件内容(True)和文档内容(如果有)
            
        Returns:
            针对该文件的转换提示字符串
        """
        if all_filenames is None:
            all_filenames = list(self.file_info.keys()) if self.file_info else []
        
        # 确定文件类型和名称
        if os.path.isabs(filename):
            file_basename = os.path.basename(filename)
        else:
            file_basename = filename
            if self.project_path and not os.path.exists(filename):
                filename = os.path.join(self.project_path, filename)
                
        module_name = os.path.splitext(file_basename)[0]
        file_type = "unknown"
        
        if file_basename in self.file_info:
            file_type = self.file_info[file_basename]["type"]
        elif file_basename.endswith(".c"):
            if file_basename == "main.c":
                file_type = "main"
            else:
                file_type = "implementation"
        elif file_basename.endswith(".h"):
            file_type = "header"
        
        # 基础提示部分
        base_prompt = f"""你是一位精通 C 和 Rust 的专家。请将以下 C 代码转换为地道的 Rust 代码。
确保遵循 Rust 的所有最佳实践、内存安全原则和惯用表达方式。

当前要转换的文件是: {file_basename}
"""
        
        if all_filenames:
            base_prompt += f"\n项目中的相关文件: {', '.join([os.path.basename(f) if os.path.isabs(f) else f for f in all_filenames])}\n"
            
        # 根据不同文件类型提供特定的指导
        if file_type == "main":
            base_prompt += self._get_main_file_prompt(module_name)
        elif file_type == "header":
            base_prompt += self._get_header_file_prompt(module_name)
        elif file_type == "implementation":
            base_prompt += self._get_implementation_file_prompt(module_name)
        else:
            base_prompt += self._get_generic_file_prompt(module_name)
        
        # 如果需要，包含文件内容
        if include_content and os.path.exists(filename):
            content = self.read_file_content(filename)
            if content:
                base_prompt += f"\n【源代码内容】\n```c\n{content}\n```\n"
        
        # 如果设置了文档路径，尝试获取并包含文档内容
        if self.document_path:
            doc_path = self.find_document_file(file_basename)
            if doc_path:
                doc_content = self.read_file_content(doc_path)
                if doc_content:
                    base_prompt += f"\n【文档说明】\n{doc_content}\n"
        
        # 通用的输出格式要求
        base_prompt += self._get_output_format_prompt()
        
        return base_prompt
    
    def _get_main_file_prompt(self, module_name):
        """生成主程序文件转换提示"""
        return """
【文件特性】
- 这是主程序文件，包含程序的入口点main函数
- 在Rust中应该被转换为main.rs文件

【转换要求】
1. 必须包含fn main()函数作为程序入口点
2. 如果原C代码引用了其他模块中的函数:
   - 在文件顶部使用mod语句引入模块: mod module_name;
   - 使用正确的模块路径调用这些函数，例如module_name::function_name()
3. 不要在main.rs中重新实现这些外部函数的逻辑，只需引用它们
4. 不要在生成的代码中包含"mod module_name {"这样的模块实现，只使用"mod module_name;"引入外部模块
5. 确保main.rs中不包含其他模块中已实现的函数定义

【输出要求】
- 只输出main.rs文件的内容，不要包含其他模块的实现
"""
    
    def _get_header_file_prompt(self, module_name):
        """生成头文件转换提示"""
        return f"""
【文件特性】
- 这是C语言的头文件，包含函数声明和可能的类型定义
- 在Rust中没有头文件的概念，应转换为模块定义文件

【转换要求】
1. 将函数声明转换为完整的函数定义，使用pub关键字表示公开可见性
2. 将类型定义（如结构体、枚举等）转换为Rust等价结构，同样使用pub标记
3. 不应包含main函数
4. 不应包含"mod {module_name};"语句或任何其他模块引用
5. 不要嵌套定义模块，所有函数和类型应在顶层定义

【输出要求】
- 转换成功时，输出{module_name}.rs文件的完整内容
- 如果函数实现已在对应的.c文件中完成，此文件也需要转换，不要跳过
- 需要特别注意，认真思考当前的.h文件是否需要转换
- 如果当前文件不需要单独转换，请只输出: Skip this file
"""
    
    def _get_implementation_file_prompt(self, module_name):
        """生成实现文件转换提示"""
        return f"""
【文件特性】
- 这是C语言的函数实现文件，实现了对应头文件中声明的函数
- 在Rust中应该被合并到模块定义中

【转换要求】
1. 所有需要被外部访问的函数必须使用pub关键字
2. 内部辅助函数可以不使用pub关键字
3. 不应包含main函数
4. 不应包含"mod {module_name};"语句或任何其他模块引用
5. 实现对应头文件中声明的所有函数

【输出要求】
- 转换成功时，输出包含所有函数实现的{module_name}.rs文件的完整内容
- 如果相关头文件(.h)中有类型定义或函数声明，请确保在这里实现它们
"""
    
    def _get_generic_file_prompt(self, module_name):
        """生成通用文件转换提示"""
        return f"""
【文件特性】
- 这是一个C语言文件，需要转换为相应的Rust模块

【转换要求】
1. 分析文件内容，确定其作用（如实用工具、特定功能组件等）
2. 将所有函数和类型转换为Rust等价实现
3. 使用pub关键字标记需要对外暴露的函数和类型
4. 不应包含"mod {module_name};"语句或其他模块引用
5. 确保生成的代码符合Rust的组织方式和惯用法

【输出要求】
- 转换成功时，输出相应的Rust模块代码
- 如果无法确定文件的明确用途，请保持原有的组织结构
"""
    
    def _get_output_format_prompt(self):
        """获取通用的输出格式要求"""
        return """
【输出格式】
请使用以下格式提供你的转换结果:

1. 首先简要分析C代码的结构和功能
2. 然后使用<rust>标记后换行提供完整的Rust实现
3. 不要在Rust代码中包含额外的解释性注释
4. 不要使用Markdown代码块格式(```或```)

例如:
这个C文件实现了计算最大值和最小值的函数。

<rust>
pub fn max(a: i32, b: i32) -> i32 {
    if a > b { a } else { b }
}

pub fn min(a: i32, b: i32) -> i32 {
    if a < b { a } else { b }
}
</rust>

如果当前文件不需要单独转换，请只输出: Skip this file
"""
    
    def generate_prompts_for_directory(self, directory_path):
        """
        为目录中的所有C文件生成转换提示
        
        Args:
            directory_path: 包含C文件的目录路径
            
        Returns:
            包含文件名到提示的字典映射
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"目录不存在: {directory_path}")
        
        prompts = {}
        all_files = []
        
        # 收集所有C和头文件
        for file in os.listdir(directory_path):
            if file.endswith('.c') or file.endswith('.h'):
                all_files.append(file)
        
        # 为每个文件生成提示
        for file in all_files:
            prompts[file] = self.get_file_prompt(file, all_files)
            
        return prompts


def get_system_prompt(filename, all_files=None, document_path=None):
    """根据文件类型生成对应的系统提示
    
    Args:
        filename: 要转换的C文件名
        all_files: 所有相关文件名列表，用于提供上下文
        document_path: 文档目录路径，用于读取文档文件
    
    Returns:
        针对该文件的转换提示字符串
    """
    # 创建Prompt生成器
    generator = C2RustPromptGenerator(document_path=document_path)
    
    if all_files is None:
        all_files = []
        # 尝试推断相关文件
        if filename.endswith(".c"):
            base_name = os.path.splitext(filename)[0]
            possible_header = f"{base_name}.h"
            if os.path.exists(possible_header):
                all_files.append(possible_header)
    
    # 加入当前文件
    if filename not in all_files:
        all_files.append(filename)
    
    # 生成文件的提示
    return generator.get_file_prompt(filename, all_files)


# 使用示例
if __name__ == "__main__":
    # 设置路径
    project_path = "./CODE_SRC/src1"
    document_path = "./document"
    
    # 创建带文档路径的Prompt生成器
    generator = C2RustPromptGenerator(project_path=project_path, document_path=document_path)
    
    # 为特定文件生成提示
    # main_prompt = generator.get_file_prompt("main.c", ["main.c", "math.h", "math.c"])
    # print("===== main.c的转换提示 =====")
    # print(main_prompt)
    
    # 也可以使用辅助函数
    math_h_prompt = get_system_prompt("main.c", ["main.c", "math.h", "math.c"], document_path)
    print("\n===== main.c的转换提示 =====")
    print(math_h_prompt)
    
    # 为整个目录生成提示
    # directory_prompts = generator.generate_prompts_for_directory("./CODE_SRC/src1")
    # print(f"为{len(directory_prompts)}个文件生成了转换提示")