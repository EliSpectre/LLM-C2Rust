mod math;

fn main() {
    let a = 10;
    let b = 20;
    println!("max={}", math::max(a, b));
    println!("min={}", math::min(a, b));
}