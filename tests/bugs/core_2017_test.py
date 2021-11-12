#coding:utf-8
#
# id:           bugs.core_2017
# title:        I/O statistics for stored procedures are not accounted in monitoring tables
# decription:
#                   We open TWO cursors within the same attachments and:
#                   1) make query to procedure inside cursor-1 (trivial count from table there);
#                   2) ask MON$ tables inside cur-2 with aquiring IO statistics (fetches) for cur-1 statement.
#                   Number of fetches should be not less then 202400 - see results for 2.1.x, 2.5.x and 3.0 below.
#
#                   17.12.2016 NOTE. Value of fetches in 3.0.2 and 4.0.0 was significantly reduced (~ twice) since ~25-nov-2016
#                   See results for: 4.0.0.459 and 3.0.2.32641
#                   Possible reason:
#                   https://github.com/FirebirdSQL/firebird/commit/8d5b1ff46ed9f22be4a394b941961c522e063ed1
#                   https://github.com/FirebirdSQL/firebird/commit/dac882c97e2642e260abef475de75c490c5e4bc7
#                   "Introduced small per-relation cache of physical numbers of data pages.
#                   It allows to reduce number of pointer page fetches and improves performance."
#
#
# tracker_id:   CORE-2017
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.5.7
# resources: None

substitutions_1 = []

init_script_1 = """
    create table T (C integer);
    commit;

    set term ^ ;

    execute block
    as
    declare i int = 0;
    begin
      while (i < 100000) do
      begin
        insert into T values (:i);
        i = i + 1;
      end
    end ^
    commit ^

    create procedure sp_test
    returns (i bigint)
    as
    begin
     select count(*)
     from T
     into :i;
     suspend;
    end ^

    commit ^
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#
#  # Obtain engine version:
#  engine = str(db_conn.engine_version) # convert to text because 'float' object has no attribute 'startswith'
#
#  stt1 = db_conn.cursor()
#  stt2 = db_conn.cursor()
#
#  sp_query = "select * from sp_test"
#  stt2.execute(sp_query)
#  for row in stt2:
#    pass
#
#  # do NOT!! >>> con1.commit()
#
#  # Threshold: minimal value of fetches that should be reflected in mon$tables.
#
#  MIN_FETCHES = 202400 if engine.startswith('2.5') else 104500
#
#  sql_io='''
#      select
#         -- i.mon$page_fetches
#         --,m.mon$sql_text
#         --,rdb$get_context('SYSTEM','ENGINE_VERSION')
#         iif( i.mon$page_fetches > %(MIN_FETCHES)s, 'IO statistics for procedure is OK',
#              'Strange low value for fetches: ' || i.mon$page_fetches
#            ) as fetches_result
#      from rdb$database r
#          left join mon$statements m on
#              m.mon$sql_text containing '%(sp_query)s'
#              and m.mon$sql_text NOT containing 'mon$statements'
#          left join  mon$io_stats i on
#              m.mon$stat_id = i.mon$stat_id and i.mon$stat_group = 3
#      ;
#  ''' % locals()
#  stt1.execute(sql_io)
#
#  for row in stt1:
#    print(row[0])
#
#  # (0, 'select * from sp_test', '2.1.0')
#  # (0, 'select * from sp_test', '2.1.1')
#  # (202472, 'select * from sp_test', '2.1.2')
#  # (202472, 'select * from sp_test', '2.1.3')
#  # (202472, 'select * from sp_test', '2.1.7')
#  # (202472, 'select * from sp_test', '2.5.0')
#  # (202472, 'select * from sp_test', '2.5.1')
#  # (202472, 'select * from sp_test', '2.5.2')
#  # (202472, 'select * from sp_test', '2.5.3')
#  # BEFORE 3.0.2.32641: (202472, 'select * from sp_test', '3.0.0') // after: 104942
#  # BEFORE 4.0.0.459:   (202472, 'select * from sp_test', '4.0.0') // after: 104942
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
IO statistics for procedure is OK
"""

@pytest.mark.version('>=2.5.7')
def test_1(act_1: Action, capsys):
    sp_query = 'select * from sp_test'
    sql_io = '''
        select
           iif( i.mon$page_fetches > 104500, 'IO statistics for procedure is OK',
                'Strange low value for fetches: ' || i.mon$page_fetches
              ) as fetches_result
        from rdb$database r
            left join mon$statements m on
                m.mon$sql_text containing 'select * from sp_test'
                and m.mon$sql_text NOT containing 'mon$statements'
            left join  mon$io_stats i on
                m.mon$stat_id = i.mon$stat_id and i.mon$stat_group = 3
        ;
    '''
    act_1.expected_stdout = expected_stdout_1
    with act_1.db.connect() as con:
        stt1 = con.cursor()
        stt2 = con.cursor()
        stt2.execute(sp_query)
        stt2.fetchall()
        stt1.execute(sql_io)
        for row in stt1:
            print(row[0])
        act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
