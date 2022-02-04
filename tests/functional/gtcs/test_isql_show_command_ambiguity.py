#coding:utf-8

"""
ID:          gtcs.isql-show-command-ambiguity
TITLE:       SHOW TABLE / VIEW: ambiguity between tables and views
DESCRIPTION:
  ::: NB :::
  ### Name of original test has no any relation with actual task of this test: ###
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_22.script

  bug #223513 ambiguity between tables and views
FBTEST:      functional.gtcs.isql_show_command_ambiguity
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create table t(a int);
    create view v as select a from t;
    show tables;
    show views;
    show table v;
    show table t;
    show view v;
    show view t;
"""

act = isql_act('db', test_script, substitutions=[('=', ''), ('[ \t]+', ' ')])

expected_stdout = """
    T
    V
    A INTEGER Nullable
    A INTEGER Nullable

    View Source:
    select a from t
"""

expected_stderr = """
    There is no table V in this database
    There is no view T in this database
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
