# bank_types 文件文档

# 文件概述

`bank_types.h` 是一个头文件，主要用于定义银行模拟系统中使用的各种数据结构和全局变量。该文件提供了事件记录、客户信息、窗口队列和历史记录等结构体的定义，以及相关全局变量的声明。其主要功能和作用是为银行模拟系统的实现提供基础的数据结构和配置参数。

# 函数说明

该文件不包含任何函数定义，仅包含结构体、枚举和全局变量的定义和声明。

# 数据结构

## 结构体定义

### `linklist` / `Event` / `Event_ptr`

```c
typedef struct linklist
{
    int OccurTime;           //事件发生的时间
    int EventType;           //事件类型，0表示到达事件，others表示窗口的离开事件
    struct linklist *next;
} Event, *EventList;
typedef Event *Event_ptr;    //定义一个指向事件的指针
```

**说明**：
- `OccurTime`：事件发生的时间。
- `EventType`：事件类型，0表示客户到达事件，其他值表示窗口的离开事件。
- `next`：指向下一个事件的指针。

**用途**：
用于记录和管理银行模拟系统中的事件，如客户到达和离开。

### `person` / `Person`

```c
typedef struct person
{
    int ArrivalTime;    //客户的到达时间
    int Duration;       //每个客户办理业务的时间，随机生成
    int num;            //每个客户取号的号，标识是第几个到银行的
} Person;
```

**说明**：
- `ArrivalTime`：客户的到达时间。
- `Duration`：客户办理业务的时间，随机生成。
- `num`：客户的编号，标识是第几个到银行的。

**用途**：
用于存储每个客户的基本信息。

### `queue` / `Window_Queue`

```c
typedef struct queue
{
    Person customer[MAX_CUSTOMERS];     //队列元素类型
    int front;
    int rear;
} Window_Queue;
```

**说明**：
- `customer`：存储队列中的客户信息，最大长度为 `MAX_CUSTOMERS`。
- `front`：队列的前端索引。
- `rear`：队列的后端索引。

**用途**：
用于实现每个银行窗口的循环队列，管理排队客户。

### `history` / `History` / `HistoryList`

```c
typedef struct history
{
    Person people;           //一个客户的信息
    int AllNum;              //定义头结点，表示这个窗口接待过多少客人
    int leave_time;
    struct history *next;
} History;
typedef History * HistoryList;
```

**说明**：
- `people`：存储一个客户的信息。
- `AllNum`：表示该窗口接待过的客户总数。
- `leave_time`：客户离开的时间。
- `next`：指向下一个历史记录的指针。

**用途**：
用于记录每个窗口接待的客户历史信息。

## 类型定义

- `Event_ptr`：指向 `Event` 结构体的指针类型。

## 全局变量

- `TotalTimes`：累计用户办理时间。
- `CustomerNum`：客户数。
- `BeginTime`：开始时间。
- `CloseTime`：关闭时间。
- `WindowsNum`：银行窗口数。
- `Ev`：事件链表。
- `Windows`：窗口队列指针数组。
- `All_History`：窗口历史记录指针数组。

# 使用示例

由于该文件仅包含数据结构和全局变量的定义，不包含具体函数实现，以下示例展示如何在其他文件中使用这些定义。

```c
#include "bank_types.h"

int main() {
    // 初始化窗口队列
    Window_Queue windows[MAX_WINDOWS_NUM];
    for (int i = 0; i < MAX_WINDOWS_NUM; i++) {
        windows[i].front = 0;
        windows[i].rear = 0;
    }

    // 创建一个事件
    EventList event_list = (EventList)malloc(sizeof(Event));
    event_list->OccurTime = 10;
    event_list->EventType = 0;
    event_list->next = NULL;

    // 添加客户到窗口队列
    Person new_customer = {15, 20, 1};
    windows[0].customer[windows[0].rear] = new_customer;
    windows[0].rear = (windows[0].rear + 1) % MAX_CUSTOMERS;

    // 处理事件（示例代码，实际处理逻辑需根据具体实现）
    Event_ptr current_event = event_list;
    while (current_event != NULL) {
        if (current_event->EventType == 0) {
            // 处理到达事件
            printf("Customer arrived at time %d\n", current_event->OccurTime);
        } else {
            // 处理离开事件
            printf("Customer left at time %d\n", current_event->OccurTime);
        }
        current_event = current_event->next;
    }

    return 0;
}
```

# 依赖关系

## 依赖的头文件

- `stdio.h`：用于输入输出函数。
- `stdlib.h`：用于内存分配和随机数生成。
- `time.h`：用于时间相关函数。

## 被依赖的文件

该头文件可能被以下文件包含和使用：

- `bank_simulation.c`：实现银行模拟系统的主要逻辑。
- `bank_utils.c`：包含银行模拟系统中使用的辅助函数。

确保在使用该头文件的源文件中包含 `#include "bank_types.h"` 以正确引用定义的数据结构和全局变量。

---
*此文档由 CFileDocGenerator 自动生成 - 2025-04-07 17:22*