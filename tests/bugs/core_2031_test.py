#coding:utf-8
#
# id:           bugs.core_2031
# title:        Null in the first record in a condition on rdb$db_key
# decription:   
# tracker_id:   CORE-2031
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_2031

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE A1 (
    FA1 INTEGER,
    FA2 INTEGER
);
commit;
insert into a1 (fa1, fa2) values (1, 1);
insert into a1 (fa1, fa2) values (1, 2);
insert into a1 (fa1, fa2) values (1, 3);
insert into a1 (fa1, fa2) values (1, 4);
insert into a1 (fa1, fa2) values (1, 5);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """update a1 a set a.fa1 =
(select 2 from a1 aa
where a.rdb$db_key = aa.rdb$db_key);
commit;
select * from A1;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
         FA1          FA2
============ ============
           2            1
           2            2
           2            3
           2            4
           2            5

"""

@pytest.mark.version('>=2.1.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

