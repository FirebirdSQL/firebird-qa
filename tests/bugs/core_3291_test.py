#coding:utf-8
#
# id:           bugs.core_3291
# title:        New pseudocolumn (RDB$RECORD_VERSION) to get number of the transaction that created a record version
# decription:   
# tracker_id:   CORE-3291
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test(id int);
    insert into test values(1) returning current_transaction - rdb$record_version as diff_ins;
    commit;
    update test set id=-id returning current_transaction - rdb$record_version as diff_upd;
    commit;
    delete from test returning sign(current_transaction - rdb$record_version) as diff_del;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DIFF_INS                        0
    DIFF_UPD                        0
    DIFF_DEL                        1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

