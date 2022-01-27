#coding:utf-8

"""
ID:          issue-6817
ISSUE:       6817
TITLE:       Command switch "-fetch_password <passwordfile>" does not work with gfix
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()

act = python_act('db')

passfile = temp_file('tmp_gh_6817.dat')

#@pytest.mark.skip('FIXME: Not IMPLEMENTED')
@pytest.mark.version('>=3.0.8')
def test_1(act: Action, passfile: Path):
    passfile.write_text(act.db.password)
    act.gfix(switches=['-user', act.db.user, '-fetch_password', str(passfile), act.db.dsn, '-w', 'async'],
             credentials=False)
    act.gfix(switches=['-fetch_password', str(passfile), act.db.dsn, '-user', act.db.user, '-w', 'async'],
             credentials=False)
    act.gfix(switches=['-user', act.db.user, act.db.dsn, '-fetch_password', str(passfile), '-w', 'async'],
             credentials=False)
    act.gfix(switches=[act.db.dsn, '-fetch_password', str(passfile), '-user', act.db.user, '-w', 'async'],
             credentials=False)
