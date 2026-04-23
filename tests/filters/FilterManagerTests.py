# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from punit import fact

from punit.filters.FilterManager import FilterManager


@fact
def bvt() -> None:
    target = FilterManager()
    assert 0 == len(target.filters), 'a freshly created FilterManager should not have any filters.'
    target.load('tests/filters-file.txt')
    assert 2 == len(target.filters), 'the test `filters-file.txt` should result in exactly two filters being defined.'
    target.remove('*')
    assert 1 == len(target.filters), 'expect `remove(...)` to succeed'
    target.add('*')
    assert 2 == len(target.filters), 'expect `add(...)` to succeed'
