import pybryt.student as _student
from pybryt.preprocessors import NotebookPreprocessor
from pybryt.utils import make_secret
import nbformat as _nbformat
import os as _os
import dill as _dill
from copy import deepcopy as _deepcopy
from tempfile import mkstemp as _mkstemp
from textwrap import dedent as _dedent
from nbconvert.preprocessors import ExecutePreprocessor as _EP
import time as _time


PYBRYT_EXECUTION_TIMEOUT_SECONDS = 120

PYBRYT_PATCHED = False

# PyBryt's default trace function (pybryt.execution.tracing.create_collector) keeps
# tracing every single line inside *every* nested call, including deep inside library
# internals like matplotlib (path math, font metrics, Agg rendering). sys.settrace fires
# on every line of that subtree, which measured ~30x slower than untraced execution for
# a two-line plot. This replacement stops descending into a library call's internals
# once it isn't student/notebook code, while still capturing the call's return value
# (e.g. `ax = plt.subplots()`) exactly like the original did, so grading results are
# unaffected. This code runs inside the student notebook's own kernel subprocess (not
# this Django process), so it's injected as source text into the first executed cell.
TRACER_PATCH_CODE = r'''
def _pybryt_fast_create_collector(skip_types=None, addl_filenames=None):
    import linecache as _ll
    import re as _re
    from copy import copy as _copy
    from types import FunctionType as _FunctionType, ModuleType as _ModuleType
    import pybryt.execution.tracing as _tracing_mod
    from pybryt.execution.memory_footprint import Event as _Event, MemoryFootprint as _MemoryFootprint
    from pybryt.execution.utils import is_ipython_frame as _is_ipython_frame
    from pybryt.execution.complexity import is_complexity_tracing_enabled as _is_complexity_tracing_enabled

    if skip_types is None:
        skip_types = [type, type(len), _FunctionType]
    if addl_filenames is None:
        addl_filenames = []

    vars_not_found = {}
    footprint = _MemoryFootprint()

    def track_value(val, event_name, seen_at=None):
        try:
            if hasattr(val, "__module__"):
                footprint.add_imports(val.__module__.split(".")[0])
            if type(val) in skip_types:
                return
            if isinstance(val, _ModuleType):
                footprint.add_imports(val.__name__.split(".")[0])
                return
            event = _Event.from_event_name(event_name)
            footprint.add_value(_copy(val), seen_at, event)
        except Exception:
            return

    def track_call(frame):
        footprint.add_call(frame.f_code.co_filename, frame.f_code.co_name)

    def in_scope(frame):
        return _is_ipython_frame(frame) or frame.f_code.co_filename in addl_filenames

    def boundary_trace(frame, event, arg):
        if event == "return":
            if not _is_complexity_tracing_enabled():
                track_value(arg, event)
            return None
        return boundary_trace

    def collect_intermidiate_results(frame, event, arg):
        scoped = in_scope(frame)

        if scoped:
            footprint.increment_counter()

        if event == "call":
            track_call(frame)
            if scoped:
                return collect_intermidiate_results
            caller = frame.f_back
            if caller is not None and in_scope(caller):
                return boundary_trace
            return None

        if _is_complexity_tracing_enabled():
            return collect_intermidiate_results

        name = frame.f_code.co_filename + frame.f_code.co_name

        if scoped:
            if event == "line" or event == "return":
                line = _ll.getline(frame.f_code.co_filename, frame.f_lineno)
                tokens = set("".join(c if c.isalnum() or c == "_" else "\n" for c in line).split("\n"))
                for t in "".join(c if c.isalnum() or c == "_" or c == "." else "\n" for c in line).split("\n"):
                    tokens.add(t)
                tokens = sorted(tokens)

                for t in tokens:
                    if "." in t:
                        try:
                            float(t)
                            continue
                        except ValueError:
                            pass
                        try:
                            val = eval(t, frame.f_globals, frame.f_locals)
                            track_value(val, event)
                        except Exception:
                            pass
                    else:
                        if t in frame.f_locals:
                            track_value(frame.f_locals[t], event)
                        elif t in frame.f_globals:
                            track_value(frame.f_globals[t], event)

                m = _re.match(r"^\s*(\w+)(\[[^\]]\]|(\.\w+)+)*\s=.*", line)
                if m:
                    vars_not_found.setdefault(name, []).append((m.group(1), event, footprint.counter.get_value()))

            if event == "return":
                track_value(arg, event)

        if event == "return" and name in vars_not_found:
            for t, event_name, step in vars_not_found.pop(name):
                if t in frame.f_locals:
                    track_value(frame.f_locals[t], event_name, step)
                elif t in frame.f_globals:
                    track_value(frame.f_globals[t], event_name, step)

        return collect_intermidiate_results

    _tracing_mod.ACTIVE_FOOTPRINT = footprint
    return footprint, collect_intermidiate_results

import pybryt.execution.tracing as _pybryt_tracing_mod_for_patch
_pybryt_tracing_mod_for_patch.create_collector = _pybryt_fast_create_collector
'''

def patch_pybryt_execute_notebook():
    global PYBRYT_PATCHED
    if PYBRYT_PATCHED:
        return
    def _patched_execute_notebook(nb, nb_path, addl_filenames=[], timeout=PYBRYT_EXECUTION_TIMEOUT_SECONDS):
        _os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        _os.environ.setdefault("PYTHONUTF8", "1")
        nb = _deepcopy(nb)
        preprocessor = NotebookPreprocessor()

        preprocessor.preprocessors = [
            p for p in preprocessor.preprocessors
            if type(p).__name__ != "IntermediateVariablePreprocessor"
        ]

        nb = preprocessor.preprocess(nb)

        fd, footprint_fp = _mkstemp()
        _os.close(fd)
        safe_fp = footprint_fp.replace("\\", "/")

        nb_dir = _os.path.abspath(_os.path.split(nb_path)[0])
        secret = make_secret()
        ftv = f"frame_tracer_{secret}"

        # Its own cell: TRACER_PATCH_CODE is already valid, self-indented Python, so it
        # must not be spliced into a differently-indented dedent()'d template below
        # (textwrap.dedent computes common leading whitespace across the WHOLE string,
        # so mixing indentation styles there produces an IndentationError).
        tracer_patch_cell = _nbformat.v4.new_code_cell(TRACER_PATCH_CODE)

        first_cell = _nbformat.v4.new_code_cell(_dedent(f"""
            import inspect, sys
            from pybryt.execution import FrameTracer
            {ftv} = FrameTracer(inspect.currentframe())
            {ftv}.start_trace(addl_filenames={addl_filenames})
            %cd {nb_dir}
        """))

        last_cell = _nbformat.v4.new_code_cell(_dedent(f"""
            {ftv}.end_trace()
            footprint = {ftv}.get_footprint()
            footprint.filter_out_unpickleable_values()
            import dill
            with open("{safe_fp}", "wb+") as f:
                dill.dump(footprint, f)
        """))

        nb["cells"].insert(0, first_cell)
        nb["cells"].insert(0, tracer_patch_cell)
        nb["cells"].append(last_cell)

        _EP(timeout=timeout, allow_errors=True).preprocess(nb)
   
        try:
            with open(footprint_fp,"rb") as f:
                footprint=_dill.load(f)

        except Exception as e:
            raise RuntimeError(
                f"PyBryt footprint 建立失敗: {e}"
            )
        finally:
            if _os.path.exists(footprint_fp):
                _os.remove(footprint_fp)

        footprint.add_imports(*preprocessor.get_imports())
        footprint.set_executed_notebook(nb)
        return footprint

    _student.execute_notebook = _patched_execute_notebook
    PYBRYT_PATCHED = True

