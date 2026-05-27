#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/ee3e78b8023e711d250bb9a6af748f4e73c8e332
TITLE:       Fix collate and null processing in package constants (#9037)
DESCRIPTION:
    Initially discussed:
        https://groups.google.com/g/firebird-devel/c/5ehuR18Wemk/m/CdLvHAFAAQAJ
        https://groups.google.com/g/firebird-devel/c/kze2LTWaeco/m/s1sLoIA2AQAJ
NOTES:
    Confirmed problems on 6.0.0.1971-61d90eb (25.05.2026 21:04):
        * 'constant k_c blob ... = ' fails with  SQLSTATE = 42000 / Token error;
        * 'constant bar int = null' causes FB crash.
    Checked on 6.0.0.1971-79b12a6.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'
test_sql = f"""
    set bail OFF;
    set heading off;
    set autoddl off;
    set autoterm on;
    commit;
    create or alter package pg_const_blob1 as
    begin
        constant k_pi blob sub_type 1 = _utf8 q'#rapport de la circonférence au diamètre#' collate unicode_ci_ai collate unicode_ci_ai;
    end
    ;

    create or alter package pg_const_blob2 as
    begin
        constant k_c blob sub_type 1 character set utf8 collate unicode_ci_ai = q'#la vitesse de la lumière dans le vide#';
    end
    ;

    create or alter package pg_const_null as
    begin
        constant bar int = null;
    end
    ;
    select '{COMPLETED_MSG}' as msg from rdb$database;
"""

db = db_factory()
act = isql_act('db', test_sql)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = f"""
        {COMPLETED_MSG}
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
