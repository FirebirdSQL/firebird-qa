#coding:utf-8
#
# id:           bugs.core_1019
# title:        Make information available regading ODS Version and Dialect via SQL
# decription:   
# tracker_id:   CORE-1019
# min_versions: []
# versions:     2.5.0
# qmid:         bugs.core_1019-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    -- Refactored 05-may-2018, to be universal for all possible ODS numbers:
    select 
          iif( mon$ods_major similar to '[[:digit:]]{1,2}', 'YES', 'NO!') as "ods_major_looks_ok ?"
        , iif( mon$ods_minor similar to '[[:digit:]]{1,2}', 'YES', 'NO!') as "ods_minor_looks_ok ?"
        , iif( mon$sql_dialect similar to '[[:digit:]]{1}', 'YES', 'NO!') as "sql_dialect_looks_ok ?"
    from mon$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ods_major_looks_ok ?            YES
    ods_minor_looks_ok ?            YES
    sql_dialect_looks_ok ?          YES
 """

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

