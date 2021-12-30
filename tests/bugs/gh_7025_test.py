#coding:utf-8
#
# id:           bugs.gh_7025
# title:        Results of negation must be the same for each datatype (smallint / int /bigint / int128) when argument is least possible value for this type
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/7025
#               
#                   Confirmed 'sqltype: 496 LONG' for -(-2147483648). Before fix was: '580 INT64'.
#                   Checked on 5.0.0.300.
#                
# tracker_id:   
# min_versions: ['5.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 5.0
# resources: None

substitutions_1 = [('^((?!sqltype:|NEG_OF_2P|SQLSTATE|overflow).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set sqlda_display on;
    select -(-32768) as neg_of_2p15 from rdb$database;
    select -(-2147483648) as neg_of_2p31 from rdb$database;
    select -(-9223372036854775808) as neg_of_2p63 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    :  name: CONSTANT  alias: NEG_OF_2P15

    NEG_OF_2P15                     32768

    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
    :  name: CONSTANT  alias: NEG_OF_2P31

    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    :  name: CONSTANT  alias: NEG_OF_2P63
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.

    Statement failed, SQLSTATE = 22003
    Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.
"""

@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout
