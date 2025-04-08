#include "../include/utils.h"
#include "../include/bank_types.h"
/*由用户输入银行窗口数量*/
int Get_WindowsNum()
{
    int num;
    printf("请输入BANK的窗口数量（最多为%d）: ", MAX_WINDOWS_NUM);
    while(1)
    {
        scanf("%d", &num);
        if(num > MAX_WINDOWS_NUM)
        {
            system("cls");
            printf("--------------------Welcome to  YANG'S BANK!!!--------------------\n\n");
            printf("您输入的窗口数超过最大窗口数%d，请重新输入：", MAX_WINDOWS_NUM);
        }else
            break;    
    }
    system("cls");
    printf("--------------------Welcome to  YANG'S BANK!!!--------------------\n\n");
    return num;
}