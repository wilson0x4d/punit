# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for parent-child call aggregation (mock_calls, child_calls)."""

from __future__ import annotations

from punit.mocks import Call, CallList, CallRecord, Mock
from punit import fact


@fact
def mock_calls_does_not_contain_leaf_call_on_root() -> None:
    """Leaf calls on children do NOT appear in parent's mock_calls."""
    m = Mock()
    m.foo.bar(1, 2)
    assert len(m.mock_calls) == 0


@fact
def child_calls_contains_aggregated_child_call() -> None:
    m = Mock()
    m.foo.bar(1, 2)
    assert len(m.child_calls) == 1
    entry = m.child_calls[0]
    assert entry.path == 'Mock.foo.bar'


@fact
def direct_self_call_appears_in_mock_calls_not_child_calls() -> None:
    m = Mock()
    m()
    assert len(m.mock_calls) == 1
    assert len(m.child_calls) == 0
    entry = m.mock_calls[0]
    assert entry.path == 'Mock'


@fact
def direct_self_call_sets_called_property() -> None:
    m = Mock()
    assert not m.called
    m()
    assert m.called


@fact
def child_mock_has_own_mock_calls_with_leaf_entry() -> None:
    m = Mock()
    m.foo.bar(1, 2)
    foo_bar = m.foo.bar
    assert len(foo_bar.mock_calls) == 1
    entry = foo_bar.mock_calls[0]
    assert entry.path == 'Mock.foo.bar'


@fact
def child_mock_has_empty_child_calls_on_leaf() -> None:
    m = Mock()
    m.foo.bar(1, 2)
    assert len(m.foo.bar.child_calls) == 0


@fact
def parent_parent_gets_aggregated_entries() -> None:
    """Deep descendant calls propagate to ancestors via child_calls."""
    m = Mock()
    a = m.a
    b = a.b
    c = b.c
    d = c.d
    d(42)

    # m.mock_calls is empty (no direct call on m itself)
    assert len(m.mock_calls) == 0
    # But child_calls[0] has the full-path entry propagated from leaf
    assert len(m.child_calls) == 1
    entry = m.child_calls[0]
    assert isinstance(entry, CallRecord)
    assert entry.path == 'Mock.a.b.c.d'
    assert entry.args == (42,)


@fact
def grandparent_child_calls_contains_leaf() -> None:
    m = Mock()
    m.a.b(1)
    assert len(m.child_calls) == 1
    assert m.child_calls[0].path == 'Mock.a.b'


@fact
def multiple_children_get_separate_entries() -> None:
    """Each child call appears as a separate entry in child_calls."""
    m = Mock()
    m.foo(1)
    m.bar(2)

    assert len(m.mock_calls) == 0
    assert len(m.child_calls) == 2
    assert m.child_calls[0].args == (1,)
    assert m.child_calls[1].args == (2,)


@fact
def called_reflects_self_call_not_child_calls() -> None:
    """was_called tracks only direct invocations on the mock itself."""
    m = Mock()
    assert not m.called
    m.foo(1)  # child call, not a call on m itself
    assert not m.called


@fact
def partial_sublist_matching_works_on_child_calls() -> None:
    """Child entries support partial-sublist matching via CallList."""
    m = Mock()
    m.a(1)
    m.b(2)

    # Use CallList for partial-sublist matching via __contains__
    subset = CallList((Call('Mock.a', (1,), {}), Call('Mock.b', (2,), {})))
    assert subset in m.child_calls


@fact
def partial_sublist_matching_fails_on_wrong_args() -> None:
    m = Mock()
    m.a(1)

    wrong = CallList((Call('Mock.a', (99,), {}),))
    assert wrong not in m.mock_calls


@fact
def reset_clears_all_aggregated_lists() -> None:
    """Reset clears mock_calls, child_calls and was_called."""
    m = Mock()
    m.foo(1)           # child call → adds to child_calls[0], not mock_calls
    assert not m.called, 'expected no call history.'
    assert len(m.child_calls) == 1, 'expected 1 child call.'
    m('bar')
    assert m.called, 'expected call history.'
    m.reset(preserve_sideeffects=False, preserve_stubs=False)
    assert len(m.mock_calls) == 0, 'expected call history reset.'
    assert len(m.child_calls) == 0, 'expected child call history reset.'
    assert not m.called, 'call history was not reset.'


@fact
def reset_clears_aggregated_lists() -> None:
    m = Mock()
    m.foo.bar(1)
    assert len(m.child_calls) == 1
    m.reset()
    assert len(m.child_calls) == 0


@fact
def reset_clears_grandchildren_too() -> None:
    """Reset clears calls across all levels of the mock hierarchy."""
    m = Mock()
    m.a.b.c(1)

    # Deep grandchild has its own entry; ancestors see it only via child_calls
    assert len(m.a.b.mock_calls) == 0      # a.b was accessed, not called
    assert len(m.a.b.child_calls) == 1      # but c's call propagated here
    assert len(m.child_calls) == 1           # top-level sees aggregated entry

    m.reset()

    # All levels cleared via traversal
    assert len(m.mock_calls) == 0
    assert len(m.a.mock_calls) == 0
    assert len(m.a.b.mock_calls) == 0
    assert len(m.child_calls) == 0


@fact
def was_called_clears_after_reset() -> None:
    """was_called returns False after reset even if there were prior self-calls."""
    m = Mock()
    m()  # direct self-call sets called to True
    assert m.called
    m.reset()
    assert not m.called


@fact
def path_uses_name_value_for_root_mock() -> None:
    """Custom mock name propagates as path prefix for child entries."""
    m = Mock(name='api')
    m.users.get(1)
    assert len(m.child_calls) == 1
    assert m.child_calls[0].path == 'api.users.get'


@fact
def context_manager_clone_is_independent() -> None:
    """Context manager produces a completely independent clone."""
    parent = Mock()
    with parent as child:
        child.foo(1)

    # Clone is fully independent — no calls propagate to parent
    assert not parent.called
    assert len(parent.mock_calls) == 0
    assert len(parent.child_calls) == 0


@fact
def call_entry_repr_no_call_prefix() -> None:
    entry = Call(path='Mock.foo', args=(1, 2), kwargs={'key': 'val'})
    assert repr(entry) == 'Mock.foo((1, 2), key=\'val\')'


@fact
def call_entry_repr_empty_args_kwargs() -> None:
    entry = Call(path='Mock.foo', args=(), kwargs={})
    assert repr(entry) == 'Mock.foo()'


@fact
def call_entry_repr_no_path_root_call() -> None:
    entry = Call(path='', args=(1,), kwargs={})
    assert repr(entry) == '(1,)'


@fact
def call_entry_eq_compares_all_fields() -> None:
    e1 = Call('Mock.foo', (1,), {})
    e2 = Call('Mock.foo', (1,), {})
    e3 = Call('Mock.bar', (1,), {})
    e4 = Call('Mock.foo', (2,), {})

    assert e1 == e2
    assert e1 != e3
    assert e1 != e4


@fact
def deep_nesting_propagates_to_all_ancestors() -> None:
    """Deep call propagates full path to ancestors via child_calls."""
    m = Mock()
    m.w.x.y.z(99)

    # m.mock_calls is empty (no direct call on m itself)
    assert len(m.mock_calls) == 0
    # child_calls[0] has the full-path entry propagated from leaf
    assert len(m.child_calls) == 1
    entry = m.child_calls[0]
    assert entry.path == 'Mock.w.x.y.z'
    assert entry.args == (99,)


@fact
def child_mock_child_calls_does_not_include_self_call() -> None:
    """A mock's child_calls should not include its own direct invocations."""
    m = Mock()
    m.foo()  # direct call on foo stub

    assert len(m.child_calls) == 1  # reached via attr access
    assert m.child_calls[0].path == 'Mock.foo'

    # But foo's own child_calls is empty (no children of foo were called)
    assert len(m.foo.child_calls) == 0


@fact
def multiple_child_calls_accumulate_in_child_calls() -> None:
    """Multiple child calls accumulate separately in child_calls."""
    m = Mock()
    m.a(1)
    m.b(2)
    m.c(3)

    # mock_calls is empty (no direct self-call on m itself)
    assert len(m.mock_calls) == 0
    # child_calls tracks all children's calls with their full paths
    assert len(m.child_calls) == 3
    assert m.child_calls[0].path == 'Mock.a'
    assert m.child_calls[1].path == 'Mock.b'
    assert m.child_calls[2].path == 'Mock.c'
