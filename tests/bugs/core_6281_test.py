#coding:utf-8
#
# id:           bugs.core_6281
# title:        Invalid timestamp errors with RDB$TIME_ZONE_UTIL.TRANSITIONS
# decription:   
#                   NB: it isn crusial for this test to add 'GMT' after each of timestamp values if we are in the Eastern hemisphere.
#                   Otherwise (e.g. 'timestamp '0001-01-01', timestamp '9999-12-31') leads to:
#                       Statement failed, SQLSTATE = 22008
#                       value exceeds the range for valid timestamps
#                       -At procedure 'RDB$TIME_ZONE_UTIL.TRANSITIONS'
#               
#                   Checked on 4.0.0.1876: all OK.
#                
# tracker_id:   CORE-6281
# min_versions: []
# versions:     4.0.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select p.* 
    from rdb$time_zone_util.transitions('Europe/Moscow', timestamp '0001-01-01 GMT', timestamp '9999-12-31 GMT') p
    order by p.rdb$zone_offset, p.rdb$dst_offset, p.rdb$effective_offset, p.rdb$start_timestamp, p.rdb$end_timestamp;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$START_TIMESTAMP             1922-09-30 21:00:00.0000 GMT
    RDB$END_TIMESTAMP               1930-06-20 21:59:59.9999 GMT
    RDB$ZONE_OFFSET                 120
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            120

    RDB$START_TIMESTAMP             1991-09-29 00:00:00.0000 GMT
    RDB$END_TIMESTAMP               1992-01-18 23:59:59.9999 GMT
    RDB$ZONE_OFFSET                 120
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            120

    RDB$START_TIMESTAMP             1991-03-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1991-09-28 23:59:59.9999 GMT
    RDB$ZONE_OFFSET                 120
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             0001-01-01 00:00:00.0000 GMT
    RDB$END_TIMESTAMP               1916-07-02 21:29:42.9999 GMT
    RDB$ZONE_OFFSET                 150
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            150

    RDB$START_TIMESTAMP             1916-07-02 21:29:43.0000 GMT
    RDB$END_TIMESTAMP               1917-07-01 20:28:40.9999 GMT
    RDB$ZONE_OFFSET                 151
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            151

    RDB$START_TIMESTAMP             1917-12-27 20:28:41.0000 GMT
    RDB$END_TIMESTAMP               1918-05-31 19:28:40.9999 GMT
    RDB$ZONE_OFFSET                 151
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            151

    RDB$START_TIMESTAMP             1917-07-01 20:28:41.0000 GMT
    RDB$END_TIMESTAMP               1917-12-27 20:28:40.9999 GMT
    RDB$ZONE_OFFSET                 151
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            211

    RDB$START_TIMESTAMP             1918-09-15 20:28:41.0000 GMT
    RDB$END_TIMESTAMP               1919-05-31 19:28:40.9999 GMT
    RDB$ZONE_OFFSET                 151
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            211

    RDB$START_TIMESTAMP             1918-05-31 19:28:41.0000 GMT
    RDB$END_TIMESTAMP               1918-09-15 20:28:40.9999 GMT
    RDB$ZONE_OFFSET                 151
    RDB$DST_OFFSET                  120
    RDB$EFFECTIVE_OFFSET            271

    RDB$START_TIMESTAMP             1919-05-31 19:28:41.0000 GMT
    RDB$END_TIMESTAMP               1919-06-30 23:59:59.9999 GMT
    RDB$ZONE_OFFSET                 151
    RDB$DST_OFFSET                  120
    RDB$EFFECTIVE_OFFSET            271

    RDB$START_TIMESTAMP             1919-08-15 20:00:00.0000 GMT
    RDB$END_TIMESTAMP               1921-02-14 19:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1921-09-30 20:00:00.0000 GMT
    RDB$END_TIMESTAMP               1922-09-30 20:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1930-06-20 22:00:00.0000 GMT
    RDB$END_TIMESTAMP               1981-03-31 20:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1981-09-30 20:00:00.0000 GMT
    RDB$END_TIMESTAMP               1982-03-31 20:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1982-09-30 20:00:00.0000 GMT
    RDB$END_TIMESTAMP               1983-03-31 20:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1983-09-30 20:00:00.0000 GMT
    RDB$END_TIMESTAMP               1984-03-31 20:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1984-09-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1985-03-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1985-09-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1986-03-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1986-09-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1987-03-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1987-09-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1988-03-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1988-09-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1989-03-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1989-09-23 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1990-03-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1990-09-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1991-03-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1992-01-19 00:00:00.0000 GMT
    RDB$END_TIMESTAMP               1992-03-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1992-09-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1993-03-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1993-09-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1994-03-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1994-09-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1995-03-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1995-09-23 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1996-03-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1996-10-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1997-03-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1997-10-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1998-03-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1998-10-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1999-03-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1999-10-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2000-03-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2000-10-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2001-03-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2001-10-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2002-03-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2002-10-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2003-03-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2003-10-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2004-03-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2004-10-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2005-03-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2005-10-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2006-03-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2006-10-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2007-03-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2007-10-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2008-03-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2008-10-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2009-03-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2009-10-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2010-03-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2010-10-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2011-03-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             2014-10-25 22:00:00.0000 GMT
    RDB$END_TIMESTAMP               9999-12-31 23:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            180

    RDB$START_TIMESTAMP             1919-07-01 00:00:00.0000 GMT
    RDB$END_TIMESTAMP               1919-08-15 19:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1921-02-14 20:00:00.0000 GMT
    RDB$END_TIMESTAMP               1921-03-20 18:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1921-08-31 19:00:00.0000 GMT
    RDB$END_TIMESTAMP               1921-09-30 19:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1981-03-31 21:00:00.0000 GMT
    RDB$END_TIMESTAMP               1981-09-30 19:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1982-03-31 21:00:00.0000 GMT
    RDB$END_TIMESTAMP               1982-09-30 19:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1983-03-31 21:00:00.0000 GMT
    RDB$END_TIMESTAMP               1983-09-30 19:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1984-03-31 21:00:00.0000 GMT
    RDB$END_TIMESTAMP               1984-09-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1985-03-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1985-09-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1986-03-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1986-09-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1987-03-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1987-09-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1988-03-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1988-09-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1989-03-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1989-09-23 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1990-03-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1990-09-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1992-03-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1992-09-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1993-03-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1993-09-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1994-03-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1994-09-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1995-03-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1995-09-23 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1996-03-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1996-10-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1997-03-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1997-10-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1998-03-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1998-10-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1999-03-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               1999-10-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2000-03-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2000-10-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2001-03-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2001-10-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2002-03-30 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2002-10-26 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2003-03-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2003-10-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2004-03-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2004-10-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2005-03-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2005-10-29 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2006-03-25 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2006-10-28 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2007-03-24 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2007-10-27 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2008-03-29 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2008-10-25 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2009-03-28 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2009-10-24 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             2010-03-27 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2010-10-30 22:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  60
    RDB$EFFECTIVE_OFFSET            240

    RDB$START_TIMESTAMP             1921-03-20 19:00:00.0000 GMT
    RDB$END_TIMESTAMP               1921-08-31 18:59:59.9999 GMT
    RDB$ZONE_OFFSET                 180
    RDB$DST_OFFSET                  120
    RDB$EFFECTIVE_OFFSET            300

    RDB$START_TIMESTAMP             2011-03-26 23:00:00.0000 GMT
    RDB$END_TIMESTAMP               2014-10-25 21:59:59.9999 GMT
    RDB$ZONE_OFFSET                 240
    RDB$DST_OFFSET                  0
    RDB$EFFECTIVE_OFFSET            240


    Records affected: 78
  """

@pytest.mark.version('>=4.0.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

