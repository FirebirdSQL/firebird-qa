#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/2710
TITLE:       Records left in RDB$PAGES after rollback of CREATE TABLE statement
DESCRIPTION:
JIRA:        CORE-2284
NOTES:
    [05.03.2026] pzotov
    See also: https://github.com/FirebirdSQL/firebird/issues/5943 (CORE-5677)
    Adjusted expected output which has changed since #b38046e1 ('Encapsulation of metadata cache'; 24-feb-2026 17:31:04 +0000).
    Checked on 6.0.0.1807-46797ab.

    [06.06.2026] pzotov
    1. Fully re-implemented.
       Bug existed up to 3.0.3.32852-e3ab348 and has been fixed in 3.0.3.32852-caa21df, 11-dec-2017 05:40:52 +0000
       ("Fixed CORE-5677: RDB$PAGES is dirty after error after phase 3 of create_relation (#135)").
       This is script that illustrates bug on 3.x snapshots before fix:
       ===============================
           alter database set linger to 0;
           commit;
           set autoddl off;
           select count(*) as RDB_PAGES_INIT_COUNT from rdb$pages;
           recreate table test (
               str_pk varchar(32) character set UTF8
               ,str_fk varchar(32) character set WIN1251
               ,constraint test_pk primary key (str_pk)
               ,constraint test_fk foreign key (str_fk) references test(str_pk)
           );
           commit; -- on 3.x .... 5.x this causes "42000/-partner index ... incompatible data type"
           -- NOT NEEDED: rollback;
           select count(*) as RDB_PAGES_CURR_COUNT from rdb$pages;
       ===============================
       (values RDB_PAGES_INIT_COUNT and RDB_PAGES_CURR_COUNT will differ; must be equal since fix)

    2. The comparison of records number in RDB$PAGES with RDB$DATABASE.RDB$RELATION_ID could be done only in 3.x ... 5.x.
       On 6.x this is incorrect because RDB$DATABASE.RDB$RELATION_ID no more increased when we run 'CREATE TABLE'.
       (the generator is used instead of this, see commit bb280120 / 6.0.0.1959; 2026.05.21 05:41:14).
    Checked on 6.0.0.1996; 5.0.5.1826; 4.0.0.2109; 3.0.14.33855
"""
from firebird.driver import DatabaseError
import pytest
from firebird.qa import *

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=3.0.3')
def test_1(act: Action, capsys):

    test_sql = """
        recreate table test (
            str_pk varchar(32) character set UTF8
            ,str_fk varchar(32) character set WIN1251
            ,constraint test_pk primary key (str_pk)
            ,constraint test_fk foreign key (str_fk) references test(str_pk)
        )
    """
    rdb_pages_init_cnt = rdb_pages_curr_cnt = -1
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute('select count(*) from rdb$pages')
        rdb_pages_init_cnt = cur.fetchall()[0][0]
        assert rdb_pages_init_cnt > 0

        try:
            con.execute_immediate(test_sql)
            con.commit()
        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)

        cur.execute('select count(*) from rdb$pages')
        rdb_pages_curr_cnt = cur.fetchall()[0][0]
        assert rdb_pages_curr_cnt > 0

    msg_prefix = 'Number of rows in RDB$PAGES before and after failed DDL'
    EXPECTED_MSG = f'{msg_prefix} remains equal.'
    if not rdb_pages_init_cnt == rdb_pages_curr_cnt:
        print('### ACHTUNG ###')
        print(f'{msg_prefix} DIFFERS.')
        print(f'{rdb_pages_init_cnt=}')
        print(f'{rdb_pages_curr_cnt=}')
    else:
        print(EXPECTED_MSG)

    expected_stdout_5x = f"""
        unsuccessful metadata update
        -partner index segment no 1 has incompatible data type
        (335544351, 335544852)
        {EXPECTED_MSG}
    """

    expected_stdout_6x = f"""
        unsuccessful metadata update
        -RECREATE TABLE "PUBLIC"."TEST" failed
        -partner index segment no 1 has incompatible data type
        (335544351, 336397289, 335544852)
        {EXPECTED_MSG}
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
