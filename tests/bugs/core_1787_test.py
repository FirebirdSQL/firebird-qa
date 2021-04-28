#coding:utf-8
#
# id:           bugs.core_1787
# title:        Consistency check when subquery is ordered by aggregate function from other context
# decription:   
# tracker_id:   CORE-1787
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST_TABLE1
(ID BIGINT,
 FK_ID INTEGER,
 REG_DATE TIMESTAMP NOT NULL);

COMMIT;

insert into test_table1 values (1,5,'01.01.2000');
insert into test_table1 values (2,5,'01.01.2001');
insert into test_table1 values (3,7,'01.01.2002');
insert into test_table1 values (4,8,'01.01.2003');
insert into test_table1 values (5,8,'01.01.2004');
insert into test_table1 values (6,8,'01.01.2005');
insert into test_table1 values (7,8,'01.01.2007');

COMMIT;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select t.fk_id,(select first 1 t1.reg_date from test_table1 t1 where t1.fk_id = t.fk_id
                order by min(t.fk_id))
from test_table1 t
group by t.fk_id;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
       FK_ID                  REG_DATE
============ =========================
           5 2000-01-01 00:00:00.0000
           7 2002-01-01 00:00:00.0000
           8 2003-01-01 00:00:00.0000

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

