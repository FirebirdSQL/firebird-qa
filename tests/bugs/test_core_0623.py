#coding:utf-8
#
# id:           bugs.core_0623
# title:        ORDER BY on a VIEW turns values in fields into NULL
# decription:   
#                   30.10.2019. NB: new datatype in FB 4.0 was introduces: numeric(38,0).
#                   It can lead to additional ident of values when we show them in form "SET LIST ON",
#                   so we have to ignore all internal spaces - see added 'substitution' section below.
#                   Checked on:
#                       4.0.0.1635 SS: 1.470s.
#                       3.0.5.33182 SS: 0.981s.
#                       2.5.9.27146 SC: 0.297s.
#                
# tracker_id:   CORE-0623
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = [('=.*', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table p1 (
      x_p1 numeric(10,0),
      f_entrada date
    );
    
    create view vp1 (
      x_p1,
      f_entrada
    ) as
    select x_p1, f_entrada from p1;
    
    create table p2 (
      x_p2 numeric(10,0),
      p1_x_p1 numeric(10,0),
      n_one numeric(10,0),
      n_two numeric(10,0)
    );
    
    create view vp2 (
      p1_x_p1,
      n_one,
      n_two
    ) as
    select p1_x_p1, sum(n_one), sum(n_two)
    from p2 group by p1_x_p1;
    
    create view vvp1 (
      p1_x_p1,
      f_entrada,
      n_one,
      n_two
    ) as
    select p1.x_p1, p1.f_entrada, p2.n_one, p2.n_two
    from vp1 p1 left join vp2 p2 on p1.x_p1=p2.p1_x_p1;
    commit;
    
    insert into p1 values (1,'07/10/2001');
    insert into p1 values (2,'07/13/2001');
    insert into p1 values (3,'08/12/2001');
    
    insert into p2 values (1,1,0,1);
    insert into p2 values (2,2,1,0);
    insert into p2 values (3,1,0,1);
    commit;
    
    select * from vvp1;
    select * from vvp1 order by f_entrada;
    
    insert into p1 values (4,'08/10/2001');
    insert into p2 values (4,2,0,1);
    insert into p2 values (5,2,1,1);
    commit;
    select * from vvp1;
    select * from vvp1 order by f_entrada;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                  P1_X_P1   F_ENTRADA                 N_ONE                 N_TWO
    ===================== =========== ===================== =====================
                        1 2001-07-10                      0                     2
                        2 2001-07-13                      1                     0
                        3 2001-08-12                 <null>                <null>
    
    
                  P1_X_P1   F_ENTRADA                 N_ONE                 N_TWO
    ===================== =========== ===================== =====================
                        1 2001-07-10                      0                     2
                        2 2001-07-13                      1                     0
                        3 2001-08-12                 <null>                <null>
    
    
                  P1_X_P1   F_ENTRADA                 N_ONE                 N_TWO
    ===================== =========== ===================== =====================
                        1 2001-07-10                      0                     2
                        2 2001-07-13                      2                     2
                        3 2001-08-12                 <null>                <null>
                        4 2001-08-10                 <null>                <null>
    
    
                  P1_X_P1   F_ENTRADA                 N_ONE                 N_TWO
    ===================== =========== ===================== =====================
                        1 2001-07-10                      0                     2
                        2 2001-07-13                      2                     2
                        4 2001-08-10                 <null>                <null>
                        3 2001-08-12                 <null>                <null>
  """

@pytest.mark.version('>=2.1.7')
def test_core_0623_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

