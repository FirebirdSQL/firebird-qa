#coding:utf-8
#
# id:           bugs.core_4075
# title:        Server bugchecks or crashes on exception in calculated index
# decription:   
#                    18.10.2016: added test case from CORE-4603.
#                    NB: 2.5.x output contains TWO lines with error message, i.e.:
#                        Statement failed, SQLSTATE = 22018
#                        conversion error from string "2014.02.33"
#                        -conversion error from string "2014.02.33"
#                    Decided to suppress second line because its unlikely to be fixed
#                    (after get reply from dimitr, letter 18.10.2016 18:47).
#               
#                    16.09.2017: added separate section for 4.0 because STDERR now
#                    contains name of index that causes problem - this is so after core-5606 
#                    was implemented ("Add expression index name to exception message ...")
#                    Checked on: build 4.0.0.744: OK, 1.500s.
#                
# tracker_id:   CORE-4075
# min_versions: ['2.5.4']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table TEST (BIT smallint);
    create index IDX_TEST_BIT on TEST computed by (bin_shl(1, TEST.BIT-1));

    -- from CORE-4603:
    recreate table T_TABLE (
        F_YEAR varchar(4),
        F_MONTH_DAY varchar(5)
    );
    create index T_INDEX on T_TABLE computed by (cast(F_YEAR || '.' || F_MONTH_DAY as date));
    commit;

  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    insert into test values (0); 

    -- from core-4603:
    insert into T_TABLE (F_YEAR, F_MONTH_DAY) values ('2014', '02.33');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Expression evaluation error for index "IDX_TEST_BIT" on table "TEST"
    -expression evaluation not supported
    -Argument for BIN_SHL must be zero or positive

    Statement failed, SQLSTATE = 22018
    Expression evaluation error for index "T_INDEX" on table "T_TABLE"
    -conversion error from string "2014.02.33"
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

