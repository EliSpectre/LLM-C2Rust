#include "../include/event_management.h"

/*初始化事件链*/
EventList InitList(EventList L)
{
    Event_ptr ev;    //event的简写
    L = (EventList)malloc(sizeof(Event));
    L->next = NULL;
    //添加一个用户到达事件到事件链
    EventInsert(L, BeginTime, 0); 
    return L;
}

/*链表尾部插入法*/
void EventInsert(EventList L, int Occurtime, int eventType)
{
    Event_ptr new_ev, ev;
    new_ev = (EventList)malloc(sizeof(Event));
    new_ev->OccurTime = Occurtime;
    new_ev->EventType = eventType;
    /*将指针指向最后一个结点*/
    ev = L;
    while(ev->next != NULL)
    {
        ev = ev->next;
    }
    /*将结点作为最后一个事件*/
    new_ev->next = ev->next;
    ev->next = new_ev;
    return;
}

/*删除第一个事件*/
EventList EventDelete(EventList L)
{
    Event_ptr ev;
    ev = L->next;
    L->next = ev->next;
    free(ev);
    ev = NULL;
    return L;
}

/*按照Occurtime排序事件*/
void Sort_Occurtime(EventList L)
{
    int i, j, len;
    len = Get_Len(L);        //获得链表长度（除了头结点）
    Event_ptr p, p_next, pre_p;
    p = L->next;
    for(i = 0; i < len-1; i++)    //如果链表长度为6，最后一轮排序，其实我们只需排序5次就够了，
    {
        j = len - i - 1;        //每循环一次，我们就可以少比较一个元素，因为每次大的都会被置到最后，没必要再比较
        while(p->next != NULL && j != 0)
        {
            j--;
            p_next = p->next;
            if(p->OccurTime > p_next->OccurTime)
            {
                pre_p = GetPreNode(L, p);
                pre_p->next = p_next;
                p->next = p_next->next;
                p_next->next = p;
            }else
            {
                p = p_next;
            }
        }
        p = L->next;
    }
    return;
}

/*获取事件链长度*/
int Get_Len(EventList L)
{
    int len = 0;
    Event_ptr p = L->next;
    while(p != NULL){
        p = p->next;
        len++;
    }
    return len;
}

/*获取前一个事件结点*/
Event_ptr GetPreNode(EventList L, Event_ptr p)
{
    Event_ptr temp;
    temp = L;
    while(temp->next != p)
    {
        temp = temp->next;
    }
    return temp;
}

/*打印事件链*/
void PrintList(EventList L)
{
    int len = 0;
    Event_ptr p = L->next;
    
    len = Get_Len(L);
    printf("\n该表共有%d条记录:\n", len);
    
    if (p != NULL){    
        do{
            printf("%d\t %d\n", p->OccurTime, p->EventType);
            p = p->next;
        }while (p != NULL);
    }
}