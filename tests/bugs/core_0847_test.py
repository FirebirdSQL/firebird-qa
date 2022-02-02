#coding:utf-8

"""
ID:          issue-1236
ISSUE:       1236
TITLE:       Computed field can't be changed to non-computed using 'alter table alter column type xy'
DESCRIPTION:
JIRA:        CORE-847
FBTEST:      bugs.core_0847
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table t (
      f1 varchar(10),
      f2 varchar(10),
      cf computed by (f1 || ' - ' || f2)
    );

    insert into t (f1,f2) values ('0123456789','abcdefghij');
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set blob off;
    set list on;

    select f1,f2,cf as cf_before_altering from t;

    select b.rdb$field_name field_name, cast(a.rdb$computed_source as varchar(80)) computed_source_before_altering
    from rdb$fields a
    join rdb$relation_fields b  on a.rdb$field_name = b.rdb$field_source
    where b.rdb$field_name = upper('CF');

    alter table t alter cf type varchar(30);
    commit;

    select f1,f2,cf as cf_after_altering from t;

    select b.rdb$field_name field_name, cast(a.rdb$computed_source as varchar(80)) computed_source_after_altering
    from rdb$fields a
    join rdb$relation_fields b  on a.rdb$field_name = b.rdb$field_source
    where b.rdb$field_name = upper('CF');
"""

act = isql_act('db', test_script)

expected_stdout = """
    F1                              0123456789
    F2                              abcdefghij
    CF_BEFORE_ALTERING              0123456789 - abcdefghij

    FIELD_NAME                      CF
    COMPUTED_SOURCE_BEFORE_ALTERING (f1 || ' - ' || f2)

    F1                              0123456789
    F2                              abcdefghij
    CF_AFTER_ALTERING               0123456789 - abcdefghij

    FIELD_NAME                      CF
    COMPUTED_SOURCE_AFTER_ALTERING  (f1 || ' - ' || f2)
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER TABLE T failed
    -Cannot add or remove COMPUTED from column CF
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

