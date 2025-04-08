# tools 文件文档

# tools.h 文件文档

## 1. 文件概述  
该头文件提供文件操作相关的实用工具函数，主要功能是通过`getFileSize`函数获取文件大小。它为开发者提供了一种标准化的方式，用于快速获取已打开文件的字节长度，适用于需要文件大小信息的场景（如内存分配、数据校验等）。

---

## 2. 函数说明  

### `long getFileSize(FILE *fp)`  
**功能**  
获取指定文件的大小（以字节为单位）。  

**参数**  
- `FILE *fp`：需要查询的文件指针，必须是已通过`fopen`等函数成功打开的有效指针。  

**返回值**  
- 成功时返回文件大小（字节）的`long`型数值。  
- 失败时返回`-1L`（例如文件未正确打开、无法定位文件末尾等错误）。  

**注意事项**  
1. 调用前需确保`fp`指向有效的已打开文件。  
2. 该函数会临时移动文件指针位置（到文件末尾再返回原位置），若需保持文件指针的当前位置，调用后需通过`fseek`手动恢复。  
3. 若文件过大导致超出`long`类型范围，可能引发溢出问题（需根据系统环境评估）。  

---

## 3. 数据结构  
该文件未定义任何结构体、枚举或类型定义。

---

## 4. 使用示例  

```c
#include "tools.h"
#include <stdio.h>

int main() {
    FILE *fp = fopen("example.txt", "rb");  // 以二进制模式打开文件
    if (fp == NULL) {
        perror("Failed to open file");
        return 1;
    }

    long size = getFileSize(fp);
    if (size == -1L) {
        perror("Failed to get file size");
        fclose(fp);
        return 1;
    }

    printf("File size: %ld bytes\n", size);
    fclose(fp);
    return 0;
}
```

**说明**  
1. 使用`fopen`打开文件后，通过`getFileSize`获取文件大小。  
2. 需检查函数返回值是否为`-1`以处理错误。  
3. 示例中使用二进制模式打开文件，避免文本模式下可能的换行符处理问题。  

---

## 5. 依赖关系  
- **依赖文件**：`stdio.h`（标准输入输出库，用于`FILE`类型和文件操作函数）。  
- **被依赖场景**：其他源文件（如`.c`文件）通过`#include "tools.h"`使用该工具函数时，需确保已正确编译并链接依赖的库。

---
*此文档由 CFileDocGenerator 自动生成 - 2025-04-07 20:01*