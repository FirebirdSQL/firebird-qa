# coding:utf-8

"""
ID:          functional.tablespace.test_drop_ts_upd2
TITLE:       DROP TABLESPACE must be prohibited if it contains a table.
DESCRIPTION:
"""

import pytest
from pathlib import Path
from firebird.qa import *

init_ddl = """
    create view v_info as
    select rr.rdb$relation_name as rel_name, rt.rdb$tablespace_name rel_ts
    from rdb$relations rr
    left join rdb$tablespaces rt using (rdb$tablespace_name)
    where rr.rdb$relation_name = upper('test_table');
    commit;
"""
db = db_factory(init=init_ddl)
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions=substitutions)


@pytest.mark.skip("Temporary disabled. To be re-implemented later.")
@pytest.mark.parametrize(
    "commit, autoddl",
    [("commit;", "set autoddl on;"), ("", "set autoddl off;")],
    ids=["autodll_on", "autodll_off"]
)
@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_path: Path, commit: str, autoddl: str):

    ts_file = tmp_path / 'tablespace.dat'

    ts_name = 'ts1'.upper()
    tb_name = 'test_table'.upper()

    test_script = f"""
        set list on;
        set echo on;
        {autoddl}
        set echo off;
        commit;

        create tablespace {ts_name} file '{ts_file}';
        {commit}

        create table {tb_name}(id int);
        {commit}

        insert into {tb_name} values (123);
        {commit}

        alter table {tb_name} set tablespace {ts_name};
        commit; -- do not subst here!

        select v.rel_name as rel_name_ini, v.rel_ts as rel_ts_ini from v_info v;

        drop tablespace {ts_name};
        rollback;

        alter table {tb_name} set tablespace primary;

        drop tablespace {ts_name};
        commit;
        select v.rel_name as rel_name_cur, v.rel_ts as rel_ts_cur from v_info v;
    """

    expected_stdout = f"""
        {autoddl}
        set echo off;

        REL_NAME_INI {tb_name}
        REL_TS_INI {ts_name}

        Statement failed, SQLSTATE = 42000
        unsuccessful metadata update
        -DROP TABLESPACE {ts_name} failed
        -cannot delete
        -TABLESPACE {ts_name}
        -there are 1 dependencies

        REL_NAME_CUR {tb_name}
        REL_TS_CUR PRIMARY
    """

    act.isql(switches=['-q'], input=test_script, combine_output=True)
    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
