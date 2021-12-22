#coding:utf-8
#
# id:           bugs.core_3924
# title:        Bugcheck 291 (cannot find record back version) if GTT is modified concurrently using at least one read-committed read-only transaction
# decription:   
# tracker_id:   CORE-3924
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('-concurrent.*', ''), ('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate global temporary table gt(f01 int) on commit preserve rows;
    commit;
    insert into gt values(1);
    commit;
    set transaction read only read committed record_version;
    delete from gt;
    set term ^;
    execute block as 
    begin 
        in autonomous transaction 
        do update gt set f01=-1; 
    end
    ^
    set term ;^
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 40001
    deadlock
    -update conflicts with concurrent update
    -At block line: 1, col: 53
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

