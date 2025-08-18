#coding:utf-8

"""
ID:          9ece23d2ca
ISSUE:       https://www.sqlite.org/src/tktview/9ece23d2ca
TITLE:       Default collation sequences lost when window function added to query
DESCRIPTION:
NOTES:
    [18.08.2025] pzotov
    Checked on 6.0.0.1204, 5.0.4.1701, 4.0.7.3231, 3.0.14.33824
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;

    create collation name_coll for utf8 from unicode case insensitive;
    create domain dm_test varchar(3) character set utf8 collate name_coll;
    create table t1(a blob, b integer, c dm_test);
    insert into t1 values(1, 2, 'abc');
    insert into t1 values(3, 4, upper('abc'));

    set count on;
    select c, c = 'Abc', 0 as z from t1 order by b;
    select c, c = 'Abc', rank() over (order by b) from t1;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    C abc
    <true>
    Z 0
    C ABC
    <true>
    Z 0
    Records affected: 2
    C abc
    <true>
    RANK 1
    C ABC
    <true>
    RANK 2
    Records affected: 2
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
