#coding:utf-8
#
# id:           bugs.core_0099
# title:        Strange/Inconsistent query results
# decription:
# tracker_id:   CORE-99
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_99

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """create table T1 (F1 char(4), F2 char(4));
create index T1_F1 on T1 (F1);

insert into T1 (F1, F2) values ('001', '001');
insert into T1 (F1, F2) values ('002', '002');
insert into T1 (F1, F2) values ('003', '003');
insert into T1 (F1, F2) values ('004', '004');

commit;
"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """select * from t1 where f1 = 3;
select * from t1 where f2 = 3;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """F1     F2
====== ======
003    003

F1     F2
====== ======
003    003

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

