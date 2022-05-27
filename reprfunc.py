"""
Utilities for making useful string representations of objects.
"""

from inspect import signature
from operator import attrgetter

__version__ = '0.1.0'
undef = object()

def repr_from_init(self=undef, *, attrs={}, skip=[], predicates={}, positional=[]):
    def __repr__(self):
        sig = signature(self.__init__)
        builder = ReprBuilder(self)

        for key, param in sig.parameters.items():
            if key in skip:
                continue

            builder.add_attr(
                    attr=attrs.get(key, key),
                    keyword=key,
                    predicate=predicates.get(key, is_default(param)),
                    positional=is_positional(key, param),
            )

        return str(builder)

    def is_positional(key, param):
        return (key in positional) or (param.kind is param.POSITIONAL_ONLY)

    def is_default(param):
        return lambda v: v is not param.default

    if self is undef:
        return __repr__
    else:
        return __repr__(self)

def repr_from_dunder(self):
    builder = ReprBuilder(self)
    args, kwargs = self.__reprargs__()

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

def eval_predicate(f, x):
    if f is True:
        return True
    if f is False:
        return False
    return f(x)


class ReprBuilder:

    def __init__(self, obj):
        self.obj = obj
        self.cls = None
        self.args = []
        self.kwargs = []

    def __str__(self):
        cls = self.cls or self.obj.__class__.__name__
        args = self.args
        kwargs = [
                f'{k}={v}'
                for k, v in self.kwargs
        ]
        return f'{cls}({", ".join((*args, *kwargs))})'

    def add_attr(self, attr, *, keyword=None, predicate=True, positional=False):
        if positional:
            self.add_positional_attr(
                    attr,
                    predicate=predicate,
            )
        else:
            self.add_keyword_attr(
                    keyword or attr,
                    attr,
                    predicate=predicate,
            )

    def add_positional_attr(self, attr, predicate=True):
        try:
            value = getter_factory(attr)(self.obj)
        except AttributeError:
            return

        if eval_predicate(predicate, value):
            self.add_positional_value(value)

    def add_positional_value(self, value):
        self.add_positional_str(repr(value))

    def add_positional_str(self, value):
        self.args.append(value)

    def add_keyword_attr(self, keyword, attr=None, *, predicate=True):
        try:
            value = getter_factory(attr or keyword)(self.obj)
        except AttributeError:
            return

        if eval_predicate(predicate, value):
            self.add_keyword_value(keyword, value)

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

