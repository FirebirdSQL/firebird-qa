#coding:utf-8
#
# id:           bugs.core_3353
# title:        Predicate (blob_field LIKE ?) describes the parameter as VARCHAR(30) rather than as BLOB
# decription:   
# tracker_id:   CORE-3353
# min_versions: ['2.5.1']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set planonly;
    select rdb$procedure_source from rdb$procedures where rdb$procedure_source like ?;
    -- NB: output in 3.0 will contain values of sqltype with ZERO in bit_0,
    -- so it will be: 520 instead of previous 521.
    -- (see also: core_4156.fbt)
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set sqlda_display on;
    set planonly;
    select rdb$procedure_source from rdb$procedures where rdb$procedure_source like ?;
    -- NB: output in 3.0 will contain values of sqltype with ZERO in bit_0,
    -- so it will be: 520 instead of previous 521.
    -- (see also: core_4156.fbt)
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

