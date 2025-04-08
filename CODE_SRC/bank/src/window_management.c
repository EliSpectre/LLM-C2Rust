#include "../include/window_management.h"

/*初始化银行窗口队列*/
void InitQueue(int WindowsNum)
{
    int i;
    //相当于定义 : Window_Queue*Windows[WindowsNum],只不过[]里不能为变量，只能用地址来表示
    Windows = (Window_Queue*)malloc(WindowsNum*sizeof(Window_Queue));
    //初始化每个窗口的队列
    Window_Queue *Window_ptr = Windows;
    for(i = 0; i < WindowsNum; i++, Window_ptr++)
    {
        Window_ptr->rear = Window_ptr->front = 0;
    }
    return;
}

/*客户进入特定窗口队列排队*/
void EnQueue(int OccurTime, int Duration, int window)
{
    int FastWindow = window - 1;          //因为要定义数组下标，所以要-1
    int queue_len = (Windows[FastWindow].rear - Windows[FastWindow].front + MAX_CUSTOMERS) % MAX_CUSTOMERS;
    if(Windows[FastWindow].front == (Windows[FastWindow].rear + 1) % MAX_CUSTOMERS)
        printf("此队列已满");
    Windows[FastWindow].customer[Windows[FastWindow].rear].ArrivalTime = OccurTime;
    Windows[FastWindow].customer[Windows[FastWindow].rear].Duration = Duration;
    Windows[FastWindow].customer[Windows[FastWindow].rear].num = CustomerNum;
    Windows[FastWindow].rear = (Windows[FastWindow].rear + 1) % MAX_CUSTOMERS;
    return;
}

/*取出最先到的客户离开队列*/
void DeQueue(int window, Person *person_ptr)
{
    window--;
    if(Windows[window].front == Windows[window].rear)
    {
        printf("队列是空的，不能出队列！");
        return;
    }
    *person_ptr = Windows[window].customer[Windows[window].front];    //获取该客户的信息
    Windows[window].front = (Windows[window].front + 1) % MAX_CUSTOMERS;
    return;
}

/*找出哪个窗口需要等待时间最短*/
int Fastest_Window()
{
    int i, j, queue_len, window_number = 0;    //i,j用于循环计数,queue_len是记录每个队列的长度,window_number是记录是哪个窗口
    int *window_time = malloc(WindowsNum * sizeof(int)); //堆分配一个数组，计算每个窗口剩余的处理时间，之后相比较
    for(i = 0; i < WindowsNum; i++)
    {
        if(Windows[i].front == Windows[i].rear) //如果此窗口为空，则为0
            window_time[i] = 0;
        else
        {
            queue_len = (Windows[i].rear - Windows[i].front + MAX_CUSTOMERS) % MAX_CUSTOMERS;
            window_time[i] = 0;
            /*循环此窗口队列排队的每个客户，累积需时间和总数*/
            for(j = 0; j < queue_len; j++)
            {
                window_time[i] += Windows[i].customer[j].Duration;
            }
        }
    }
    /*进行比较，找最短的窗口*/
    for(i = 0; i < WindowsNum; i++)
    {
        if(window_time[window_number] >= window_time[i])
            window_number = i;
    }
    free(window_time);
    return window_number + 1;
}

/*打印特定队列*/
void PrintQueue(int window)
{
    int queue_len = (Windows[window].rear - Windows[window].front + MAX_CUSTOMERS) % MAX_CUSTOMERS;
    int i = Windows[window].front;
    while((i % MAX_CUSTOMERS) != Windows[window].rear)
    {
        printf("编号: %d\t窗口：%d\t到达时间：%d\t处理时间:%d\n",
               Windows[window].customer[i].num, window,
               Windows[window].customer[i].ArrivalTime,
               Windows[window].customer[i].Duration);
        i++;
    }
    return;
}

/*打印所有队列*/
void PrintAllQueue(int WindowsNum)
{
    int i = 0;
    for(i = 0; i < WindowsNum; i++)
    {
        PrintQueue(i);
        printf("\n\n\n");
    }
    return;
}