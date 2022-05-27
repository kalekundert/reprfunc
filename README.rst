********
reprfunc
********

.. image:: https://img.shields.io/pypi/v/reprfunc.svg
   :alt: Last release
   :target: https://pypi.python.org/pypi/reprfunc

.. image:: https://img.shields.io/pypi/pyversions/reprfunc.svg
   :alt: Python version
   :target: https://pypi.python.org/pypi/reprfunc

.. image:: 
   https://img.shields.io/github/workflow/status/kalekundert/reprfunc/Test%20and%20release/master
   :alt: Test status
   :target: https://github.com/kalekundert/reprfunc/actions

.. image:: https://img.shields.io/coveralls/kalekundert/reprfunc.svg
   :alt: Test coverage
   :target: https://coveralls.io/github/kalekundert/reprfunc?branch=master

.. image:: https://img.shields.io/github/last-commit/kalekundert/reprfunc?logo=github
   :alt: Last commit
   :target: https://github.com/kalekundert/reprfunc

``reprfunc`` is a library that makes it easier to implement ``__repr__()`` for 
your classes.  It implements a few common repr strategies (e.g. mimicking the 
contructor, getting values from a custom dunder method, displaying a hard-coded 
list of object attributes) and allows you use them simply by assigning to 
``__repr__``.

Installation
============

Install ``reprfunc`` from PyPI::

  $ pip install reprfunc

Version numbers obey semantic versioning.

Examples
========
Make a repr-string that matches the arguments to the constructor::

  >>> from reprfunc import *
  >>> class MyObj:
  ...
  ...     def __init__(self, a, b):
  ...         self.a = a
  ...         self.b = b
  ...
  ...     __repr__ = repr_from_init
  ...
  >>> MyObj(1, 2)
  MyObj(a=1, b=2)

The same as above, but with variable positional and keyword arguments.  These 
are handled as expected::

  >>> class MyObj:
  ...
  ...     def __init__(self, *args, **kwargs):
  ...         self.args = args
  ...         self.kwargs = kwargs
  ...
  ...     __repr__ = repr_from_init
  ...
  >>> MyObj(1, 2, a=3, b=4)
  MyObj(1, 2, a=3, b=4)

The same as above, but demonstrating a variety of ways to control the output::

  >>> class _MyObj:
  ...
  ...     def __init__(self, a, b, c, d=None, _state={}):
  ...         self.a = a
  ...         self._b = b
  ...         self.c = c
  ...         self.d = d
  ...         self._state = _state
  ...
  ...     __repr__ = repr_from_init(
  ...         # This option lets you change the class name at the beginning of 
  ...         # the repr-string.
  ...         cls='MyObj',
  ...
  ...         # This option lets you explicitly map argument names to either
  ...         # attribute names, or callables that accept the object in
  ...         # question as their only argument.
  ...         attrs={'b': '_b'},
  ...
  ...         # These options allows you to exclude certain arguments from the
  ...         # repr-string.  The first is unconditional, and the second
  ...         # depends on the value of the given function.  By default,
  ...         # attributes with the same value as the default (like `d` in this
  ...         # example) will be skipped automatically.  Note that the
  ...         # predicate can be `True` to unconditionally include an argument,
  ...         # even if it still has its default value.
  ...         skip=['_state'],
  ...         predicates={'c': lambda self, x: x},
  ...
  ...         # This option allows you to specify that certain arguments should 
  ...         # be rendered using the "positional" syntax.  Positional-only
  ...         # arguments are rendered this way by default.
  ...         positional=['a'],
  ...     )
  >>> _MyObj(1, 2, 0, _state={3: 4})
  MyObj(1, b=2)

Make a repr-string that gets its values from a ``__reprargs__()`` method 
defined by the object in question::

  >>> class MyObj:
  ...
  ...     def __init__(self, a, b):
  ...         self.a = a
  ...         self.b = b
  ...
  ...     def __reprargs__(self):
  ...         # This function should return a list and a dictionary.  Any
  ...         # values in the list will be rendered as positional arugments,
  ...         # and any items in the dictionary will be rendered as keyword
  ...         # arguments.
  ...         return [self.a], {'b': self.b}
  ...
  ...     __repr__ = repr_from_dunder
  ...
  >>> MyObj(1, 2)
  MyObj(1, b=2)

Make a repr-string from a hard-coded list of attributes::

  >>> class MyObj:
  ...
  ...     def __init__(self, a, b):
  ...         self.a = a
  ...         self.b = b
  ...
  ...     # Note that 'b' is specified twice here.  You can avoid this by
  ...     # specifying ``b=Key()``.
  ...     __repr__ = repr_from_attrs('a', b='b')
  ...
  >>> MyObj(1, 2)
  MyObj(1, b=2)

Use ``ReprBuilder`` to help formatting bespoke repr-strings.  You can think of 
this class as a collection of positional and keyword arguments that knows how 
to format itself.  It provides many more methods for registering 
positional/keyword arguments beyond what's demonstrated here, so consult the 
source code if this seems useful::

  >>> class MyObj:
  ...
  ...    def __init__(self, a, b):
  ...        self.a = a
  ...        self.b = b
  ...
  ...    def __repr__(self):
  ...        builder = ReprBuilder(self)
  ...        builder.add_positional_attr('a')
  ...        builder.add_keyword_attr('b')
  ...        return str(builder)
  ...
  >>> MyObj(1, 2)
  MyObj(1, b=2)

Alternatives
============
There are several other libraries out there that help with formatting 
repr-strings.  Overall, the reason I wrote ``reprfunc`` was to make something 
more flexible and more succinct than the alternatives.

- ``represent``: This is a pretty similar library overall.  The main difference 
  is that it uses class decorators and/or inheritance to add its repr functions 
  to your objects.  One big advantage of this approach is that it allows 
  "pretty-print" reprs for IPython to be added at the same time, but it also 
  has a heavier feel.

- ``reprutils``: This is also a pretty similar library, but it only supports 
  the equivalent of ``repr_from_attrs()``.

- ``reprtools``: This library doesn't have much documentation, but seems to be 
  mostly superseded by f-strings.
