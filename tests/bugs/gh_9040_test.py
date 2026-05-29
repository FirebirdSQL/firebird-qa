#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9040
TITLE:       SIMILAR TO does not work with wildcard combined with OR operator
DESCRIPTION:
NOTES:
    [29.05.2026]
    Confirmed bug on 6.0.0.1971-79b12a6.
    Checked on 6.0.0.1975-bfb596a; 5.0.5.1826-d65849c.
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """
    set list on;

    recreate table test(nm varchar(50));
    insert into test(nm) values('95450');
    insert into test(nm) values('97008');

    set count on;
    select 'case-01' as msg, nm from test where nm similar to '95450|97008' order by 1; -- works ok
    select 'case-02' as msg, nm from test where nm similar to '9545_|97008' order by 1;  -- does not find 97008
    select 'case-03' as msg, nm from test where nm similar to '95450|9700_' order by 1;  -- ok
    select 'case-04' as msg, nm from test where nm similar to '95_+|97008' order by 1;  -- does not find 97008
    select 'case-05' as msg, nm from test where nm similar to '95[[:digit:]]+|97008' order by 1;  -- does not find 97008

"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    MSG case-01
    NM 97008
    MSG case-01
    NM 95450
    Records affected: 2

    MSG case-02
    NM 97008
    MSG case-02
    NM 95450
    Records affected: 2

    MSG case-03
    NM 97008
    MSG case-03
    NM 95450
    Records affected: 2

    MSG case-04
    NM 97008
    MSG case-04
    NM 95450
    Records affected: 2

    MSG case-05
    NM 97008
    MSG case-05
    NM 95450
    Records affected: 2
"""

@pytest.mark.version('>=5.0.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
