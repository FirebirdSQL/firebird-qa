#coding:utf-8
#
# id:           bugs.core_5268
# title:        Nested OR conditions may lead to incorrest results
# decription:   
# tracker_id:   CORE-5268
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Reproduced wrong result on WI-T4.0.0.238.
    -- (note on single difference between sp_test and sp_test2: parenthesis that enclose 'OR' expression.
    -- Checked on LI-T4.0.0.242 after fix was committed - all works fine.

    create or alter procedure sp_test(a_inp varchar(50)) as begin end;
    create or alter procedure sp_test2(a_inp varchar(50)) as begin end;
    recreate table testtab (
        feld_a varchar(50),
        feld_b varchar(10),
        feld_c char(10)
    );

    recreate table result (
        feld_a varchar(50),
        feld_b varchar(10),
        feld_c char(10)
    );
    
    create index testtab_idx1 on testtab (feld_b);
    create index testtab_idx2 on testtab (feld_a);
    commit;

    insert into testtab (feld_a, feld_b, feld_c) values ('aaaa', 'bb', 'cc ');
    insert into testtab (feld_a, feld_b, feld_c) values ('aaa', 'aa', 'aaa ');
    insert into testtab (feld_a, feld_b, feld_c) values ('uuu', 'uuu', 'uuu ');
    insert into testtab (feld_a, feld_b, feld_c) values ('uuu', 'uu', 'uu ');

    
    commit;


    -- test sqls
    -- wrong: should get at least 3 records, but gives only 1
    set term ^;
    create or alter procedure sp_test(a_inp varchar(50)) as
    begin
        delete from result;
        insert into result
        select * 
        from testtab t
        where
          :a_inp='123456' -- a_inp = 'blub' for testcase
          or
          (
            upper(t.feld_b) starting with upper('u')
            or
            t.feld_a starting with 'a' /* with index */
          )
        ;
    end
    ^

    create or alter procedure sp_test2(a_inp varchar(50)) as
    begin
        delete from result;
        insert into result
        select * 
        from testtab t
        where
          :a_inp='123456' -- a_inp = 'blub' for testcase
          or
          upper(t.feld_b) starting with upper('u')
          or
          t.feld_a starting with 'a' /* with index */
       ;
    end
    ^
    set term ;^
    commit;

    set list on;

    execute procedure sp_test('blub');
    select '1' as result, r.* from result r;

    execute procedure sp_test2('blub');
    select '2' as result, r.* from result r;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          1
    FELD_A                          aaaa
    FELD_B                          bb
    FELD_C                          cc

    RESULT                          1
    FELD_A                          aaa
    FELD_B                          aa
    FELD_C                          aaa

    RESULT                          1
    FELD_A                          uuu
    FELD_B                          uuu
    FELD_C                          uuu

    RESULT                          1
    FELD_A                          uuu
    FELD_B                          uu
    FELD_C                          uu


    RESULT                          2
    FELD_A                          aaaa
    FELD_B                          bb
    FELD_C                          cc

    RESULT                          2
    FELD_A                          aaa
    FELD_B                          aa
    FELD_C                          aaa

    RESULT                          2
    FELD_A                          uuu
    FELD_B                          uuu
    FELD_C                          uuu

    RESULT                          2
    FELD_A                          uuu
    FELD_B                          uu
    FELD_C                          uu
  """

@pytest.mark.version('>=3.0.1')
def test_core_5268_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

