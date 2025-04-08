#ifndef WINDOW_MANAGEMENT_H
#define WINDOW_MANAGEMENT_H

#include "bank_types.h"

/*窗口队列管理函数*/
void InitQueue(int WindowsNum);              //初始化银行窗口队列
void EnQueue(int OccurTime, int Duration, int window); //客户进入特定窗口队列排队
void DeQueue(int window, Person *person_ptr); //取出最先到的客户离开队列
int Fastest_Window();                        //找出哪个窗口需要等待时间最短
void PrintQueue(int window);                 //打印特定队列
void PrintAllQueue(int WindowsNum);          //打印所有队列

#endif // WINDOW_MANAGEMENT_H