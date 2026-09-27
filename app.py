TypeError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/arrays/arrow/array.py", line 1000, in _cmp_method
    result = pc_func(self._pa_array, self._box_pa(other))
File "/home/adminuser/venv/lib/python3.14/site-packages/pyarrow/compute.py", line 254, in wrapper
    return func.call(args, None, memory_pool)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
File "pyarrow/_compute.pyx", line 399, in pyarrow._compute.Function.call
File "pyarrow/error.pxi", line 155, in pyarrow.lib.pyarrow_internal_check_status
    return check_status(status)
File "pyarrow/error.pxi", line 92, in pyarrow.lib.check_status
    raise convert_status(status)
ArrowNotImplementedError
During handling of the above exception, another exception occurred:
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/arrays/arrow/array.py", line 1007, in _cmp_method
    result[valid] = op(np_array[valid], other)
                    ~~^^^^^^^^^^^^^^^^^^^^^^^^
TypeError
During handling of the above exception, another exception occurred:
File "/mount/src/marketplace-shqiperi/app.py", line 394, in <module>
    filtered_df = filtered_df[(filtered_df['cmimi'] >= min_c) & (filtered_df['cmimi'] <= max_c)]
                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/ops/common.py", line 85, in new_method
    return method(self, other)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/arraylike.py", line 62, in __ge__
    return self._cmp_method(other, operator.ge)
           ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/series.py", line 6735, in _cmp_method
    res_values = ops.comparison_op(lvalues, rvalues, op)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/ops/array_ops.py", line 341, in comparison_op
    res_values = op(lvalues, rvalues)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/ops/common.py", line 85, in new_method
    return method(self, other)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/arraylike.py", line 62, in __ge__
    return self._cmp_method(other, operator.ge)
           ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/arrays/string_arrow.py", line 591, in _cmp_method
    result = super()._cmp_method(other, op)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/arrays/arrow/array.py", line 1009, in _cmp_method
    result = ops.invalid_comparison(self, other, op)
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/core/ops/invalid.py", line 55, in invalid_comparison
    raise TypeError(f"Invalid comparison between dtype={left.dtype} and {typ}")