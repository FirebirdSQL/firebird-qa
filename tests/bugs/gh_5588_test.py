#coding:utf-8
#
# id:           bugs.gh_5588
# title:        Support full SQL standard binary string literal syntax [CORE5311]
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/5588
#               
#                   Checked on intermediate build 5.0.0.22.
#                
# tracker_id:   
# min_versions: ['5.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 5.0
# resources: None

substitutions_1 = [('line\\s+\\d+,\\s+col.*', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set blob all;
    set list on;
    select x'01AB' as good_bin_literal_1 from rdb$database;

    select x' 0 1 a b' as good_bin_literal_2 from rdb$database;

    select x'01' 'ab' as good_bin_literal_3 from rdb$database;

    select x'01'/*comment*/'a b' as good_bin_literal_4 from rdb$database;

    select x'01' 'ab' /*comment*/ 'ff00' as good_bin_literal_5 from rdb$database;

    select x'01' -- comment and newline
    'ab' as good_bin_literal_6
    from rdb$database;


    select x'0                                                                                                                                              1' -- comment and newline



    /*
    foo
    --*/
    /**/
    /*
    */





       																											'ab'

    /*
    bar
    --*/


       																																	'cd'
    as good_bin_literal_7
    from rdb$database;

    select x'ab''cd' as poor_bin_literal_1 from rdb$database; -- should not be valid.

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    GOOD_BIN_LITERAL_1              01AB
    GOOD_BIN_LITERAL_2              01AB
    GOOD_BIN_LITERAL_3              01AB
    GOOD_BIN_LITERAL_4              01AB
    GOOD_BIN_LITERAL_5              01ABFF00
    GOOD_BIN_LITERAL_6              01AB
    GOOD_BIN_LITERAL_7              01ABCD
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 13
    -'cd'
"""

@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

    assert act_1.clean_stdout == act_1.clean_expected_stdout
