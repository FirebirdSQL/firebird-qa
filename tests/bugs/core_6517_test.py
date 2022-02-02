#coding:utf-8

"""
ID:          issue-6746
ISSUE:       6746
TITLE:       Regression: CREATE DATABASE fails with 'Token unknown' error when DB name is
  enclosed in double quotes and 'DEFAULT CHARACTER SET' is specified after DB name
DESCRIPTION:
JIRA:        CORE-6517
FBTEST:      bugs.core_6517
"""

import pytest
from pathlib import Path
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_db = temp_file('tmp_core_6517.fdb')

@pytest.mark.version('>=3.0.8')
def test_1(act: Action, test_db: Path):
    act.isql(switches=[], input=f'create database "{act.get_dsn(test_db)}" default character set utf8;',
               connect_db=False)
