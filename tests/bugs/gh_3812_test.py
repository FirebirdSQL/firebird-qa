#coding:utf-8

"""
ID:          issue-3812
ISSUE:       3812
TITLE:       Query with SP doesn't accept explicit plan [CORE3451]
NOTES:
    [18.02.2023] pzotov
        Confirmed problem on 5.0.0.743, got:
            Statement failed, SQLSTATE = 42S02
            -Invalid command
            -there is no alias or table named sp_test at this scope level
        Checked on 5.0.0.745 - all OK.
    [13.04.2026] pzotov
        Adjusted output in 6.x to current (letter from dimitr, 13.04.2026 0855).
        Checked on 6.0.0.1891; 5.0.4.1808.
"""
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

init_script = """
    set bail on;
    recreate table test1(
       fld1 int
       ,fld2 int
       ,fld3 int
    );
    create index tmp_tbl1_fld2 on test1(fld2);

    recreate table test2(
       fld1 int
       ,fld2 int
       ,fld3 int
    );
    create index tmp_tbl2_fld1 on test2(fld1);


    recreate table test3(
       fld1 int
       ,fld2 int
       ,fld3 int
    );
    create index tmp_tbl3_fld1 on test3(fld1);

    set term ^;
    create or alter procedure sp_test returns(fld1 int) as
    begin
        fld1 = 2;
        suspend;
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init = init_script)

act = python_act('db')

@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):

    if act.is_version('<6'):
        desired_plan = 'PLAN JOIN (SP_TEST NATURAL, T1 INDEX (TMP_TBL1_FLD2), T2 INDEX (TMP_TBL2_FLD1), T3 INDEX (TMP_TBL3_FLD1))'
    else:
        desired_plan = 'PLAN JOIN ("PUBLIC"."SP_TEST" NATURAL, "T1" INDEX ("PUBLIC"."TMP_TBL1_FLD2"), "T2" INDEX ("PUBLIC"."TMP_TBL2_FLD1"), "T3" INDEX ("PUBLIC"."TMP_TBL3_FLD1"))'

    test_sql = f"""
        select t2.fld1
        from test2 t2
        join test1 t1 on t1.fld1=t2.fld1
        join SP_TEST on sp_test.fld1=t1.fld2
        join test3 t3 on t3.fld1=t1.fld3
        where t2.fld2=2
        {desired_plan}
        ;
    """

    with act.db.connect() as con:
        cur = con.cursor()
        ps, rs = None, None
        try:
            cur = con.cursor()
            ps = cur.prepare(test_sql)

            print(ps.plan)

            # Print explained plan with padding eash line by dots in order to see indentations:
            #print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)
        finally:
            if rs:
                rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
            if ps:
                ps.free()
    
    expected_stdout = f"""
        {desired_plan}
    """

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
