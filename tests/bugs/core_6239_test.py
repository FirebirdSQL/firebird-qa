#coding:utf-8
#
# id:           bugs.core_6239
# title:        Procedures and EXECUTE BLOCK without RETURNS should not be allowed to use SUSPEND
# decription:   
#                   Checked on 4.0.0.1763.
#                
# tracker_id:   CORE-6239
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- these two collations and domain not needed for TEST per se.
    -- We create them here only for reference in declaration of SP input params, see below:
    create collation nums_coll for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
    create collation name_coll for utf8 from unicode no pad case insensitive accent insensitive;
    create domain dm_test varchar(20) character set utf8 default 'foo' not null collate nums_coll;
    commit;

    -- All following statements should be declined with 
    --     Statement failed, SQLSTATE = 42000
    --     Dynamic SQL Error
    --     -SQL error code = -104
    --     -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK

    set term ^ ;
    execute block as
    begin
       suspend;
    end
    ^

    execute block (a_x int not null = ?) as
    begin
       suspend;
    end
    ^

    create or alter procedure sp_missed_returns_in_its_header_1 as
    begin
       -- we use SUSPEND clause but there is no
       -- output parameters in this SP header:
       suspend;
    end
    ^

    create or alter procedure sp_missed_returns_in_its_header_2 (a_x varchar(10) not null) as
    begin
       suspend;
    end
    ^

    create or alter procedure sp_missed_returns_in_its_header_3 (p1 varchar(20) character set utf8 not null collate nums_coll default 'foo') SQL SECURITY DEFINER as
    begin
       suspend;
    end
    ^


    recreate package pg_test_1 as
    begin
        procedure pg_proc(
            p1 varchar(20) character set utf8 not null collate nums_coll default 'foo'
           ,p2 dm_test default 'qwe'
           ,p3 dm_test default 'bar'
           ,p4 dm_test collate name_coll default 'rio'
        );
    end
    ^

    create package body pg_test_1 as
    begin
        procedure pg_proc(
            p1 varchar(20) character set utf8 not null collate nums_coll
           ,p2 dm_test
           ,p3 dm_test
           ,p4 dm_test collate name_coll
        ) as
        begin
            suspend;
        end
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE SP_MISSED_RETURNS_IN_ITS_HEADER_1 failed
    -Dynamic SQL Error
    -SQL error code = -104
    -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE SP_MISSED_RETURNS_IN_ITS_HEADER_2 failed
    -Dynamic SQL Error
    -SQL error code = -104
    -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE SP_MISSED_RETURNS_IN_ITS_HEADER_3 failed
    -Dynamic SQL Error
    -SQL error code = -104
    -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE PACKAGE BODY PG_TEST_1 failed
    -Dynamic SQL Error
    -SQL error code = -104
    -SUSPEND could not be used without RETURNS clause in PROCEDURE or EXECUTE BLOCK
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

