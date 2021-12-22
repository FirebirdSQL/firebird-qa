#coding:utf-8
#
# id:           bugs.core_1379
# title:        Invalid parameter type when using it in CHAR_LENGTH function
# decription:   
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         bugs.core_1379

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('-At block line: [\\d]+, col: [\\d]+', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns(r int) as
    begin
        execute statement ('select 1 from rdb$database where char_length(?) = 0') (1) into r;
        suspend;
    end
    ^
    execute block returns(r int) as
    begin
        execute statement ('select 1 from rdb$database where char_length(?) = 0') ('') into r;
        suspend;
    end
    ^
    execute block returns(r int) as
        declare c varchar(1) = '';
    begin
        execute statement ('select 1 from rdb$database where char_length(?) = 0') (c) into r;
        suspend;
    end
    ^
    set term ;^
    -- 05.05.2015: 
    -- 1) changed min version to 2.5 (according to ticket header info; output in 2.5 and 3.0 now fully matches)
    -- 2) removed STDOUT (for the first ES);
    -- 3) changed expected STDERR: all three ES must now raise exception 'Data type unknown'.
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY004
    Dynamic SQL Error
    -SQL error code = -804
    -Data type unknown
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = HY004
    Dynamic SQL Error
    -SQL error code = -804
    -Data type unknown
    -At block line: 3, col: 9

    Statement failed, SQLSTATE = HY004
    Dynamic SQL Error
    -SQL error code = -804
    -Data type unknown
    -At block line: 3, col: 9
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

