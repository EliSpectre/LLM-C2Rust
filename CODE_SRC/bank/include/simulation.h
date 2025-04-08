#ifndef SIMULATION_H
#define SIMULATION_H

#include "bank_types.h"

/*模拟运行相关函数*/
void OpenForDay();                                        //开始模拟营业
void Simulation();                                        //运行模拟
void Interact();                                          //交互查询历史记录
void Event_Drive(Event_ptr p);                            //事件驱动处理
void Arrival_Event(EventList L, Event_ptr p);             //处理到达事件
void Leave_Event(EventList L, Event_ptr p);               //处理离开事件

#endif // SIMULATION_H