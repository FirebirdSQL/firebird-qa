#coding:utf-8
#
# id:           bugs.core_6252
# title:        UNIQUE / PRIMARY KEY constraint can be violated when AUTODDL = OFF and mixing commands for DDL and DML
# decription:   
#                   Reproduced bug on 3.0.6.33247, 4.0.0.1782.
#                   Checked on 3.0.6.33255; 4.0.0.1785 (both - SS and CS) - works fine.
#                
# tracker_id:   CORE-6252
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off; -- [ !! ]
    commit;

    recreate table test1(
        a int not null,
        b int not null
    );

    recreate table test2(
        u int not null,
        v int not null
    );

    commit;

    insert into test1(a, b) values (1,1);
    insert into test1(a, b) values (1,2);

    insert into test2(u, v) values (1,1);
    insert into test2(u, v) values (1,2);
    commit;


    -------------------------------------------------------
    update test1 set b = 1;
    alter table test1 add constraint test1_unq unique (a);
    commit;

    -------------------------------------------------------
    rollback; -- otherwise exception about PK violation will be supressed by 1st one (about test1_UNQ)
    -------------------------------------------------------

    update test2 set v = 1;
    alter table test2 add constraint test2_pk primary key (u);
    commit;

    set list on;
    select * from test1;
    select * from test2;
    rollback;

    -- We have to ensure that there are no indices that were created (before this bug fixed)
    -- for maintainace of PK/UNQ constraints:
    select
        ri.rdb$index_name idx_name
        ,ri.rdb$unique_flag idx_uniq
    from rdb$database r
    left join rdb$indices ri on
        ri.rdb$relation_name starting with 'TEST'
        and ri.rdb$system_flag is distinct from 1
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               1
    B                               1
    A                               1
    B                               2

    U                               1
    V                               1
    U                               1
    V                               1

    IDX_NAME                        <null>
    IDX_UNIQ                        <null>
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST1_UNQ" on table "TEST1"
    -Problematic key value is ("A" = 1)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST2_PK" on table "TEST2"
    -Problematic key value is ("U" = 1)
  """

@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

