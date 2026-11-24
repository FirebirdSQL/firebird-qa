#coding:utf-8

"""
ID:          functional.util.test_gbak_restore_meta_dictionary
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9290
TITLE:       Improve metadata lookup during restore: use tree-based dictionary instead of linear search
DESCRIPTION:
    Commit 0627be4a (PR #9290) replaces linear search over linked lists of
    relations / procedures / packages / missed-privilege objects by tree-based
    dictionary (BurpGlobals::metaDictionary, keyed by object type + qualified name).
    Behavior must remain the same: this test is a REGRESSION GUARD that heavily
    exercises the changed code paths and verifies full correctness of restore.

    Scenario:
    * test database contains 256 tables, each with one data row;
    * SELECT is granted to test user on every second table (128 grants);
      other tables stay ungranted for negative check;
    * also created and granted to the same user: view, selectable procedure,
      package with packaged procedure, and sequence (USAGE privilege),
      so that get_relation / get_procedure / get_package / miss-privs dictionary
      lookups are involved during restore of RDB$USER_PRIVILEGES records;
    * backup and restore are made by gbak;
    * verified for the restored database:
        - number of user tables equals to the source (256);
        - number of privileges granted to test user equals to the source (132);
        - data of first / middle / last tables is identical to the source;
        - as the test user: SELECT from granted table and view, EXECUTE of procedure
          and packaged procedure, GEN_ID for sequence - all succeed;
        - as the test user: SELECT from non-granted table fails.
    Test MUST pass both before and after the change (the commit is internal
    optimization without functional difference). Its purpose is to catch possible
    regressions of the restore path when number of objects is significant, so that
    dictionary put/get for every kind of metadata object is checked.
NOTES:
    https://github.com/FirebirdSQL/firebird/commit/0627be4a0420b030a363eeddc4338735b321747f
    "Improve metadata lookup during restore: use tree-based dictionary instead of linear search (#9290)"

    [19.11.2026] pzotov
    Checked on 6.0.0.2496-f0accd6 and 6.0.0.2488-6158583: passed on both.
"""

from pathlib import Path

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory(charset = 'UTF8')
act = python_act('db')

db_res = db_factory(filename = 'gbak_meta_dict_restored.fdb', charset = 'UTF8')
act_res = python_act('db_res')

tmp_fbk = temp_file('gbak_meta_dict.fbk')

tmp_usr = user_factory('db', name = 'tmp_gh_dict_usr', password = '123')

N_TABLES = 256
GRANTED_TABLES = N_TABLES // 2 # select is granted on tables with even numbers only

def build_script(tmp_usr: User) -> str:
    ddl = ['set bail on;', 'set list on;', 'set term ^;']
    for i in range(1, N_TABLES + 1):
        tbl = f"t_d{i:03d}"
        ddl.append(f"create table {tbl}(id int not null primary key, s varchar(60))^")
        ddl.append(f"insert into {tbl} values({i}, 'row_{i}')^")
        if i % 2 == 0:
            ddl.append(f"grant select on table {tbl} to {tmp_usr.name}^")
    ddl.extend(
        [
             "create view v_d_first as select id, s from t_d002^"
            ,f"grant select on v_d_first to {tmp_usr.name}^"
            ,"create sequence g_d_1^"
            ,f"grant usage on sequence g_d_1 to {tmp_usr.name}^"
            ,"create procedure sp_d_1 returns(n int) as begin n = 42; suspend; end^"
            ,f"grant execute on procedure sp_d_1 to {tmp_usr.name}^"
            ,"create package pkg_d_1 as begin procedure pp_d_1 returns(n int); end^"
            ,"create package body pkg_d_1 as begin procedure pp_d_1 returns(n int) as begin n = 7; suspend; end end^"
            ,f"grant execute on package pkg_d_1 to {tmp_usr.name}^"
            ,"set term ;^"
            ,"commit;"
        ]
    )
    return '\n'.join(ddl)

SAMPLE_QUERY = f"""
    select 1 as tag, id, s from t_d001
    union all
    select 2, id, s from t_d{(N_TABLES // 2):03d}
    union all
    select 3, id, s from t_d{N_TABLES:03d}
    order by 1
"""

def count_tables(a: Action) -> int:
    with a.db.connect() as con:
        return con.cursor().execute(
            "select count(*) from rdb$relations r where r.rdb$system_flag = 0 and r.rdb$view_blr is null"
        ).fetchone()[0]

def count_grants(a: Action, user_name: str) -> int:
    with a.db.connect() as con:
        return con.cursor().execute(
            "select count(*) from rdb$user_privileges where rdb$user = ?",
            (user_name.upper(),)
        ).fetchone()[0]

def fetch_sample(a: Action) -> str:
    with a.db.connect() as con:
        rows = con.cursor().execute(SAMPLE_QUERY).fetchall()
        return '; '.join(f"{r[0]}={r[1]}/{r[2]}" for r in rows)

#-----------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, act_res: Action, tmp_usr: User, tmp_fbk: Path, capsys):

    max_par = 0
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute("select g.rdb$config_value from rdb$config g where g.rdb$config_name = 'MaxParallelWorkers'")
        max_par = cur.fetchone()[0]

    act.isql(switches=['-q'], input = build_script(tmp_usr), combine_output = True)
    assert act.return_code == 0, act.stdout
    act.reset()

    src_tables, src_grants, src_sample = count_tables(act), count_grants(act, tmp_usr.name), fetch_sample(act)
    act.reset()

    act.gbak(switches = ['-b', '-par', max_par, '-v', act.db.dsn, str(tmp_fbk)])
    assert act.return_code == 0, act.return_code
    assert act.clean_stderr == '', f"unexpected gbak errors on backup:\n{act.stderr}"
    act.reset()

    act.gbak(switches = ['-rep', '-par', max_par, '-v', str(tmp_fbk), act_res.db.dsn])
    assert act.return_code == 0, act.return_code
    assert act.clean_stderr == '', f"unexpected gbak errors on restore:\n{act.stderr}"
    act.reset()

    res_tables, res_grants, res_sample = count_tables(act_res), count_grants(act_res, tmp_usr.name), fetch_sample(act_res)

    print(f"user tables: src={src_tables}, restored={res_tables}")
    print(f"grants to {tmp_usr.name.upper()}: src={src_grants}, restored={res_grants}")
    print(f"sample data (tag=id/s): src={src_sample}")
    print(f"sample data (tag=id/s): restored={res_sample}")

    with act_res.db.connect(user = tmp_usr.name, password = tmp_usr.password) as con:
        cur = con.cursor()
        # positive checks -- all objects must remain accessible after restore:
        assert cur.execute("select id, s from t_d002 where id = 2").fetchall() == [(2, 'row_2')]
        assert cur.execute("select id, s from v_d_first where id = 2").fetchall() == [(2, 'row_2')]
        assert cur.execute("select n from sp_d_1").fetchall() == [(42,)]
        assert cur.execute("select n from pkg_d_1.pp_d_1").fetchall() == [(7,)]
        gen_id_value = cur.execute("select gen_id(g_d_1, 0) from rdb$database").fetchone()[0]
        print(f"positive checks as granted user: OK, gen_id(g_d_1,0)={gen_id_value}")
        # negative check -- table without any grant to the user must be denied:
        try:
            cur.execute("select id from t_d001").fetchall()
            print("select from non-granted t_d001: ALLOWED (unexpected!)")
        except DatabaseError as e:
            print("select from non-granted t_d001: DENIED as expected")

    act.expected_stdout = f"""
        user tables: src={N_TABLES}, restored={N_TABLES}
        grants to {tmp_usr.name.upper()}: src=132, restored=132
        sample data (tag=id/s): src=1=1/row_1; 2=128/row_128; 3=256/row_256
        sample data (tag=id/s): restored=1=1/row_1; 2=128/row_128; 3=256/row_256
        positive checks as granted user: OK, gen_id(g_d_1,0)=0
        select from non-granted t_d001: DENIED as expected
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act_res.reset()
