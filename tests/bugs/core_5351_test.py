#coding:utf-8
#
# id:           bugs.core_5351
# title:        LEFT JOIN incorrectly pushes UDF into the inner stream causing wrong results
# decription:   
#                   25.01.2019: totally changed: use ticket author's sample + dimitr's suggestion 
#                   to operate with usual PSQL fcuntion (rather than UDF). 
#                   Thus test nothing has to do with UDF or UDR.
#                   Checked on:
#                       3.0.5.33086: OK, 1.891s.
#                       4.0.0.1172: OK, 6.703s.
#                       4.0.0.1340: OK, 2.953s.
#                       4.0.0.1378: OK, 3.312s.
#                  Confirmed wrong result on 
#                      WI-V3.0.0.32136 (Release Candidate 1; 06.11.2015) and 4.0.0.98 (30.03.2016)
#               
#                  Old comment:
#                      Confirmed  on 3.0.1.32597, 4.0.0.371 (wrong result).
#                      Works fine on 3.0.1.32598, 4.0.0.372,
#                
# tracker_id:   CORE-5351
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
    set bail on;
    set term ^;
    create or alter function psql_strlen (val varchar(10)) returns int as 
    begin 
      return char_length(coalesce(val, '')); 
    end
    ^
    set term ;^
    commit;

    recreate table test_table1 ( 
        id integer not null, 
        testtable2_id integer 
    ); 

    alter table test_table1 add primary key (id); 
    commit; 

    recreate table test_table2 ( 
        id integer not null, 
        groupcode varchar(10) 
    ); 
    alter table test_table2 add primary key (id); 
    commit; 

    insert into test_table1 (id,testtable2_id) values (1,100); 
    insert into test_table2 (id,groupcode) values (100,'a'); 
    commit; 

    set count on;
    set list on;

    select t1.id 
    from test_table1 t1 
    left join test_table2 t2 on t2.id=t1.testtable2_id
    where psql_strlen(t2.groupcode) = 0 ;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
"""

@pytest.mark.version('>=3.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

