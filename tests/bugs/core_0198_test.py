#coding:utf-8
#
# id:           bugs.core_0198
# title:        wrong order by in table join storedproc
# decription:   
# tracker_id:   CORE-0198
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
    recreate table my_table
    (
        k varchar(10) not null,
        d1 integer,
        d2 integer,
        v1 varchar(10),
        primary key (k)
    );

    set term ^;
    create or alter procedure select_me returns(
      data varchar(10)
    ) as
    begin
        data = 'one';
        suspend;
        data = 'two';
        suspend;
        data = 'three';
        suspend;
    end
    ^
    set term ;^
    commit;

    insert into my_table values ('one', 1, 99, 'zz');
    insert into my_table values ('two', 2, 98, 'yy');
    insert into my_table values ('three', 3, 97, 'xx');
    commit;
    
    set list on;

    select *
    from my_table t join select_me p on (t.k = p.data)
    order by t.d1
    ;
    commit;

    create index i1 on my_table(d1);
    commit;

    select *
    from my_table t join select_me p on (t.k = p.data)
    order by t.d1
    ;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    K                               one
    D1                              1
    D2                              99
    V1                              zz
    DATA                            one

    K                               two
    D1                              2
    D2                              98
    V1                              yy
    DATA                            two

    K                               three
    D1                              3
    D2                              97
    V1                              xx
    DATA                            three

    K                               one
    D1                              1
    D2                              99
    V1                              zz
    DATA                            one

    K                               two
    D1                              2
    D2                              98
    V1                              yy
    DATA                            two

    K                               three
    D1                              3
    D2                              97
    V1                              xx
    DATA                            three
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

