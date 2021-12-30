#coding:utf-8
#
# id:           bugs.gh_6797
# title:        DECRYPT() must return BLOB if its first argument is blob, otherwise returnted datatype must be VARCHAR with charset NONE
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6797
#               
#                   NOTE: as of current FB 4.x doc, following is wrong: "Functions return ... *varbinary* for all other types."
#                   (see note by Alex in the tracker, 11.05.2021 11:17).
#               
#                   Checked on 4.0.0.2479; 5.0.0.20
#               
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
    set blob all;
    set list on;
    set sqlda_display on;
    set planonly;
    select
        decrypt(cast('' as varchar(1)) using aes mode ofb key '0123456701234567' iv '1234567890123456') as decrypt_vchr
       ,decrypt(cast('' as blob) using aes mode ofb key '0123456701234567' iv '1234567890123456') as decrypt_blob
    from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 1 charset: 1 OCTETS
    02: sqltype: 520 BLOB scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
