#coding:utf-8
#
# id:           bugs.core_0149
# title:        Left joining views with null fails
# decription:   
# tracker_id:   CORE-0149
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    
    -- Initial comment by johnsparrowuk, 19/Mar/04 12:00 AM:
    recreate view currentpeople(k) as select 1 as k from rdb$database;
    recreate view finishedpeople(k) as select 1 as k from rdb$database; 
    commit;
    
    recreate table mytable (
        person varchar(20) not null,
        status int not null, primary key (person,status)
    );
    
    recreate view currentpeople(person) as 
    select distinct person as person
    from mytable where status = 1;
    
    recreate view finishedpeople(person) as 
    select distinct person as person
    from mytable where status = 2;
    
    insert into mytable values ('john',1);
    insert into mytable values ('john',2);
    insert into mytable values ('fred',1);
    commit;
    
    -- This works fine: fred-null, john-john
    select * 
    from currentpeople c 
    left join finishedpeople f on c.person = f.person
    order by c.person, f.person
    ;
    
    -- This is as expected too: john-john
    select *
    from currentpeople c 
    left join finishedpeople f
    on c.person = f.person where f.person = 'john'
    order by c.person, f.person
    ;
    
    -- WHATS HAPPENING HERE????? fred-null, JOHN-NULL where does the john-null come from???
    select * 
    from currentpeople c 
    left join finishedpeople f on c.person = f.person
    where f.person is null
    order by c.person, f.person
    ;
    commit;
    
    --#################################################
    
    -- Alice F. Bird added a comment - 14/Jun/06 09:32 AM
    recreate table test (
        id int not null,
        name varchar(15),
        pid integer
    );
    
    insert into test(id, name, pid) values(1, 'Car',    null);
    insert into test(id, name, pid) values(2, 'Engine',    1);
    insert into test(id, name, pid) values(3, 'Body',      1);
    insert into test(id, name, pid) values(4, 'Oil Filter',2);
    insert into test(id, name, pid) values(5, 'Air Filter',2);
    insert into test(id, name, pid) values(6, 'Door Left', 3);
    insert into test(id, name, pid) values(7, 'Door Right',3);
    commit;
    
    -- This query issued WRONG result on 1.5.6
    -- (because first data source - 'TEST' - has not alias)
    select *
    from test
      left outer join test t2
        on test.pid=t2.id
    order by test.id, t2.id
    ;
    
    -- This works fine:
    select *
    from test t1
      left outer join test t2
        on t1.pid=t2.id
    order by t1.id, t2.id
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PERSON                          fred
    PERSON                          <null>
    
    PERSON                          john
    PERSON                          john
    
    
    
    PERSON                          john
    PERSON                          john
    
    
    
    PERSON                          fred
    PERSON                          <null>
    
    
    
    ID                              1
    NAME                            Car
    PID                             <null>
    ID                              <null>
    NAME                            <null>
    PID                             <null>
    
    ID                              2
    NAME                            Engine
    PID                             1
    ID                              1
    NAME                            Car
    PID                             <null>
    
    ID                              3
    NAME                            Body
    PID                             1
    ID                              1
    NAME                            Car
    PID                             <null>
    
    ID                              4
    NAME                            Oil Filter
    PID                             2
    ID                              2
    NAME                            Engine
    PID                             1
    
    ID                              5
    NAME                            Air Filter
    PID                             2
    ID                              2
    NAME                            Engine
    PID                             1
    
    ID                              6
    NAME                            Door Left
    PID                             3
    ID                              3
    NAME                            Body
    PID                             1
    
    ID                              7
    NAME                            Door Right
    PID                             3
    ID                              3
    NAME                            Body
    PID                             1
    
    
    
    ID                              1
    NAME                            Car
    PID                             <null>
    ID                              <null>
    NAME                            <null>
    PID                             <null>
    
    ID                              2
    NAME                            Engine
    PID                             1
    ID                              1
    NAME                            Car
    PID                             <null>
    
    ID                              3
    NAME                            Body
    PID                             1
    ID                              1
    NAME                            Car
    PID                             <null>
    
    ID                              4
    NAME                            Oil Filter
    PID                             2
    ID                              2
    NAME                            Engine
    PID                             1
    
    ID                              5
    NAME                            Air Filter
    PID                             2
    ID                              2
    NAME                            Engine
    PID                             1
    
    ID                              6
    NAME                            Door Left
    PID                             3
    ID                              3
    NAME                            Body
    PID                             1
    
    ID                              7
    NAME                            Door Right
    PID                             3
    ID                              3
    NAME                            Body
    PID                             1
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

