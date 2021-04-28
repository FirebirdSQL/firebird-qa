#coding:utf-8
#
# id:           bugs.core_0117
# title:        Expression evaluation not supported on LEFT JOIN
# decription:   
# tracker_id:   CORE-0117
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
    -- Output is fine in WI-V1.5.6.5026 and all above.
    set list on;

    recreate table t1(
        id numeric( 18, 0) not null,
        id2 numeric( 18,0),
        date1 date,
        constraint pk_t1 primary key (id)
    );
    
    recreate table t2(
        id numeric( 18, 0) not null,
        id2 numeric( 18,0),
        date1 date,
        constraint pk_t2 primary key (id)
    );
    
    
    insert into t1(id, id2, date1) values (1, 1, '10/13/2003');
    insert into t1(id, id2, date1) values (2, 2, '09/13/2003');
    insert into t2(id, id2, date1) values (1, 1, '09/13/2003');
    commit;
    
    --executing the following query in isql returns the error
    --message "expression evaluation not supported" after
    --retrieving the
    --first row.


    select t_1.id2, t_1.date1 as d1, t_2.date1 as d2
    from t1 t_1
    left join t2 t_2 on t_1.id2=t_2.id2
    where
        extract(month from t_1.date1)
        <>
        extract(month from t_2.date1)
    ;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID2                             1
    D1                              2003-10-13
    D2                              2003-09-13
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

