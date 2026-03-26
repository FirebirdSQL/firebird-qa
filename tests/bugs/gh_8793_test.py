#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8793
TITLE:       Fix gbak output some errors and warnings to stderr instead of stdout
DESCRIPTION:
NOTES:
    [26.03.2026] pzotov
    ::: NOTE :::
    Problem detected when make restore using FBSVCMGR: lost part of message that was in STDOUT before this fix.
    (see https://github.com/FirebirdSQL/firebird/pull/8793#issuecomment-4129482729).
    Currently test verifies only GBAK. Additional check (FBSVCMGR) will be added after fix.

    Confirmed problem on 6.0.0.1835
    Checked on 6.0.0.1843.
"""
import locale
import re
from pathlib import Path
import subprocess
import time
import pytest
from firebird.qa import *


init_script = """
    create table test(id int);
    insert into test select row_number()over() from rdb$types rows 10;
    commit;
    set term ^; execute block as begin rdb$set_context('USER_SESSION', 'TMP', 1); end ^ set term ;^
    create unique index test_x_unq on test computed by ( coalesce(cast(rdb$get_context('USER_SESSION', 'TMP') as int), 0) * id );
    commit;
"""
db = db_factory(init = init_script)

tmp_fbk = temp_file('gh_8793_tmp.fbk')
tmp_res = temp_file('gh_8793_tmp.res')
tmp_log = temp_file('gh_8793_tmp.log')
tmp_err = temp_file('gh_8793_tmp.err')


def strip_white(value):
    value = re.sub('(?m)^\\s+', '', value)
    return re.sub('(?m)\\s+$', '', value)

act = python_act('db')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fbk: Path, tmp_res: Path, tmp_log: Path, tmp_err: Path, capsys):

    act.gbak(switches=['-b', act.db.dsn, str(tmp_fbk)])
    act.reset()

    act.expected_stderr = 'MUST BE SOME NON-EMPTY TEXT! SEE QA-PLUGIN SOURCE!'
    act.gbak(switches=['-rep', str(tmp_fbk), 'localhost:' + str(tmp_res)])

    for line in act.clean_stdout.splitlines():
        if (s := line.strip()):
            print('gbak STDOUT:' + s)

    for line in act.clean_stderr.splitlines():
        if (s := line.strip()):
            print('gbak STDERR:' + s)

    expected_out = """
        gbak STDERR:gbak:cannot commit index "PUBLIC"."TEST_X_UNQ"
        gbak STDERR:gbak: ERROR:attempt to store duplicate value (visible to active transactions) in unique index "PUBLIC"."TEST_X_UNQ"
        gbak STDERR:gbak: ERROR:    Problematic key value is (<expression> = 0)
        gbak STDERR:gbak: ERROR:Database is not online due to failure to activate one or more indices.
        gbak STDERR:gbak: ERROR:    Run gfix -online to bring database online without active indices.
    """
    
    assert strip_white(expected_out) == strip_white(capsys.readouterr().out)
