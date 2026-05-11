#coding:utf-8

"""
ID:          issue-7269
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7269
TITLE:       Database restore must make every effort on activating deferred indexes
DESCRIPTION:
    Test uses unrecoverable .fbk that was provided in the ticket and tries to restore it using '-verbose' option.
    After restore finish, we check its log. It must contain SEVERAL errors related to indices (PK and two FK),
    and also it must have messages about FINAL point of restore (regardless error that follows after this):
        gbak:finishing, closing, and going home
        gbak:adjusting the ONLINE and FORCED WRITES flags
NOTES:
    [02.11.2024] pzotov
        Checked on 5.0.2.1551, 6.0.0.415.
    [11.05.2026] pzotov
        Refactored: *every* line that contain info about PK/FK error must present in the restore log.
        But the *order* of their appearance if UNDEFINED (letter from Vlad, letter 11.05.26 1148).
        We have accumulate such lines in the set and then print it as ordered list.
        Checked on 6.0.0.1910; 5.0.5.1819.
"""
import subprocess
from pathlib import Path
import zipfile
import locale
import re
import string

import pytest
from firebird.qa import *
from firebird.driver import SrvRestoreFlag

db = db_factory()
act = python_act('db')
tmp_fbk = temp_file('gh_7269.tmp.fbk')
tmp_fdb = temp_file('gh_7269.tmp.fdb')

@pytest.mark.version('>=5.0.2')
def test_1(act: Action, tmp_fbk: Path, tmp_fdb: Path, capsys):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'gh_7269.zip', at = 'gh-7269-unrecoverable.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())

    act.gbak(switches = ['-rep', '-v', str(tmp_fbk), str(tmp_fdb)], combine_output = True, io_enc = locale.getpreferredencoding())

    violation_patterns = \
    (
         'violation of ((PRIMARY or UNIQUE)|FOREIGN) KEY constraint'
        ,'Cannot create foreign key constraint'
    )
    violation_patterns = [ re.compile(p, re.IGNORECASE) for p in violation_patterns ]

    # From entire restore log we are interesting only for following lines:
    # ===================
    #    gbak: ERROR:violation of PRIMARY or UNIQUE KEY constraint "PK_A3" on table "A3"
    #    gbak: ERROR:violation of PRIMARY or UNIQUE KEY constraint "PK_A1" on table "A1"
    #    gbak: ERROR:Cannot create foreign key constraint FK_A1. Partner index does not exist or is inactive.
    #    gbak: ERROR:violation of FOREIGN KEY constraint "FK_A2" on table "B2"
    #    gbak: ERROR:Cannot create foreign key constraint FK_A3. Partner index does not exist or is inactive.
    # ===================
    # All of them must present in the restore log, but the order of their appearance if UNDEFINED.
    # We accumulate such lines in the set and then print it as ordered list:
    #
    problematic_constraints_set = set()
    for line in act.stdout.splitlines():
        for p in violation_patterns:
            if (x := p.search(line)):
                x = line[ x.span()[1]+1 : ].replace('"PUBLIC"', '') # remove schema name (6.x), it is irrelevant here.
                # remove all punkt signs (double quotes, dots etc):
                problematic_constraints_set.add( x.translate(str.maketrans('', '', string.punctuation)) )
                break
                
    for p in sorted(problematic_constraints_set):
        print(p)

    act.expected_stdout = """
        FKA1 Partner index does not exist or is inactive
        FKA2 on table B2
        FKA3 Partner index does not exist or is inactive
        PKA1 on table A1
        PKA3 on table A3
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
