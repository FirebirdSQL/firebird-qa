#coding:utf-8
#
# id:           bugs.core_1533
# title:        JOIN on first record of ordered derived table returns wrong record
# decription:   
# tracker_id:   CORE-1533
# min_versions: []
# versions:     2.0.4
# qmid:         bugs.core_1533

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.4
# resources: None

substitutions_1 = []

init_script_1 = """create table X (
    ID integer,
    DAT DATE
);
commit;
insert into X (ID, DAT) values (1, '2006-05-16');
insert into X (ID, DAT) values (2, '2004-11-16');
insert into X (ID, DAT) values (3, '2007-01-01');
insert into X (ID, DAT) values (4, '2005-07-11');
commit;
create index IDX_X on X (DAT);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select X2.ID, x1.ID,x2.dat from X as X2 left join (select first 1 X.ID from X order by X.DAT) X1 on X1.ID=X2.ID;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID           ID         DAT
============ ============ ===========
           1       <null> 2006-05-16
           2            2 2004-11-16
           3       <null> 2007-01-01
           4       <null> 2005-07-11

"""

@pytest.mark.version('>=2.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

