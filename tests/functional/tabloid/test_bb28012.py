#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/bb280120e9a181bafa900dba3f331324167a6167
TITLE:       Use generator instead field in rdb$database to generate relation ID
DESCRIPTION:
    Bug was found during attempts to re-implement test for CORE-6336: 'ALTER DATABASE <some_sttm>' prevented
    further execution of CREATE TABLE with issuing SQLSTATE = 40001 / ... -update conflicts ... / -concurrent ...
    (see letter to FB team 11.05.2026 0309).
    Test use pre-defined alias in databases.conf for which set set small value of DeadLockTimeot (much less than default 10).
    An attempt to create table after 'alter databse' must be complted instantly without any error.
    We check this for each isolation level (but with lock_timeout = 0).
NOTES:
    Bug exists up to snapshot 6.0.0.1959-a5ec02b.
    Checked on 6.0.0.1959-bb28012 - all OK.
"""
import re
from pathlib import Path
from firebird.driver import tpb, Isolation, DatabaseError

import pytest
from firebird.qa import *

# Name of alias for self-security DB in the QA_root/files/qa-databases.conf.
# This file must be copied manually to each testing FB homw folder, with replacing
# databases.conf there:
#
REQUIRED_ALIAS = 'tmp_bb28012_alias'

db = db_factory(filename = '#' + REQUIRED_ALIAS)
act = python_act('db', substitutions=[('[ \t]+', ' '), ] )

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder. This name will be used further as target database (tmp_fdb).
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            #print(line, p_required_alias_ptn.search(line))
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_7598_alias = $(dir_sampleDb)/qa/tmp_gh_7598.fdb
                # - then we extract filename: 'tmp_gh_7598.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break
    assert fname_in_dbconf

    tx_isol_lst = [ Isolation.READ_COMMITTED_NO_RECORD_VERSION,
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                    Isolation.SERIALIZABLE,
                  ]

    for x_isol in tx_isol_lst:
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)
        with act.db.connect() as con:
            try:
                tx = con.transaction_manager(custom_tpb)
                tx.begin()
                cur = tx.cursor()
                cur.execute('alter database set linger to 1234')
                cur.execute('recreate table t_test(id int)')
                tx.commit()
                print(x_isol.name,'-  passed')
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)

        act.expected_stdout = f'{x_isol.name} - passed'
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
