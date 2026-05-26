#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/a5ec02b568902e284f1305fe8aaf8f607bed9c25
TITLE:       Fixed NOT NULL fields in virtual tables
DESCRIPTION:
    Fields MON$SEC_DATABASE and MON$FILE_ID (from MON$SEC_DATABASE) were displayed in SQLDA as NULLABLE
    since shared metacache was introduced (6.0.0.1771).
NOTES:
    Original letter to FB-team: 10.05.2026 2214, subj:
    "shared-metacache: weird SQLDA for query to mon$database ( MON$FILE_ID & MON$SEC_DATABASE )"
    [26.05.2025] pzotov
    Confirmed bug on 6.0.0.1771, 6.0.0.1959.
    Checked on 6.0.0.1965-f9a8d1a.
"""

import pytest
from firebird.qa import *

test_sql = f"""
    set list on;
    set sqlda_display on;
    select mon$sec_database, mon$file_id from mon$database rows 0;
"""

db = db_factory()
substitutions = [ ('^((?!SQLSTATE|sqltype:).)*$', ''), ]
act = isql_act('db', test_sql, substitutions = substitutions)

@pytest.mark.version('>=6')
def test_1(act: Action):
    act.expected_stdout = f"""
        01: sqltype: 452 TEXT scale: 0 subtype: 0 len: 7 charset: 2 SYSTEM.ASCII
        02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 255 charset: 2 SYSTEM.ASCII
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
