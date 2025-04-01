mod math {
    pub fn max(x: i32, y: i32) -> i32 {
        if x > y { x } else { y }
    }

    pub fn min(x: i32, y: i32) -> i32 {
        if x < y { x } else { y }
    }
}

fn main() {
    let a = 10;
    let b = 20;
    println!("max={}", math::max(a, b));
    println!("min={}", math::min(a, b));
}

