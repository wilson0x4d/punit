# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Numeric assertion helpers for approximate comparisons and checks.

Provides the ``approx`` class (inspired by pytest.approx) for directional
tolerance-based numeric comparisons, plus standalone helpers like
``isclose``, ``isnan``, ``isinfinite``, and ``percentage``.

The ``approx`` class supports natural Python comparison syntax with
directional (one-sided) tolerance:

    * ``x == approx(expected)``; approximately equal (bidirectional tolerance)
    * ``x > approx(threshold)``; strictly greater than (tolerance extends below)
    * ``x >= approx(threshold)``;  at least the threshold (tolerance extends below)
    * ``x < approx(threshold)``;  strictly less than (tolerance extends above)
    * ``x <= approx(threshold)``;  at most the threshold (tolerance extends above)

Example
-------

.. code-block:: python

    from punit.assertions.numeric import approx, isclose, isnan

    assert 0.1 + 0.2 == approx(0.3)
    assert isclose(1 + 2j, 1.0 + 2.0j)
    assert not isclose(3, 3.000000001)
    assert isnan(float('nan'))

"""

from __future__ import annotations

from decimal import Decimal
import math
from typing import cast
from typing_extensions import override


Numeric = float | int | complex
_NonComplex = float | int


def _as_non_complex(v: object) -> _NonComplex:
    """
    Narrow *v* from ``object`` to a real-only numeric by excluding complex.

    This is safe because callers only pass through ``_guard``, which already
    rejects non-numeric types and the comparators' equality chains never reach
    it with a complex value (complex handling is done in ``isclose`` /
    ``_approximately_equal``).
    """
    if isinstance(v, complex):
        raise TypeError('Expected real numeric; got complex')
    return cast(_NonComplex, v)


def _guard_complex(other: object) -> Numeric:
    """Validate *other* is a supported numeric and return it unchanged."""
    if isinstance(other, (Decimal, complex, float, int)):
        return cast(Numeric, other)
    raise NotImplementedError(f'Unsupported comparison value: {type(other).__name__}')  # type: ignore[unreachable]


def _real_expected(base: '_ApproxComparator') -> float:
    """
    Return *base._expected* as float for real-only operations.

    Raises ``TypeError`` when the expected value is complex;  those
    comparisons belong to ``isclose`` / ``_approximately_equal``.
    """
    if isinstance(base._expected, complex):
        raise TypeError('Expected real numeric; got complex')
    return float(base._expected)


def isclose(
    a: Numeric,
    b: Numeric,
    *,
    rel_tol: float = 1e-9,
    abs_tol: float = 0.0,
) -> bool:
    """
    Check if two numeric values are approximately equal within tolerance.

    A drop-in ``math.isclose`` replacement that accepts the full ``Numeric`` type
    (``float | int | complex``). For real inputs the stdlib is used directly; for
    complex inputs the real and imaginary parts are compared independently using the
    same tolerances.

    Args:
        a: First numeric value.
        b: Second numeric value.
        rel_tol: Relative tolerance (default 1e-9).
        abs_tol: Absolute tolerance (default 0.0).

    Returns:
        True if ``|a - b| <= max(rel_tol * |b|, abs_tol)`` for real values, or
        equivalent per-component comparison for complex.

    Example
    -------

    .. code-block:: python

        from punit.assertions.numeric import isclose

        assert isclose(1 + 2j, 1.0 + 2.0j)
        assert not isclose(3, 3.000000001)
        assert isclose(3, 3.000000001, rel_tol=1e-6)
    """
    if isinstance(a, complex) or isinstance(b, complex):
        a_c = a if isinstance(a, complex) else complex(a, 0)
        b_c = b if isinstance(b, complex) else complex(b, 0)
        return math.isclose(a_c.real, b_c.real, rel_tol=rel_tol, abs_tol=abs_tol) and \
            math.isclose(a_c.imag, b_c.imag, rel_tol=rel_tol, abs_tol=abs_tol)

    # Both real: delegate to stdlib (safe float cast for int/float)
    return math.isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=abs_tol)


def _approximately_equal(
    actual: Numeric | None,
    expected: Numeric | None,
    rel_tol: float = 1e-9,
    abs_tol: float = 0.0,
    directional: bool = False,
) -> bool:
    """
    Check if two numeric values are approximately equal within tolerance.

    Uses the formula |actual - expected| <= max(rel_tol * |expected|, abs_tol).
    For complex numbers, real and imaginary parts are compared independently.

    When ``directional=True``, uses asymmetric (one-sided) tolerance: the value is
    accepted if it lies within one tolerance unit **above** the threshold
    (lower-bound direction). This is useful for strict inequality checks where only
    one side of the boundary matters.

    :param actual: The actual numeric value to check.
    :param expected: The expected numeric value.
    :param rel_tol: Relative tolerance (default 1e-9, like pytest.approx).
    :param abs_tol: Absolute tolerance (default 0.0).
    :param directional: If True, use asymmetric tolerance (one-sided above threshold).
    :returns bool: True if values are approximately equal, False otherwise.
    """
    if actual is None or expected is None:
        return False

    if isinstance(actual, complex) or isinstance(expected, complex):
        a = actual if isinstance(actual, complex) else complex(actual, 0)
        e = expected if isinstance(expected, complex) else complex(expected, 0)
        tol = rel_tol * abs(e) if e != 0 else abs_tol
        if directional:
            return (e.real - tol <= a.real <= e.real + tol and
                    e.imag - tol <= a.imag <= e.imag + tol)
        return (isclose(a.real, e.real, rel_tol=rel_tol, abs_tol=abs_tol) and
                isclose(a.imag, e.imag, rel_tol=rel_tol, abs_tol=abs_tol))

    tol = max(rel_tol * abs(float(expected)), abs_tol) if expected else abs_tol
    if directional:
        return float(actual) >= expected - tol  # type: ignore[operator]
    return isclose(float(actual), float(expected), rel_tol=rel_tol, abs_tol=abs_tol)


class _ApproxComparator:
    """Base class for approx comparison operators."""
    __slots__ = ('_expected', '_rel_tol', '_abs_tol')

    def __init__(self, expected: Numeric, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> None:
        self._expected = expected
        self._rel_tol = rel_tol
        self._abs_tol = abs_tol

    def _guard(self, other: object) -> Numeric:
        return _guard_complex(other)

    def _tol(self) -> float:
        """Compute tolerance magnitude from relative and absolute tolerances."""
        if isinstance(self._expected, complex):
            scale = abs(self._expected)
        else:
            scale = abs(float(self._expected))
        tol = self._rel_tol * scale
        return tol if tol else self._abs_tol


class GreaterThanComparator(_ApproxComparator):
    """
    Comparator returned by approx.greater_than(): value >= expected.

    Accepts values within tolerance of the threshold, or strictly above it.
    Tolerance extends below the threshold for asymmetric bounds (one-sided).
    """
    __slots__ = ()

    @override
    def _guard(self, other: object) -> _NonComplex:
        ok = _guard_complex(other)
        return _as_non_complex(ok)

    @override
    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return ok >= re - tol

    def __le__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) and
                (float(ok) <= re + tol))

    def __lt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary less than *other*? (chaining semantics for ``al < x``)."""
        ok = self._guard(other)
        return _approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol, directional=True)

    def __gt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary greater than *other*? (chaining semantics for ``al > x``)."""
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) and
                (float(ok) <= re + tol))

    def __ge__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, gt = self.__eq__(other), self.__gt__(other)
        if eq is NotImplemented or gt is NotImplemented:
            return NotImplemented
        return eq or gt


class LessThanComparator(_ApproxComparator):
    """
    Comparator returned by approx.less_than(): value <= expected.

    Accepts values within tolerance of the threshold, or strictly below it.
    Tolerance extends above the threshold for asymmetric bounds (one-sided).
    """
    __slots__ = ()

    @override
    def _guard(self, other: object) -> _NonComplex:
        ok = _guard_complex(other)
        return _as_non_complex(ok)

    @override
    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return ok <= re + tol

    def __le__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) and
                (float(ok) >= re - tol))

    def __lt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary less than *other*? (chaining semantics for ``am < x``)."""
        ok = self._guard(other)
        return _approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol, directional=False)

    def __gt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary greater than *other*? (chaining semantics for ``am > x``)."""
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return (_approximately_equal(ok, self._expected, self._rel_tol, tol) and
                (float(ok) >= re - tol))

    def __ge__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, gt = self.__eq__(other), self.__gt__(other)
        if eq is NotImplemented or gt is NotImplemented:
            return NotImplemented
        return eq or gt


class AtLeastComparator(_ApproxComparator):
    """
    Comparator returned by approx.at_least(): value >= expected.

    Tolerance extends below the threshold for asymmetric bounds (one-sided).
    """
    __slots__ = ()

    @override
    def _guard(self, other: object) -> _NonComplex:
        ok = _guard_complex(other)
        return _as_non_complex(ok)

    @override
    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return ok >= re - tol

    def __le__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary <= *other*? (chaining semantics for ``al <= x``)."""
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) and
                (float(ok) <= re + tol))

    def __lt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary < *other*? (chaining semantics for ``al < x``)."""
        ok = self._guard(other)
        tol_for_ok = max(self._rel_tol * abs(float(ok)), self._abs_tol) if float(ok) else self._abs_tol  # type: ignore[arg-type]
        return _approximately_equal(ok, self._expected, self._rel_tol, tol_for_ok, directional=True)

    def __gt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary > *other*? (chaining semantics for ``al > x``)."""
        ok = self._guard(other)
        re = _real_expected(self)
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) or  # noqa: PLR2004
                (float(ok) <= re + self._tol()))

    def __ge__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, gt = self.__eq__(other), self.__gt__(other)
        if eq is NotImplemented or gt is NotImplemented:
            return NotImplemented
        return eq or gt


class AtMostComparator(_ApproxComparator):
    """
    Comparator returned by approx.at_most(): value <= expected.

    Tolerance extends above the threshold for asymmetric bounds (one-sided).
    """
    __slots__ = ()

    @override
    def _guard(self, other: object) -> _NonComplex:
        ok = _guard_complex(other)
        return _as_non_complex(ok)

    @override
    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        tol = self._tol()
        return ok <= re + tol

    def __le__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary <= *other*? (chaining semantics for ``am <= x``)."""
        ok = self._guard(other)
        re = _real_expected(self)
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) or  # noqa: PLR2004
                (float(ok) >= re - self._tol()))

    def __lt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary < *other*? (chaining semantics for ``am < x``)."""
        re = _real_expected(self)
        return re < float(other)  # type: ignore[arg-type]

    def __gt__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary > *other*? (chaining semantics for ``am > x``)."""
        ok = self._guard(other)
        re = _real_expected(self)
        return (_approximately_equal(ok, self._expected, self._rel_tol, self._abs_tol) or  # noqa: PLR2004
                (float(ok) >= re - self._tol()))

    def __ge__(self, other: object) -> bool | None:  # type: ignore[override]
        """Is this boundary >= *other*? (chaining semantics for ``am >= x``)."""
        eq, gt = self.__eq__(other), self.__gt__(other)
        if eq is NotImplemented or gt is NotImplemented:
            return NotImplemented
        return eq or gt


class StrictGreaterThanComparator(_ApproxComparator):
    """
    Comparator for strictly greater-than checks (one-sided tolerance below threshold).

    Accepts values at or above the threshold within one tolerance unit below it.
    For a threshold of T with tol, the band is ``[T - tol, inf)``.
    Strictly rejects any value more than tol below the expected boundary.
    """
    __slots__ = ()

    @override
    def _guard(self, other: object) -> _NonComplex:
        ok = _guard_complex(other)
        return _as_non_complex(ok)

    @override
    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        return ok >= re - self._tol()


class StrictLessThanComparator(_ApproxComparator):
    """
    Comparator for strictly less-than checks (one-sided tolerance above threshold).

    Accepts values at or below the threshold within one tolerance unit above it.
    For a threshold of T with tol, the band is ``(-inf, T + tol]``.
    Strictly rejects any value more than tol above the expected boundary.
    """
    __slots__ = ()

    @override
    def _guard(self, other: object) -> _NonComplex:
        ok = _guard_complex(other)
        return _as_non_complex(ok)

    @override
    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        re = _real_expected(self)
        return ok <= re + self._tol()


class ApproxRangeComparator:
    """Comparator returned by approx.in_range(): checks [lower, upper]."""
    __slots__ = ('_lower', '_upper', '_rel_tol', '_abs_tol', '_exclusive')

    def __init__(self, lower: float, upper: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> None:
        self._lower = lower
        self._upper = upper
        self._rel_tol = rel_tol
        self._abs_tol = abs_tol
        self._exclusive = False

    def inclusive(self, flag: bool = True) -> ApproxRangeComparator:
        """
        Return a new ``ApproxRangeComparator`` with toggled inclusivity.

        Unlike a destructive mutation, this method returns a fresh instance so that
        the original comparator remains unaffected when the result is reused.
        """
        copy = ApproxRangeComparator(self._lower, self._upper, self._rel_tol, self._abs_tol)
        copy._exclusive = not flag  # noqa: SLF001
        return copy

    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        if not isinstance(other, (int, float)):
            return NotImplemented
        if self._exclusive:
            # exclusive bounds: exclude exact boundaries but allow tolerance beyond them
            lo_tol = max(self._rel_tol * abs(self._lower), self._abs_tol) if self._lower else 0.0
            hi_tol = max(self._rel_tol * abs(self._upper), self._abs_tol) if self._upper else 0.0
            at_lower = other == self._lower
            at_upper = other == self._upper
            strictly_between = not (at_lower or at_upper) and other > self._lower and other < self._upper  # type: ignore[operator]
            below_tol = other < self._lower and other >= self._lower - lo_tol  # type: ignore[operator]
            above_tol = other > self._upper and other <= self._upper + hi_tol  # type: ignore[operator]
            return strictly_between or below_tol or above_tol  # type: ignore[operator]
        lo = _approximately_equal(other, self._lower, self._rel_tol, self._abs_tol)
        hi = _approximately_equal(other, self._upper, self._rel_tol, self._abs_tol)
        between: bool = other >= self._lower and other <= self._upper  # type: ignore[operator]
        return lo or hi or between

    def __ne__(self, other: object) -> bool | None:  # type: ignore[override]
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

    def __lt__(self, other: object) -> bool | None:  # type: ignore[override]
        if not isinstance(other, (int, float)):
            return NotImplemented
        return other < self._lower  # type: ignore[operator]

    def __le__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, lt = self.__eq__(other), self.__lt__(other)
        if eq is NotImplemented or lt is NotImplemented:
            return NotImplemented
        return eq or lt

    def __gt__(self, other: object) -> bool | None:  # type: ignore[override]
        if not isinstance(other, (int, float)):
            return NotImplemented
        return other > self._upper  # type: ignore[operator]

    def __ge__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, gt = self.__eq__(other), self.__gt__(other)
        if eq is NotImplemented or gt is NotImplemented:
            return NotImplemented
        return eq or gt


class ZeroComparator(_ApproxComparator):
    """Comparator returned by approx.zero(): checks if value is approximately zero."""

    def __init__(self, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> None:
        super().__init__(0, rel_tol, abs_tol)

    def _eq(self, other: object) -> bool | None:
        ok = self._guard(other)
        # For zero comparison use absolute tolerance (relative doesn't work for 0 baseline)
        tol = self._abs_tol if self._abs_tol else 1e-9
        return abs(complex(ok)) <= tol

    def __eq__(self, other: object) -> bool | None:  # type: ignore[override]
        result = self._eq(other)
        return bool(result)

    def __ne__(self, other: object) -> bool | None:  # type: ignore[override]
        eq = self.__eq__(other)
        return not eq

    def __lt__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        tol = self._abs_tol if self._abs_tol else 1e-9
        eq = _approximately_equal(ok, 0, abs_tol=tol)
        if isinstance(ok, complex):
            lt = abs(ok) < tol  # type: ignore[operator]
        else:
            lt = float(ok) < -tol  # type: ignore[arg-type]
        return eq or lt

    def __le__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, lt = self.__eq__(other), self.__lt__(other)
        return eq or lt

    def __gt__(self, other: object) -> bool | None:  # type: ignore[override]
        ok = self._guard(other)
        tol = self._abs_tol if self._abs_tol else 1e-9
        eq = _approximately_equal(ok, 0, abs_tol=tol)
        if isinstance(ok, complex):
            gt = abs(ok) > tol  # type: ignore[operator]
        else:
            gt = float(ok) > tol  # type: ignore[arg-type]
        return eq or gt

    def __ge__(self, other: object) -> bool | None:  # type: ignore[override]
        eq, gt = self.__eq__(other), self.__gt__(other)
        return eq or gt


def isnan(value: Numeric) -> bool:
    """
    Check if value is NaN (Not a Number).

    For complex inputs, returns True only if both the real and imaginary parts are NaN.

    Args:
        value: The numeric value to check.

    Returns:
        True if value is NaN, False otherwise.

    Example
    -------

    .. code-block:: python

        from punit.assertions.numeric import isnan

        assert isnan(float('nan'))
        assert not isnan(0.0)
    """
    if isinstance(value, complex):
        return math.isnan(value.real) and math.isnan(value.imag)
    return math.isnan(float(value))


def isinfinite(value: Numeric) -> bool:
    """
    Check if value is infinite (positive or negative).

    For complex inputs, returns True only if either the real or imaginary part is infinite.

    Args:
        value: The numeric value to check.

    Returns:
        True if value is infinite, False otherwise.

    Example
    -------

    .. code-block:: python

        from punit.assertions.numeric import isinfinite

        assert isinfinite(float('inf'))
        assert not isinfinite(0.0)
    """
    if isinstance(value, complex):
        return math.isinf(value.real) or math.isinf(value.imag)
    return math.isinf(float(value))


def percentage(
    value_a: Numeric,
    value_b: Numeric,
    relative_to_expected: bool = True,
) -> float:
    """
    Calculate the percentage difference between two numeric values.

    When relative_to_expected=True, uses value_b as reference::

        abs(a - b) / |b| * 100

    When relative_to_expected=False, uses symmetric form::

        abs(a - b) / ((|a| + |b|) / 2) * 100

    For complex inputs, magnitudes (``abs()``) are used consistently: the numerator is
    the magnitude of the difference, and the denominator is the magnitude of the reference.

    Args:
        value_a: The first numeric value.
        value_b: The second numeric value (reference when relative_to_expected=True).
        relative_to_expected: If True, use value_b as reference (default).

    Returns:
        The percentage difference as a float. Returns ``inf`` if both values are zero but differ, otherwise ``0.0``.

    Example
    -------

    .. code-block:: python

        from punit.assertions.numeric import percentage

        assert percentage(10, 100) == 90.0
        assert percentage(0, 0) == 0.0
    """
    diff_mag = abs(value_a - value_b)
    if relative_to_expected:
        ref_mag = abs(value_b)
    else:
        ref_mag = (abs(value_a) + abs(value_b)) / 2

    if ref_mag == 0:
        return float('inf') if diff_mag > 0 else 0.0
    return diff_mag / ref_mag * 100


class approx:
    """
    Wrapper for approximate comparisons using ``==``, ``<``, ``>``, etc.

    Enables natural Python syntax like ``0.1 + 0.2 == approx(0.3)``.
    Supports chained methods for range/inequality checks:

        x == approx(expected)                  -- approximately equal (default expected=0)
        x == approx(threshold).greater_than()   -- >= threshold (one-sided tol below)
        x == approx(threshold).less_than()      -- <= threshold (one-sided tol above)
        x == approx(threshold).at_least()       -- at least the threshold (one-sided tol below)
        x == approx(threshold).at_most()        -- at most the threshold (one-sided tol above)
        x == approx(threshold).strict_greater_than()  -- > threshold (tolerance above only)
        x == approx(threshold).strict_less_than()     -- < threshold (tolerance below only)
        x == approx().in_range(lower, upper)   -- within [lower, upper] with directional tol
        x == approx().zero()                   -- approximately zero

    :param expected: The expected numeric value (default 0 for zero-checks).
    :param rel_tol: Relative tolerance (default 1e-9).
    :param abs_tol: Absolute tolerance (default 0.0).
    """
    __slots__ = ('_expected', '_rel_tol', '_abs_tol')

    def __init__(self, expected: float | int | complex = 0, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> None:
        """Create an ``approx`` instance with the given *expected* value and tolerances."""
        self._expected = expected
        self._rel_tol = rel_tol
        self._abs_tol = abs_tol

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, float, complex)):
            abs_tol = self._abs_tol if self._abs_tol else 1e-9
            return _approximately_equal(  # type: ignore[arg-type]
                other, self._expected, self._rel_tol, abs_tol)
        return False

    def greater_than(self) -> GreaterThanComparator:
        """Return a comparator for ``>= expected`` checks (one-sided tolerance below)."""
        return GreaterThanComparator(self._expected, self._rel_tol, self._abs_tol)

    def less_than(self) -> LessThanComparator:
        """Return a comparator for ``<= expected`` checks (one-sided tolerance above)."""
        return LessThanComparator(self._expected, self._rel_tol, self._abs_tol)

    def at_least(self) -> AtLeastComparator:
        """Return a comparator for ``>= expected`` inclusive boundary checks (one-sided tol below)."""
        return AtLeastComparator(self._expected, self._rel_tol, self._abs_tol)

    def at_most(self) -> AtMostComparator:
        """Return a comparator for ``<= expected`` inclusive boundary checks (one-sided tol above)."""
        return AtMostComparator(self._expected, self._rel_tol, self._abs_tol)

    def strict_greater_than(self) -> StrictGreaterThanComparator:
        """Return a ``StrictGreaterThanComparator`` for strictly ``> expected`` (one-sided tolerance above)."""
        return StrictGreaterThanComparator(self._expected, self._rel_tol, self._abs_tol)

    def strict_less_than(self) -> StrictLessThanComparator:
        """Return a ``StrictLessThanComparator`` for strictly ``< expected`` (one-sided tolerance below)."""
        return StrictLessThanComparator(self._expected, self._rel_tol, self._abs_tol)

    def in_range(self, min_val: float, max_val: float) -> ApproxRangeComparator:
        """Return a comparator for ``[min_val, max_val]`` range checks with directional tolerance."""
        return ApproxRangeComparator(min_val, max_val, self._rel_tol, self._abs_tol)

    def zero(self) -> ZeroComparator:
        """Return a comparator for approximate zero checks."""
        return ZeroComparator(self._rel_tol, self._abs_tol)

    def __gt__(self, _other: Numeric | None = None) -> StrictGreaterThanComparator:  # noqa: SLF001
        """Return a ``StrictGreaterThanComparator`` for strictly ``> expected`` (one-sided tolerance above)."""
        return self.strict_greater_than()

    def __lt__(self, _other: Numeric | None = None) -> StrictLessThanComparator:  # noqa: SLF001
        """Return a ``StrictLessThanComparator`` for strictly ``< expected`` (one-sided tolerance below)."""
        return self.strict_less_than()

    def __le__(self, _other: Numeric | None = None) -> AtMostComparator:  # noqa: SLF001
        """Return an ``AtMostComparator`` for ``<= expected`` inclusive boundary."""
        return self.at_most()

    def __ge__(self, _other: Numeric | None = None) -> AtLeastComparator:  # noqa: SLF001
        """Return an ``AtLeastComparator`` for ``>= expected`` inclusive boundary."""
        return self.at_least()


__all__ = [
    'approx',
    'isnan',
    'isinfinite',
    'isclose',
    'percentage',
]
