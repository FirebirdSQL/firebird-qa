#coding:utf-8
#
# id:           bugs.core_3362_complex
# title:        Cursors should ignore changes made by the same statement
# decription:   
#                  This test verifies PSQL issues that were accumulated in miscenaleous tickets.
#                
# tracker_id:   CORE-3362
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('line: [\\d]+[,]{0,1} col: [\\d]+', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- see also:
    -- https://www.sql.ru/forum/1319017/obnovlenie-zapisi-po-kursoru
    -- Discussed  13.11.2019 with hvlad and dimitr (related to CORE-5794)
    recreate table test (
        id    int not null
        ,data1 int
        ,data2 int
        ,data3 int
        ,data4 int
    );
    set term ^;
    create or alter procedure sp_set_ctx(a_point varchar(20), a_data1 int, a_data2 int, a_data3 int, a_data4 int) as
    begin
        -- Store values of cursor fields in the context variable which name is passed here as 'a_point'.
        rdb$set_context( 
            'USER_SESSION', 
            a_point,
                      coalesce(cast( a_data1 as char(6)),'#null#') 
            || ' ' || coalesce(cast( a_data2 as char(6)),'#null#')
            || ' ' || coalesce(cast( a_data3 as char(6)),'#null#')
            || ' ' || coalesce(cast( a_data4 as char(6)),'#null#') 
        );
    end
    ^

    create or alter procedure sp_test1a as
    begin
        -- ::: NOTE :::
        -- Only IMPLICIT cursors are stable in 3.0+.
        -- #############
        -- Do _NOT_ try to check following statements using explicit cursor
        -- (i.e. OPEN <C>; FETCH ...; CLOSE <C>)
        for
            select t.id, t.data1, t.data2, t.data3, t.data4 from test t where t.id = 1 
            as cursor c
        do begin
          
            execute procedure sp_set_ctx('point_0', c.data1, c.data2, c.data3, c.data4 );

            update test t set t.data1 = 100001 where current of c;
            -- make "photo" of all cursor fields:
            execute procedure sp_set_ctx('point_1', c.data1, c.data2, c.data3, c.data4 );

            -- at this point value of c.data1 remains NULL from cursor POV because
            -- "UPDATE WHERE CURRENT OF C" sees record as it was no changes at all:
            update test t set t.data2 = 100002 where current of c;
            -- make "photo" of all cursor fields:
            execute procedure sp_set_ctx('point_2', c.data1, c.data2, c.data3, c.data4 );

            -- at this point value of c.data1 and c.data2 remain NULL from cursor POV because
            -- "UPDATE WHERE CURRENT OF C" sees record as it was no changes at all:
            update test t set t.data3 = 100003 where current of c;
            -- make "photo" of all cursor fields:
            execute procedure sp_set_ctx('point_3', c.data1, c.data2, c.data3, c.data4 );

            delete from test t where current of c; -- this must prevent following UPDATE from execution

            -- this must fail with "no current record for fetch operation":
            update test t set t.data4 = 100004 where current of c;
            execute procedure sp_set_ctx('point_4', c.data1, c.data2, c.data3, c.data4 );


        end
    end
    ^
    set term ;^

    commit;
    insert into test (id) values (1);
    commit;

    set bail off;
    set list on;

    execute procedure sp_test1a;
    select * from test;
    select mon$variable_name as ctx_name, mon$variable_value ctx_value from mon$context_variables where mon$attachment_id = current_connection;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    DATA1                           <null>
    DATA2                           <null>
    DATA3                           <null>
    DATA4                           <null>

    CTX_NAME                        point_0
    CTX_VALUE                       #null# #null# #null# #null#

    CTX_NAME                        point_1
    CTX_VALUE                       100001 #null# #null# #null#

    CTX_NAME                        point_2
    CTX_VALUE                       #null# 100002 #null# #null#

    CTX_NAME                        point_3
    CTX_VALUE                       #null# #null# 100003 #null#
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22000
    no current record for fetch operation
    -At procedure 'SP_TEST1A'
  """

@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

