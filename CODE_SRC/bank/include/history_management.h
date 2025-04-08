#ifndef HISTORY_MANAGEMENT_H
#define HISTORY_MANAGEMENT_H

#include "bank_types.h"

/*历史记录管理函数*/
void InitHistory(int WindowsNum);                           //初始化窗口历史记录
void HistoryInsert(int window, Person people, int occurtime); //添加指定窗口的历史记录
void PrintHistory(int window);                              //打印特定窗口的历史记录

#endif // HISTORY_MANAGEMENT_H