use crate::indicators::{Eval, ExponentialMovingAverage};

pub struct MovingAverageConvergenceDivergence {
    ema_short: ExponentialMovingAverage,
    ema_long: ExponentialMovingAverage,
    ema_signal: ExponentialMovingAverage,
}

impl MovingAverageConvergenceDivergence {
    pub fn new(short_period: usize, long_period: usize, signal_period: usize) -> Result<Self, ()> {
        let macd = MovingAverageConvergenceDivergence {
            ema_short: ExponentialMovingAverage::new(short_period, None)?,
            ema_long: ExponentialMovingAverage::new(long_period, None)?,
            ema_signal: ExponentialMovingAverage::new(signal_period, None)?,
        };

        Ok(macd)
    }
}

impl Eval for MovingAverageConvergenceDivergence {
    fn eval(&mut self, val: f64) -> Option<f64> {
        let s = self.ema_short.eval(val);
        let l = self.ema_long.eval(val);

        let diff = match (s, l) {
            (Some(s_val), Some(l_val)) => Some(s_val - l_val),
            _ => None,
        };

        let signal = match diff {
            Some(diff) => self.ema_signal.eval(diff),
            None => None,
        };

        match (diff, signal) {
            (Some(diff), Some(signal)) => Some(diff - signal),
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::indicators::Eval;

    #[test]
    fn test_eval() -> Result<(), ()> {
        // TODO: use better data
        let mut macd = MovingAverageConvergenceDivergence::new(2, 3, 2)?;
        let test_data = [0f64, 2f64, 1f64, 10f64, 5f64];
        let mut out_data: [Option<f64>; 5] = [None; 5];
        let expected_data = [
            None,
            None,
            None,
            Some(0.7499999999999996),
            Some(-0.11111111111111116),
        ];

        for (idx, val) in test_data.iter().cloned().enumerate() {
            out_data[idx] = macd.eval(val);
        }

        assert_eq!(expected_data, out_data);
        Ok(())
    }
}
