#coding:utf-8
#
# id:           bugs.core_2431
# title:        String values in error messages are not converted to connection charset
# decription:
# tracker_id:   CORE-2431
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(from_backup='core2431.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    select c.rdb$character_set_name as connection_cset
    from mon$attachments a
    join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
    where a.mon$attachment_id = current_connection;

    set term ^;
    execute block as
    begin
      exception ex_bad_remainder using (-8);
    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONNECTION_CSET                 WIN1251
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_BAD_REMAINDER
    -Новый остаток изделия будет отрицательным: -8
    -At block line: 3, col: 7
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute(charset='win1251')
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

