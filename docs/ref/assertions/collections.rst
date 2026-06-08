Collection Helpers
==================

.. py:currentmodule:: punit.collections

.. py:function:: are_same(actual: Sequence, expected: Sequence, sort: bool = False, sort_function: Callable[[Any], Any] = None) -> bool

    Use :py:func:`~punit.collections.are_same` to assert that two sequences contain the same elements in the same order.

    Check if two sequences contain the same elements in the same order.
    
    :param Sequence[Any]|None actaul: The sequence to check
    :param Sequence[Any]|None expected: The sequence to compare against
    :param Optional[bool] sort: Sort sequences before performing comparisons.
    :param Optional[Callable[[Any], Any]] sort_function: Custom function to use when sorting.
    :returns bool: True if the sequences contain the same elements in the same order, False otherwise.
    
.. rubric:: Example

.. code:: python

    from punit import collections

    a = [1, 2, 3]
    b = [1, 2, 3]
    c = [3, 2, 1]

    assert collections.are_same(a, b)
    assert not collections.are_same(b, c)
    # and some less obvious behaviors
    assert collections.are_same(a, a)
    assert collections.are_same(None, None)
    assert not collections.are_same(a, None)
    assert not collections.are_same(None, b)

.. py:function:: has_length(actual: Sequence[Any] | set[Any] | dict[Any, Any] | None, min: Optional[int] = None, max: Optional[int] = None) -> bool

    Check if ``actual``'s length falls within the inclusive range ``[min, max]``.
    At least one of ``min`` or ``max`` must be provided; passing both as ``None`` returns ``False``.

    :param Sequence[Any]|set[Any]|dict[Any, Any]|None actual: The sequence (or collection) to check
    :param int|None min: Inclusive lower bound on length (``len(actual) >= min``)
    :param int|None max: Inclusive upper bound on length (``len(actual) <= max``)
    :returns bool: True if the length satisfies the bounds, False otherwise

    When ``actual`` is ``None``, returns ``True`` only when both bounds are effectively zero
    (i.e. ``None`` or ``0``); otherwise returns ``False``.

.. rubric:: Example

.. code:: python

    from punit import collections

    a = [1]
    b = [1, 2]
    c = [3, 2, 1]

    assert collections.has_length(a, min=1)
    assert collections.has_length(b, min=2)
    assert collections.has_length(c, max=3)
    assert collections.has_length(b, min=1, max=3)
    assert not collections.has_length(a, min=2)
    assert not collections.has_length(b, max=1)

    # None behavior
    assert collections.has_length(None, min=0)  # True: None counts as length 0 when bounds are 0/None
    assert not collections.has_length(None, min=1)  # False: None doesn't satisfy a positive lower bound

.. py:function:: is_none_or_empty(sequence:Sequence) -> bool

    Check if a sequence is None or empty.

    :param Sequence[Any]|None sequence: The sequence to check
    :returns bool: True if the sequence is None or empty, False otherwise

.. rubric:: Example

.. code:: python

    from punit import collections

    a = [1, 2, 3]
    b = []
    c = None

    assert not collections.is_none_or_empty(a)
    assert collections.is_none_or_empty(b)
    assert collections.is_none_or_empty(c)

