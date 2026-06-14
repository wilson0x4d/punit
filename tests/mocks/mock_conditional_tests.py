# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for the conditional 'when..then..' fluent API on Mock.

Covers condition creation, deduplication, dispatch routing, call tracking,
and edge cases for subgraph-based conditional mocking.
"""

from __future__ import annotations

from punit.mocks import Mock, is_any, is_gt, is_gte, is_lte, contains  # noqa: F401
from punit import fact

# ---------------------------------------------------------------------------
# Group 1: Creation & deduplication
# ---------------------------------------------------------------------------


@fact
def when_creates_subgraph_mock() -> None:
    m = Mock(name='svc')
    sg = m.do_stuff.when(is_lte(42))
    assert isinstance(sg, Mock)
    assert 'when' in sg._u.name  # type: ignore[attr-defined]


@fact
def identical_conditions_deduplicate() -> None:
    m = Mock(name='svc')
    sg1 = m.do_stuff.when(is_lte(42))
    sg2 = m.do_stuff.when(is_lte(42))
    assert sg1 is sg2  # same instance


@fact
def different_conditions_create_different_subgraphs() -> None:
    m = Mock(name='svc')
    sg_low = m.do_stuff.when(is_lte(42))
    sg_high = m.do_stuff.when(is_gt(42))
    assert sg_low is not sg_high


@fact
def identical_kw_conditions_deduplicate() -> None:
    m = Mock(name='svc')
    s1 = m.do_stuff.when(x=is_any())
    s2 = m.do_stuff.when(x=is_any())
    assert s1 is s2  # is_any singleton + kwarg comparison == True


@fact
def different_kwargs_create_different_subgraphs() -> None:
    m = Mock(name='svc')
    s1 = m.do_stuff.when(x=is_gt(10))
    s2 = m.do_stuff.when(x=is_gt(20))
    assert s1 is not s2


@fact
def when_with_no_matchers_raises_mock_error() -> None:
    m = Mock(name='svc')
    try:
        m.do_stuff.when()  # type: ignore[call-arg]
    except Exception as exc:
        assert 'when() requires at least one matcher argument' in str(exc)
    else:
        assert False, 'Expected MockError'


@fact
def when_subgraph_has_own_independent_children() -> None:
    m = Mock(name='svc')
    sg1 = m.do_stuff.when(is_lte(42)).foo  # creates subgraph + child 'foo'
    sg2 = m.do_stuff.when(is_gt(42)).bar   # creates subgraph + child 'bar'
    assert sg1 is not sg2
    sg1_foo = m.do_stuff.when(is_lte(42)).foo  # should reuse cached subgraph's children
    sg2_bar = m.do_stuff.when(is_gt(42)).bar
    # Each subgraph has its own children namespace
    assert sg1_foo is not sg2_bar


# ---------------------------------------------------------------------------
# Group 2: Dispatch routing (definitive user example)
# ---------------------------------------------------------------------------


@fact
def definitive_user_example() -> None:
    m = Mock(name='svc')
    m.do_stuff.when(is_lte(42)).foo.returns('AAA')
    m.do_stuff.when(is_lte(42)).bar.returns('BBB')
    m.do_stuff.when(is_gt(42)).foo.returns('CCC')
    m.do_stuff.when(is_gt(42)).bar.returns('DDD')

    assert m.do_stuff.when(is_lte(42)) is m.do_stuff.when(is_lte(42))  # dedup
    assert m.do_stuff.when(is_lte(42)) is not m.do_stuff.when(is_gt(42))

    assert m.do_stuff(42).foo() == 'AAA'
    assert m.do_stuff(41).bar() == 'BBB'

    assert m.do_stuff(44).foo() == 'CCC'
    assert m.do_stuff(47).bar() == 'DDD'


@fact
def matching_condition_forwards_call_to_subgraph() -> None:
    m = Mock(name='svc')
    m.num.when(is_gt(10)).returns('high')
    m.num.when(is_lte(10)).returns('low')
    assert m.num(5) == 'low'
    assert m.num(20) == 'high'


@fact
def non_matching_falls_through_to_flat_returns() -> None:
    m = Mock(name='svc')
    m.do_stuff.returns('default')
    # No conditions configured — falls through to flat .returns()
    result = m.do_stuff(99)
    assert result == 'default'


@fact
def non_matching_falls_through_to_flat_side_effect() -> None:
    m = Mock(name='svc')
    calls: list[int] = []
    m.do_stuff.side_effect(lambda x: calls.append(x) or x * 10)  # type: ignore[func-returns-value]
    # No conditions configured — falls through to flat side_effect
    result = m.do_stuff(7)
    assert result == 70
    assert calls == [7]


@fact
def first_match_wins_on_overlapping_conditions() -> None:
    m = Mock(name='svc')
    # is_gt(0) matches before is_gt(42) because it was registered first
    m.num.when(is_gt(0)).returns('positive')
    m.num.when(is_gt(42)).returns('big')
    assert m.num(50) == 'positive'  # is_gt(0) matches first


@fact
def multiple_conditions_route_independently() -> None:
    m = Mock(name='svc')
    # Conditions are non-overlapping — each value matches exactly one
    m.do_stuff.when(is_lte(41)).foo.returns('low-foo')
    m.do_stuff.when(is_gte(43)).bar.returns('gte-bar')
    m.do_stuff.when(is_gt(41)).baz.returns('gt-baz')  # matches 42 and above

    # 41: only is_lte(41) matches → 'low-foo'; is_gt(41) does NOT match (not strictly greater)
    assert m.do_stuff(41).foo() == 'low-foo'

    # 42: is_gt(41) matches first → 'gt-baz'; no foo config on that subgraph
    assert m.do_stuff(42).baz() == 'gt-baz'

    # 43: is_gte(43) matches → 'gte-bar'
    assert m.do_stuff(43).bar() == 'gte-bar'


# ---------------------------------------------------------------------------
# Group 3: Call tracking
# ---------------------------------------------------------------------------


@fact
def conditional_call_dispatched_to_subgraph() -> None:
    """When a condition matches, the call is forwarded to the subgraph and child_calls record the chain."""
    m = Mock(name='svc')
    ds = m.do_stuff
    ds.when(is_lte(42))  # register condition on do_stuff
    # Access .bar child via the condition's subgraph so it's cached on the subgraph
    ds.when(is_lte(42)).bar  # noqa: FURB118

    m.do_stuff(42).bar()  # type: ignore[unused-coroutine]
    # Child calls propagate through conditional subgraph dispatch
    assert len(m.child_calls) > 0


@fact
def conditional_subgraph_tracks_its_own_calls() -> None:
    m = Mock(name='svc')
    m.foo.when(is_lte(5)).bar.returns('x')
    m.foo(3).bar()  # noqa: FURB113 (result discarded on purpose)

    # Get the registered subgraph from conditions and verify its children's call counts
    for (exp_args, exp_kwargs, subgraph) in m.foo._u.when_conditions:
        assert subgraph.bar.call_count == 1
        return

    AssertionError('subgraph not found')


@fact
def conditional_child_calls_propagate() -> None:
    m = Mock(name='svc')
    m.do_stuff.when(is_lte(5)).bar.baz.returns('deep')
    m.do_stuff(3).bar().baz()  # noqa: FURB113 (result discarded on purpose)
    assert len(m.child_calls) > 0


@fact
def reset_clears_conditional_call_history() -> None:
    m = Mock(name='svc')
    m.foo.when(is_lte(5)).bar.returns('x')
    sg = m.foo.when(is_lte(5))
    m.foo(3).bar()  # noqa: FURB113 (result discarded on purpose)

    # Conditional subgraph call history also cleared via __traverse
    assert sg.bar.call_count == 1, 'expected call_count == 1'

    m.reset()
    assert sg.bar.call_count == 0, 'expected call_count == 0'


# ---------------------------------------------------------------------------
# Group 4: Edge cases
# ---------------------------------------------------------------------------


@fact
def when_with_is_any_matcher() -> None:
    m = Mock(name='svc')
    m.do_stuff.when(is_any()).returns('anything')
    assert m.do_stuff(1) == 'anything'
    assert m.do_stuff('hello') == 'anything'


@fact
def when_condition_with_kwargs_matches_correctly() -> None:
    m = Mock(name='svc')
    m.service.when(x=is_gt(10)).action.returns('matched')
    assert m.service(x=15).action() == 'matched'

    # No match for x=5 — falls through to flat behavior (returns self, which chains)
    result = m.service(x=5).action()  # noqa: FURB113 (result discarded on purpose)
    assert result is m.service.action  # cached child access


@fact
def side_effect_and_condition_both_set_on_same_mock() -> None:
    """Conditional dispatch has highest priority; flat config used when condition doesn't match."""
    m = Mock(name='svc')
    m.do_stuff.side_effect(lambda x: x * 10)
    m.do_stuff.when(is_gt(5)).returns('conditional')

    assert m.do_stuff(3) == 30   # no condition matches → falls through to side_effect
    assert m.do_stuff(10) == 'conditional'  # condition matches → conditional wins


@fact
def returns_and_condition_both_set_on_same_mock() -> None:
    """Conditional dispatch has highest priority; flat .returns used when condition doesn't match."""
    m = Mock(name='svc')
    m.foo.returns('flat')
    m.foo.when(is_gt(10)).returns('cond')

    assert m.foo(5) == 'flat'     # no match → flat returns
    assert m.foo(15) == 'cond'    # condition matches


@fact
def nested_conditions_resolve_correctly() -> None:
    """A subgraph can have its own conditions for further dispatch."""
    m = Mock(name='svc')
    outer_subgraph = m.num.when(is_gt(0))
    outer_subgraph.val.when(is_gt(10)).returns('high')
    outer_subgraph.val.when(is_lte(10)).returns('low')

    # 5 → is_gt(0) matches → subgraph; val: is_lte(10) matches (5 <= 10)
    assert m.num(1).val(5) == 'low', f'expected low val, got {m.num(5)}'
    # 20 → is_gt(0) matches → subgraph; val: is_gt(10) matches
    assert m.num(1).val(20) == 'high', f'expected high val, got {m.num(20)}'


@fact
def when_with_multiple_matchers_deduplicates() -> None:
    """Conditions with multiple matchers deduplicate correctly."""
    m = Mock(name='svc')
    sg1 = m.do_stuff.when(is_gt(0), is_lte(10))
    sg2 = m.do_stuff.when(is_gt(0), is_lte(10))
    assert sg1 is sg2


@fact
def when_condition_with_multiple_kwarg_matchers_deduplicates() -> None:
    """Conditions with multiple kwarg matchers deduplicate correctly."""
    m = Mock(name='svc')
    s1 = m.do_stuff.when(x=is_gt(0), y=contains('hello'))
    s2 = m.do_stuff.when(x=is_gt(0), y=contains('hello'))
    assert s1 is s2
