#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/config.h"
#include "../include/stu.h"
#include "../include/tools.h"
#include "../include/vars.h"

//初始化
void init(){
    FILE *fp;
    //打开文件
    printf("Now opening the file.....%s\n",FILENAME);
    if( (fp=fopen(FILENAME, "rb+")) == NULL && (fp=fopen(FILENAME, "wb+")) == NULL ){
        // pause("Error on open %s file!", FILENAME);
        printf("Error on open %s file!\n", FILENAME);
        exit(EXIT_FAILURE);
    }

    //获取文件长度
    long fileSize = getFileSize(fp);
    printf("The size of file:%ld\n", fileSize);
}


// 提示用户按键继续的函数
void pause(const char *message) {
    printf("%s\n", message);
    getchar();  // 等待用户按任意键继续
}

// 读取学生信息并返回成功读取的学生数量
int readStudentData(STU students[], int max_students) {
    FILE *fp = fopen(FILENAME, "r");
    if (fp == NULL) {
        perror("Failed to open file");
        return 0;
    }

    char line[1024];
    int count = 0;

    // 跳过第一行表头
    if (fgets(line, sizeof(line), fp) == NULL) {
        printf("Failed to read the header.\n");
        fclose(fp);
        return 0;
    }

    // 读取每一行学生数据
    while (fgets(line, sizeof(line), fp) && count < max_students) {
        STU stu;

        // 使用 sscanf 解析每一行
        if (sscanf(line, "%d,%63[^,],%9[^,],%d,%f,%f,%f", 
            &stu.id, stu.name, stu.sex, &stu.age, &stu.math, &stu.cn, &stu.en) == 7) {
            students[count++] = stu;
        } else {
            // 如果某一行格式不正确，打印错误
            printf("Error reading line: %s\n", line);
        }
    }

    fclose(fp);
    return count;
}

// 显示所有学生信息
void showAllStu() {
    STU students[100];  // 假设最多有100个学生
    int student_count = readStudentData(students, 100);

    if (student_count == 0) {
        pause("没有学生信息可显示！按任意键返回...");
        return;
    }

    // 打印表头
    printf("ID\tName\tSex\tAge\tMath\tChinese\tEnglish\n");
    printf("-----------------------------------------------------\n");

    // 打印所有学生信息
    for (int i = 0; i < student_count; i++) {
        printf("%d\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\n", 
            students[i].id, students[i].name, students[i].sex, students[i].age, 
            students[i].math, students[i].cn, students[i].en);
    }
}

// 根据成绩查询学生信息
void findStuByScores() {
    // 设定成绩查询的范围
    float min_score, max_score;

    // 提示用户输入成绩范围
    printf("Enter the minimum score:");
    scanf("%f", &min_score);
    printf("Enter the maximum score:");
    scanf("%f", &max_score);

    STU students[100];  // 假设最多有100个学生
    int student_count = readStudentData(students, 100);

    if (student_count == 0) {
        pause("No student information to query! Press any key to return..");
        return;
    }

    int found = 0;  // 用于标记是否找到符合条件的学生

    // 打印表头
    printf("ID\tName\tSex\tAge\tMath\tChinese\tEnglish\n");
    printf("-----------------------------------------------------\n");

    // 查找符合条件的学生
    for (int i = 0; i < student_count; i++) {
        if (students[i].math >= min_score && students[i].math <= max_score) {
            printf("%d\t%s\t%s\t%d\t%.1f\t%.1f\t%.1f\n", 
                students[i].id, students[i].name, students[i].sex, students[i].age, 
                students[i].math, students[i].cn, students[i].en);
            found = 1;
        }
    }

    // 如果没有找到符合条件的学生，提示错误信息
    if (!found) {
        pause("No student information to query! Press any key to return...");
    }
}