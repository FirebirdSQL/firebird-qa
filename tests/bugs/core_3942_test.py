#coding:utf-8
#
# id:           bugs.core_3942
# title:        Restore from gbak backup using service doesn't report an error
# decription:
#                    Checked on:
#                      WI-V2.5.6.26994 SC
#                      WI-V3.0.0.32474 SS/SC/CS
#                      LI-T4.0.0.130 // 11.04.2016
#                      WI-T4.0.0.132 // 12.04.2016
#
# tracker_id:   CORE-3942
# min_versions: ['2.5']
# versions:     2.5
# qmid:         None

"""
ID:          issue-4275
ISSUE:       4275
TITLE:       Restore from gbak backup using service doesn't report an error
DESCRIPTION:
JIRA:        CORE-3942
"""

import pytest
from pathlib import Path
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()

act = python_act('db')

fbk_file = temp_file('test.fbk')

@pytest.mark.version('>=2.5')
def test_1(act: Action, fbk_file: Path):
    with act.connect_server() as srv:
        srv.database.backup(database=act.db.db_path, backup=fbk_file)
        srv.wait()
        # Try overwrite existing database file
        with pytest.raises(DatabaseError,
                           match='atabase .* already exists.  To replace it, use the -REP switch'):
            srv.database.restore(database=act.db.db_path, backup=fbk_file)
            srv.wait()


