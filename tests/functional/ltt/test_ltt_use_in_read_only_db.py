#coding:utf-8

"""
ID:          n/a
TITLE:       LOCAL TEMPORARY TABLE - must be avaliable for usage in read-only database
DESCRIPTION:
NOTES:
    [28.02.2026] pzotov
    See letter from Adriano, 28.02.2026 04:58:20 +0300.
    Confirmed bug (regression) on 6.0.0.1794-f0cac4e: attempt to create LTT fails with
    attempted update on read-only DB / gds=335544765 (no such error on 6.0.0.1465-3bbe725)
"""
import locale
import time
from pathlib import Path

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory(charset = 'utf8')

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    act.gfix(switches=['-mode','read_only', act.db.dsn], combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.return_code == 0 and act.stdout == ''

    try:
        init_ddl = """
            create local temporary table ltt_test (id int not null, s varchar(2000)) on commit preserve rows
            ^
            commit
            ^
            create unique index ltt_test_id on ltt_test(id)
            ^
            commit
            ^
            insert into ltt_test(id, s) select row_number()over(), lpad('', 2000, uuid_to_char(gen_uuid()))
            from rdb$types rows 100
            ^
        """
        check_dml = """
            select
                d.mon$read_only as mon_read_only
               ,sign(t.mon$table_id) as ltt_table_id_sign
               ,(select count(*) from ltt_test where id > 0) as ltt_count
            from mon$database d
            left join mon$local_temporary_tables t on t.mon$table_name = upper('ltt_test')
            ^
        """
        
        with act.db.connect() as con:
            for line in init_ddl.split('^'):
                if (s := line.strip()):
                    if s.lower() == 'commit':
                        con.commit()
                    else:
                        con.execute_immediate(s)
            con.commit()
            #-----------------------------------
            cur = con.cursor()
            for line in check_dml.split('^'):
                if (s := line.strip()):
                    cur.execute(s)
                    for r in cur:
                        for i,col in enumerate(cur.description):
                            print((col[0] +':').ljust(32), r[i])
    except DatabaseError as e:
        print(e.__str__())
        print(e.gds_codes)

    act.expected_stdout = """
        MON_READ_ONLY:                   1
        LTT_TABLE_ID_SIGN:               1
        LTT_COUNT:                       100
    """
   
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
