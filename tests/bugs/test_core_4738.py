#coding:utf-8
#
# id:           bugs.core_4738
# title:        Command "Alter table <T> alter <C> type <domain_>" does not work: "BLR syntax error: expected valid BLR code at offset 15, encountered 255"
# decription:   
# tracker_id:   CORE-4738
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain dm_id int;
    commit;
    
    create table test(num int);
    commit;
    
    alter table test alter num type dm_id;
    commit;
    
    show table test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NUM                             (DM_ID) INTEGER Nullable
  """

@pytest.mark.version('>=2.0.7')
def test_core_4738_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

