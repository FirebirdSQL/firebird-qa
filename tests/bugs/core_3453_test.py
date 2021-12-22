#coding:utf-8
#
# id:           bugs.core_3453
# title:        Added not null timestamp col with default causes error on select of old null records
# decription:   
# tracker_id:   CORE-3453
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table "Temp" ("Dummy" int);
    commit;
    insert into "Temp" ("Dummy") values (1);
    commit;
    alter table "Temp" add "New" timestamp default '0001-01-01' not null;
    commit;
    set list on;
    select * from "Temp";
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Dummy                           1
    New                             0001-01-01 00:00:00.0000
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

