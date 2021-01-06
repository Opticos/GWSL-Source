"""
Tkinter model class creator from a dataclass.

Usage:
    TkModelClass = tk_model(MyDataclass)
"""
import tkinter as tk
import types
from dataclasses import fields, MISSING
from typing import TypeVar, Any

T = TypeVar("T")
S = TypeVar("S")

TYPE_MAP = {int: tk.IntVar, str: tk.StringVar, float: tk.DoubleVar, bool: tk.BooleanVar}


def _constructor(self: S, *_args: Any, **kwargs: Any):
    for fld in fields(self.__dataclass__):
        att_name = f"_{fld.name}"
        try:
            att_type = TYPE_MAP[fld.type]
        except KeyError:
            try:
                att_type = TYPE_MAP[fld.type._member_type_]
            except (KeyError, AttributeError):
                raise TypeError(f"{fld.name} type {fld.type} not supported by tkinter.")
        if att_name in kwargs:
            init_value = kwargs[att_name]
        elif fld.default != MISSING:
            init_value = fld.default
        elif fld.default_factory != MISSING:
            init_value = fld.default_factory()
        else:
            init_value = None
        self.__dict__[att_name] = att_type(value=init_value)


def _getter(self: S, item: str) -> Any:
    if item in self.__attrs_names__:
        return getattr(self, f"_{item}").get()
    raise AttributeError(item)


def _setter(self, key, value):
    if key not in self.__attrs_names__:
        raise AttributeError(key)
    getattr(self, f"_{key}").set(value)


def _to_dataclass(self: S) -> T:
    data = {fld.name: getattr(self, fld.name) for fld in fields(self.__dataclass__)}
    return self.__dataclass__(**data)


def tk_model(name: str, datacls: T) -> S:
    """
    Create a model class for tkinter GUIs from a dataclass.

    Takes the field of the dataclass to create protected attributes
    with the corresponding tkinter variable type.

    Default values or factories are honored.
    """
    cls = types.new_class(name)
    cls.__dataclass__ = datacls
    cls.__attrs_names__ = {f.name for f in fields(datacls)}
    cls.__init__ = _constructor
    cls.__getattr__ = _getter
    cls.__setattr__ = _setter
    cls.to_dataclass = _to_dataclass
    return cls
