mod exponential_moving_average;
mod relative_strength_index;
mod simple_moving_average;

pub trait Eval {
    fn eval(&mut self, value: f64) -> Option<f64>;
}

pub use exponential_moving_average::ExponentialMovingAverage;
pub use relative_strength_index::RelativeStrengthIndex;
pub use simple_moving_average::SimpleMovingAverage;
