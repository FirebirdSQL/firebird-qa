#coding:utf-8
#
# id:           functional.gtcs.computed_fields_17
# title:        computed-fields-17
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_17.script
#               	SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script
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

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create generator gen1;
    set generator gen1 to 999;

    create generator gen2;
    set generator gen2 to 199;

    create generator gen3;
    set generator gen3 to 29;

    create table t0 (
            a integer,
            genid_field1 computed by (gen_id(gen1, 1)),
            genid_field2 computed by (gen_id(gen2, genid_field1)),
            genid_field3 computed by (gen_id(gen3, genid_field2))
    );
    commit;

    insert into t0(a) values(4);
    insert into t0(a) values(1);

    /*************************************************
           first row:
           a:  4
           genid_field3:=genid3+(genid2+(genid1+1))
                       :=29+(199+(999+1)
                       :=29+(199+1000)
                       :=29+1199
                       :=1228
           second row:
           a: 1
           genid_field3:=genid3+(genid2+(genid1+1))
                       :=1228+(1199+(1000+1)
                       :=1228+(1199+1001)
                       :=1228+(2200)
                       :=3428

        so expected result is:

                   A          GENID_FIELD3
        ============ =====================

                   4                  1228
                   1                  3428

    *************************************************/

    select 'point-1' msg, p.a, p.genid_field3 from t0 p;

    /*************************************************
           first row:
           a:  4
           genid_field3:=genid3+(genid2+(genid1+1))
                       :=3428+(2200+(1001+1)
                       :=3428+(2200+1002)
                       :=3429+3202
                       :=6630
           genid_field2:=genid2+(genid1+1)
                       :=3202+(1002+1)
                       :=3202+1003
                       :=4205
           genid_field1:=genid1+1
                       :=1003+1
                       :=1004

           second row:
           a:  1
           genid_field3:=genid3+(genid2+(genid1+1))
                       :=6630+(4205+(1004+1))
                       :=6630+(4205+1005)
                       :=6630+5210
                       :=11840
           genid_field2:=genid2+(genid1+1)
                       :=5210+(1005+1)
                       :=5210+1006
                       :=6216
           genid_field1:=genid1+1
                       :=1006+1
                       :=1007

        so expected result is:

                   A          GENID_FIELD1          GENID_FIELD2          GENID_FIELD3
        ============ ===================== ===================== =====================

                   4                  1004                  4205                  6630
                   1                  1007                  6216                 11840

    **************************************************/

    select 'point-2' msg, p.* from t0 p;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                A          GENID_FIELD3
    point-1            4                  1228
    point-1            1                  3428

    MSG                A          GENID_FIELD1          GENID_FIELD2          GENID_FIELD3
    point-2            4                  1004                  4205                  6630
    point-2            1                  1007                  6216                 11840
  """

@pytest.mark.version('>=2.5')
def test_computed_fields_17_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

