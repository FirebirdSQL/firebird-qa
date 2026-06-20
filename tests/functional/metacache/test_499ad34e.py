#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/499ad34e9b69b98128ec3687a2f3ed88914e5903
TITLE:       Shared metacache. Fixed rebuild of expression & conditional indices when field used in expression/condition changed
DESCRIPTION:
NOTES:
    [19.06.2026] pzotov
    Bug has been found occasinally during investigating consequences of #3fadfabe ("#9001: Restart value of Identity field failed").
    Discussed with Alex, letters since 15.06.2026 0223 (FB hanged after issuing 'Finish' message).
    This test verifies THREE types of tables: permanent and both GTTs.
    ::: NB :::
    For 'GTT on commit DELETE rows' problem has been fixed in 6.0.0.2022-3bca222.
    (see report to Alex, 19.06.2026 0308).
    Checked on 6.0.0.2018-fdd011c; 6.0.0.2022-3bca222.
"""

import time
import subprocess
from pathlib import Path

import pytest
from firebird.qa import *
#from firebird.driver import tpb, Isolation, DatabaseError, FirebirdWarning

db = db_factory()
act = python_act('db')

tmp_sql = temp_file('tmp_499ad34e.sql')
tmp_log = temp_file('tmp_499ad34e.log')

@pytest.mark.version('>=6')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    # K = relation type; V = (rel_type, rel_name, optional_ddl_suffix):
    tab_ddl_map = {
        'permanent' : (0, '',                 't_permanent'.upper(), '')
       ,'gtt_sessn' : (4, 'global temporary', 't_gtt_preserve'.upper(), 'on commit preserve rows')
       ,'gtt_trans' : (5, 'global temporary', 't_gtt_del_rows'.upper(), 'on commit delete rows')
    }

    for tab_type, tab_opts in tab_ddl_map.items():

        tt_type, tt_pref, tt_name, tt_suff = tab_opts[:4]
        tab_type_ddl = f'recreate {tt_pref} table {tt_name}(f01 smallint) {tt_suff}'

        actual_output = f'{tab_type=} {tt_suff} - start.\n'

        test_sql = f"""
            set bail on;
            set heading off;
            connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}';
            {tab_type_ddl};
            create unique index {tt_name}_f01_unq on {tt_name}(f01);
            create index {tt_name}_f01_expr on {tt_name} computed by(f01 || '');
            create index {tt_name}_f01_cond on {tt_name}(f01) where f01 is not null;
             
            insert into {tt_name}(f01) values(null);
            commit;
             
            alter table {tt_name} alter f01 type varchar(100) character set utf8;
            commit;
             
            set bail OFF; 
            insert into {tt_name}(f01) values('1970 Paranoid');
            select q'#{tab_type=} {tt_suff} - finish.#' as msg from rdb$database;
        """

        tmp_sql.write_text(test_sql)
        with open(tmp_log, 'w') as f_log:
            p = subprocess.run( [ act.vars['isql'],
                                  '-q',
                                  '-i', str(tmp_sql)
                                ], 
                                stdout = f_log, stderr = subprocess.STDOUT,
                                timeout = 5
                              )

        actual_output += tmp_log.read_text()
        expected_out = f"""
            {tab_type=} {tt_suff} - start.
            {tab_type=} {tt_suff} - finish.
        """

        act.expected_stdout = expected_out
        act.stdout = actual_output
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
