#coding:utf-8
#
# id:           bugs.core_0101
# title:        JOIN the same table - problem with alias names
# decription:
# tracker_id:   CORE-0101
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
    -- Confirmed wrong result on WI-V1.5.6.5026, all above wirks fine.
    recreate table test(id int);
    insert into test values(1);
    insert into test values(-1);
    insert into test values(-2);
    insert into test values(2);
    commit;

    --set plan on;
    set list on;

    select *
    from (
        select test.id a_id, b.id as b_id
        from test test
        join test b on test.id = b.id
    ) order by 1,2
    ;

    create index test_id on test(id);

    select *
    from (
        select test.id a_id, b.id as b_id
        from test test
        join test b on test.id = b.id
    ) order by 1,2
    ;

    select *
    from (
        select test.id a_id, b.id as b_id
        from (select id from test order by id) test
        join (select id from test order by id) b on test.id = b.id
    ) order by 1,2
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A_ID                            -2
    B_ID                            -2

    A_ID                            -1
    B_ID                            -1

    A_ID                            1
    B_ID                            1

    A_ID                            2
    B_ID                            2



    A_ID                            -2
    B_ID                            -2

    A_ID                            -1
    B_ID                            -1

    A_ID                            1
    B_ID                            1

    A_ID                            2
    B_ID                            2



    A_ID                            -2
    B_ID                            -2

    A_ID                            -1
    B_ID                            -1

    A_ID                            1
    B_ID                            1

    A_ID                            2
    B_ID                            2
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

