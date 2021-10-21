#coding:utf-8
#
# id:           bugs.core_5341
# title:        User collate doesn't work with blobs
# decription:
#                  Reproduced bug on 3.0.1.32594.
#                  All fine on WI-V3.0.1.32596, WI-T4.0.0.366.
#
# tracker_id:   CORE-5341
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = [('BLOB_ID.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
    begin
      execute statement 'drop collation pxw_cyrl_ci_ai';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    create collation pxw_cyrl_ci_ai for win1251 from pxw_cyrl case insensitive accent insensitive;
    commit;

    set list on;
    set count on;

    with A as(
      select cast('update' as blob sub_type text) as blob_id from rdb$database
      union all
      select 'UPDATE' from rdb$database
    )
    select * from a
    where blob_id collate PXW_CYRL_CI_AI like '%update%';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    update
    UPDATE
    Records affected: 2
  """

@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.charset = 'WIN1251'
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

