#coding:utf-8
#
# id:           bugs.core_2741
# title:        Naive metadata extraction code in isql is defeated by "check" keyword typed in mixed case
# decription:   
# tracker_id:   CORE-2741
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain dm_int int cHeCk(vAlUE<>0);
    create domain dm_dts timestamp cHeCk(valUe<>cUrrent_timEstamp);
    commit;
    show domain dm_int;
    show domain dm_dts;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DM_INT                          INTEGER Nullable
                                    cHeCk(vAlUE<>0)
    DM_DTS                          TIMESTAMP Nullable
                                    cHeCk(valUe<>cUrrent_timEstamp)
  """

@pytest.mark.version('>=2.5')
def test_core_2741_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

