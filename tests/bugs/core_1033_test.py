#coding:utf-8
#
# id:           bugs.core_1033
# title:        like doesn't work for computed values (at least in a view)
# decription:   
# tracker_id:   CORE-1033
# min_versions: []
# versions:     2.5
# qmid:         bugs.core_1033

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """create table TABLE_X (
  id numeric(10,0) not null,
  descr varchar(50) not null
);

commit;

create view X_VW (id, description)
as select id, x.descr || ' ('||x.id||')' from TABLE_X as x;

commit;

insert into TABLE_X values (1,'xyz');
insert into TABLE_X values (2,'xyzxyz');
insert into TABLE_X values (3,'xyz012');

commit;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from X_VW ;

select * from X_VW where description like 'xyz (1)' ;

select * from X_VW where description like 'xyz (%)' ;

select * from X_VW where description like 'xyz%' ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                   ID DESCRIPTION                                                            
===================== ====================================================================== 
                    1 xyz (1)                                                                
                    2 xyzxyz (2)                                                             
                    3 xyz012 (3)                                                             


                   ID DESCRIPTION                                                            
===================== ====================================================================== 
                    1 xyz (1)                                                                


                   ID DESCRIPTION                                                            
===================== ====================================================================== 
                    1 xyz (1)                                                                


                   ID DESCRIPTION                                                            
===================== ====================================================================== 
                    1 xyz (1)                                                                
                    2 xyzxyz (2)                                                             
                    3 xyz012 (3)                                                             
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

