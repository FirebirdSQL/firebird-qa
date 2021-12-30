#coding:utf-8
#
# id:           bugs.gh_6816
# title:        Illegal output length in base64/hex_encode/decode functions
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6816
#               
#                   Confirmed wrong lengths in SQLDA output on 4.0.0.2481, 5.0.0.20.
#                   Checked on 4.0.0.2489, 5.0.0.40 -- all OK.
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!(sqltype)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set list on;
    select hex_encode(cast('' as varbinary(5))), base64_encode(cast('' as varbinary(5))) from rdb$database where 1 <> 1;
    -- produces lengths 14 & 12 with 10 & 8 expected
    select base64_decode(cast('' as varchar(4) character set utf8)), hex_decode(cast('' as varchar(4) character set utf8)) from rdb$database where 1<>1;
    -- produces lengths 12 & 8 with 3 & 2 expected
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 10 charset: 2 ASCII
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 8 charset: 2 ASCII
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 3 charset: 1 OCTETS
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 2 charset: 1 OCTETS
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
