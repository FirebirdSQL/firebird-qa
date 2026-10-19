# coding:utf-8

"""
ID:          test_create_ts_with_empty_section
FBTEST:      
TITLE:       Test for separating directories.conf with empty section.
DESCRIPTION: Creates a file with alias, which doesn't exist.
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [('I/O error during "CreateFile \\(create\\)" operation for file.*', 'I/O error during "open O_CREAT" operation for file'),
                 ('I/O error during "open O_CREAT" operation for file.*', 'I/O error during "open O_CREAT" operation for file'),
                 ('-The system cannot find the path specified.', '-No such file or directory')]

db = db_factory()
act = isql_act('db', substitutions=substitutions)

new_config = temp_file('new_directories.conf')

expected_stdout = ""

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-CREATE TABLESPACE TS1 failed
-I/O error during "open O_CREAT" operation for file
-Error while trying to create file
-No such file or directory
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path, store_config: ConfigManager, new_config: Path):

    alias = 'test_dir'
    alias_dir = "ts_test_dir"
    alias_path = tmpdir / alias_dir
    alias_path.mkdir()

    directories_conf = f"""
    database
    {{
        tablespaces
        {{

        }}
    }}
    """

    new_config.write_text(directories_conf)
    store_config.replace('directories.conf', new_config)

    script = f"""
    create tablespace ts1 file 'test_dir/ts1.dat';
    commit;
    """

    act.expected_stderr = expected_stderr
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=script)

    assert act.clean_stderr == act.clean_expected_stderr
    assert act.clean_stdout == act.clean_expected_stdout
