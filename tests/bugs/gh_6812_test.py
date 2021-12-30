#coding:utf-8
#
# id:           bugs.gh_6812
# title:        BASE64_ENCODE and HEX_ENCODE can exceed maximum widths for VARCHAR
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6812
#               
#                   Confirmed bug on 4.0.0.2489, 5.0.0.40.
#                   Checked on 4.0.0.2490, 5.0.0.42 - all OK.
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!(sqltype|enc)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    select hex_encode(cast('' as char(32767))) as "enc_01" from rdb$database where 1 <> 1;
    select base64_encode(cast('' as char(32767))) as "enc_02" from rdb$database where 1 <> 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 520 BLOB scale: 0 subtype: 1 len: 8 charset: 2 ASCII
    :  name: HEX_ENCODE  alias: enc_01
    01: sqltype: 520 BLOB scale: 0 subtype: 1 len: 8 charset: 2 ASCII
    :  name: BASE64_ENCODE  alias: enc_02
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
