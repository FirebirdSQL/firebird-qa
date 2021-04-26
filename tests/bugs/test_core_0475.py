#coding:utf-8
#
# id:           bugs.core_0475
# title:        ORDER BY has no effect
# decription:   
# tracker_id:   CORE-0475
# min_versions: ['2.5.6']
# versions:     2.5.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure getChilds as begin end;
    recreate table test (
        code integer not null primary key using index test_pk,
        name varchar(2) not null unique,
        parent integer,
        foreign key (parent) references test(code) using index test_fk
    );

    set term ^;
    create or alter procedure getChilds(par integer) returns (code integer,children integer) as
    begin
        for 
            select 
                m.code, Min(c.code) from
            test m 
            left join test c on m.code = c.parent
            where m.parent = :par or (m.parent is null and :par is null)
            group by m.code 
        into :code,:children 
        do
            suspend;
    end
    ^
    set term ;^
    commit;

    insert into test values (0,'A',null);
    insert into test values (1,'AA',0);
    insert into test values (3,'AB',0);
    insert into test values (4,'AC',0);
    insert into test values (2,'AD',0);
    insert into test values (5,'B',null);
    insert into test values (6,'BA',5);
    insert into test values (7,'BB',5);
    insert into test values (8,'BC',5);
    insert into test values (9,'BD',5);
    insert into test values (10,'BE',5);
    insert into test values (11,'BF',5);

    set list on;

    select * 
    from getChilds(0) 
    inner join test 
    on getChilds.code = test.code
    order by name
    ;


    select * 
    from getChilds(0) 
    inner join test 
    on getChilds.code = test.code
    order by name desc
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CODE                            1
    CHILDREN                        <null>
    CODE                            1
    NAME                            AA
    PARENT                          0

    CODE                            3
    CHILDREN                        <null>
    CODE                            3
    NAME                            AB
    PARENT                          0

    CODE                            4
    CHILDREN                        <null>
    CODE                            4
    NAME                            AC
    PARENT                          0

    CODE                            2
    CHILDREN                        <null>
    CODE                            2
    NAME                            AD
    PARENT                          0



    CODE                            2
    CHILDREN                        <null>
    CODE                            2
    NAME                            AD
    PARENT                          0

    CODE                            4
    CHILDREN                        <null>
    CODE                            4
    NAME                            AC
    PARENT                          0

    CODE                            3
    CHILDREN                        <null>
    CODE                            3
    NAME                            AB
    PARENT                          0

    CODE                            1
    CHILDREN                        <null>
    CODE                            1
    NAME                            AA
    PARENT                          0
  """

@pytest.mark.version('>=2.5.6')
def test_core_0475_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

