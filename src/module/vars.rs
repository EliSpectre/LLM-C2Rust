use std::sync::{Mutex, MutexGuard};
use std::fs::File;

pub static FP: Mutex<Option<File>> = Mutex::new(None);
pub static STU_COUNT: Mutex<i32> = Mutex::new(0);
pub static FILE_SIZE: Mutex<i64> = Mutex::new(0);