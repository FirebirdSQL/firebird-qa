#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8912
TITLE:       Context variables clear/re-initialization support
DESCRIPTION:
NOTES:
    [29.03.2026] pzotov
    Checked on 6.0.0.1858; 5.0.4.1791.
"""
import pytest
from firebird.qa import *

db = db_factory()

CTX_MAX_COUNT = 1000
test_script = f"""
    set bail on;
    set list on;
    set term ^;
    execute block as
        declare i smallint = 0;
        declare n smallint = {CTX_MAX_COUNT};
    begin
        while (i < n) do
        begin
            rdb$set_context('USER_SESSION', 'ATT_VAR_' || i, i);
            rdb$set_context('USER_TRANSACTION', 'TRN_VAR_' || i, i);
            i = i + 1;
        end
    end ^
    set term ;^
    select count(mon$attachment_id) as init_att_cnt, count(mon$transaction_id) as init_trn_cnt from mon$context_variables;
    -- must pass w/o errors:
    select rdb$reset_context('USER_SESSION') as drop_att_cnt, rdb$reset_context('USER_TRANSACTION') as drop_trn_cnt from rdb$database;
    commit;
    -- both must be zero:
    select count(mon$attachment_id) as curr_att_cnt, count(mon$transaction_id) as curr_trn_cnt from mon$context_variables;
    commit;
    set bail off;
    -- following must fail:
    select rdb$reset_context('SYSTEM') as drop_sys_cnt from rdb$database;
    select rdb$reset_context('DDL_TRIGGER') as drop_ddl_cnt from rdb$database;
    select rdb$reset_context(null) as drop_null_cnt from rdb$database;
    select rdb$reset_context('') as drop_empty_cnt from rdb$database;
    select rdb$reset_context('UNKNOWN_NAMESPACE') as drop_unkn_cnt from rdb$database;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = f"""
    INIT_ATT_CNT {CTX_MAX_COUNT}
    INIT_TRN_CNT {CTX_MAX_COUNT}
    
    DROP_ATT_CNT {CTX_MAX_COUNT}
    DROP_TRN_CNT {CTX_MAX_COUNT}
    
    CURR_ATT_CNT 0
    CURR_TRN_CNT 0

    Statement failed, SQLSTATE = HY000
    Invalid namespace name 'SYSTEM' passed to RDB$RESET_CONTEXT
    
    Statement failed, SQLSTATE = HY000
    Invalid namespace name 'DDL_TRIGGER' passed to RDB$RESET_CONTEXT
    
    Statement failed, SQLSTATE = HY000
    Invalid argument passed to RDB$RESET_CONTEXT
    
    Statement failed, SQLSTATE = HY000
    Invalid namespace name '' passed to RDB$RESET_CONTEXT
    
    Statement failed, SQLSTATE = HY000
    Invalid namespace name 'UNKNOWN_NAMESPACE' passed to RDB$RESET_CONTEXT
"""

@pytest.mark.version('>=5.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
