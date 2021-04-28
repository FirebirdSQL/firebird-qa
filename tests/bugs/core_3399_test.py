#coding:utf-8
#
# id:           bugs.core_3399
# title:        Allow write operations to temporary tables in read only transactions
# decription:   
# tracker_id:   CORE-3399
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(from_backup='core3399-read_only.fbk', init=init_script_1)

test_script_1 = """
    -- ======= from the ticket: ========
    -- Implementation allows:
    -- 1) writes into all kind of GTT's in read only transactions in read write database 
    -- and also 
    -- 2) make writabe GTT ON COMMIT DELETE in read only transactions in read only database.
    -- =================================
    -- Database will be in the state "force write, no reserve, read only".
    -- This test verifies only SECOND issue from ticket: allow GTT with attribute "on commit DELETE rows"
    -- to be writeable when database is READ-ONLY.
    commit;
    set transaction read only;
    insert into gtt_del_rows(id) values(1);
    select * from gtt_del_rows;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
         ID
    =======
          1 
  """

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

