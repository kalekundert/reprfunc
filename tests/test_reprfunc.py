#!/usr/bin/env python3

import sys, pytest
import parametrize_from_file as pff

pytest.mark.python38 = pytest.mark.skipif(
        sys.version_info < (3, 8),
        reason="python3.8 required",
)
with_repr = pff.Namespace(
        'import reprfunc',
        'from reprfunc import *',
)

@pff.parametrize(schema=with_repr.error_or('expected'))
def test_repr(obj, expected, error, request):
    obj = with_repr.exec(obj)['obj']
    with error:
        assert repr(obj) == expected

@pff.parametrize
def test_repr_builder(builder, expected):
    class Obj:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    builder = with_repr.fork(Obj=Obj).exec(builder, get='builder')
    assert str(builder) == expected

