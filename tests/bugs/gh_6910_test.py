#coding:utf-8
#
# id:           bugs.gh_6910
# title:        Add way to retrieve statement BLR with Statement::getInfo and ISQL's SET EXEC_PATH_DISPLAY BLR
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6910
#               
#                   Test issues 'set exec_path_display blr' and runs empty EXECUTE BLOCK, then it does reconnect
#                   and run empty EB again.
#               
#                   We verify that:
#                   * BLR-statements are issued for this EB;
#                     ( https://github.com/FirebirdSQL/firebird/commit/55704efd24b706272211f921d69db602e838ea38 )
#                   * state of 'set exec_path_display blr' command will not change after reconnect.
#                     ( https://github.com/FirebirdSQL/firebird/commit/32c3cf573bf36f576b6116983786107df5a2cb33 )
#               
#                   Checked on: 5.0.0.264, 4.0.1.2554 -- all OK.
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set exec_path_display blr;
    set term ^;

    execute block as
    begin

    end^
    commit^

    connect '$(DSN)' user sysdba password 'masterkey'^

    execute block as
    begin

    end^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Execution path (BLR):
    0 blr_version5,
    1 blr_begin,
    2    blr_message, 1, 1,0,
    6       blr_short, 0,
    8    blr_begin,
    9       blr_stall,
    10       blr_label, 0,
    12          blr_begin,
    13             blr_end,
    14       blr_end,
    15    blr_send, 1,
    17       blr_begin,
    18          blr_assignment,
    19             blr_literal, blr_short, 0, 0,0,
    24             blr_parameter, 1, 0,0,
    28          blr_end,
    29    blr_end,
    30 blr_eoc
    Execution path (BLR):
    0 blr_version5,
    1 blr_begin,
    2    blr_message, 1, 1,0,
    6       blr_short, 0,
    8    blr_begin,
    9       blr_stall,
    10       blr_label, 0,
    12          blr_begin,
    13             blr_end,
    14       blr_end,
    15    blr_send, 1,
    17       blr_begin,
    18          blr_assignment,
    19             blr_literal, blr_short, 0, 0,0,
    24             blr_parameter, 1, 0,0,
    28          blr_end,
    29    blr_end,
    30 blr_eoc
"""

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
