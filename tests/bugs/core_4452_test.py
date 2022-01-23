#coding:utf-8

"""
ID:          issue-4772
ISSUE:       4772
TITLE:       Can`t create two collations with different names if autoddl OFF in FB 2.5.3
DESCRIPTION:
JIRA:        CORE-4452
"""

import pytest
from firebird.qa import *

substitutions = [('COLL-VERSION=\\d{2,}.\\d{2,}', 'COLL-VERSION=111.222'),
                 ('COLL-VERSION=\\d+\\.\\d+\\.\\d+\\.\\d+', 'COLL-VERSION=111.222')]

db = db_factory()

test_script = """
show collation;
set autoddl off;
commit;
create collation name_coll for utf8 from unicode CASE INSENSITIVE;
create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
commit;
show collation;
drop collation name_coll;
drop collation nums_coll;
commit;
create collation name_coll for utf8 from unicode CASE INSENSITIVE;
create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
commit;
show collation;
drop collation name_coll;
drop collation nums_coll;
commit;
show collation;
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
NAME_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88'
NUMS_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88;NUMERIC-SORT=1'

NAME_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88'
NUMS_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88;NUMERIC-SORT=1'
"""

expected_stderr = """
There are no user-defined collations in this database
There are no user-defined collations in this database
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

