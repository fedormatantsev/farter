use std::collections::VecDeque;
use std::num::NonZeroUsize;

pub struct SimpleMovingAverage {
    buffer: VecDeque<f64>,
    sum: Option<f64>,
    period: NonZeroUsize,
}

impl SimpleMovingAverage {
    pub fn new(period: usize) -> Result<Self, ()> {
        let sma = SimpleMovingAverage {
            buffer: Default::default(),
            sum: Default::default(),
            period: NonZeroUsize::new(period).ok_or(())?,
        };

        Ok(sma)
    }
}

impl crate::indicators::Eval for SimpleMovingAverage {
    fn eval(&mut self, val: f64) -> Option<f64> {
        self.buffer.push_back(val);
        let period = self.period.get();

        self.sum = match self.sum {
            Some(sum) => {
                debug_assert_eq!(period + 1, self.buffer.len());
                let old_val = self.buffer.front().unwrap().clone();
                self.buffer.pop_front();

                Some(sum + val - old_val)
            }
            None => {
                if self.buffer.len() < period {
                    return None;
                }

                let sum = self.buffer.iter().sum();

                Some(sum)
            }
        };

        self.sum.map(|val| val / (period as f64))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::indicators::Eval;

    #[test]
    fn test_eval() -> Result<(), ()> {
        let mut sma = SimpleMovingAverage::new(2)?;
        let test_data = [0f64, 2f64, 4f64, 6f64, 8f64];
        let mut out_data: [Option<f64>; 5] = [None; 5];
        let expected_data = [None, Some(1f64), Some(3f64), Some(5f64), Some(7f64)];

        for (idx, val) in test_data.iter().cloned().enumerate() {
            out_data[idx] = sma.eval(val);
        }

        assert_eq!(expected_data, out_data);
        Ok(())
    }
}
