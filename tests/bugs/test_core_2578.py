#coding:utf-8
#
# id:           bugs.core_2578
# title:        select rdb$db_key from a view with a more than 1 table joined, results in conversion error
# decription:   
# tracker_id:   CORE-2578
# min_versions: []
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TABLE_A (
    F_A INTEGER,
    F_B INTEGER
);

CREATE TABLE TABLE_B(
    F_A INTEGER,
    F_C INTEGER
);

CREATE VIEW VIEW_A(
    K1,
    K2,
    F_A,
    F_B,
    F_C)
AS
select A.rdb$db_key, B.rdb$db_key, A.F_A, A.F_B, B.F_C from table_A A
left join table_B B on A.F_A = B.F_A;

commit;

insert into TABLE_A (F_A,F_B) values (1,1) ;
insert into TABLE_B (F_A,F_C) values (1,1) ;
commit;

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select rdb$db_key from VIEW_A order by 1 ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
DB_KEY
================================
81000000010000008000000001000000

"""

@pytest.mark.version('>=2.1.4')
def test_core_2578_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

