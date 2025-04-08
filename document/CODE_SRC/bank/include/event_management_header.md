# event_management 文件文档

# 文件概述

`event_management.h` 是一个头文件，主要用于定义和管理事件队列的相关操作。该文件提供了一系列函数，以便于初始化、插入、删除、排序、获取长度、获取前驱节点以及打印事件链。这些功能对于事件驱动的系统（如银行模拟系统）中的事件管理至关重要。

# 函数说明

## `EventList InitList(EventList L)`

### 功能
初始化一个事件链表。

### 参数
- `EventList L`：待初始化的事件链表。

### 返回值
返回初始化后的空事件链表。

### 注意事项
- 调用此函数前，应确保传入的 `EventList` 指针非空。

## `void EventInsert(EventList L, int Occurtime, int eventType)`

### 功能
在事件链表中插入一个新事件。

### 参数
- `EventList L`：事件链表。
- `int Occurtime`：事件发生的时间。
- `int eventType`：事件的类型。

### 返回值
无。

### 注意事项
- 插入事件时，应确保事件链表已初始化。

## `EventList EventDelete(EventList L)`

### 功能
删除事件链表中的第一个事件。

### 参数
- `EventList L`：事件链表。

### 返回值
返回删除第一个事件后的链表。

### 注意事项
- 删除前应确保链表非空。

## `void Sort_Occurtime(EventList L)`

### 功能
按照事件发生的时间对事件链表进行排序。

### 参数
- `EventList L`：事件链表。

### 返回值
无。

### 注意事项
- 排序前应确保链表已初始化。

## `int Get_Len(EventList L)`

### 功能
获取事件链表的长度。

### 参数
- `EventList L`：事件链表。

### 返回值
返回链表的长度。

### 注意事项
- 链表长度计算前应确保链表已初始化。

## `Event_ptr GetPreNode(EventList L, Event_ptr p)`

### 功能
获取当前事件节点的前驱节点。

### 参数
- `EventList L`：事件链表。
- `Event_ptr p`：当前事件节点。

### 返回值
返回前驱节点的指针。

### 注意事项
- 当前节点应为链表中的有效节点。

## `void PrintList(EventList L)`

### 功能
打印事件链表中的所有事件。

### 参数
- `EventList L`：事件链表。

### 返回值
无。

### 注意事项
- 打印前应确保链表已初始化。

# 数据结构

该文件未直接定义结构体或枚举，但使用了以下类型定义：

- `EventList`：事件链表的类型。
- `Event_ptr`：事件节点的指针类型。

这些类型定义在 `bank_types.h` 文件中定义，具体结构体和枚举的详细信息请参考 `bank_types.h` 文件。

# 使用示例

```c
#include "event_management.h"

int main() {
    EventList L = InitList(L); // 初始化事件链表
    EventInsert(L, 10, 1);     // 插入事件，发生时间10，类型1
    EventInsert(L, 5, 2);      // 插入事件，发生时间5，类型2
    Sort_Occurtime(L);         // 按发生时间排序
    PrintList(L);              // 打印事件链表
    L = EventDelete(L);        // 删除第一个事件
    PrintList(L);              // 再次打印事件链表
    return 0;
}
```

# 依赖关系

- **依赖文件**：
  - `bank_types.h`：定义了 `EventList` 和 `Event_ptr` 等类型。

- **被依赖文件**：
  - 该头文件可能被其他需要事件管理功能的源文件引用，如 `main.c` 或其他模块文件。

确保在使用该头文件前，已正确包含并处理了 `bank_types.h` 文件。

---
*此文档由 CFileDocGenerator 自动生成 - 2025-04-07 17:23*