#coding:utf-8
#
# id:           bugs.core_6034
# title:        The original time zone should be set to the current time zone at routine invocation
# decription:   
#                   Confirmed bug on 4.0.0.1457: FAILED.
#                   Checked on 4.0.0.1479: OK, 1.377s.
#                
# tracker_id:   CORE-6034
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns (ts1 varchar(100), ts2 varchar(100))
    as
        declare procedure p0 returns (t1 timestamp with time zone, t2 timestamp with time zone) as
        begin
            set time zone 'America/New_York';
            t1 = current_timestamp;
            set time zone local;
            t2 = current_timestamp;
        end

        declare procedure p1 returns (t1 timestamp with time zone, t2 timestamp with time zone) as
        begin
            set time zone 'America/Los_Angeles';
            execute procedure p0 returning_values t1, t2;
        end
        declare t1 timestamp with time zone;
        declare t2 timestamp with time zone;
    begin
        -- Initial time zone: 'America/Sao_Paulo';
        execute procedure p1 returning_values t1, t2;
        ts1 = substring( cast(t1 as varchar(100)) from 26 );
        ts2 = substring( cast(t2 as varchar(100)) from 26 );
        suspend;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TS1                             America/New_York
    TS2                             America/Los_Angeles
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

