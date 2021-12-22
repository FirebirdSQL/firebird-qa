#coding:utf-8
#
# id:           bugs.core_6171
# title:        "No current record for fetch operation" with queries with aggregated subselect
# decription:   
#                   Confrmed bug on: 4.0.0.1635, 3.0.5.33182.
#                   Works fine on:
#                       4.0.0.1639 SS: 1.291s.
#                       3.0.5.33183 SS: 0.769s.
#                
# tracker_id:   CORE-6171
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    recreate table tmain( s varchar(10) );
    recreate table tdetl( s varchar(10), u int );
    commit;

    insert into tmain(s) values('foo');
    insert into tmain(s) values('bar');
    insert into tmain(s) values('rio');
    insert into tmain(s) values('boo');
    insert into tmain(s) values('');
    commit;

    insert into tdetl(s, u) values('foo', 100);
    insert into tdetl(s, u) values('bar', 200);
    insert into tdetl(s, u) values('rio', 300);
    insert into tdetl(s, u) values('boo', 400);
    commit;

    create index tmain_s on tmain(s);
    commit;

    set heading off;
    set plan on;

    select r.s
    from tmain r
    where
        r.s = ''
        or (
               select sum(d.u)
               from tdetl d
               where d.s = r.s
           ) > 0
    ;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (D NATURAL)
    PLAN (R NATURAL)

    foo        
    bar        
    rio        
    boo        
"""

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

