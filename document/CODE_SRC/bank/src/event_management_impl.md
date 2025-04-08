# event_management 文件文档

# 文件概述

`event_management.c` 文件是事件管理系统的核心实现文件，主要负责事件链表的初始化、插入、删除、排序和打印等操作。该文件通过一系列函数提供对事件链表的高效管理，适用于需要按时间顺序处理事件的场景。

# 函数说明

## `EventList InitList(EventList L)`

### 功能
初始化一个事件链表，并添加一个初始的用户到达事件。

### 参数
- `EventList L`：指向事件链表的头指针。

### 返回值
返回初始化后的事件链表头指针。

### 注意事项
- 该函数会分配内存给链表头节点，调用者需确保在不再使用时释放内存。

## `void EventInsert(EventList L, int Occurtime, int eventType)`

### 功能
在事件链表的尾部插入一个新的事件。

### 参数
- `EventList L`：指向事件链表的头指针。
- `int Occurtime`：事件发生的时间。
- `int eventType`：事件的类型。

### 返回值
无。

### 注意事项
- 该函数会分配内存给新事件节点，调用者需确保在不再使用时释放内存。

## `EventList EventDelete(EventList L)`

### 功能
删除事件链表中的第一个事件。

### 参数
- `EventList L`：指向事件链表的头指针。

### 返回值
返回删除后的链表头指针。

### 注意事项
- 删除操作会释放第一个事件节点的内存。

## `void Sort_Occurtime(EventList L)`

### 功能
按照事件发生的时间（Occurtime）对事件链表进行排序。

### 参数
- `EventList L`：指向事件链表的头指针。

### 返回值
无。

### 注意事项
- 排序算法为简单的冒泡排序，适用于事件数量不多的场景。

## `int Get_Len(EventList L)`

### 功能
获取事件链表的长度（不包括头节点）。

### 参数
- `EventList L`：指向事件链表的头指针。

### 返回值
返回链表的长度。

### 注意事项
- 该函数的时间复杂度为O(n)。

## `Event_ptr GetPreNode(EventList L, Event_ptr p)`

### 功能
获取指定事件节点的前一个节点。

### 参数
- `EventList L`：指向事件链表的头指针。
- `Event_ptr p`：指向目标事件节点的指针。

### 返回值
返回前一个事件节点的指针。

### 注意事项
- 如果目标节点是头节点，返回值将是头节点本身。

## `void PrintList(EventList L)`

### 功能
打印事件链表中的所有事件。

### 参数
- `EventList L`：指向事件链表的头指针。

### 返回值
无。

### 注意事项
- 打印格式为“OccurTime\t EventType”。

# 数据结构

由于文件中未定义新的结构体或枚举，以下是对引用头文件中可能存在的结构体的假设说明：

```c
typedef struct Event {
    int OccurTime;  // 事件发生的时间
    int EventType;  // 事件的类型
    struct Event* next;  // 指向下一个事件的指针
} Event, *EventList, *Event_ptr;
```

# 使用示例

```c
#include <stdio.h>
#include "../include/event_management.h"

int main() {
    EventList L = NULL;
    
    // 初始化事件链表
    L = InitList(L);
    
    // 插入新事件
    EventInsert(L, 10, 1);
    EventInsert(L, 5, 2);
    
    // 排序事件
    Sort_Occurtime(L);
    
    // 打印事件链表
    PrintList(L);
    
    // 删除第一个事件
    L = EventDelete(L);
    
    // 再次打印事件链表
    PrintList(L);
    
    // 释放链表内存（示例中未展示，实际使用时需逐个释放节点）
    
    return 0;
}
```

# 依赖关系

- **依赖文件**：`../include/event_management.h`（定义了事件链表相关的结构体和函数声明）
- **被依赖文件**：无（该文件为实现文件，不直接被其他文件依赖，但通过头文件间接被使用）

确保在使用该文件前已正确包含并实现了`event_management.h`头文件中的相关定义。

---
*此文档由 CFileDocGenerator 自动生成 - 2025-04-07 17:19*