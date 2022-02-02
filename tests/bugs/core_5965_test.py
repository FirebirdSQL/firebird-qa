#coding:utf-8

"""
ID:          issue-6219
ISSUE:       6219
TITLE:       FB3 Optimiser chooses less efficient plan than FB2.5 optimiser
DESCRIPTION:
  Filling of database with data from ticket can take noticable time.
  Instead of this it was decided to extract form ZIP archieve .fbk and then to restore it.
  Instead of actual execution we can only obtain PLAN by querying cursor read-only property "plan"
JIRA:        CORE-5965
FBTEST:      bugs.core_5965
"""

import pytest
import zipfile
from pathlib import Path
from firebird.qa import *

db = db_factory()
db_tmp = db_factory(filename='tmp_core_5965.fdb', do_not_create=True)

act = python_act('db')

expected_stdout = """
    PLAN SORT (OPT_TEST INDEX (O_CLID_CUSTTY_CUSTID))
    PLAN SORT (OPT_TEST INDEX (O_CLID_CUSTTY_CUSTID))
"""

fbk_file = temp_file('core_5965.fbk')

@pytest.mark.version('>=3.0')
def test_1(act: Action, fbk_file: Path, db_tmp: Database, capsys):
    zipped_fbk_file = zipfile.Path(act.files_dir / 'core_5965.zip', at='core_5965.fbk')
    fbk_file.write_bytes(zipped_fbk_file.read_bytes())
    #
    with act.connect_server() as srv:
        srv.database.restore(backup=fbk_file, database=db_tmp.db_path)
        srv.wait()
    # Test
    with db_tmp.connect() as con:
        c1 = con.cursor()
        c2 = con.cursor()
        c1.execute("select 1 from opt_test where clid = 23 and cust_type = 1 and cust_id = 73 order by order_no desc")
        print(c1.statement.plan)
        #
        c2.execute("select 2 from opt_test where sysid = 1 and clid = 23 and cust_type = 1 and cust_id = 73 order by order_no desc")
        print(c2.statement.plan)
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
