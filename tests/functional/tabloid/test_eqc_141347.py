#coding:utf-8
#
# id:           functional.tabloid.eqc_141347
# title:        Check correctness of LEFT JOIN result when right source has two FK and one of fields from FK present both in ON and WHERE clauses.
# decription:   
# tracker_id:   
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
    recreate table t2 (
        id     int primary key,
        pid0  int,
        pid1  int
    );
    recreate table t1 (id int primary key);
    recreate table t0 (id int primary key);
    
    alter table t2
        add constraint fk_t0 foreign key (pid0) references t0
        ,add constraint fk_t1 foreign key (pid1) references t1
    ;
    commit;
    
    insert into t0 (id) values (1);
    
    insert into t1 (id) values (1);
    insert into t1 (id) values (2);
    insert into t1 (id) values (3);
    insert into t1 (id) values (4);
    
    insert into t2 (id, pid1, pid0) values (1, 1, 1);
    insert into t2 (id, pid1, pid0) values (2, 4, 1);
    commit;
    
    select a.id, b.pid1
    from t1 a
    left join t2 b on ( a.id = b.pid1 ) and ( b.pid0 = 1 )
    where (b.pid1 is null);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              2
    PID1                            <null>

    ID                              3
    PID1                            <null>
  """

@pytest.mark.version('>=2.5')
def test_eqc_141347_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

