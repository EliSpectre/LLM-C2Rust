# window_management 文件文档

# 文件概述

`window_management.c` 文件主要负责银行窗口队列的管理，包括初始化窗口队列、客户入队、客户出队、查找最短等待时间窗口、打印特定队列和打印所有队列等功能。该文件通过一系列函数实现对银行窗口队列的高效管理，适用于模拟银行排队系统。

# 函数说明

## `void InitQueue(int WindowsNum)`

### 功能
初始化指定数量的银行窗口队列。

### 参数
- `WindowsNum`：整数，表示需要初始化的窗口数量。

### 返回值
无。

### 注意事项
- 该函数会动态分配内存以存储窗口队列，使用后需确保适当释放内存。

## `void EnQueue(int OccurTime, int Duration, int window)`

### 功能
将客户信息添加到指定窗口的队列中。

### 参数
- `OccurTime`：整数，表示客户到达的时间。
- `Duration`：整数，表示客户处理业务所需的时间。
- `window`：整数，表示客户选择的窗口编号。

### 返回值
无。

### 注意事项
- 如果指定窗口的队列已满，会打印提示信息。

## `void DeQueue(int window, Person *person_ptr)`

### 功能
从指定窗口的队列中移除最先到达的客户，并获取该客户的信息。

### 参数
- `window`：整数，表示窗口编号。
- `person_ptr`：指向`Person`结构体的指针，用于存储移除的客户信息。

### 返回值
无。

### 注意事项
- 如果指定窗口的队列为空，会打印提示信息。

## `int Fastest_Window()`

### 功能
查找当前等待时间最短的窗口。

### 参数
无。

### 返回值
- 整数，表示等待时间最短的窗口编号。

### 注意事项
- 该函数会动态分配内存以计算每个窗口的剩余处理时间，使用后需确保适当释放内存。

## `void PrintQueue(int window)`

### 功能
打印指定窗口的队列信息。

### 参数
- `window`：整数，表示窗口编号。

### 返回值
无。

### 注意事项
- 该函数会打印队列中所有客户的信息。

## `void PrintAllQueue(int WindowsNum)`

### 功能
打印所有窗口的队列信息。

### 参数
- `WindowsNum`：整数，表示窗口数量。

### 返回值
无。

### 注意事项
- 该函数会调用`PrintQueue`函数来打印每个窗口的队列信息。

# 数据结构

该文件中未定义结构体和枚举，但使用了外部定义的`Window_Queue`和`Person`结构体。以下是这些结构体的假设定义：

```c
typedef struct {
    int ArrivalTime; // 客户到达时间
    int Duration;    // 客户处理业务所需时间
    int num;        // 客户编号
} Person;

typedef struct {
    Person customer[MAX_CUSTOMERS]; // 客户数组
    int front;                      // 队列头指针
    int rear;                       // 队列尾指针
} Window_Queue;
```

# 使用示例

以下是一个简单的示例，展示如何使用`window_management.c`中的主要功能：

```c
#include "../include/window_management.h"

int main() {
    int WindowsNum = 3;
    InitQueue(WindowsNum);

    EnQueue(10, 5, 1);
    EnQueue(12, 3, 1);
    EnQueue(15, 4, 2);

    Person person;
    DeQueue(1, &person);
    printf("离开的客户编号: %d\n", person.num);

    int fastestWindow = Fastest_Window();
    printf("最短等待时间的窗口: %d\n", fastestWindow);

    PrintAllQueue(WindowsNum);

    return 0;
}
```

# 依赖关系

- **依赖文件**：`../include/window_management.h`，该头文件定义了所需的结构体、常量和函数声明。
- **被依赖文件**：无明确指出，但通常会被主程序文件或其他模块文件引用以实现银行排队系统的完整功能。

确保在使用该文件前已正确包含并初始化所有依赖项。

---
*此文档由 CFileDocGenerator 自动生成 - 2025-04-07 17:21*