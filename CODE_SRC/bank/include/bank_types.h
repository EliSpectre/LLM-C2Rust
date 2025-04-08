#ifndef BANK_TYPES_H
#define BANK_TYPES_H

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_DURATION 40             //最大办理业务时间，单位为min
#define MAX_WINDOWS_NUM 10          //设置最大业务窗口数量
#define MAX_CUSTOMERS 50            //设置每个队列最多排多少人
#define MAX_CUSTOMERS_ARRIVAL 10    //设置用户到达银行的间隔时间

/*--------------结构体定义--------------*/
/*事件记录，包含两类事件*/
typedef struct linklist
{
    int OccurTime;           //事件发生的时间
    int EventType;           //事件类型，0表示到达事件，others表示窗口的离开事件
    struct linklist *next;
} Event, *EventList;
typedef Event *Event_ptr;    //定义一个指向事件的指针

/*银行窗口队列的元素，每个排队的客户信息*/
typedef struct person
{
    int ArrivalTime;    //客户的到达时间
    int Duration;       //每个客户办理业务的时间，随机生成
    int num;            //每个客户取号的号，标识是第几个到银行的
} Person;

/*定义每个窗口的队列(循环队列)*/
typedef struct queue
{
    Person customer[MAX_CUSTOMERS];     //队列元素类型
    int front;
    int rear;
} Window_Queue;

/*每个窗口接待的顾客的历史接待情况*/
typedef struct history
{
    Person people;           //一个客户的信息
    int AllNum;              //定义头结点，表示这个窗口接待过多少客人
    int leave_time;
    struct history *next;
} History;
typedef History * HistoryList;

/*-----------------全局变量-----------------*/
extern int TotalTimes;      //累计用户办理时间
extern int CustomerNum;     //客户数
extern int BeginTime;       //开始时间
extern int CloseTime;       //关闭时间
extern int WindowsNum;      //银行窗口数
extern EventList Ev;        //事件链表
extern Window_Queue* Windows; //窗口队列指针数组
extern HistoryList *All_History; //窗口历史记录指针数组

#endif // BANK_TYPES_H