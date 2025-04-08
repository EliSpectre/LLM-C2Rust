# history_management 文件文档

# 文件概述

`history_management.c` 文件主要负责管理和记录银行窗口的历史业务数据。该文件提供了初始化窗口历史记录、插入历史记录以及打印特定窗口历史记录的功能。通过这些功能，可以有效地追踪和分析每个窗口的业务处理情况。

# 函数说明

## `void InitHistory(int WindowsNum)`

### 功能
初始化指定数量的窗口历史记录。

### 参数
- `WindowsNum`：整数，表示需要初始化的窗口数量。

### 返回值
无。

### 注意事项
- 该函数会为每个窗口分配内存，用于存储历史记录。
- 调用该函数前应确保 `WindowsNum` 是一个有效的正整数。

## `void HistoryInsert(int window, Person people, int occurtime)`

### 功能
向指定窗口的历史记录中插入一条新的记录。

### 参数
- `window`：整数，表示窗口编号。
- `people`：`Person` 结构体，包含客户信息。
- `occurtime`：整数，表示客户离开的时间（以分钟为单位）。

### 返回值
无。

### 注意事项
- `window` 参数应从1开始，内部会自动减1以匹配数组索引。
- 插入操作采用链表的尾部插入法。

## `void PrintHistory(int window)`

### 功能
打印指定窗口的历史记录。

### 参数
- `window`：整数，表示窗口编号。

### 返回值
无。

### 注意事项
- 该函数会打印出窗口的总服务客户数、每位客户的到达时间、办理业务时间和离开时间。
- `window` 参数应从0开始。

# 数据结构

虽然该文件中没有定义新的结构体或枚举，但使用了以下外部定义的结构体：

- `HistoryList`：指向 `History` 结构体的指针，用于存储历史记录的链表。
- `Person`：包含客户信息的结构体，具体定义在 `history_management.h` 中。

# 使用示例

以下是一个简单的示例，展示如何使用 `history_management.c` 中的功能：

```c
#include "../include/history_management.h"

int main() {
    int windowNum = 3;
    Person person1 = {1, 30, 10}; // 假设客户编号为1，到达时间为30分钟，办理业务时间为10分钟
    Person person2 = {2, 45, 15}; // 假设客户编号为2，到达时间为45分钟，办理业务时间为15分钟

    // 初始化窗口历史记录
    InitHistory(windowNum);

    // 插入历史记录
    HistoryInsert(1, person1, 40); // 窗口1，客户1，离开时间40分钟
    HistoryInsert(1, person2, 60); // 窗口1，客户2，离开时间60分钟

    // 打印窗口1的历史记录
    PrintHistory(0);

    return 0;
}
```

# 依赖关系

- **依赖文件**：
  - `../include/history_management.h`：包含历史记录管理相关的结构体定义和函数声明。

- **被依赖文件**：
  - 该文件可能被其他需要使用历史记录管理功能的文件所依赖，例如主程序文件或其他模块文件。

通过以上文档，开发者可以清晰地了解 `history_management.c` 文件的功能和使用方法，便于后续的开发和维护工作。

---
*此文档由 CFileDocGenerator 自动生成 - 2025-04-07 17:20*