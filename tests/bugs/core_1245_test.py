#coding:utf-8

"""
ID:          issue-1669
ISSUE:       1669
TITLE:       Incorrect column values with outer joins and views
DESCRIPTION:
JIRA:        CORE-1245
FBTEST:      bugs.core_1245
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE T1 (N INTEGER);
CREATE TABLE T2 (N INTEGER);
CREATE VIEW V (N1, N2, N3) AS
    select t1.n, t2.n, 3
        from t1
        full join t2
            on (t1.n = t2.n)
;

insert into t1 values (1);
insert into t1 values (2);
insert into t2 values (2);
"""

db = db_factory(init=init_script)

test_script = """select rdb$relation_id, v.rdb$db_key, v.*
    from rdb$database
    full outer join v
        on (1 = 0)
    ;
"""

act = isql_act('db', test_script)

expected_stdout = """
RDB$RELATION_ID DB_KEY                                     N1           N2           N3
=============== ================================ ============ ============ ============
         <null> 81000000010000008000000002000000            2            2            3
         <null> 00000000000000008000000001000000            1       <null>            3
            131 <null>                                 <null>       <null>       <null>

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

