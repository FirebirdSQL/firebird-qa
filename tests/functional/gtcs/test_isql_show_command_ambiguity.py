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
    create view "t" as select a from t;

    create table "v"(a int);
    create view v as select a from "v";

    set echo on;
    show tables;
    show views;

    show table v;
    show table "v";

    show table t;
    show table "t";

    show view v;
    show view "v";
"""

act = isql_act('db', test_script, substitutions=[('=', ''), ('[ \t]+', ' ')])

@pytest.mark.version('>=3')
def test_1(act: Action):

    expected_stdout_5x = f"""
        show tables;
        T
        v
        show views;
        V
        t
        show table v;
        There is no table V in this database
        show table "v";
        A INTEGER Nullable
        show table t;
        A INTEGER Nullable
        show table "t";
        There is no table t in this database
        show view v;
        A INTEGER Nullable
        View Source:
        select a from "v"
        show view "v";
        There is no view v in this database

    """

    expected_stdout_6x = f"""
        show tables;
        PUBLIC.T
        PUBLIC."v"
        show views;
        PUBLIC.V
        PUBLIC."t"
        show table v;
        There is no table V in this database
        show table "v";
        Table: PUBLIC."v"
        A INTEGER Nullable
        show table t;
        Table: PUBLIC.T
        A INTEGER Nullable
        show table "t";
        There is no table "t" in this database
        show view v;
        View: PUBLIC.V
        A INTEGER Nullable
        View Source:
        select a from "v"
        show view "v";
        There is no view "v" in this database
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
