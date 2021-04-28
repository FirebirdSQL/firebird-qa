#coding:utf-8
#
# id:           bugs.core_4569
# title:        BIN_SHL and BIN_SHR does not work in Dialect 1
# decription:   
# tracker_id:   CORE-4569
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    set list on;
    select bin_shl(1073741824, 2) bin_shl from rdb$database
    union all
    select bin_shl(1, 32) from rdb$database
    union all
    select bin_shl(0, 1) from rdb$database
    union all
    select bin_shl(-1073741824, 2) from rdb$database
    union all
    select bin_shl(-1, 32) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    BIN_SHL                         4294967296
    BIN_SHL                         4294967296
    BIN_SHL                         0
    BIN_SHL                         -4294967296
    BIN_SHL                         -4294967296
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

