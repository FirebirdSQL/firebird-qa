#coding:utf-8
#
# id:           bugs.core_3502
# title:        DROP VIEW ignores the existing non-column dependencies
# decription:   
# tracker_id:   CORE-3502
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """
    set autoddl on;
    commit;
    create or alter procedure p as begin end;
    commit;
    
    create or alter view v (id) as select rdb$relation_id from rdb$database;
    commit;
    
    set term ^;
    create or alter procedure p as
      declare id int;
    begin
      select id from v rows 1 into id;
    end^
    set term ;^
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    execute procedure p;
    commit;
    drop view v;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN V.ID
    -there are 1 dependencies
  """

@pytest.mark.version('>=2.5.1')
def test_core_3502_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

