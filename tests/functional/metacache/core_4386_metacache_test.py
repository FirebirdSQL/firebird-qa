#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/4708
TITLE:       Error 'object in use' must NOT raise in 6.x with shared metacache (opposite outcome to prior versions).
DESCRIPTION:
    Test creates such metadata that when we call top-level procedure then all DB objects
    that are called/involved in subsequent levels become loaded into metadata cache:
    =====================================================================================
    proc sp_test
          +-------> proc sp_worker
                         +----------> view v_test
                         |                 +-----------> table test1 (with indexed field)
                         |
                         +----------> func fn_worker
                                           +-----------> table test2 (with indexed field)
    =====================================================================================
    If we run 'select * from sp_test(...)' and keep transaction active then all callees:
        1) will NOT be avaliable for DROP statement with issuing 'object in use' -- PRIOR 6.x;
        2) CAN be dropped without issuing any error since 6.0.0.1771-f73321c (25.02.2026).
    This test checks SECOND case. Its outcome is OPPOSITE to similar test in the 'bugs/' folder.
    Check is performed for every existing TIL.
JIRA:        CORE-4386
NOTES:
    [12.04.2026] pzotov
    Checked on 6.0.0.1891.
"""
from difflib import unified_diff
import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation

db = db_factory()

act = python_act('db')

ddl_script = """
    set bail on;
    create or alter procedure sp_worker as begin end;
    create or alter procedure sp_test as begin end;
    create or alter view v_test as select 1 x from rdb$database;
    commit;

    recreate table test1(id int,x int);
    recreate table test2(id int,x int);
    commit;

    create index test1_id on test1(id);
    commit;
    create descending index test2_x on test2(x);
    commit;

    create or alter view v_test as select id,x from test1 where id between 15 and 30;
    commit;

    set term ^;
    create or alter function fn_worker(a_x int) returns int as
        declare v_id int;
    begin
        execute statement ('select max(b.id) from test2 b where b.x >= ?') (:a_x) into v_id;
        return v_id;
    end
    ^
    create or alter procedure sp_worker(a_id int) returns(x int) as
    begin
      for
          execute statement ('select v.x from v_test v where v.id = ? and v.id >= fn_worker(v.x)') (:a_id)
          into x
      do
          suspend;
    end
    ^
    create or alter procedure sp_test(a_id int) returns(x int) as
    begin
      for
          execute statement ('select x from sp_worker(?)') (:a_id)
          into x
      do
          suspend;
    end
    ^
    set term ;^
    commit;

    insert into test1 values(11,111);
    insert into test1 values(21,222);
    insert into test1 values(31,333);
    insert into test1 values(41,444);
    commit;

    insert into test2 select * from test1;
    commit;
"""

@pytest.mark.version('>=4.0')
@pytest.mark.perf_measure               # To be reworked for new meta cache - all objects are deleteable
def test_1(act: Action, capsys):

    # all of them must PASS in 6.x with shared metacache:
    drop_commands = [ 'drop procedure sp_test',
                      'drop procedure sp_worker',
                      'drop function fn_worker',
                      'drop view v_test',
                      'drop index test2_x',
                      'drop table test2',
                      'drop index test1_id',
                      'drop table test1',
                     ]

    tx_isol_lst = [ Isolation.READ_COMMITTED_NO_RECORD_VERSION,
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                    Isolation.SERIALIZABLE,
                  ]

    # for any isolation mode attempt to drop object that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:

        init_meta_sql = act.extract_meta()

        #-----------------------------------------------------------------------------
        act.isql(switches = ['-q'], input = ddl_script, combine_output = True)
        assert act.clean_stdout == '', 'Initial script FAILED:\n' + act.clean_stdout
        act.reset()
        #-----------------------------------------------------------------------------

        with act.db.connect() as con1:

            cur1 = con1.cursor()
            cur1.execute('select x from sp_test(21)').fetchall()

            for cmd in drop_commands:
                with act.db.connect() as con2:
                    custom_tpb = tpb(isolation = x_isol, lock_timeout=0)
                    tx2 = con2.transaction_manager(custom_tpb)
                    tx2.begin()
                    cur2 = tx2.cursor()
                    try:
                        cur2.execute(cmd)
                        tx2.commit() # <<< this MUST PASS on 6.x with shared metacache
                    except Exception as e:
                        print(x_isol.name, 'FAILED: ', cmd)
                        print(e.__str__())
                        print(e.gds_codes)

        curr_meta_sql = act.extract_meta()
        meta_diff = unified_diff(init_meta_sql, curr_meta_sql)
        if any(meta_diff):
            print('UNEXPECTED. INITIAL METADATA NOT EQUALS TO CURRENT ONE FOR TIL={x_isol.name}:')
            for line in meta_diff:
                if line.startswith('+'):
                    print(line)

    # No output must be.
    expected_stdout_6x = f"""
    """
    
    act.expected_stdout = expected_stdout_6x                
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
