#coding:utf-8
#
# id:           functional.gtcs.invalid_stream_when_use_trim
# title:        GTCS/tests/CF_ISQL_32. Statement with TRIM raises "bad BLR -- invalid stream"
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_32.script
#               
#                   Source description (Rudo Mihal, message of 2004-05-06 11:32:10; FB 1.5.1.4443):
#                   https://sourceforge.net/p/firebird/mailman/message/17016190/
#               
#                   Example for reproducing (by N. Samofatov, with UDF usage):
#                   https://sourceforge.net/p/firebird/mailman/message/17017012/
#               
#                   Checked on: 4.0.0.1804 SS; 3.0.6.33271 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('TRIM_RESULT.*', 'TRIM_RESULT')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select trim(TRAILING FROM (select max(rdb$relation_id) from rdb$database)) trim_result from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TRIM_RESULT 128
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

