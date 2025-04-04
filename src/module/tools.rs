use std::fs::File;
use std::io::{self, Seek, SeekFrom};

pub fn get_file_size(file: &mut File) -> io::Result<u64> {
    let current_pos = file.stream_position()?;
    file.seek(SeekFrom::End(0))?;
    let size = file.stream_position()?;
    file.seek(SeekFrom::Start(current_pos))?;
    Ok(size)
}