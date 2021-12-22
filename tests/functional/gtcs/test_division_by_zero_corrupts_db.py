#coding:utf-8
#
# id:           functional.gtcs.division_by_zero_corrupts_db
# title:        GTCS/tests/CF_ISQL_29. Zero divide in SP can crash database when call this SP several times.
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_29.script
#               
#                   Issue in original test:
#                   Division by 0 corrupt database
#               
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [("-At procedure 'SPX_AUX_TEST' line: .*", ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^ ;
    create procedure spx_aux_test (par1 bigint) returns (ret1 bigint)
    as
        declare lok1 bigint ;
        declare itmpvar integer;
    begin
        begin
            lok1=2;
            itmpvar = 1/0;
            when any do
            begin
                exception;
            end
        end
    end
    ^
    commit
    ^
    set term ;^

    connect '$(DSN)' user 'SYSDBA' password 'masterkey'; -- this is done in original script.

    set term ^;
    create or alter procedure spx_aux_test (par1 bigint) returns (ret1 bigint)
    as
        declare lok1 bigint ;
        declare itmpvar integer;
    begin
        begin
            lok1=2;
            itmpvar = 1/0;
        end
    end
    ^
    commit
    ^
    set term ;^

    execute procedure spx_aux_test (1);
    execute procedure spx_aux_test (1);
    execute procedure spx_aux_test (1);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.

    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.

    Statement failed, SQLSTATE = 22012
    arithmetic exception, numeric overflow, or string truncation
    -Integer divide by zero.  The code attempted to divide an integer value by an integer divisor of zero.
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

