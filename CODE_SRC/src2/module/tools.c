#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <conio.h>
#include <stdarg.h>

//获取文件大小（以字节计）
long getFileSize(FILE *fp){
    long fsize;
    long curr = ftell(fp);       // 保存当前位置
    fseek(fp, 0, SEEK_END);      // 移动到文件末尾
    fsize = ftell(fp);           // 获取当前位置，也就是文件大小
    fseek(fp, curr, SEEK_SET);   // 恢复到原来的位置
    return fsize;
}