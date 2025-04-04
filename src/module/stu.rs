use std::io::{self, BufRead, BufReader, Write};
use std::fs::File;

// 在文件顶部定义一个常量
const FILE_PATH: &str = "./data/stu.csv";

pub struct Stu {
    pub id: i32,
    pub name: String,
    pub sex: String,
    pub age: i32,
    pub math: f32,
    pub cn: f32,
    pub en: f32,
}

pub fn init() {
    // 确保目录存在
    std::fs::create_dir_all("./data").expect("无法创建目录");
    
    if !std::path::Path::new(FILE_PATH).exists() {
        let mut file = std::fs::File::create(FILE_PATH).expect("无法创建文件");
        // 写入表头
        writeln!(file, "ID,Name,Sex,Age,Math,Chinese,English").expect("无法写入表头");
        println!("创建了新的学生数据文件");
    }
    let metadata = std::fs::metadata(FILE_PATH).expect("无法获取文件元数据");
    println!("文件大小：{} 字节", metadata.len());
}

pub fn pause(message: &str) {
    println!("{}", message);
    let _ = std::io::stdin().read_line(&mut String::new());
}

pub fn read_student_data() -> Result<Vec<Stu>, Box<dyn std::error::Error>> {
    // 使用相同的常量
    let file = std::fs::File::open(FILE_PATH)?;
    let reader = std::io::BufReader::new(file);

    let mut students = Vec::new();

    let mut lines = reader.lines();
    if let Some(Ok(_)) = lines.next() {}

    for line_result in lines {
        let line = line_result?;
        let parts: Vec<&str> = line.split(',').collect();
        if parts.len() != 7 {
            eprintln!("无效的行格式：{}", line);
            continue;
        }

        let id = parts[0].parse::<i32>()?;
        let name = parts[1].trim().to_string();
        if name.len() > 19 {
            eprintln!("姓名超过长度限制：{}", name);
            continue;
        }
        let sex = parts[2].trim().to_string();
        if sex.len() > 9 {
            eprintln!("性别字段过长：{}", sex);
            continue;
        }
        let age = parts[3].parse::<i32>()?;
        let math = parts[4].parse::<f32>()?;
        let cn = parts[5].parse::<f32>()?;
        let en = parts[6].parse::<f32>()?;

        students.push(Stu {
            id,
            name,
            sex,
            age,
            math,
            cn,
            en,
        });
    }

    Ok(students)
}

pub fn show_all_stu() {
    match read_student_data() {
        Ok(students) => {
            if students.is_empty() {
                pause("没有学生信息可显示。按任意键继续...");
                return;
            }
            println!(
                "ID\tName\tSex\tAge\tMath\tChinese\tEnglish"
            );
            println!("{}", "-----------------------------------------------------");
            for stu in students.iter() {
                println!(
                    "{}\t{}\t{}\t{}\t{:.1}\t{:.1}\t{:.1}",
                    stu.id, stu.name, stu.sex, stu.age, stu.math, stu.cn, stu.en
                );
            }
            pause("按任意键继续...");
        }
        Err(e) => {
            eprintln!("读取学生数据时出错: {}", e);
            pause("错误发生。按任意键继续...");
        }
    }
}

pub fn find_stu_by_scores() {
    println!("输入最低数学成绩：");
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).unwrap();
    let min_score: f32 = input.trim().parse().expect("请输入有效数字");

    println!("输入最高数学成绩：");
    input.clear();
    std::io::stdin().read_line(&mut input).unwrap();
    let max_score: f32 = input.trim().parse().expect("请输入有效数字");

    match read_student_data() {
        Ok(students) => {
            let mut found = false;
            println!(
                "ID\tName\tSex\tAge\tMath\tChinese\tEnglish"
            );
            println!("{}", "-----------------------------------------------------");
            for stu in students.iter() {
                if (stu.math >= min_score) && (stu.math <= max_score) {
                    println!(
                        "{}\t{}\t{}\t{}\t{:.1}\t{:.1}\t{:.1}",
                        stu.id, stu.name, stu.sex, stu.age, stu.math, stu.cn, stu.en
                    );
                    found = true;
                }
            }
            if !found {
                pause("没有找到符合条件的学生。按任意键继续...");
            } else {
                pause("按任意键继续...");
            }
        }
        Err(e) => {
            eprintln!("读取学生数据时出错: {}", e);
            pause("错误发生。按任意键继续...");
        }
    }
}