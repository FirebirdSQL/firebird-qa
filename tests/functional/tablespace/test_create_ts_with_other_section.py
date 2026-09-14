# coding:utf-8

"""
ID:          test_read_ts_with_other_section
FBTEST:      
TITLE:       Test for separating directories.conf with false section.
DESCRIPTION: Creates a file with alias, which doesn`t defined in true section.
"""

import pytest
from firebird.qa import *
from pathlib import Path

substitutions = [('.*test_dir/ts1.dat', 'test_dir/ts1.dat'), ('=+ =+', '======'), 
                 ('.*test_dir\\\\ts1.dat', 'test_dir/ts1.dat'), 
                 ('-The system cannot find the path specified.', '-No such file or directory')]

db = db_factory()
act = python_act('db', substitutions=substitutions)

new_config = temp_file('new_directories.conf')

expected_stdout = ""

expected_stderr = """
Statement failed, SQLSTATE = 08001
unsuccessful metadata update
-CREATE TABLESPACE TS1 failed
test_dir/ts1.dat"
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
        blobs
        {{
            {alias} = {alias_path}
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
