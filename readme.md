# 可以按照接下来的操作实现C2Rust

技术路线：
现在已经基本实现了C2Rust代码的转换，路线是先将C语言的代码prompt化，然后每次转换的时候借助这个prompt。
C语言转换时，依次循环读取整个文件夹，根据prompt决定具体如何去转换。


代码运行的流程：
运行main.py文件即可将main.c及其相关的C语言文件转换为Rust语言的文件.
原始代码在"CODE_SRC"中，转换完的代码在"my_project"中。


```
python main.py
```

在my_project文件路径下运行下边的代码即可
```
cargo run
```



当前C语言文件转换的结果，my_project的代码在rust分支下

