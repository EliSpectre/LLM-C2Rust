#ifndef EVENT_MANAGEMENT_H
#define EVENT_MANAGEMENT_H

#include "bank_types.h"

/*事件队列管理函数*/
EventList InitList(EventList L);                      //初始化事件链
void EventInsert(EventList L, int Occurtime, int eventType); //插入事件
EventList EventDelete(EventList L);                   //删除第一个事件
void Sort_Occurtime(EventList L);                     //按照发生事件排序
int Get_Len(EventList L);                             //获取事件链长度
Event_ptr GetPreNode(EventList L, Event_ptr p);       //获取当前事件前面的一个事件
void PrintList(EventList L);                          //打印事件链

#endif // EVENT_MANAGEMENT_H