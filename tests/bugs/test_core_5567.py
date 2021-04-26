#coding:utf-8
#
# id:           bugs.core_5567
# title:        Direct system table modifications are not completely prohibited
# decription:   
#                   30SS, build 3.0.3.32738: OK, 0.828s.
#                   40SS, build 4.0.0.680: OK, 0.938s.
#                
# tracker_id:   CORE-5567
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = [('line: [\\d]+, col: [\\d]+', ''), ('.*At block.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
    begin
      execute statement 'drop domain dm_test';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    create domain dm_test numeric(18, 2);
    commit;

    set term ^;
    execute block as
        declare procedure hack as
        begin
            update rdb$fields set rdb$field_scale = -3 where rdb$field_name = upper('dm_test');
        end
    begin
        execute procedure hack;
    end
    ^
    set term ;^
    commit;

    set list on;
    select ff.rdb$field_scale domain_precision
    from rdb$fields ff
    where ff.rdb$field_name = upper('dm_test')
    ;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DOMAIN_PRECISION                -2
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    UPDATE operation is not allowed for system table RDB$FIELDS
    -At sub procedure 'HACK'
  """

@pytest.mark.version('>=3.0.3')
def test_core_5567_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

