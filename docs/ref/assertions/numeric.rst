Numeric Helpers
===============

.. py:currentmodule:: punit.assertions.numeric

approx
------

.. py:class:: approx(expected: float | int | complex = 0, rel_tol: float = 1e-9, abs_tol: float = 0.0)

    Wrapper for approximate comparisons using ``==``, ``<``, ``>``, etc., all with
    **directional (one-sided) tolerance**.

    :param float|int|complex expected: The expected numeric value (default 0 for zero-checks).
    :param float rel_tol: Relative tolerance (default 1e-9).
    :param float abs_tol: Absolute tolerance (default 0.0).
    :returns bool: True if expression is approximate.

.. tip::

    All infix operators accept tolerations **at the boundary**, extending in the
    **opposite direction** of the comparison such boundary values pass directional tests: ``x > approx(5)``
    accepts 4.99, ``x < approx(5)`` accepts 5.01. Use chain methods like ``inclusive(False)`` or
    ``strict_greater_than()`` when directional boundaries are required.

.. rubric:: Operators

.. code:: python

    from punit.assertions.numeric import approx

    # Infix == — approximately equal (bidirectional tol)
    assert 0.1 + 0.2 == approx(0.3)          # floating point quirks handled
    assert 10    == approx(9.999, rel_tol=1e-3)   # custom tolerance
    assert 1+2j  == approx(1.0+2.0j)        # works with complex too

    # Infix < and > — strictly less/greater than (one-sided tol opposite side)
    assert 5.0 <  approx(5)                   # exact boundary passes (tol below)
    assert 4.9 <  approx(5)
    assert 5.1 >  approx(5)                   # exact boundary passes (tol above)
    assert 5.0 >  approx(5)

    # Infix <= and >= — inclusive boundaries (one-sided tol above/below)
    assert 5   <= approx(5)                    # exact boundary included
    assert 5.1 <= approx(5)                    # within tol above threshold
    assert 5   >= approx(5)
    assert 4.9 >= approx(5)                    # within tol below threshold

.. rubric:: Method Chains

.. code:: python

    from punit.assertions.numeric import approx

    # Chained comparators — same directional semantics as infix
    assert 3 == approx(5).greater_than()        # >= 5 (tol extends below)
    assert 3 == approx(1).less_than()           # <= 1  (tol extends above)
    assert 3 == approx(5).at_least()            # at least 5
    assert 3 == approx(1).at_most()             # at most 1
    assert 6 == approx(5).strict_greater_than()  # > 5 (tol above only)
    assert 4 == approx(5).strict_less_than()     # < 5 (tol below only)
    assert 1e-10 == approx().zero()              # approximately zero

    # Range checks
    assert 0.5 == approx().in_range(0, 1)       # in [0, 1] with directional tol
    assert 2.5 == approx().in_range(-1, 6).inclusive(False)   # exclusive bounds

.. py:function:: isclose(a: Numeric, b: Numeric, *, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool

    Use :py:func:`~punit.assertions.numeric.isclose` to check if two numeric values are approximately equal within tolerance.

    A drop-in ``math.isclose`` replacement that accepts ``float | int | complex``. For real inputs the stdlib is used directly; for complex inputs the real and imaginary parts are compared independently.

    :param a: First numeric value.
    :param b: Second numeric value.
    :param float rel_tol: Relative tolerance (default 1e-9).
    :param float abs_tol: Absolute tolerance (default 0.0).
    :returns bool: True if ``|a - b| <= max(rel_tol * |b|, abs_tol)`` for real values, or equivalent per-component comparison for complex.

.. rubric:: Example

.. code:: python

    from punit.assertions.numeric import isclose

    assert isclose(1 + 2j, 1.0 + 2.0j)
    assert not isclose(3, 3.000000001)
    assert isclose(3, 3.000000001, rel_tol=1e-6)

.. py:function:: isnan(value: Numeric) -> bool

    Check if value is NaN (Not a Number).

    For complex inputs, returns True only if both the real and imaginary parts are NaN.

    :param Numeric value: The value to check.
    :returns bool: True if *value* is NaN, False otherwise.

.. rubric:: Example

.. code:: python

    from punit.assertions.numeric import isnan

    assert isnan(float('nan'))
    assert isnan(complex(float('nan'), float('nan')))
    assert not isnan(0.0)
    assert not isnan(1.0)

.. py:function:: isinfinite(value: Numeric) -> bool

    Check if value is infinite (positive or negative).

    For complex inputs, returns True only if either the real or imaginary part is infinite.

    :param Numeric value: The value to check.
    :returns bool: True if *value* is infinite, False otherwise.

.. rubric:: Example

.. code:: python

    from punit.assertions.numeric import isinfinite

    assert isinfinite(float('inf'))
    assert isinfinite(float('-inf'))
    assert not isinfinite(0.0)
    assert not isinfinite(1.0)

.. py:function:: percentage(value_a: Numeric, value_b: Numeric, relative_to_expected: bool = True) -> float

    Calculate the percentage difference between two numeric values.

    When *relative_to_expected* is True (the default), uses *value_b* as reference: ``abs(a - b) / |b| * 100``.
    When False, uses the symmetric form: ``abs(a - b) / ((|a| + |b|) / 2) * 100``.

    For complex inputs, magnitudes (``abs()``) are used consistently.

    :param Numeric value_a: The first numeric value.
    :param Numeric value_b: The second numeric value (reference when *relative_to_expected* is True).
    :param bool relative_to_expected: Which value to use as reference (default True).
    :returns float: The percentage difference. Returns ``inf`` if both values are zero but differ, otherwise ``0.0``.

.. rubric:: Example

.. code:: python

    from punit.assertions.numeric import percentage

    assert percentage(10, 100) == 90.0
    assert percentage(10, 100, relative_to_expected=False) == 81.818...
    assert percentage(0, 0) == 0.0
    assert percentage(0, 1) == float('inf')
