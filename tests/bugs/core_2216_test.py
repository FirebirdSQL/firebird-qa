#coding:utf-8

"""
ID:          issue-2644
ISSUE:       2644
TITLE:       Nbackup as online dump
DESCRIPTION:
  We create table and leave it empty, than we run "nbackup -b 0 <source_db> <nbk_level_0>".
  After this add one row in the table in source DB.
  Then we obtain database GUID of sourec DB and use it in following commands:
    1. nbackup -b <GUID> <source_db> <addi_file>
    2. nbackup -i -r <nbk_level_0> <addi_file>
  Finally, we:
    1. Check that inserted record actually does exist in <nbk_level_0>;
    2. Run online validation of <nbk_level_0> - it sould NOT produce any errors.
JIRA:        CORE-2216
"""

import pytest
from pathlib import Path
from firebird.qa import *
from firebird.driver import SrvNBackupFlag

substitutions = [('BLOB_ID.*', ''),
                   ('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]', ''),
                   ('Relation [0-9]{3,4}', 'Relation')]

init_script = """
create table test(id int, s varchar(10) unique using index test_s, t timestamp, b blob);
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=substitutions)

nbak_file_base = temp_file('nbak-file.fdb')
nbak_file_add = temp_file('nbak-file.add')

expected_stdout_a = """
    ID                              1
    S                               qwerty
    T                               2013-12-11 14:15:16.1780
    foo-rio-bar
    Records affected: 1
"""

expected_stdout_b = """
    Validation started
    Relation (TEST)
    process pointer page    0 of    1
    Index 1 (TEST_S)
    Relation (TEST) is ok
    Validation finished
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, nbak_file_base: Path, nbak_file_add: Path):
    with act.connect_server() as srv, act.db.connect() as con:
        # Backup base database
        srv.database.nbackup(database=act.db.db_path, backup=nbak_file_base,
                             level=0)
        c = con.cursor()
        # get db GUID
        c.execute('select rb.rdb$guid as db_guid from rdb$backup_history rb')
        db_guid = c.fetchone()[0]
        # Insert data
        c.execute("insert into test(id,s,t,b) values(1, 'qwerty', '11.12.2013 14:15:16.178', 'foo-rio-bar')")
        con.commit()
        # Backup changes
        srv.database.nbackup(database=act.db.db_path, backup=nbak_file_add,
                             guid=db_guid)
        # Restore inplace
        srv.database.nrestore(flags=SrvNBackupFlag.IN_PLACE, database=nbak_file_base,
                              backups=[str(nbak_file_add)])
        # Check restored database
        act.expected_stdout = expected_stdout_a
        act.isql(switches=[str(nbak_file_base)],
                   connect_db=False,
                   input="set list on;set count on;set blob all;select id,s,t,b as blob_id from test;")
        assert act.clean_stdout == act.clean_expected_stdout
        # Validate restored database
        srv.database.validate(database=nbak_file_base)
        act.reset()
        act.expected_stdout = expected_stdout_b
        act.stdout = '\n'.join(srv.readlines())
        assert act.clean_stdout == act.clean_expected_stdout
