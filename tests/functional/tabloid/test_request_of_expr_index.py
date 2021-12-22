#coding:utf-8
#
# id:           functional.tabloid.request_of_expr_index
# title:        request of expression index could run outside of main request's snapshot.
# decription:   
#                   Test verifies fix that is described here:
#                       https://github.com/FirebirdSQL/firebird/commit/26ee42e69d0a381c166877e3c2a17893d85317e0
#                   Thanks Vlad for example of implementation and suggestions.
#                   ::: NOTE :::
#                   It is crusial that final SELECT must run in TIL = read committed read consistency.
#               
#                   Confirmed bug on 4.0.0.1810.
#                   Checked on 4.0.0.1812 (SS/CS) - all OK.
#                
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate global temporary table gtt_snap (id bigint) on commit delete rows;

    set term ^;
    create or alter function fn_idx returns int as
        declare ret int;
    begin
        insert into gtt_snap values (rdb$get_context('SYSTEM', 'SNAPSHOT_NUMBER'));
        return 1;
    end
    ^
    set term ;^
    commit;

    recreate table fix_test (id int);
    create index t_expr_idx on fix_test computed by ((fn_idx()));
    commit;

    set transaction read committed READ CONSISTENCY; -- ::: NB :::

    insert into fix_test values (rdb$get_context('SYSTEM', 'SNAPSHOT_NUMBER'));

    -- numbers must be equal:
    set list on;
    select 
       -- f.id as fix_id, g.id as gtt_id,
       iif( f.id = g.id
           ,'Expected: values are equal.'
           ,'MISMATCH: fixed table ID=' || coalesce( cast(f.id as varchar(20)), '<null>' ) || '; GTT ID=' || coalesce( cast(g.id as varchar(20)), '<null>' )
          ) as result
    from fix_test f
    cross join gtt_snap g
    ;
    commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          Expected: values are equal.
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

