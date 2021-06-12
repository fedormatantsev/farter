use crate::indicators::{Eval, SimpleMovingAverage};

pub struct ExponentialMovingAverage {
    sma: SimpleMovingAverage,
    prev_ema: Option<f64>,
    smoothing_factor: f64,
}

impl ExponentialMovingAverage {
    pub fn new(period: usize, smoothing_factor: Option<f64>) -> Result<Self, ()> {
        let sma = SimpleMovingAverage::new(period)?;
        let default_smoothing_factor = 2f64 / ((1 + period) as f64);

        let ema = ExponentialMovingAverage {
            sma,
            prev_ema: Default::default(),
            smoothing_factor: smoothing_factor.unwrap_or(default_smoothing_factor),
        };

        Ok(ema)
    }
}

impl Eval for ExponentialMovingAverage {
    fn eval(&mut self, value: f64) -> Option<f64> {
        match self.prev_ema {
            Some(prev_ema) => {
                let cur_ema =
                    value * self.smoothing_factor + prev_ema * (1f64 - self.smoothing_factor);
                self.prev_ema = Some(cur_ema);
                Some(cur_ema)
            }
            None => {
                let cur_ema = self.sma.eval(value);
                self.prev_ema = cur_ema;
                cur_ema
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::indicators::Eval;

    #[test]
    fn test_eval() -> Result<(), ()> {
        let mut ema = ExponentialMovingAverage::new(2, None)?;
        let test_data = [0f64, 2f64, 4f64, 6f64, 8f64];
        let mut out_data: [Option<f64>; 5] = [None; 5];
        let expected_data = [None, Some(1f64), Some(3f64), Some(5f64), Some(7f64)];

        for (idx, val) in test_data.iter().cloned().enumerate() {
            out_data[idx] = ema.eval(val);
        }

        assert_eq!(expected_data, out_data);
        Ok(())
    }
}
