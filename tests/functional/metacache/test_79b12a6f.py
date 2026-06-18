#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/79b12a6fc86f57827309b922f689043e78899701
TITLE:       Ensure base relation pages are filled when index to be marked for deletion
DESCRIPTION:
NOTES:
    [19.06.2026] pzotov
    The bug has been found occasionally during analysis of fail reason of test for CORE-5036.
    Discussed with Alex, starting letter 28.04.2026 00:13 ("CORE-5036: weird outcome with 'DROP INDEX' and subsequent error code in DDL...")
    Bug has been fixed in #79b12a6 27.05.2026 19:13:23 ("Ensure base relation pages are filled when index to be marked for deletion")
    Confirmed problem on 6.0.0.1971-ee3e78b (27.05.2026 11:15:35).
    Checked on 6.0.0.1971-79b12a6.
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'

db = db_factory() # charset = 'utf8')
act = isql_act('db')

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    TAB_NAME = 'test'.upper()
    test_sql = f"""
        recreate table {TAB_NAME}(
            id int
            ,x int
            ,y int
            ,r double precision
            ,s varchar(64) default 'DB_NAME'
        );
         
        create index {TAB_NAME}_eval1 on {TAB_NAME} computed by ( x/id );
        insert into {TAB_NAME}(id, x) values(0, 1);
        rollback;

        drop index {TAB_NAME}_eval1;
         
        create index {TAB_NAME}_eval2 on {TAB_NAME} computed by ( log10(r-15) );
        insert into {TAB_NAME}(id, r) values(1, 12);
        rollback;
        drop index {TAB_NAME}_eval2;
         
        create index {TAB_NAME}_eval3 on {TAB_NAME} computed by ( rdb$get_context('SYSTEM', s ) );
        insert into {TAB_NAME}(id, s) values(2, 'KHREN_ZNAYET_4TO');
        rollback;
        drop index {TAB_NAME}_eval3;
         
        create index {TAB_NAME}_eval4 on {TAB_NAME} computed by ( mod(x , (y-x) ) );
        insert into {TAB_NAME}(id, x, y) values(3, 10, 10);
        rollback;
        drop index {TAB_NAME}_eval4;
         
        create index {TAB_NAME}_eval5 on {TAB_NAME} computed by ( substring(s from x for id+y)  );
        insert into {TAB_NAME}(id, x, y, s) values( 4, 3, -7, 'qwerty' );
        drop index {TAB_NAME}_eval5;
         
        set count on;
        set list on;
        select id, s from {TAB_NAME};
        rollback;
    """

    act.expected_stdout = f"""
        Statement failed, SQLSTATE = 22012
        Expression evaluation error for index "PUBLIC"."{TAB_NAME}_EVAL1" on table "PUBLIC"."{TAB_NAME}"
        -arithmetic exception, numeric overflow, or string truncation
        -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.

        Statement failed, SQLSTATE = 42000
        Expression evaluation error for index "PUBLIC"."{TAB_NAME}_EVAL2" on table "PUBLIC"."{TAB_NAME}"
        -expression evaluation not supported
        -Argument for LOG10 must be positive

        Statement failed, SQLSTATE = HY000
        Expression evaluation error for index "PUBLIC"."{TAB_NAME}_EVAL3" on table "PUBLIC"."{TAB_NAME}"
        -Context variable 'KHREN_ZNAYET_4TO' is not found in namespace 'SYSTEM'

        Statement failed, SQLSTATE = 22012
        Expression evaluation error for index "PUBLIC"."{TAB_NAME}_EVAL4" on table "PUBLIC"."{TAB_NAME}"
        -arithmetic exception, numeric overflow, or string truncation
        -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.

        Statement failed, SQLSTATE = 22011
        Expression evaluation error for index "PUBLIC"."{TAB_NAME}_EVAL5" on table "PUBLIC"."{TAB_NAME}"
        -Invalid length parameter -3 to SUBSTRING. Negative integers are not allowed.
        Records affected: 0
    """
    act.isql(switches = ['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
