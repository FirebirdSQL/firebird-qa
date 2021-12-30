#coding:utf-8
#
# id:           bugs.gh_6998
# title:        Problems with access to RDB$CONFIG table for non-privileged user when he has grant on execution of SP which has necessary access rights (created by SYSDBA with SQL DEFINER clause)
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6998
#               
#                   Confirmed ticket issue on 5.0.0.243.
#                   Checked on: 5.0.0.244, 4.0.1.2625, SS/CS, intermediate build (09-oct-2021 06:39).
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
    set bail on;
    set list on;
    create or alter user tmp$gh_6998 password '123' revoke admin role;
    commit;

    set term ^;
    create or alter procedure sp_check_rdb$config_avaliable
        returns (cnt int)
        sql security definer
    as
    begin
        select count(*) from rdb$config into cnt;
        suspend;
    end
    ^
    set term ;^
    commit;

    grant execute on procedure sp_check_rdb$config_avaliable to user tmp$gh_6998;
    commit;

    connect '$(DSN)' user tmp$gh_6998 password '123';
    commit;
    
    select current_user as who_am_i, sign(p.cnt) as is_rdb$config_avaliable
    from sp_check_rdb$config_avaliable p;
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$gh_6998;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP$GH_6998
    IS_RDB$CONFIG_AVALIABLE         1
"""

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
