#include <stdio.h>
#include <stdlib.h>
#include <time.h>  // 添加 time.h 头文件
#include "./include/bank_types.h"
#include "./include/simulation.h"

/*全局变量定义*/
int TotalTimes = 0, CustomerNum = 0;        //累计用户办理时间，客户数
int BeginTime = 0, CloseTime = 630;         //1110min，银行人民银行时间，18:30
int WindowsNum = 0;                         //银行窗口数
EventList Ev;                              //事件链表
Window_Queue* Windows = NULL;              //窗口队列指针数组
HistoryList *All_History = NULL;           //窗口历史记录指针数组

int main()
{
    system("chcp 65001"); // 设置控制台编码为 UTF-8
    srand((unsigned int)time(NULL));
    OpenForDay();
    Simulation();
    return 0;
}