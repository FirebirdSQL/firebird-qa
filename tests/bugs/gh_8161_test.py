#coding:utf-8

"""
ID:          issue-8161
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8161
TITLE:       Cardinality estimation should use primary record versions only
DESCRIPTION:
    Test must use .fbk file from core-5602. It was copied to separate file and packed into gh_8161.zip
    We check explained plan of query (making 'padding' of every line with '.' character for preserving indentation).
    Statistics is not checked.
    Numeric suffixes of index names from RDB tables are suppressed because they can change in the future.
    Also, we suppress output of rows with 'line NNN, column NNN' (FB 5.x+) because they have no matter in this test.
NOTES:
    [20.06.2024] pzotov
    Despite that we use 'clean' (i.e. just restored) DB, back-versions CAN exists there for system tables,
    particularly (for this .fbk) - in rdb$dependencies and rdb$procedures.
    For that test not only back-versions but also blobs and fragments matter.
    See letters from dimitr and hvlad: 20.06.2024 10:36, 10:39.

    Confirmed bug (regression) on 3.0.12.33735 (date of build: 09-mar-2024).
    Checked on 3.0.12.33764, 4.0.5.3112, 5.0.1.1416, 6.0.0.374.
"""
import zipfile
from pathlib import Path
import locale
import re

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('INDEX_\\d+', 'INDEX_nn'), ('\\(?line \\d+, column \\d+\\)?', '')] 

act = python_act('db', substitutions = substitutions)
tmp_fbk = temp_file('gh_8161.tmp.fbk')

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=3.0.12')
def test_1(act: Action, tmp_fbk: Path, capsys):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'gh_8161.zip', at = 'gh_8161.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())

    act.gbak(switches = ['-rep', str(tmp_fbk), act.db.db_path], combine_output = True, io_enc = locale.getpreferredencoding())
    print(act.stdout) # must be empty

    test_sql = """
        execute block as
            declare relname varchar(32);
            declare cnt int;
        begin
            for select X.RDB$RELATION_NAME
                  from RDB$RELATION_FIELDS X
                 where X.RDB$FIELD_SOURCE = 'BOOL_EMUL'
                into :relname
            do begin
               select count(*)
                 from RDB$DEPENDENCIES DEP, RDB$PROCEDURES PRC
                where DEP.RDB$DEPENDED_ON_NAME = :relname
                  AND DEP.RDB$FIELD_NAME = :relname
                  AND DEP.RDB$DEPENDED_ON_TYPE = 0 /* obj_relation */
                  AND DEP.RDB$DEPENDENT_TYPE = 5 /* obj_procedure */
                  AND DEP.RDB$DEPENDENT_NAME = PRC.RDB$PROCEDURE_NAME
                  AND PRC.RDB$PACKAGE_NAME IS NULL
              into :cnt;
            end
        end
    """

    with act.db.connect() as con:
        cur = con.cursor()
        ps = cur.prepare(test_sql)
        print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

    expected_stdout = """
        Select Expression
        ....-> Singularity Check
        ........-> Aggregate
        ............-> Nested Loop Join (inner)
        ................-> Filter
        ....................-> Table "RDB$DEPENDENCIES" as "DEP" Access By ID
        ........................-> Bitmap
        ............................-> Index "RDB$INDEX_28" Range Scan (full match)
        ................-> Filter
        ....................-> Table "RDB$PROCEDURES" as "PRC" Access By ID
        ........................-> Bitmap
        ............................-> Index "RDB$INDEX_21" Unique Scan
        Select Expression
        ....-> Filter
        ........-> Table "RDB$RELATION_FIELDS" as "X" Access By ID
        ............-> Bitmap
        ................-> Index "RDB$INDEX_3" Range Scan (full match)
    """
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
