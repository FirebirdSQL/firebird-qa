#coding:utf-8
#
# id:           bugs.core_3761
# title:        Conversion error when using a blob as an argument for the EXCEPTION statement
# decription:   
# tracker_id:   CORE-3761
# min_versions: ['2.5']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """
    CREATE EXCEPTION CHECK_EXCEPTION 'Check exception';
    COMMIT;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    SET TERM ^;
    EXECUTE BLOCK AS
    BEGIN
        EXCEPTION CHECK_EXCEPTION CAST ('WORD' AS BLOB SUB_TYPE TEXT);
    END^^
    SET TERM ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -CHECK_EXCEPTION
    -WORD
    -At block line: 4, col: 2
  """

@pytest.mark.version('>=2.5.6')
def test_core_3761_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

