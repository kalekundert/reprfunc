"""
Utilities for making useful string representations of objects.
"""

from inspect import signature
from operator import attrgetter
from collections.abc import Mapping

__version__ = '0.2.0'
undef = object()

def repr_from_init(self=undef, *, cls=None, attrs={}, skip=[], predicates={}, positional=[]):
    def __repr__(self):
        sig = signature(self.__init__)
        builder = ReprBuilder(self)
        builder.cls = cls

        before_var = set()
        for key, param in sig.parameters.items():
            before_var.add(key)
            if param.kind is param.VAR_POSITIONAL:
                break
        else:
            before_var.clear()

        for key, param in sig.parameters.items():
            if key in skip:
                continue

            builder.add_attr(
                    attr=attrs.get(key, key),
                    keyword=key,
                    predicate=predicates.get(key, is_default(param)),
                    positional=is_positional(key, param, before_var),
                    variable=is_variable(param),
            )

        return str(builder)

    def is_default(param):
        return lambda self, v: v is not param.default

    def is_positional(key, param, before_var):
        return (
                key in positional or
                key in before_var or
                param.kind is param.POSITIONAL_ONLY or
                param.kind is param.VAR_POSITIONAL
        )

    def is_variable(param):
        return (
                param.kind is param.VAR_POSITIONAL or
                param.kind is param.VAR_KEYWORD
        )

    if self is undef:
        return __repr__
    else:
        return __repr__(self)

def repr_from_dunder(self):
    builder = ReprBuilder(self)
    fields = self.__reprargs__()
    cls, args, kwargs = None, [], {}

    if len(fields) == 3:
        cls, args, kwargs = fields
    elif len(fields) == 2:
        args, kwargs = fields
    else:
        raise ValueError(f"expected `{self.__class__.__name__}.__reprargs__()` to return (cls, args, kwargs) or (args, kwargs), not {fields!r}")

    builder.cls = cls
    for value in args:
        builder.add_positional_value(value)
    for key, value in kwargs.items():
        builder.add_keyword_value(key, value)

    return str(builder)

def repr_from_attrs(*args, **kwargs):
    def __repr__(self):
        builder = ReprBuilder(self)

        for attr in args:
            builder.add_positional_attr(attr)

        for key, attr in kwargs.items():
            if isinstance(attr, Key): attr = key
            builder.add_keyword_attr(key, attr)

        return str(builder)
    return __repr__


def getter_factory(x):
    return attrgetter(x) if isinstance(x, str) else x

def eval_predicate(f, obj, x):
    if f is True:
        return True
    if f is False:
        return False
    return f(obj, x)

class ReprBuilder:

    def __init__(self, obj):
        self.obj = obj
        self.cls = None
        self.args = []
        self.kwargs = []

    def __str__(self):
        cls = self.cls or self.obj.__class__.__name__
        if callable(cls):
            cls = cls(self.obj)

        args = self.args
        kwargs = [
                f'{k}={v}'
                for k, v in self.kwargs
        ]
        return f'{cls}({", ".join((*args, *kwargs))})'

    def add_attr(self, attr, *, keyword=None, predicate=True, positional=False, variable=False):
        if positional:
            self.add_positional_attr(
                    attr,
                    predicate=predicate,
                    variable=variable,
            )
        else:
            self.add_keyword_attr(
                    keyword or attr,
                    attr,
                    predicate=predicate,
                    variable=variable,
            )

    def add_positional_attr(self, attr, predicate=True, variable=False):
        try:
            value = getter_factory(attr)(self.obj)
        except AttributeError:
            return

        values = value if variable else [value]

        for value in values:
            if eval_predicate(predicate, self.obj, value):
                self.add_positional_value(value)

    def add_positional_value(self, value):
        self.add_positional_str(repr(value))

    def add_positional_str(self, value):
        self.args.append(value)

    def add_keyword_attr(self, keyword, attr=None, *, predicate=True, variable=False):
        try:
            value = getter_factory(attr or keyword)(self.obj)
        except AttributeError:
            return

        values = value if variable else {keyword: value}

        for key, value in values.items():
            if eval_predicate(predicate, self.obj, value):
                self.add_keyword_value(key, value)

    def add_keyword_value(self, keyword, value):
        self.add_keyword_str(keyword, repr(value))

    def add_keyword_str(self, keyword, value):
        self.kwargs.append((keyword, value))

class Key:
    pass

class verbatim:

    def __init__(self, str):
        self.str = str

    def __repr__(self):
        return self.str

