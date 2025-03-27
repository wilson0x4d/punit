Collection Helpers
==================

.. py:currentmodule:: punit.collections

.. py:function:: areSame(a:Sequence, b:Sequence, sort:bool=False, sortFunction:Callable[[Any], Any]=None) -> bool

    Use :py:func:`~punit.collections.areSame` to assert that two sequences contain the same elements in the same order.

    Check if two sequences contain the same elements in the same order.
    
    :param Sequence[Any]|None a: The sequence to check
    :param Sequence[Any]|None b: The sequence to compare against
    :param Optional[bool] sort: Sort sequences before performing comparisons.
    :param Optional[Callable[[Any], Any]] sortFunction: Custom function to use when sorting.
    :returns bool: True if the sequences contain the same elements in the same order, False otherwise.
    
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

    Check if a sequence has the expected number of elements.
    
    :param Sequence[Any]|None sequence: The sequence to check
    :param int|None expected: The expected number of elements
        
    :returns bool: True if the sequence has exactly the expected number of elements, False otherwise

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

    Check if a sequence is None or empty.

    :param Sequence[Any]|None sequence: The sequence to check
    :returns bool: True if the sequence is None or empty, False otherwise

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

