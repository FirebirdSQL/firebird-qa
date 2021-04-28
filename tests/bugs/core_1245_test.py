#coding:utf-8
#
# id:           bugs.core_1245
# title:        Incorrect column values with outer joins and views
# decription:   
# tracker_id:   CORE-1245
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (N INTEGER);
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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select rdb$relation_id, v.rdb$db_key, v.*
    from rdb$database
    full outer join v
        on (1 = 0)
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
RDB$RELATION_ID DB_KEY                                     N1           N2           N3
=============== ================================ ============ ============ ============
         <null> 81000000010000008000000002000000            2            2            3
         <null> 00000000000000008000000001000000            1       <null>            3
            131 <null>                                 <null>       <null>       <null>

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

