use std::ffi::c_void;
use ta::indicators::{Eval, ExponentialMovingAverage, RelativeStrengthIndex, SimpleMovingAverage};

pub enum Indicator {
    SimpleMovingAverage(SimpleMovingAverage),
    ExponentialMovingAverage(ExponentialMovingAverage),
    RelativeStrengthIndex(RelativeStrengthIndex),
}

impl Eval for Indicator {
    fn eval(&mut self, value: f64) -> Option<f64> {
        match self {
            Indicator::SimpleMovingAverage(sma) => sma.eval(value),
            Indicator::ExponentialMovingAverage(ema) => ema.eval(value),
            Indicator::RelativeStrengthIndex(rsi) => rsi.eval(value),
        }
    }
}

#[no_mangle]
pub extern "C" fn create_simple_moving_average(period: usize) -> *mut c_void {
    match SimpleMovingAverage::new(period) {
        Err(_) => std::ptr::null_mut(),
        Ok(sma) => {
            let indicator = Box::new(Indicator::SimpleMovingAverage(sma));
            let res = Box::leak(indicator);
            res as *mut _ as *mut c_void
        }
    }
}

#[no_mangle]
pub extern "C" fn create_exponential_moving_average(period: usize) -> *mut c_void {
    match ExponentialMovingAverage::new(period, None) {
        Err(_) => std::ptr::null_mut(),
        Ok(ema) => {
            let indicator = Box::new(Indicator::ExponentialMovingAverage(ema));
            let res = Box::leak(indicator);
            res as *mut _ as *mut c_void
        }
    }
}

#[no_mangle]
pub extern "C" fn create_relative_strength_index(period: usize) -> *mut c_void {
    match RelativeStrengthIndex::new(period) {
        Err(_) => std::ptr::null_mut(),
        Ok(rsi) => {
            let indicator = Box::new(Indicator::RelativeStrengthIndex(rsi));
            let res = Box::leak(indicator);
            res as *mut _ as *mut c_void
        }
    }
}

#[no_mangle]
pub extern "C" fn destroy_indicator(ptr: *mut c_void) {
    if ptr.is_null() {
        return;
    }

    unsafe {
        let indicator = Box::from_raw(ptr as *mut Indicator);
        drop(indicator);
    }
}

#[repr(C)]
pub enum EvalResult {
    Ok,       // Evaluation is successful, output value was written.
    NotReady, // Evaluation is successful, but there is no output value available.
    Error,    // Error during evaluation.
}

#[no_mangle]
pub extern "C" fn eval_indicator(ptr: *mut c_void, value: f64, out: *mut f64) -> EvalResult {
    if ptr.is_null() || out.is_null() {
        return EvalResult::Error;
    }

    unsafe {
        let mut indicator = Box::from_raw(ptr as *mut Indicator);
        let res = match indicator.eval(value) {
            Some(out_val) => {
                let out_ref = &mut *out as &mut f64;
                *out_ref = out_val;
                EvalResult::Ok
            }
            None => EvalResult::NotReady,
        };

        Box::leak(indicator);
        return res;
    }
}
