# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit.assertions.numeric import (
    _approximately_equal,
    approx,
    Numeric,
    isnan,
    isinfinite,
    percentage
)
from punit import theory, inlinedata


@theory
@inlinedata('Exact match', 1.0, 1.0, True)
@inlinedata('Within default tolerance', 1.0, 1.0 + 1e-10, True)
@inlinedata('Just above default tolerance', 1.0, 1.0 + 1e-8, False)
@inlinedata('Negative values within tolerance', -1.0, -1.0 + 1e-10, True)
@inlinedata('Large values within tolerance', 1e9, 1e9 + 1e0, True)
@inlinedata('Large value exact match', 1e6, 1e6, True)
@inlinedata('Integer exact match', 3, 3, True)
@inlinedata('Integer difference', 3, 4, False)
def _approximately_equal_when_float(when: str, a: float, b: float, then: bool):
    assert then == _approximately_equal(a, b), when


@theory
@inlinedata('Custom rel_tol', 1.0, 1.0 + 1e-5, True, 1e-4, 0.0)
@inlinedata('Custom abs_tol on zero', 0.0, 1e-5, True, 1e-9, 1e-4)
def _approximately_equal_custom_tolerances(when: str, a: float, b: float, then: bool, rel_tol: float, abs_tol: float):
    assert then == _approximately_equal(a, b, rel_tol=rel_tol, abs_tol=abs_tol), when


@theory
@inlinedata('Complex exact match', complex(1, 2), complex(1, 2), True)
@inlinedata('Complex same real close imag', complex(1, 2), complex(1, 2 + 1e-10), True)
@inlinedata('Complex different real', complex(1, 2), complex(2, 2), False)
def _approximately_equal_when_complex(when: str, a: complex, b: complex, then: bool):
    assert then == _approximately_equal(a, b), when


@theory
@inlinedata('Left is None', None, 1.0, False)
@inlinedata('Right is None', 1.0, None, False)
@inlinedata('Both are None', None, None, False)
def _approximately_equal_when_none(when: str, a: float | int | complex | None, b: float | int | complex | None, then: bool):
    assert then == _approximately_equal(a, b), when


@theory
@inlinedata('NaN', float('nan'), True)
@inlinedata('Finite number', 1.0, False)
@inlinedata('Zero is finite', 0.0, False)
def nan_tests(when: str, value: float, then: bool):
    assert then == isnan(value), when


@theory
@inlinedata('Positive inf', float('inf'), True)
@inlinedata('Negative inf', -float('inf'), True)
@inlinedata('Finite number', 1.0, False)
def infinite_tests(when: str, value: float, then: bool):
    assert then == isinfinite(value), when


@theory
@inlinedata('Same values', 10, 10, 0.0)
@inlinedata('Double reference', 10, 20, 50.0)
@inlinedata('Half of reference', 20, 10, 100.0)
def percentage_when(when: str, a: float, b: float, then: float):
    assert percentage(a, b) == then, when


@theory
@inlinedata('Same values symmetric', 10, 10, True)
@inlinedata('Double value symmetric', 10, 20, False)
def percentage_symmetric(when: str, a: float, b: float, relative: bool):
    result = percentage(a, b, relative_to_expected=relative)
    expected = 66.6667 if not relative else 0.0
    assert abs(result - expected) < 0.1, when


@theory
@inlinedata('Approx zero default (exact)', 0.0, True)
@inlinedata('Approx zero default (float)', 0.0, True)
@inlinedata('Approx zero default (tiny within tol)', 1e-10, True)
@inlinedata('Approx zero default (non-zero)', 0.1, False)
def approx_zero_default(when: str, value: float, then: bool):
    assert (value == approx()) is then, when


@theory
@inlinedata('Exact match', 1.0, 1.0, True)
@inlinedata('Within default tolerance', 1.0, 1.0 + 1e-10, True)
@inlinedata('Just above default tolerance', 1.0, 1.0 + 1e-8, False)
@inlinedata('Negative values within tolerance', -1.0, -1.0 + 1e-10, True)
@inlinedata('Large values within tolerance', 1e9, 1e9 + 1e0, True)
@inlinedata('Integer exact match', 3, 3, True)
@inlinedata('Integer difference', 3, 4, False)
def approx_when_float(when: str, a: float, b: float, then: bool):
    assert (a == approx(b)) is then, when


@theory
@inlinedata('Custom rel_tol', 1.0, 1.0 + 1e-5, True, 1e-4)
@inlinedata('Custom abs_tol on zero', 0.0, 1e-5, True, 1e-9, 1e-4)
def approx_custom_tolerances(when: str, a: float, b: float, then: bool, rel_tol: float, abs_tol: float = 0.0):
    assert (a == approx(b, rel_tol=rel_tol, abs_tol=abs_tol)) is then, when


@theory
@inlinedata('Complex exact match', complex(1, 2), complex(1, 2), True)
@inlinedata('Complex close imaginary', complex(1, 2), complex(1, 2 + 1e-10), True)
@inlinedata('Complex different real', complex(1, 2), complex(2, 2), False)
def approx_when_complex(when: str, a: complex, b: complex, then: bool):
    assert (a == approx(b)) is then, when


@theory
@inlinedata('Left is None', None, 1.0, False)
@inlinedata('Right is None', 1.0, None, False)
@inlinedata('String comparison', 'hello', 1.0, False)
def approx_when_non_numeric(when: str, a: object, b: float | int | complex | None, then: bool):
    assert (a == approx(b)) is then, when  # type: ignore[arg-type]


@theory
@inlinedata('Exact threshold', 3.0, 3.0, True)
@inlinedata('Above threshold', 5.0, 3.0, True)
@inlinedata('Below threshold', 1.0, 3.0, False)
@inlinedata('Within tolerance (above)', 3.000000001, 3.0, True)
@inlinedata('Within tolerance (below)', 2.999999999, 3.0, True)
def approx_greater_than(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).greater_than()) is then, when


@theory
@inlinedata('Exact threshold int', 3, 3, True)
@inlinedata('Above threshold int', 5, 3, True)
@inlinedata('Below threshold int', 1, 3, False)
def approx_greater_than_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).greater_than()) is then, when


@theory
@inlinedata('Exact threshold', 1.0, 1.0, True)
@inlinedata('Below threshold', 0.5, 1.0, True)
@inlinedata('Above threshold', 3.0, 1.0, False)
@inlinedata('Within tolerance (below)', 0.999999999, 1.0, True)
@inlinedata('Within tolerance (above)', 1.0 + 1e-10, 1.0, True)
def approx_less_than(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).less_than()) is then, when


@theory
@inlinedata('Exact threshold int', 1, 1, True)
@inlinedata('Below threshold int', 0, 1, True)
@inlinedata('Above threshold int', 3, 1, False)
def approx_less_than_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).less_than()) is then, when


@theory
@inlinedata('Exact threshold', 3.0, 3.0, True)
@inlinedata('Above threshold', 5.0, 3.0, True)
@inlinedata('Below threshold', 1.0, 3.0, False)
@inlinedata('Within tolerance (above)', 3.0 + 1e-10, 3.0, True)
@inlinedata('Within tolerance (at bound)', 2.999999999, 3.0, True)
def approx_at_least(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).at_least()) is then, when


@theory
@inlinedata('Exact threshold int', 3, 3, True)
@inlinedata('Above threshold int', 5, 3, True)
@inlinedata('Below threshold int', 1, 3, False)
def approx_at_least_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).at_least()) is then, when


@theory
@inlinedata('Exact threshold', 1.0, 1.0, True)
@inlinedata('Below threshold', 0.5, 1.0, True)
@inlinedata('Above threshold', 3.0, 1.0, False)
@inlinedata('Within tolerance (below)', 0.999999999, 1.0, True)
@inlinedata('Within tolerance (at bound)', 1.0 - 1e-10, 1.0, True)
def approx_at_most(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).at_most()) is then, when


@theory
@inlinedata('Exact threshold int', 1, 1, True)
@inlinedata('Below threshold int', 0, 1, True)
@inlinedata('Above threshold int', 3, 1, False)
def approx_at_most_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).at_most()) is then, when


@theory
@inlinedata('In middle', 5.0, 1.0, 10.0, True)
@inlinedata('At lower bound', 1.0, 1.0, 10.0, True)
@inlinedata('At upper bound', 10.0, 1.0, 10.0, True)
@inlinedata('Below lower', 0.0, 1.0, 10.0, False)
@inlinedata('Above upper', 11.0, 1.0, 10.0, False)
@inlinedata('Within tolerance at lower', 1.0000000001, 1.0, 10.0, True)
def approx_in_range_inclusive(when: str, value: float, lower: float, upper: float, then: bool):
    assert (value == approx().in_range(lower, upper)) is then, when


@theory
@inlinedata('Negative range', -2.0, -5.0, 5.0, True)
@inlinedata('Negative at bound', -5.0, -5.0, 5.0, True)
def approx_in_range_negative(when: str, value: float, lower: float, upper: float, then: bool):
    assert (value == approx().in_range(lower, upper)) is then, when


@theory
@inlinedata('In middle', 5.0, 1.0, 10.0, True)
@inlinedata('At lower excluded', 1.0, 1.0, 10.0, False)
@inlinedata('At upper excluded', 10.0, 1.0, 10.0, False)
@inlinedata('Below lower', 0.0, 1.0, 10.0, False)
@inlinedata('Above upper', 11.0, 1.0, 10.0, False)
def approx_in_range_exclusive(when: str, value: float, lower: float, upper: float, then: bool):
    assert (value == approx().in_range(lower, upper).inclusive(False)) is then, when


@theory
@inlinedata('Exact zero', 0.0, True)
@inlinedata('Tiny value', 1e-10, True)
@inlinedata('Non-zero', 0.001, False)
def approx_zero_method(when: str, value: float, then: bool):
    assert (value == approx().zero()) is then, when


@theory
@inlinedata('In range', 5.0, True)
@inlinedata('Below range', -1.0, False)
@inlinedata('Above range', 15.0, False)
def approx_chain(when: str, value: float, then: bool):
    at_least_cmp = approx(0).at_least()
    at_most_cmp = approx(10).at_most()
    assert ((value == at_least_cmp) and (value == at_most_cmp)) is then, when


@theory
@inlinedata('Lt operator below', 3.0, True)
@inlinedata('Gt operator above', 7.0, True)
@inlinedata('Le operator within', 5.0, True)
@inlinedata('Ge operator within', 5.0, True)
def approx_comparator_ops(when: str, value: float, then: bool):
    am = approx(10).at_most()
    al = approx(0).at_least()
    assert ((al < value <= am)) is then, when


@theory
@inlinedata('Lt on at_most', 0.5, False)
@inlinedata('Gt on at_most', 3.0, True)
def approx_at_most_ops(when: str, value: float, then: bool):
    am = approx(1.0).at_most()
    assert (am < value) is then, when


@theory
@inlinedata('Lt on at_least', 5.0, True)
@inlinedata('Gt on at_least', 0.5, False)
def approx_at_least_ops(when: str, value: float, then: bool):
    al = approx(1.0).at_least()
    assert (al < value) is then, when


@theory
@inlinedata('Default inclusive=True', 1.0, 1.0, 10.0, True)
@inlinedata('Explicit inclusive(True)', 1.0, 1.0, 10.0, True)
@inlinedata('inclusive(False) excludes bound', 1.0, 1.0, 10.0, False)
def approx_range_inclusive_flag(when: str, value: float, lower: float, upper: float, then: bool):
    if then:
        result = (value == approx().in_range(lower, upper).inclusive())
    else:
        result = (value == approx().in_range(lower, upper).inclusive(False))
    assert result is then, when


@theory
@inlinedata('Exact threshold', 3.0, 3.0, True)
@inlinedata('Above threshold', 5.0, 3.0, True)
@inlinedata('Below threshold', 1.0, 3.0, False)
@inlinedata('Within tolerance (above)', 3.0 + 1e-10, 3.0, True)
@inlinedata('Within tolerance (below)', 2.999999999, 3.0, True)
def approx_dunder_gt(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).__gt__()) is then, when


@theory
@inlinedata('Exact threshold int', 3, 3, True)
@inlinedata('Above threshold int', 5, 3, True)
@inlinedata('Below threshold int', 1, 3, False)
def approx_dunder_gt_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).__gt__()) is then, when


@theory
@inlinedata('Exact threshold', 1.0, 1.0, True)
@inlinedata('Below threshold', 0.5, 1.0, True)
@inlinedata('Above threshold', 3.0, 1.0, False)
@inlinedata('Within tolerance (below)', 0.999999999, 1.0, True)
@inlinedata('Within tolerance (above)', 1.0 + 1e-10, 1.0, True)
def approx_dunder_lt(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).__lt__()) is then, when


@theory
@inlinedata('Exact threshold int', 1, 1, True)
@inlinedata('Below threshold int', 0, 1, True)
@inlinedata('Above threshold int', 3, 1, False)
def approx_dunder_lt_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).__lt__()) is then, when


@theory
@inlinedata('Exact threshold', 1.0, 1.0, True)
@inlinedata('Below threshold', 0.5, 1.0, True)
@inlinedata('Above threshold', 3.0, 1.0, False)
@inlinedata('Within tolerance (below)', 0.999999999, 1.0, True)
@inlinedata('Within tolerance (at bound)', 1.0 - 1e-10, 1.0, True)
def approx_dunder_le(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).__le__()) is then, when


@theory
@inlinedata('Exact threshold int', 1, 1, True)
@inlinedata('Below threshold int', 0, 1, True)
@inlinedata('Above threshold int', 3, 1, False)
def approx_dunder_le_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).__le__()) is then, when


@theory
@inlinedata('Exact threshold', 3.0, 3.0, True)
@inlinedata('Above threshold', 5.0, 3.0, True)
@inlinedata('Below threshold', 1.0, 3.0, False)
@inlinedata('Within tolerance (above)', 3.0 + 1e-10, 3.0, True)
@inlinedata('Within tolerance (at bound)', 2.999999999, 3.0, True)
def approx_dunder_ge(when: str, actual: float, expected: float, then: bool):
    assert (actual == approx(expected).__ge__()) is then, when


@theory
@inlinedata('Exact threshold int', 3, 3, True)
@inlinedata('Above threshold int', 5, 3, True)
@inlinedata('Below threshold int', 1, 3, False)
def approx_dunder_ge_int(when: str, actual: int, expected: int, then: bool):
    assert (actual == approx(expected).__ge__()) is then, when


@theory
@inlinedata('In range with dunders', 5.0, True)
@inlinedata('Below range with dunders', -1.0, False)
@inlinedata('Above range with dunders', 15.0, False)
def approx_dunder_range(when: str, value: float, then: bool):
    gt_cmp = approx(0).__ge__()
    lt_cmp = approx(10).__le__()
    assert ((value == gt_cmp) and (value == lt_cmp)) is then, when


@theory
@inlinedata('gt matches greater_than', 5.0, 3.0)
@inlinedata('lt matches less_than', 0.5, 1.0)
@inlinedata('le matches at_most', 0.5, 1.0)
@inlinedata('ge matches at_least', 5.0, 3.0)
def approx_dunder_consistency(when: str, actual: float, expected: float):
    assert ((actual == approx(expected).__gt__()) is (actual == approx(expected).greater_than())) and \
           ((actual == approx(expected).__lt__()) is (actual == approx(expected).less_than())) and \
           ((actual == approx(expected).__le__()) is (actual == approx(expected).at_most())) and \
           ((actual == approx(expected).__ge__()) is (actual == approx(expected).at_least())), when


@theory
@inlinedata('gt on 0', 5.0, True)
@inlinedata('lt on 10', 5.0, True)
def approx_dunder_combined(when: str, value: float, then: bool):
    result = (value == approx(0).__gt__()) and (value == approx(10).__lt__())
    assert result is then, when
