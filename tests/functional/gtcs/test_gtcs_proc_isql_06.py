#coding:utf-8
#
# id:           functional.gtcs.gtcs_proc_isql_06
# title:        gtcs-proc-isql-06
# decription:   
#               	Original test see in:
#                       https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROC_ISQL_06.script
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
    create procedure proc6 returns (a varchar(20), b integer) as
    begin
        for
            select pname,weight
            from p
            where weight > (select (avg(weight)+3) from p)
            into :a, :b
        do
            suspend;
    end
    ^
    set term ; ^

    execute procedure proc6 ;

    set count on;
    select 'point-1' msg, p.* from proc6 p;
    select 'point-2' msg, max(p.a) from proc6 p;
    select 'point-3' msg, p.b from proc6 p;
    select 'point-4' msg, p.a, p.b from proc6 p order by a;
    select 'point-5' msg, p.a, avg(p.b) from proc6 p group by a having avg(p.b) > 35;
    select 'point-6' msg, p.a, avg(p.b) from proc6 p group by a ;
    select 'point-7' msg, p.a , b from proc6 p where b = (select avg(x.b) from proc6 x);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               B
    Cog                            19

    MSG     A                               B
    point-1 Cog                            19
    Records affected: 1

    MSG     MAX
    point-2 Cog
    Records affected: 1
    
    MSG                B
    point-3           19
    Records affected: 1
    
    MSG     A                               B
    point-4 Cog                            19
    Records affected: 1
    
    Records affected: 0
    
    MSG     A                                      AVG
    point-6 Cog                                     19
    Records affected: 1
    
    MSG     A                               B
    point-7 Cog                            19
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
def test_gtcs_proc_isql_06_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

