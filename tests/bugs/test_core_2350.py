#coding:utf-8
#
# id:           bugs.core_2350
# title:        Too long column name for select alias should be rejected
# decription:   
#                     26.01.2019, code for FB 4.0: added filtering 'where rdb$system_flag is distinct from 1' for query to rdb$procedures.
#                     Currently there is one system-defined package (RDB$TIME_ZONE_UTIL) and one stand-alone procedure (RDB$TRANSITIONS)
#                     Checked on:
#                       3.0.4.33034: OK, 2.906s.
#                       3.0.5.33097: OK, 1.453s.
#                       4.0.0.1340: OK, 2.328s.
#                       4.0.0.1410: OK, 2.453s.
#                
# tracker_id:   CORE-2350
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t1 (i integer);
    commit;

    insert into t1 values(1);
    commit;

    set list on;
    --set echo on;

    select i as i23456789012345678901234567890123456 from t1;
    select i23456789012345678901234567890123456
    from (
      select i as i23456789012345678901234567890123456
      from t1
    );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_2350_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

# version: 4.0
# resources: None

substitutions_2 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    select '-  column title, ASCII, width = 63' as 
    i23456789012345678901234567890123456789012345678901234567890123
    from rdb$database;

    select '- column title, ASCII, width = 64' as 
    i234567890123456789012345678901234567890123456789012345678901234
    from rdb$database;
        
    select '- column title, UTF8, width = 63' as 
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
    from rdb$database;

    select '- column title, UTF8, width = 64' as 
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯВ"
    from rdb$database;

    set term ^;

    create or alter procedure sp_63a returns(o1 double precision) as
        declare
    v23456789012345678901234567890123456789012345678901234567890123
        int;
    begin
        select rand()*1000 as
    a23456789012345678901234567890123456789012345678901234567890123
        from rdb$database as
    t23456789012345678901234567890123456789012345678901234567890123
        into
    v23456789012345678901234567890123456789012345678901234567890123;
        o1 = sqrt(
    v23456789012345678901234567890123456789012345678901234567890123
    );
        suspend;
    end
    ^

    create or alter procedure sp_63u returns(o1 double precision) as
        declare
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        int;
    begin
        select rand()*1000 as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        from rdb$database as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        into
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ";
        o1 = sqrt(
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
    );
        suspend;
    end
    ^

    create or alter procedure sp_64u1 returns(o1 double precision) as
        declare
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ1" -- 64 characters, UTF8
        int;
    begin
        select rand()*1000 as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        from rdb$database as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        into
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ1";
        o1 = sqrt(
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ1"
    );
        suspend;
    end
    ^

    create or alter procedure sp_64u2 returns(o1 double precision) as
        declare
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        int;
    begin
        select rand()*1000 as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ1" -- 64 characters, UTF8
        from rdb$database as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        into
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ";
        o1 = sqrt(
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
    );
        suspend;
    end
    ^
    create or alter procedure sp_64u3 returns(o1 double precision) as
        declare
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        int;
    begin
        select rand()*1000 as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
        from rdb$database as
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ1" -- 64 characters, UTF8
        into
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ";
        o1 = sqrt(
    "ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ"
    );
        suspend;
    end
    ^

    create or alter procedure sp_64a1 returns(o1 double precision) as
        declare
    v234567890123456789012345678901234567890123456789012345678901234 -- 64 characters, ascii
        int;
    begin
        select rand()*1000 as
    a23456789012345678901234567890123456789012345678901234567890123
        from rdb$database as
    t23456789012345678901234567890123456789012345678901234567890123
        into
    v234567890123456789012345678901234567890123456789012345678901234;
        o1 = sqrt(
    v23456789012345678901234567890123456789012345678901234567890123
    );
        suspend;
    end
    ^
    create or alter procedure sp_64a2 returns(o1 double precision) as
        declare
    v23456789012345678901234567890123456789012345678901234567890123
        int;
    begin
        select rand()*1000 as
    a234567890123456789012345678901234567890123456789012345678901234 -- 64 characters, ascii
        from rdb$database as
    t23456789012345678901234567890123456789012345678901234567890123
        into
    v23456789012345678901234567890123456789012345678901234567890123;
        o1 = sqrt(
    v23456789012345678901234567890123456789012345678901234567890123
    );
        suspend;
    end
    ^
    create or alter procedure sp_64a3 returns(o1 double precision) as
        declare
    v23456789012345678901234567890123456789012345678901234567890123
        int;
    begin
        select rand()*1000 as
    a23456789012345678901234567890123456789012345678901234567890123
        from rdb$database as
    t234567890123456789012345678901234567890123456789012345678901234 -- 64 characters, ascii
        into
    v23456789012345678901234567890123456789012345678901234567890123;
        o1 = sqrt(
    v23456789012345678901234567890123456789012345678901234567890123
    );
        suspend;
    end
    ^
    set term ;^
    commit;
    set list on;
    set count on;
    select rdb$procedure_name from rdb$procedures where rdb$system_flag is distinct from 1;
  
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    I23456789012345678901234567890123456789012345678901234567890123 -  column title, ASCII, width = 63
    ЛевНиколаевичТолстойАннаКаренинаМнеотмщениеиазвоздамЧАСТЬПЕРВАЯ - column title, UTF8, width = 63
    RDB$PROCEDURE_NAME              SP_63A                                                                                                                                                                                                                                                      
    RDB$PROCEDURE_NAME              SP_63U  
    Records affected: 2
  """
expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size

    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size
  """

@pytest.mark.version('>=4.0')
def test_core_2350_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr
    assert act_2.clean_expected_stdout == act_2.clean_stdout

