#coding:utf-8

"""
ID:          issue-8115
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8115
TITLE:       Avoid reading/hashing the inner stream(s) if the leader stream is empty
DESCRIPTION:
    Original title: "FB 5.0.0.1306 - unexpected results using LEFT JOIN with When "
NOTES:
    [16.09.2024] pzotov
    Confirmed bug in 5.0.1.1369-8c31082 (17.03.2024)
    Bug was fixed in 5.0.1.1369-bbd35ab (20.03.2024)
    Commit:
        https://github.com/FirebirdSQL/firebird/commit/bbd35ab07c129e9735f081fcd29172a8187aa8ab
        Avoid reading/hashing the inner stream(s) if the leader stream is empty

    [18.01.2025] pzotov
    Resultset of cursor that executes using instance of selectable PreparedStatement must be stored
    in some variable in order to have ability close it EXPLICITLY (before PS will be freed).
    Otherwise access violation raises during Python GC and pytest hangs at final point (does not return control to OS).
    This occurs at least for: Python 3.11.2 / pytest: 7.4.4 / firebird.driver: 1.10.6 / Firebird.Qa: 0.19.3
    The reason of that was explained by Vlad, 26.10.24 17:42 ("oddities when use instances of selective statements").
    
    Checked on 6.0.0.457, 5.0.2.1499
"""
import zipfile
from pathlib import Path
import locale
import re

from firebird.driver import DatabaseError
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('INDEX_\\d+', 'INDEX_nn'),] 

act = python_act('db', substitutions = substitutions)
tmp_fbk = temp_file('gh_8115.tmp.fbk')

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.1')
def test_1(act: Action, tmp_fbk: Path, capsys):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'gh_8115.zip', at = 'gh_8115.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())

    act.gbak(switches = ['-rep', str(tmp_fbk), act.db.db_path], combine_output = True, io_enc = locale.getpreferredencoding())
    print(act.stdout) # must be empty

    test_sql = """
        select aa.id, ab.CNP_USER, ab.ID_USER
        from sal_inperioada2('7DC51501-0DF2-45BE-93E5-382A541505DE', '15.05.2024') aa
        left join user_cnp(aa.cnp, '15.05.2024') ab on ab.CNP_USER = aa.cnp
        where ab.ID_USER = '04B23787-2C7F-451A-A12C-309F79D6F13A'
    """

    with act.db.connect() as con:
        cur = con.cursor()
        ps, rs = None, None
        try:
            ps = cur.prepare(test_sql)
            print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

            # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
            # We have to store result of cur.execute(<psInstance>) in order to
            # close it explicitly.
            # Otherwise AV can occur during Python garbage collection and this
            # causes pytest to hang on its final point.
            # Explained by hvlad, email 26.10.24 17:42
            rs = cur.execute(ps)
            for r in rs:
                for p in r:
                    print(p)
        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)
        finally:
            if rs:
                rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
            if ps:
                ps.free()

    expected_stdout_5x = """
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Procedure "SAL_INPERIOADA2" as "AA" Scan
        ........-> Filter
        ............-> Filter
        ................-> Procedure "USER_CNP" as "AB" Scan

        000DD4E1-B4D0-4D6E-9D9F-DE9A7D0D6492
        E574F734-CECB-4A8F-B9BE-FAF51BC61FAD
        04B23787-2C7F-451A-A12C-309F79D6F13A
    """

    expected_stdout_6x = """
        Select Expression
        ....-> Filter
        ........-> Nested Loop Join (inner)
        ............-> Procedure "SAL_INPERIOADA2" as "AA" Scan
        ............-> Filter
        ................-> Procedure "USER_CNP" as "AB" Scan
        000DD4E1-B4D0-4D6E-9D9F-DE9A7D0D6492
        E574F734-CECB-4A8F-B9BE-FAF51BC61FAD
        04B23787-2C7F-451A-A12C-309F79D6F13A
    """
    
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
