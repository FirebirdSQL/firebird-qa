#coding:utf-8

"""
ID:          issue-5123
ISSUE:       5123
TITLE:       Make ISQL display character set when sqlda_display is on
DESCRIPTION:
JIRA:        CORE-4826
FBTEST:      bugs.core_4826
NOTES:
    [12.12.2023] pzotov
    Added 'SQLSTATE' in substitutions: runtime error must not be filtered out by '?!(...)' pattern
    ("negative lookahead assertion", see https://docs.python.org/3/library/re.html#regular-expression-syntax).
    Added 'combine_output = True' in order to see SQLSTATE if any error occurs.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- Before WI-T3.0.0.31876 charsets were displeyd for field of ANY type, not only for text.
    recreate table test1(
      id1 smallint,
      id2 int,
      id3 bigint,
      nf1 numeric(12,4),
      nf2 double precision,
      nf3 float,
      tf1 date,
      tf2 time,
      tf3 timestamp,
      boo boolean,
      tx1 char character set utf8,
      tx2 varchar(10) character set iso8859_1,
      tx3 nchar,
      -- doesn`t compile: tx4 nvarchar(10),
      tx4 national character varying(32760),
      tb1 blob sub_type 1 character set win1251,
      tb2 blob sub_type 0
    );
    commit;

    set sqlda_display on;
    select * from test1;
    commit;
"""

act = isql_act('db', test_script, substitutions = [ ('^((?!SQLSTATE|sqltype).)*$', ''), ('[ \t]+', ' ') ] )

expected_stdout = """
    01: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
    02: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    04: sqltype: 580 INT64 Nullable scale: -4 subtype: 1 len: 8
    05: sqltype: 480 DOUBLE Nullable scale: 0 subtype: 0 len: 8
    06: sqltype: 482 FLOAT Nullable scale: 0 subtype: 0 len: 4
    07: sqltype: 570 SQL DATE Nullable scale: 0 subtype: 0 len: 4
    08: sqltype: 560 TIME Nullable scale: 0 subtype: 0 len: 4
    09: sqltype: 510 TIMESTAMP Nullable scale: 0 subtype: 0 len: 8
    10: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
    11: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 4 charset: 4 UTF8
    12: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 10 charset: 21 ISO8859_1
    13: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 1 charset: 21 ISO8859_1
    14: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 32760 charset: 21 ISO8859_1
    15: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 52 WIN1251
    16: sqltype: 520 BLOB Nullable scale: 0 subtype: 0 len: 8
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout

