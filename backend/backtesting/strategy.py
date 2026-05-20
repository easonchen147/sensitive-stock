from __future__ import annotations

import inspect
import math
from dataclasses import dataclass
from typing import Any, Callable, Dict

import numpy as np
import pandas as pd

from . import indicators

DEFAULT_STRATEGY_CODE = """# 编写 generate_signals(data, ctx) 函数即可
def generate_signals(data, ctx):
    # 获取参数，默认快线5，慢线20
    fast_window = ctx.params.get("fast_window", 5)
    slow_window = ctx.params.get("slow_window", 20)

    close = data["close"]
    fast = ctx.sma(close, fast_window)
    slow = ctx.sma(close, slow_window)

    signal = ctx.new_signal()
    signal[ctx.cross_over(fast, slow)] = 1
    signal[ctx.cross_under(fast, slow)] = 0
    return signal.ffill().fillna(0)
"""


class StrategyExecutionError(RuntimeError):
    """Raised when the provided strategy code cannot be executed."""


ALLOWED_IMPORTS = {"math", "numpy", "pandas"}


class StrategyHelpers:
    """Expose indicator helpers and convenience accessors to strategy authors."""

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any] = None) -> None:
        self._data = data
        self._params = params or {}

    @property
    def params(self) -> Dict[str, Any]:
        return self._params

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @property
    def close(self) -> pd.Series:
        return self._data["close"]

    @property
    def pre_close(self) -> pd.Series:
        return self._data["pre_close"]

    @property
    def open(self) -> pd.Series:
        return self._data["open"]

    @property
    def high(self) -> pd.Series:
        return self._data["high"]

    @property
    def low(self) -> pd.Series:
        return self._data["low"]

    @property
    def volume(self) -> pd.Series:
        return self._data["volume"]

    def new_signal(self, default_value: float = 0.0) -> pd.Series:
        return pd.Series(default_value, index=self._data.index, dtype=float)

    def __getattr__(self, name: str) -> Any:
        if hasattr(indicators, name):
            return getattr(indicators, name)
        raise AttributeError(name)


def _limited_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root not in ALLOWED_IMPORTS:
        raise ImportError(f"不允许导入模块 {name}")
    return __import__(name, globals, locals, fromlist, level)


def _safe_builtins() -> Dict[str, Callable[..., Any]]:
    allowed = {
        "abs": abs,
        "min": min,
        "max": max,
        "round": round,
        "pow": pow,
        "sum": sum,
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "all": all,
        "any": any,
        "sorted": sorted,
        "map": map,
        "filter": filter,
        "float": float,
        "int": int,
        "bool": bool,
        "str": str,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,
        "locals": locals,
        "globals": globals,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "print": print,
    }
    # math helpers
    for attr in ("sqrt", "log", "log10", "exp", "ceil", "floor"):
        allowed[attr] = getattr(math, attr)
    allowed["__import__"] = _limited_import
    return allowed


def _normalize_series(result: Any, index: pd.Index) -> pd.Series:
    if isinstance(result, pd.DataFrame):
        if "signal" in result:
            result = result["signal"]
        else:
            raise StrategyExecutionError("请返回 pd.Series 或包含 signal 列的 DataFrame")

    if isinstance(result, pd.Series):
        series = result.copy()
    elif isinstance(result, (list, tuple, np.ndarray)):
        series = pd.Series(result, index=index[: len(result)])
    else:
        raise StrategyExecutionError("strategy 的返回值无法识别，请返回 pandas Series")

    series = series.astype(float)
    series = series.reindex(index)
    series = series.ffill().fillna(0.0)
    return series


@dataclass
class StrategyExecutor:
    allowed_globals: Dict[str, Any] = None

    def __post_init__(self) -> None:
        safe_globals = {
            "__builtins__": _safe_builtins(),
            "np": np,
            "pd": pd,
            "locals": locals,
            "globals": globals,
        }
        for name in dir(indicators):
            if name.startswith("_"):
                continue
            attr = getattr(indicators, name)
            if callable(attr):
                safe_globals[name] = attr
        self.allowed_globals = safe_globals

    def execute(self, code: str, data: pd.DataFrame, params: Dict[str, Any] = None) -> pd.Series:
        namespace: Dict[str, Any] = {}
        globals_dict = dict(self.allowed_globals)

        try:
            exec(code, globals_dict, namespace)
        except Exception as exc:  # pragma: no cover
            raise StrategyExecutionError(f"策略代码执行出错: {exc}") from exc

        strategy_func = namespace.get("generate_signals") or globals_dict.get("generate_signals")
        if not callable(strategy_func):
            raise StrategyExecutionError("策略中必须定义 generate_signals(data, ctx) 函数")

        helpers = StrategyHelpers(data, params)
        param_len = len(inspect.signature(strategy_func).parameters)
        try:
            if param_len <= 1:
                result = strategy_func(data.copy())
            else:
                result = strategy_func(data.copy(), helpers)
        except Exception as exc:  # pragma: no cover
            raise StrategyExecutionError(f"generate_signals 执行失败: {exc}") from exc
        return _normalize_series(result, data.index)
