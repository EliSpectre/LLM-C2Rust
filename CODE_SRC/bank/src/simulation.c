#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/simulation.h"
#include "../include/event_management.h"
#include "../include/window_management.h"
#include "../include/history_management.h"
#include "../include/utils.h"

/*初始化银行业模拟*/
void OpenForDay()
{
    printf("--------------------Welcome to  YANG'S BANK!!!--------------------\n\n");
    //初始化事件链
    Ev = InitList(Ev);
    //初始化银行窗口队列
    WindowsNum = Get_WindowsNum();
    InitQueue(WindowsNum);
    //初始化窗口服务历史记录
    InitHistory(WindowsNum);
    return;
}

/*运行模拟*/
void Simulation()
{
    while(Ev->next != NULL)
        Event_Drive(Ev->next);
    Interact();
    return;
}

/*交互查询历史记录*/
void Interact()
{
    int window;
    while(1)
    {
        printf("Please enter the window number to view the service transaction history. Enter 0 to exit.");
        scanf("%d", &window);
        if(window >= 1 && window <= WindowsNum)
        {
            window--;
            PrintHistory(window);
        }else if(window == 0)
        {
            break;
        }else
        {
            printf("Sorry, the window number you entered doesn't exist!");
        }
        system("pause");
        system("cls");
        printf("--------------------Welcome to  YANG'S BANK!!!--------------------\n\n");
    }
    
}

/*事件驱动处理*/
void Event_Drive(Event_ptr p)
{
    if(p != NULL)
    {
        if(p->EventType == 0)
            Arrival_Event(Ev, p);    //处理到达事件
        else
            Leave_Event(Ev, p);        //处理离开事件
        Sort_Occurtime(Ev);
        Ev = EventDelete(Ev);
    }else
        printf("The event is empty!!!\n");
    return;
}

/*到达事件处理*/
void Arrival_Event(EventList L, Event_ptr p)
{
    int Occurtime = rand() % MAX_CUSTOMERS_ARRIVAL + 1;        //随机生成下一个到达事件发生的时间
    int Duration = rand() % MAX_DURATION + 1;                //随机生成此事件的客户办理业务的时间
    int window = Fastest_Window();
    Occurtime += p->OccurTime;        //基于在处理的当前事件的发生事件计算下一个到达事件的发生事件
    if(Occurtime <= CloseTime)
        EventInsert(Ev, Occurtime, 0);
    CustomerNum++;
    EnQueue(p->OccurTime, Duration, window);            //将此用户加入特定窗口队列排队
    EventInsert(Ev, p->OccurTime + Duration, window);    //为刚加入的用户添加离开事件
    return;
}

/*离开事件处理*/
void Leave_Event(EventList L, Event_ptr p)
{
    Person people;
    int window = p->EventType;
    DeQueue(window, &people);        //取出最先到的客户离开队列
    HistoryInsert(window, people, p->OccurTime);    //添加指定窗口的历史记录
    TotalTimes += people.Duration;    //累加客户办理业务的时间到总办理业务时间
}