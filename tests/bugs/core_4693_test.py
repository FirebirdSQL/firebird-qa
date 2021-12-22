#coding:utf-8
#
# id:           bugs.core_4693
# title:        CTE Aliases ('Column unknown' when recursive CTE contain join with *alias* rather than table name)
# decription:   
# tracker_id:   CORE-4693
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table gd_goodgroup (
        id integer,
        parent integer,
        name varchar(20)
    );
    commit;
    
    insert into gd_goodgroup(id, parent, name) values( 1, null, 'Big Brother');
    insert into gd_goodgroup(id, parent, name) values( 2,    1, 'Middle Manager #1');
    insert into gd_goodgroup(id, parent, name) values( 3,    1, 'Middle Manager #2');
    insert into gd_goodgroup(id, parent, name) values( 4,    2, 'Worker #1');
    insert into gd_goodgroup(id, parent, name) values( 5,    2, 'Worker #2');
    insert into gd_goodgroup(id, parent, name) values( 6,    3, 'Worker #3');
    commit;

    set list on;

    with recursive
    group_tree as (
        select id, parent, name, cast('' as varchar(255)) as indent
        from gd_goodgroup
        where parent is null
        
        union all
        
        select g.id, g.parent, g.name, h.indent || rpad('', 2)
        from gd_goodgroup g join group_tree h
        on g.parent = h.id
    )
    select gt.indent || gt.name as info
    from group_tree gt;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INFO                            Big Brother
    INFO                              Middle Manager #1
    INFO                                Worker #1
    INFO                                Worker #2
    INFO                              Middle Manager #2
    INFO                                Worker #3
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

