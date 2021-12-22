#coding:utf-8
#
# id:           bugs.core_0857
# title:        Containing not working correctly
# decription:
#                   Could not find build 2.0 RC3.
#                   Checked on:
#                       4.0.0.1713 SS: 1.625s.
#                       4.0.0.1346 SC: 1.675s.
#                       3.0.5.33218 SS: 1.000s.
#                       3.0.5.33084 SC: 0.890s.
#                       2.5.9.27149 SC: 0.266s.
#
#                   02-mar-2021. Re-implemented in ordeer to have ability to run this test on Linux.
#                   We run 'init_script' using charset = utf8 but then run separate ISQL-process
#                   with request to establish connection using charset = win1252.
#
#                   Checked on:
#                   * Windows: 4.0.0.2377, 3.0.8.33420, 2.5.9.27152
#                   * Linux:   4.0.0.2377, 3.0.8.33415
#
# tracker_id:   CORE-857
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
set echo on;
set bail on;
        create collation test_coll_ci_ai for win1252 from WIN_PTBR
        case insensitive
        accent insensitive
        ;

        create table test (
                id int,
                f01 varchar(100),
                f02 varchar(100) collate WIN_PTBR
        );

        insert into test(id, f01) values(1, 'IHF|groß|850xC|P1');
        update test set f02=f01;
        commit;
        create view v_test as
        select octet_length(t.f01) - octet_length(replace(t.f01, 'ß', '')) as "octet_length diff:" from test t;
"""

db_1 = db_factory(charset='WIN1252', sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  sql_cmd='''
#      set names win1252;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#          set list on;
#      select c.rdb$character_set_name as connection_cset
#      from mon$attachments a
#      join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
#      where a.mon$attachment_id = current_connection;
#
#          select t.id as "test_1 result:" from rdb$database r left join test t on t.f01 not containing 'P1' and t.f01 like 'IHF|gro_|850_C|P1';
#          select t.id as "test_2 result:" from rdb$database r left join test t on t.f01 containing 'P1' and t.f01 like 'IHF|gro_|850_C|P1';
#          select t.id as "ci_ai result:" from rdb$database r left join test t on lower(t.f02) = upper(t.f02);
#          select t.id as "between result:" from rdb$database r left join test t on lower(t.f01) between lower(t.f02) and upper(t.f02);
#          select * from v_test;
#  ''' % dict(globals(), **locals())
#  runProgram( 'isql', [ '-q' ], sql_cmd)
#
#
#---

expected_stdout_1 = """
        CONNECTION_CSET                 WIN1252
        test_1 result:                  <null>
        test_2 result:                  1
        ci_ai result:                   1
        between result:                 1
        octet_length diff:              1
"""

test_script_1 = """
    set list on;
    select c.rdb$character_set_name as connection_cset
    from mon$attachments a
    join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
    where a.mon$attachment_id = current_connection;

    select t.id as "test_1 result:" from rdb$database r left join test t on t.f01 not containing 'P1' and t.f01 like 'IHF|gro_|850_C|P1';
    select t.id as "test_2 result:" from rdb$database r left join test t on t.f01 containing 'P1' and t.f01 like 'IHF|gro_|850_C|P1';
    select t.id as "ci_ai result:" from rdb$database r left join test t on lower(t.f02) = upper(t.f02);
    select t.id as "between result:" from rdb$database r left join test t on lower(t.f01) between lower(t.f02) and upper(t.f02);
    select * from v_test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout


