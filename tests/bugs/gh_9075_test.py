#coding:utf-8

"""
ID:          issue-9075
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9075
TITLE:       Improve gbak logging of ignored records with skip/include (schema) data by mentioning the table name
DESCRIPTION:
    Test creates several schemas (besides PUBLIC) and two tables in each of them.
    Then we do backup and run restore two times with '-SKIP_DATA' and '-SKIP_SCHEMA_DATA' command switches.
    First time we require to skip data of TABLE with name 'T_OPTIONAL', second time - all objects from schema 'S_OPTIONAL'.
    Logs of each restore must contain lines like:
        gbak:skipping data for table ...
        gbak: <NNNN> records ignored
    (we obtain them using 're.findall(<pattern>, flags=re.MULTILINE)').
NOTES:
    [09.07.2026] pzotov
    Currently only log of *restore* contains info about names of skipped DB objects. This is not so for BACKUP log.
    See https://github.com/FirebirdSQL/firebird/issues/9075#issuecomment-4926599975
    Test probably will be changed later.
    Confirmed improvement on 6.0.0.2070-d2cb23c.
"""

import os
import re
import locale
from pathlib import Path
import time

import pytest
from firebird.qa import *

substitutions = [('[ \t]+', ' '), ]

NUM_ROWS = 10000
init_script = f"""
    create table t_required(id int);
    create table t_optional(id int);

    create schema s_required;
    create schema s_optional;

    create table s_required.t_required(id int);
    create table s_required.t_optional(id int);

    create table s_optional.t_required(id int);
    create table s_optional.t_optional(id int);
    commit;

    insert into t_required(id) select i from generate_series(1, {NUM_ROWS}) as s(i);
    insert into t_optional(id) select id from t_required;

    insert into s_required.t_required(id) select id from t_required;
    insert into s_required.t_optional(id) select id from t_required;

    insert into s_optional.t_required(id) select id from t_required;
    insert into s_optional.t_optional(id) select id from t_required;
    commit;
"""

db = db_factory(init = init_script)
act = python_act('db', substitutions=substitutions)

tmp_fdb = temp_file('tmp_gh_9075.fdb')
tmp_fbk = temp_file('tmp_gh_9075.fbk')
tmp_log = temp_file('tmp_gh_9075.log')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fdb: Path, tmp_fbk: Path, tmp_log: Path, capsys):

    act.gbak(switches=['-b', act.db.dsn, str(tmp_fbk)])

    skip_map = { 
        '-skip_data'        : 't_optional'.upper(),
        '-skip_schema_data' : 's_optional'.upper(),
    }

    for k,v in skip_map.items():
        act.gbak(switches=['-rep', str(tmp_fbk), str(tmp_fdb), '-verbose', k, v ], combine_output = True, io_enc = locale.getpreferredencoding())
        matches = re.findall(r"^gbak:skipping data for table \S+\s*\ngbak:\s+\d+ records? ignored", act.clean_stdout, flags=re.MULTILINE)
        for p in matches:
            print(p)
        act.reset()

    act.expected_stdout = f"""
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored

        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        gbak: {NUM_ROWS} records ignored
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
