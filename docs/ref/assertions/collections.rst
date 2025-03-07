Collection Helpers
==================

.. py:currentmodule:: punit.collections

.. py:function:: areSame(a:Sequence, b:Sequence) -> bool

    Use :py:func:`~punit.collections.areSame` to assert that two sequences contain the same elements in the same order.
    
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

.. py:function:: hasLength(sequence:Sequence, expected:int) -> bool

    Use :py:func:`~punit.collections.hasLength` to assert that a sequence has the expected number of elements.

.. rubric:: Example

.. code:: python

    from punit import *

    a = [1]
    b = [1,2]
    c = [3,2,1]

    assert collections.hasLength(a, 1)
    assert collections.hasLength(b, 2)
    assert collections.hasLength(c, 3)
    assert not collections.hasLength(a, 2)
    assert not collections.hasLength(b, 3)

.. py:function:: isNoneOrEmpty(sequence:Sequence) -> bool

    Use :py:func:`~punit.collections.isNoneOrEmpty` to assert that a sequence is ``None`` or empty.

.. rubric:: Example

.. code:: python

    from punit import *

    a = [1,2,3]
    b = []
    c = None

    assert collections.isNoneOrEmpty(a)
    assert collections.isNoneOrEmpty(b)
    assert collections.isNoneOrEmpty(c)
    assert not collections.isNoneOrEmpty(a)
    assert not collections.isNoneOrEmpty(b)
    assert not collections.isNoneOrEmpty(c)

