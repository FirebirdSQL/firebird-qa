#coding:utf-8

"""
ID:          issue-1475
ISSUE:       1475
TITLE:       A query could produce different results, depending on the presence of an index
DESCRIPTION:
JIRA:        CORE-1056
FBTEST:      bugs.core_1056
"""

import pytest
from firebird.qa import *

init_script = """create table t (c varchar(10) character set win1250 collate pxw_csy);
insert into t values ('ch');
commit;
"""

db = db_factory(init=init_script)

test_script = """set plan on;

select * from t where c starting with 'c';
commit;

create index t_c on t (c);
commit;

select * from t where c starting with 'c';
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T NATURAL)

C
==========
ch


PLAN (T INDEX (T_C))

C
==========
ch

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

