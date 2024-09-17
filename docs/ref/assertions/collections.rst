Collection Helpers
==================

.. py:currentmodule:: punit.collections

.. py:function:: areSame(a:Sequence, b:Sequence) -> bool

    Use :py:func:`~punit.collections.areSame` to assert that two collections have equivalent element values or equivalent reference values.
    
.. rubric:: Example

.. code:: python

    from punit import *

    a = [1,2,3]
    b = [1,2,3]
    c = [3,2,1]

    assert collections.areSame(a, b)
    assert not collections.areSame(b, c)
    # and some less obvious behaviors
    assert collections.areSame(a, a)
    assert collections.areSame(None, None)
    assert not collections.areSame(a, None)
    assert not collections.areSame(None, b)
