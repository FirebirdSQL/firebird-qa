#coding:utf-8

"""
ID:          issue-1939
ISSUE:       1939
TITLE:       Computed field + index not working in WHERE
DESCRIPTION:
JIRA:        CORE-1525
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table test_1 (
      id integer not null,
      last_day date,
      comp_last_day computed by (coalesce(last_day, cast('2999-12-31' as date)))
    );


    insert into test_1 values (1, '2007-10-10');
    insert into test_1 values (2, null);
    commit;

    set list on;

    select *
    from test_1
    where cast ('2007-09-09' as date) < comp_last_day;

    create index idx_1 on test_1 computed by ( coalesce(last_day, cast('2999-12-31' as date)) );
    commit;
    set plan on;

    select *
    from test_1
    where cast ('2007-09-09' as date) < comp_last_day;
"""

act = isql_act('db', test_script)

expected_stdout = """
    ID                              1
    LAST_DAY                        2007-10-10
    COMP_LAST_DAY                   2007-10-10
    ID                              2
    LAST_DAY                        <null>
    COMP_LAST_DAY                   2999-12-31

    PLAN (TEST_1 INDEX (IDX_1))

    ID                              1
    LAST_DAY                        2007-10-10
    COMP_LAST_DAY                   2007-10-10
    ID                              2
    LAST_DAY                        <null>
    COMP_LAST_DAY                   2999-12-31
"""

@pytest.mark.version('>=2.0.7')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

