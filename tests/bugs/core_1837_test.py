#coding:utf-8
#
# id:           bugs.core_1837
# title:        Procedure text is stored truncated in system tables if any variable have default value
# decription:   
# tracker_id:   CORE-1837
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = [('RDB\\$PROCEDURE_SOURCE.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure sp_test
    as
    declare x int = 0;
    begin
      exit;
    end ^
    commit ^

    set list on ^
    set blob all ^
    select p.rdb$procedure_source from rdb$procedures p where p.rdb$procedure_name = upper('sp_test') ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$PROCEDURE_SOURCE            1a:0
    declare x int = 0;
    begin
      exit;
    end
  """

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

