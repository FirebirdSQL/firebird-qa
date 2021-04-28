#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_05
# title:        gtcs-proc-isql-05
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_05.script
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

db_1 = db_factory(from_backup='gtcs_sp1.fbk', init=init_script_1)

test_script_1 = """
    set bail on;
    set term ^;
    create procedure proc5 returns (a varchar(20),  b integer) as
    begin
        for
            select pname, avg(weight)
            from p
            group by pname
            having avg(weight) > 18
            into :a, :b
        do
            suspend;
    end
    ^
    set term ; ^

    execute procedure proc5 ;

    set count on;
    select p.* from proc5 p;
    select 'point-1' msg, max(p.a) from proc5 p;
    select 'point-2' msg, p.b from proc5 p;
    select 'point-3' msg, p.a, p.b from proc5 p order by p.a;
    select 'point-4' msg, p.a, avg(p.b) from proc5 p group by p.a having avg(p.b) > 35;
    select 'point-5' msg, p.a, avg(p.b) from proc5 p group by p.a;
    select 'point-6' msg, p.a, p.b from proc5 p where p.b = (select avg(x.b) from proc5 x);

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               B
    Cog                            19

    A                               B
    Cog                            19
    Records affected: 1

    MSG     MAX
    point-1 Cog
    Records affected: 1

    MSG                B
    point-2           19
    Records affected: 1

    MSG     A                               B
    point-3 Cog                            19
    Records affected: 1

    Records affected: 0

    MSG     A                                      AVG
    point-5 Cog                                     19
    Records affected: 1

    MSG     A                               B
    point-6 Cog                            19
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

