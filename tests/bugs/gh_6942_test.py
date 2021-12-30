#coding:utf-8
#
# id:           bugs.gh_6942
# title:        Incorrect singleton error with MERGE and RETURNING
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6942
#               
#                   Confirmed bug on 5.0.0.172.
#                   Checked on: 5.0.0.181 - works fine.
#                
# tracker_id:   
# min_versions: ['5.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test(
        n1 integer,
        n2 integer
    );

    insert into test values (1, 10);
    insert into test values (2, 20);
    commit;

    --------------------------------------------------

    merge into test
        using (
            select 2 x from rdb$database
            union all
            select 3 x from rdb$database
        ) t
            on test.n1 = t.x
        when not matched then insert values (3, 30)
        returning n1, n2;
    rollback;

    --------------------------------------------------

    set term ^;
    execute block returns (
        o1 integer,
        o2 integer
    )
    as
    begin
        merge into test
            using (
                select 2 x from rdb$database
                union all
                select 3 x from rdb$database
            ) t
                on test.n1 = t.x
            when not matched then insert values (3, 30)
            returning n1, n2 into o1, o2;

        suspend;
    end
    ^
    set term ;^

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    N1                              3
    N2                              30
    O1                              3
    O2                              30
"""

@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
