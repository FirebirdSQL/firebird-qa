#coding:utf-8
#
# id:           bugs.core_2957
# title:        count(*) from big table returns negative result
# decription:   
#                   NB: in fact, this test must check data types in SQLDA for columns that are results of aggregated functions
#                   COUNT and (maybe) SUM.
#                   As of 2.5, COUNT(*) is still displayed as `LONG` (sql_len = 4 bytes ==> integer, max 2^32-1) rather than INT64.
#                   Test was made only for 3.0 (as it was said in the ticket header, "Fixed version(s)") and I've added here
#                   also check for results of aggregating (for smallint, int and bigint) and ranging analytical functions.
#               
#                   30.10.2019. Separated code for 4.0 because of new output types:
#                       ** sum(<bigint>) - its type is "32752 numeric(38)";
#                       ** added new column: sum(<decfloat>) - it will have type "32762 decfloat(34)".
#                   Checked on: 4.0.0.1635 SS: 1.236s; 3.0.5.33182 SS: 1.001s.
#                   25.06.2020, 4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
#                
# tracker_id:   CORE-2957
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test(id bigint, fx int, fs smallint);
    commit;
    set sqlda_display;
    set planonly;

    select 
         count( id ) cnt_agg
        ,sum( id ) sum_agg_n64
        ,sum( fx ) sum_agg_n32
        ,sum( fs ) sum_agg_n16
    from test;

    select
         count( id )over()  cnt_ovr
        ,sum( id )over()    sum_ovr_n64
        ,sum( fx )over()    sum_ovr_n32
        ,sum( fs )over()    sum_ovr_n16

        ,row_number()over() cnt_ovr_n64
        ,rank()over()       rnk_ovr_n64
        ,dense_rank()over() drn_ovr_n64
    from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    02: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    04: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    02: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    04: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    05: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    06: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    07: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_2957_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('^((?!sqltype).)*$', ''), ('[ \t]+', ' ')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    recreate table test(id bigint, fx int, fs smallint, dx decfloat(34), ds decfloat(16) );
    commit;
    set sqlda_display;
    set planonly;

    select 
         count( id ) cnt_agg
        ,sum( id ) sum_agg_n64
        ,sum( fx ) sum_agg_n32
        ,sum( fs ) sum_agg_n16
        ,sum( dx ) sum_agg_df34
        ,sum( ds ) sum_agg_df16
    from test;

    select
         count( id )over()  cnt_ovr
        ,sum( id )over()    sum_ovr_n64
        ,sum( fx )over()    sum_ovr_n32
        ,sum( fs )over()    sum_ovr_n16
        ,sum( dx )over()    sum_ovr_df34
        ,sum( ds )over()    sum_ovr_df16

        ,row_number()over() cnt_ovr_n64
        ,rank()over()       rnk_ovr_n64
        ,dense_rank()over() drn_ovr_n64
    from test;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    02: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    04: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    05: sqltype: 32762 DECFLOAT(34) Nullable scale: 0 subtype: 0 len: 16
    06: sqltype: 32762 DECFLOAT(34) Nullable scale: 0 subtype: 0 len: 16
    01: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    02: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    04: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    05: sqltype: 32762 DECFLOAT(34) Nullable scale: 0 subtype: 0 len: 16
    06: sqltype: 32762 DECFLOAT(34) Nullable scale: 0 subtype: 0 len: 16
    07: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    08: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
    09: sqltype: 580 INT64 scale: 0 subtype: 0 len: 8
  """

@pytest.mark.version('>=4.0')
def test_core_2957_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

