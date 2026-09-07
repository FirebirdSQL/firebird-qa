#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9081
TITLE:       Error creating unique expression index
DESCRIPTION:
    Test creates a table with three columns: (id int, f1 varchar, f2 varchar).
    Values in f1 and f2 are defined by id and must have lot of duplicates.
    It is crucial for this test:
        * nature of values that we store in columns f1 and f2. This test reproduces bug for numeric values changing in range 0...999;
        * the *order* of changing `Id` column that is base for further evaluation of `f1 || f2` (see ':n' in PSQL loop).

    Test stores in f1 values evaluated as id/1000 and in f2 values that are evaluated as mod(:id, 1000).
NOTES:
    [07.09.2026] pzotov
    1. Table must occupy more that one Pointer Page.
    2. Server config must have 'ParallelWorkers' with value more than 1.
    3. Suppose that this counter is changed in ASCENDING order, from 0 to <INIT_ROWS_COUNT> (say, 1000000).
       Then FIRST duplicate of expression `f1 || f2` will be found for id pair = {1010, 11000}.
       The 'distance' between problematic Id values: 11000 - 1010 = 9990; 
       Engine will handle 10999 records before encountering first duplicate of `f1||f2`.

       Now suppose that we change Id in DESCENDING order, from <INIT_ROWS_COUNT> = 1000000 down to 0.
       Then FIRST duplicate of expression `f1 || f2` will be found for pair = {999099, 99999}.
       The 'distance' between problematic Id values: abs(99999 - 999099) = 899100. 
       Engine will handle 1000000 - 99999 = 900001 records before encountering first duplicate of `f1||f2`.

       The ratio (DESC vs ASC direction of values to be stored in `Id` column):
           1) between how many records must be handled before 1st duplicate will be encountered is: 900001 / 10999 = 81.
           2) between 'distances' between Id values which produce duplicated result of `f1||f2` is: 899100 /  9990 = 90.

       The fact that such ratios for ASCENDING order are much smaller then for DESCENDING one points that both duplicates
       most likely will be found for records that live at the same PP (if counter for `id` is changed in ASCENDING order).
       This, in turn, allows to REPRODUCE bug (in fact, bugcheck will appear in almost 100% of runs).
       In contrary, if DESCENDING order for 'id' will be used then bug will appear with probability approx 1/20 ... 1/30.

       Queries to obtain first pair of 'id' which produce duplicated value of `f1 || f2`:
       * when column 'id' was filled in ASCENDING order:
             select x.* from (
                select a.id as id_a, a.f1 as f1_a, a.f2 as f2_a, trim(a.f1) || trim(a.f2) as f1_f2, b.id as id_b, b.f1 as f1_b, b.f2 as f2_b
                from t_9081 a
                join t_9081 b on a.id < b.id and trim(a.f1) || trim(a.f2) = trim(b.f1) || trim(b.f2)
             ) x
             order by x.id_a asc rows 1;
         outcome:
             ID_A F1_A   F2_A   F1_F2                ID_B F1_B   F2_B
             ==== ====== ====== ============ ============ ====== =====
             1010 1      10     110                 11000 11     0

       * when column 'id' was filled in DESCENDING order:
             select x.* from (
                 select a.id as id_a, a.f1 as f1_a, a.f2 as f2_a, trim(a.f1) || trim(a.f2) as f1_f2, b.id as id_b, b.f1 as f1_b, b.f2 as f2_b
                 from t_9081 a join t_9081 b on a.id > b.id and trim(a.f1) || trim(a.f2) = trim(b.f1) || trim(b.f2)
             ) x
             order by x.id_a desc rows 1;
         outcome:
               ID_A F1_A   F2_A   F1_F2                ID_B F1_B   F2_B
             ====== ====== ====== ============ ============ ====== ====
             999099 999    99     99999               99999 99     99

    Great thanks to Vlad for suggestions and provided example. Discussed 03...06 september 2026.
    Confirmed bug on 6.0.0.2068-d3f717f; 5.0.5.1861-8a4a032.
    Checked on 6.0.0.2169-0-6a5c761 ; 5.0.5.1862-81236c1.
"""
import re
from difflib import unified_diff
from firebird.driver import DatabaseError
import pytest
from firebird.qa import *

CHECK_PAGE_SIZE = 8192
INIT_ROWS_COUNT = 400000 if CHECK_PAGE_SIZE == 8192 else 1000000 if CHECK_PAGE_SIZE == 16384 else 3200000

db = db_factory(page_size = CHECK_PAGE_SIZE)
act = python_act('db')

@pytest.mark.version('>=5.0.5')
def test_1(act: Action, capsys):

    init_script = f"""
        set bail on;
        create exception exc_insufficient_rows 'Test table must occupy more than one Pointer Page. One need to increase INIT_ROWS_COUNT={INIT_ROWS_COUNT}.';
        create exception exc_min_parallel_wcnt 'Test requires ParallelWorkers to be more than 1. One need to adjust firebird.conf';
        recreate table t_9081
        (
           id int,
           f1 varchar(4),
           f2 varchar(4)
        );
        commit;

        set term ^;
        execute block as
            declare n int = 0;
            declare v smallint;
        begin
            select rdb$config_value from rdb$config where upper(rdb$config_name) = upper('ParallelWorkers') into v;
            if ( coalesce(v, 0) < 2 ) then
            begin
                exception exc_min_parallel_wcnt;
            end

            -- #####################################################
            -- ###                  A C H T U N G                ###
            -- ### --------------------------------------------- ###
            -- ### DO NOT USE LOOP WITH DESCENDING COUNTER HERE! ###
            -- #####################################################
            while (n < {INIT_ROWS_COUNT}) do
            begin
                n = n + 1;
                insert into t_9081 values (:n, :n / 1000, mod(:n, 1000));
            end
            if ( singular(select 1 from rdb$pages p join rdb$relations r using(rdb$relation_id) where r.rdb$relation_name = upper('t_9081') and p.rdb$page_type = 4) ) then
            begin
                exception exc_insufficient_rows using({INIT_ROWS_COUNT});
            end
        end ^
        set term ;^
        commit;
    """
    
    act.isql(switches = ['-q'], input = init_script, combine_output = True)
    assert act.return_code == 0, 'Initial script failed:\n\n' + act.clean_stdout
    act.reset()
    
    with act.db.connect() as con:
        fblog_1 = act.get_firebird_log()
        cur = con.cursor()
        try:
            cur.execute('create unique index idx_t_9081 on t_9081 computed by ( trim(f1) || trim(f2) )')
            # Check N1: only 'attempt to store duplicate value' must occur here. No bugcheck with "error reading connection":
            con.commit()
        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)
        finally:
            pass
        fblog_2 = act.get_firebird_log()

    # Check N2: verify that firebird.log has no any messages after 'create index' execution:
    for i,line in enumerate(unified_diff(fblog_1, fblog_2)):
        if i == 0:
            print('UNEXPECTED messages in firbird.log:')
        print(line)

    expected_stdout_5x = """
        attempt to store duplicate value (visible to active transactions) in unique index "IDX_T_9081"
        -Problematic key value is (<expression> = '110')
        (335544349, 335545072)
    """
    expected_stdout_6x = """
        unsuccessful metadata update
        -CREATE INDEX "PUBLIC"."IDX_T_9081" failed
        -attempt to store duplicate value (visible to active transactions) in unique index "PUBLIC"."IDX_T_9081"
        -Problematic key value is (<expression> = '110')
        (335544351, 336397316, 335544349, 335545072)
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
