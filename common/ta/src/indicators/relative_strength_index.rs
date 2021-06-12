use crate::indicators::{Eval, ExponentialMovingAverage};

pub struct RelativeStrengthIndex {
    ema_down: ExponentialMovingAverage,
    ema_up: ExponentialMovingAverage,
    prev_val: Option<f64>,
}

impl RelativeStrengthIndex {
    pub fn new(period: usize) -> Result<Self, ()> {
        let smoothing_factor = 1f64 / (period as f64);

        let rsi = RelativeStrengthIndex {
            ema_down: ExponentialMovingAverage::new(period, Some(smoothing_factor))?,
            ema_up: ExponentialMovingAverage::new(period, Some(smoothing_factor))?,
            prev_val: Default::default(),
        };

        Ok(rsi)
    }

    fn tick(&mut self, prev_val: f64, val: f64) -> Option<f64> {
        let (up, down) = if prev_val == val {
            let up = self.ema_up.eval(0f64);
            let down = self.ema_down.eval(0f64);
            (up, down)
        } else if prev_val < val {
            let up = self.ema_up.eval(val - prev_val);
            let down = self.ema_down.eval(0f64);
            (up, down)
        } else {
            let up = self.ema_up.eval(0f64);
            let down = self.ema_down.eval(prev_val - val);
            (up, down)
        };

        let res = match (up, down) {
            (Some(up), Some(down)) => {
                let rs = up / down;
                Some(1f64 - 1f64 / (1f64 + rs))
            }
            (None, None) => None,
            _ => {
                unreachable!(false);
            }
        };

        res
    }
}

impl crate::indicators::Eval for RelativeStrengthIndex {
    fn eval(&mut self, val: f64) -> Option<f64> {
        let res = match self.prev_val {
            Some(prev_val) => self.tick(prev_val, val),
            None => None,
        };

        self.prev_val = Some(val);
        res
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::indicators::Eval;

    #[test]
    fn test_eval() -> Result<(), ()> {
        // TODO: use better data
        let mut rsi = RelativeStrengthIndex::new(2)?;
        let test_data = [0f64, 2f64, 1f64];
        let mut out_data: [Option<f64>; 3] = [None; 3];
        let expected_data = [None, None, Some(0.6666666666666667)];

        for (idx, val) in test_data.iter().cloned().enumerate() {
            out_data[idx] = rsi.eval(val);
        }

        assert_eq!(expected_data, out_data);
        Ok(())
    }
}
