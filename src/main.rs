mod module{
    pub mod stu;
}

fn main() {
    module::stu::init();
    module::stu::show_all_stu();
    module::stu::find_stu_by_scores();
}