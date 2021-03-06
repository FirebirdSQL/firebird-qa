#coding:utf-8
#
# id:           bugs.core_1173
# title:        Expression index based on computed fields
# decription:   
#                   Index based on COMPUTED-BY column must be taken in account by optimizer.
#                   13.08.2020: replaced expected_stdout with only PLAN output (concrete data values no matter in this test).
#                   Checked on:
#                       4.0.0.2151 SS: 1.475s.
#                       3.0.7.33348 SS: 1.172s.
#                       2.5.9.27150 SC: 0.311s.
#                 
# tracker_id:   
# min_versions: ['2.5.4']
# versions:     2.5.4
# qmid:         bugs.core_1173

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create sequence g;
    recreate table test (
      fcode integer not null,
      fdate date not null,
      ftime time not null,
      fcomp computed by (fdate+ftime),
      constraint test_pk primary key (fcode)
    );

    insert into test(fcode, fdate, ftime)
    select gen_id(g,1), dateadd( gen_id(g,1) day to cast('01.01.2010' as date) ), dateadd( gen_id(g,1) second to cast('00:00:00' as time) ) from rdb$types rows 200;
    commit;

    -- #########################################################################

    -- Index on COMPUTED BY field, ascending:
    create index test_on_computed_field_asc on test computed by (fcomp);
    commit;

    set plan on;

    select * from test where fcomp>'now' rows 0;
    commit;

    drop index test_on_computed_field_asc;
    commit;

    -- COMPUTED-BY index with expression equal to computed-by column, ascending:
    create index test_fdate_ftime_asc on test computed by (fdate+ftime);
    select * from test where fcomp>'now' rows 0;
    commit;

    drop index test_fdate_ftime_asc;
    commit;

    -- #########################################################################

    -- Index on COMPUTED BY field, descending:
    create descending index test_on_computed_field_dec on test computed by (fcomp);
    commit;

    set plan on;

    select * from test where fcomp>'now' rows 0;
    commit;

    drop index test_on_computed_field_dec;
    commit;

    -- COMPUTED-BY index with expression equal to computed-by column, decending:
    create descending index test_fdate_ftime_dec on test computed by (fdate+ftime);
    select * from test where fcomp>'now' rows 0;
    commit;

    drop index test_fdate_ftime_dec;
    commit;

    set plan off;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST INDEX (TEST_ON_COMPUTED_FIELD_ASC))
    PLAN (TEST INDEX (TEST_FDATE_FTIME_ASC))
    PLAN (TEST INDEX (TEST_ON_COMPUTED_FIELD_DEC))
    PLAN (TEST INDEX (TEST_FDATE_FTIME_DEC))
  """

@pytest.mark.version('>=2.5.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

