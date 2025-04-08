#include "../include/history_management.h"

/*初始化窗口历史记录*/
void InitHistory(int WindowsNum)
{
    int i;
    All_History = (HistoryList*)malloc(WindowsNum * sizeof(HistoryList));
    /*初始化每个窗口的历史记录*/
    for(i = 0; i < WindowsNum; i++)
    {
        All_History[i] = (HistoryList)malloc(sizeof(History));
        All_History[i]->next = NULL;
        All_History[i]->AllNum = 0;        //把这个窗口的接待客户历史数量放到头结点的AllNum中
    }
    return;
}

/*添加指定窗口的历史记录*/
void HistoryInsert(int window, Person people, int occurtime)
{
    HistoryList L, p, new_history;
    window--;
    L = All_History[window];    //将L指向要操作的窗口的历史记录
    /*链表采用尾部插入法*/
    new_history = (HistoryList)malloc(sizeof(History));
    new_history->people = people;
    new_history->leave_time = occurtime;
    L->AllNum++;
    p = L;
    while(p->next != NULL)
    {
        p = p->next;
    }
    new_history->next = p->next;
    p->next = new_history;
    return;
}

/*打印特定窗口的历史记录*/
void PrintHistory(int window)
{
    HistoryList L, p;
    int arrival_hour, arrival_min;
    int leave_hour, leave_min; 
    Person people;
    L = All_History[window];
    int Num = L->AllNum;
    printf("\n\n今日处理业务总时间: %d分钟\t\t今日客户总数:     %d人\n", TotalTimes, CustomerNum);
    printf("银行今日开业时间:   8:00\t\t银行今日打烊时间: %d:%d\n", CloseTime/60+8, CloseTime%60);
    printf("\n --------------------%d号窗口共服务了%d位客户！---------------------\n", window+1, Num);
    p = L->next;
    printf("┌──────────┬──────────┬──────────┬────────────────┬──────────┐\n");
    printf("│客户编号    │窗口编号    │到达时间    │办理业务时间    │离开时间    │\n");
    while(p != NULL)
    {
        people = p->people;
        arrival_hour = people.ArrivalTime/60+8;
        arrival_min = people.ArrivalTime%60;
        leave_hour = p->leave_time/60+8;
        leave_min = p->leave_time%60;
        printf("├──────────┼──────────┼──────────┼────────────────┼──────────┤\n");
        printf("│%-12d│%-12d│%-2.2d:%-9.2d│%-16d│%-2.2d:%-9.2d│\n",
               people.num, window+1, arrival_hour, arrival_min, people.Duration, leave_hour, leave_min);
        p = p->next;
    }
    printf("└──────────┴──────────┴──────────┴────────────────┴──────────┘\n");
    printf(" ---------------------------------------------------------------------\n"); 
    return;
}