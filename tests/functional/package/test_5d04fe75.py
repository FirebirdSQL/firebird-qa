#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9039
TITLE:       Fix constant status check for BoolExprNode #9039
DESCRIPTION:
    Source description:
    https://groups.google.com/g/firebird-devel/c/mtPIIHhd95c/m/mGvQuh_OAQAJ
    ("Declaration of package constants as expressions")
NOTES:
    Confirmed problem on 6.0.0.1971-61d90eb (25.05.2026 21:04), get:
        Statement failed, SQLSTATE = 42000
        CREATE OR ALTER PACKAGE "PUBLIC"."PG_CONST_IIF0" failed
        -The constant "PUBLIC"."PG_CONST_IIF0"."K_IIF" must be initialized by a constant expression
    Checked on 6.0.0.1971-79b12a6.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'
test_sql = f"""
    set bail on;
    set heading off;
    set autoddl off;
    set autoterm on;
    commit;
    create or alter package pg_const_iif0 as
    begin
        constant k_iif int = iif(0 > 3, 1, 0);
    end
    ;
    create or alter package pg_const_iif1 as
    begin
        constant k_iif int = iif(pi() > 3, 1, 0);
    end
    ;
    create or alter package pg_const_iif2 as
    begin
        constant k_iif int = iif(sign(pi()) > 0, 55, -33);
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
