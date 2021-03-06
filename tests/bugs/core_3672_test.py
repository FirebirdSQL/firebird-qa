#coding:utf-8
#
# id:           bugs.core_3672
# title:        computed index by substring function for long columns
# decription:   
# tracker_id:   CORE-3672
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
         col1 varchar(8190) character set utf8 collate unicode_ci_ai
        ,col2 computed by ( substring(col1 from 1 for 169) )
        ,col3 computed by ( substring(trim( col2 from col1 ) from 1 for 169) )
    );
    commit;

    -- Index on UTF8-field which should be collate in CI_AI manner, will contain 6 bytes per one character (hereafter this is 'N').
    -- This mean that maximum length of key for default page_size = 4096 is: 
    -- max_key_length = floor( (page_size / 4 - 9) / N ) = 169 characters.

    -- Verify that we CAN do that w/o error:
    create index test_col1_idx_a on test computed by ( substring(col1 from 1 for 169) );
    create index test_col1_idx_b on test computed by ( substring(trim( col2 from col1 ) from 1 for 169) );
    create index test_col2_idx_a on test computed by ( col2 );
    create index test_col2_idx_b on test computed by ( substring(col2 from 1 for 169) );
    create index test_col3_idx_a on test computed by ( col3 );
    create index test_col3_idx_b on test computed by ( substring(col3 from 1 for 169) );
    commit;
    -- Confirmed for 2.5.5: "-key size exceeds implementation restriction"

    show index test_col1_idx_a;
    show index test_col1_idx_b;
    show index test_col2_idx_a;
    show index test_col2_idx_b;
    show index test_col3_idx_a;
    show index test_col3_idx_b;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST_COL1_IDX_A INDEX ON TEST COMPUTED BY ( substring(col1 from 1 for 169) )
    TEST_COL1_IDX_B INDEX ON TEST COMPUTED BY ( substring(trim( col2 from col1 ) from 1 for 169) )
    TEST_COL2_IDX_A INDEX ON TEST COMPUTED BY ( col2 )
    TEST_COL2_IDX_B INDEX ON TEST COMPUTED BY ( substring(col2 from 1 for 169) )
    TEST_COL3_IDX_A INDEX ON TEST COMPUTED BY ( col3 )
    TEST_COL3_IDX_B INDEX ON TEST COMPUTED BY ( substring(col3 from 1 for 169) )
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

