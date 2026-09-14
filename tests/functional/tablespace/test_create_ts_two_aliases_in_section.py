# coding:utf-8

"""
ID:          functional.tablespace.test_create_ts_two_aliases_in_section
TITLE:       A test that checks which alias is used from the section
DESCRIPTION: 
"""

import pytest
from firebird.qa import *
from pathlib import Path

db = db_factory()
act = isql_act('db')

expected_stdout = """ 
"""

new_config = temp_file('new_directories.conf')


@pytest.mark.version('>=6.0')
def test_1(act: Action, tmpdir: Path, store_config: ConfigManager, new_config: Path):

    alias = 'test_dir'
    alias_dir = "ts_test_dir"
    alias_path = tmpdir / alias_dir
    alias_path.mkdir()

    alias_dir2 = "ts_test_dir2"
    alias_path2 = tmpdir / alias_dir2
    alias_path2.mkdir()

    directories_conf = f"""
    database
    {{
        tablespaces
        {{
            {alias} = {alias_path2}
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

    act.isql(switches=['-q'], input=script, combine_output=True)

    check_script = """
    select RDB$FILE_NAME from RDB$TABLESPACES where RDB$TABLESPACE_NAME='TS1';
    """

    act.reset()
    act.isql(switches=['-q'], input=check_script, combine_output=True)
    act.expected_stdout = expected_stdout

    assert act.clean_stdout == act.clean_expected_stdout
