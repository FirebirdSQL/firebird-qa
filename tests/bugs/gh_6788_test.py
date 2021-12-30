#coding:utf-8
#
# id:           bugs.gh_6788
# title:        Extend EXTRACT to extract time zone strings
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6788
#               
#                   Commit ('master' only; not 4.0!):
#                       https://github.com/FirebirdSQL/firebird/commit/a02f0dea8163de64caa13c9a8637fa28eea0e9d3
#                   
#                   Checked on intermediate build 4.0.0.2452 (timestamp: 03-may-2021 14:48).
#                
# tracker_id:   
# min_versions: ['5.0']
# versions:     5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 5.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    -- Examples from ticket:
    select extract(timezone_name from timestamp '2021-05-03 10:00 America/Sao_Paulo') as tz_info1 from rdb$database; -- America/Sao_Paulo
    select extract(timezone_name from timestamp '2021-05-03 10:00 -3:00')  as tz_info2  from rdb$database; -- -03:00

    --================================
    -- Additional check.
    -- Every record of RDB$TIME_ZONE  table must have value in 'rdb$time_zone_name' column
    -- that can be extracted correctly and result must be exactly this value.
    -- Spaces between date/time and timezone_name are intentionally replaced with chr(9) sequences
    -- (to make parser life more harder :)).
    set term ^;
    create or alter procedure sp_get_tz_name returns(tz_name rdb$time_zone_name ) as
      declare v_stt varchar(255);
    begin
      for
        select z.rdb$time_zone_name from rdb$time_zones z -- 4debug: where z.rdb$time_zone_name <> 'America/Sao_Paulo'
      as cursor c
      do begin
        v_stt = 'extract(timezone_name from timestamp ''2021-05-03'|| lpad('',15,ascii_char(9)) || '10:00' || lpad('', 150, ascii_char(9)) || trim(c.rdb$time_zone_name) || ''')';
        execute statement 'select ' || v_stt || ' from rdb$database' into tz_name;
        suspend;
      end
    end
    ^
    set term ;^
    commit;
    -- Following query must always return empty resultset (0 rows).
    -- Otherwise we can conclude that EXTRACT(TIMEZONE_NAME ...) fails
    -- for some argument from rdb$time_zones table:
    select tz_name, iif(min(i)=1,1,null) as "found_in_rdb$time_zones", iif(max(i)=2, 1, null) as "correctly_extracted_in_sp"
    from (
        select z.rdb$time_zone_name as tz_name, 1 as i
        from rdb$time_zones z
        union all
        select p.tz_name, 2 as i
        from sp_get_tz_name p
    )
    group by tz_name
    having min(i) is distinct from 1 or max(i) is distinct from 2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TZ_INFO1 America/Sao_Paulo
    TZ_INFO2 -03:00
"""

@pytest.mark.version('>=5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
