use crate::indicators::{Eval, SimpleMovingAverage};
use std::ffi::c_void;

pub enum Indicator {
    SimpleMovingAverage(SimpleMovingAverage),
}

impl Eval for Indicator {
    fn eval(&mut self, value: f64) -> Option<f64> {
        match self {
            Indicator::SimpleMovingAverage(sma) => sma.eval(value),
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
pub extern "C" fn destroy_indicator(ptr: *mut c_void) {
    if ptr.is_null() {
        return;
    }

    unsafe {
        let indicator = Box::from_raw(ptr as *mut Indicator);
        drop(indicator);
    }
}

#[no_mangle]
#[repr(C)]
pub enum EvalResult {
    EvalOk,   // Evaluation is successful, output value was written.
    EvalNone, // Evaluation is successful, but there is no output value available.
    EvalErr,  // Error during evaluation.
}

#[no_mangle]
pub extern "C" fn eval_indicator(ptr: *mut c_void, value: f64, out: *mut f64) -> EvalResult {
    if ptr.is_null() || out.is_null() {
        return EvalResult::EvalErr;
    }

    unsafe {
        let mut indicator = Box::from_raw(ptr as *mut Indicator);
        match indicator.eval(value) {
            Some(out_val) => {
                let out_ref = &mut *out as &mut f64;
                *out_ref = out_val;
                EvalResult::EvalOk
            }
            None => EvalResult::EvalNone,
        }
    }
}
