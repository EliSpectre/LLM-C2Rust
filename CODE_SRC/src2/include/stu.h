#ifndef _STU_H
#define _STU_H
//学生信息结构体
typedef struct _STU{
    int id;  //学号
    char name[20];  //姓名
    char sex[10];  //性别
    int age;  //年龄
    float math;  //数学成绩
    float cn;  //语文成绩
    float en;  //英语成绩
}STU;

//初始化
extern void init();
//学生信息增删改查
extern void findStuByScores();
extern void showAllStu();
#endif