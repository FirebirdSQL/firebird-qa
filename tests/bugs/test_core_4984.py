#coding:utf-8
#
# id:           bugs.core_4984
# title:        Ordering by compound index together with a range condition gives wrong results
# decription:   
# tracker_id:   CORE-4984
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed on WI-V3.0.0.32081: wrong output for CHECKED_RESULT_1, CHECKED_RESULT_3 & CHECKED_RESULT_4
    -- (but this was only for ASC index; for DESC index all was fine).
    -- Since WI-V3.0.0.32137 result is correct.

    recreate table test_idx(
        id integer not null,
        val integer,
        create_date date,
        primary key (id)
    );
    commit;

    insert into test_idx values(1,1,'2016-01-01');
    insert into test_idx values(2,1,'2015-01-02');
    insert into test_idx values(3,2,'1999-09-09');
    insert into test_idx values(4,2,'2015-02-02');
    insert into test_idx values(5,3,'2015-03-01');
    insert into test_idx values(6,3,'2015-03-02');
    insert into test_idx values(7,4,'2015-04-01');
    commit;

    set list on;
    
    select 'natural_scan' as msg, cast(min(create_date) as date) as expected_result from test_idx where val >=1 and val <=3;
    commit;

    create index idx_val_create_date_asc on test_idx (val, create_date);
    commit;

    select 'index_scan_ascending' as msg, cast(min(create_date) as date) as checked_result_1 
    from test_idx where val >=1 and val <=3;
    select 'index_scan_ascending' as msg, cast(min(create_date) as date) as checked_result_2 
    from (select * from test_idx where val > 0 and val < 4 order by val);
    select 'index_scan_ascending' as msg, cast(min(create_date) as date) as checked_result_3 
    from test_idx where 4 > val and 0 < val;
    select 'index_scan_ascending' as msg, cast(min(create_date) as date) as checked_result_4 
    from test_idx where val between 1 and 3;
    select 'index_scan_ascending' as msg, cast(min(create_date) as date) as checked_result_5 
    from test_idx where val in (1,2,3);
    commit;

    drop index idx_val_create_date_asc;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';

    create descending index idx_val_create_date_desc on test_idx (val, create_date);
    commit;

    select 'index_scan_descending' as msg, cast(min(create_date) as date) as checked_result_1 
    from test_idx where val >=1 and val <=3;
    select 'index_scan_descending' as msg, cast(min(create_date) as date) as checked_result_2 
    from (select * from test_idx where val > 0 and val < 4 order by val desc);
    select 'index_scan_descending' as msg, cast(min(create_date) as date) as checked_result_3 
    from test_idx where 4 > val and 0 < val;
    select 'index_scan_descending' as msg, cast(min(create_date) as date) as checked_result_4 
    from test_idx where val between 1 and 3;
    select 'index_scan_descending' as msg, cast(min(create_date) as date) as checked_result_5 
    from test_idx where val in (1,2,3);

    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             natural_scan
    EXPECTED_RESULT                 1999-09-09

    MSG                             index_scan_ascending
    CHECKED_RESULT_1                1999-09-09
    MSG                             index_scan_ascending
    CHECKED_RESULT_2                1999-09-09
    MSG                             index_scan_ascending
    CHECKED_RESULT_3                1999-09-09
    MSG                             index_scan_ascending
    CHECKED_RESULT_4                1999-09-09
    MSG                             index_scan_ascending
    CHECKED_RESULT_5                1999-09-09

    MSG                             index_scan_descending
    CHECKED_RESULT_1                1999-09-09
    MSG                             index_scan_descending
    CHECKED_RESULT_2                1999-09-09
    MSG                             index_scan_descending
    CHECKED_RESULT_3                1999-09-09
    MSG                             index_scan_descending
    CHECKED_RESULT_4                1999-09-09
    MSG                             index_scan_descending
    CHECKED_RESULT_5                1999-09-09
  """

@pytest.mark.version('>=3.0')
def test_core_4984_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

