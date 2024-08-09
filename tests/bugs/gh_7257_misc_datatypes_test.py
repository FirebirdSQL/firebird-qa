#coding:utf-8

"""
ID:          issue-7257
ISSUE:       7257
TITLE:       Support for partial indices
DESCRIPTION:
    Additional test to check misc datatypes in partial indices.
NOTES:
    Checked on 6.0.0.409, 5.0.1.1469
"""

import pytest
from firebird.qa import *
from decimal import Decimal

db = db_factory()
act = python_act('db', substitutions = [('[ \t]+', ' '), ])

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

def run_ddl_dml(act, capsys, dtype, v_chk, v_max, use_rand = True):

    with act.db.connect() as con:
        cur = con.cursor()
        idx_partial_name = f'test_f01_{dtype.split()[0]}_partial'.upper()
        idx_common_name = f'test_f02_{dtype.split()[0]}_common'.upper()
        if dtype =='date':
            v_chk = 'current_date'
            insert_sttm = f"insert into test(id, f01) select row_number()over(), iif(mod(row_number()over(), 100) = 0, {v_chk}, dateadd(rand()*1000 day to date '01.01.2000')) from rdb$types,rdb$types rows 1000"
        elif dtype == 'time with time zone':
            v_chk = "time '11:11:11.111 Indian/Cocos'"
            insert_sttm = f"insert into test(id, f01) select row_number()over(), iif(mod(row_number()over(), 100) = 0, {v_chk}, time '11:11:11.111 Pacific/Fiji' ) from rdb$types,rdb$types rows 1000"
        elif dtype == 'varchar(80) character set utf8':
            idx_partial_name = f'test_f01_utf8_partial'.upper()
            idx_common_name = f'test_f02_utf8_common'.upper()
            v_chk = "'Sporvognsskinneskidtskraberkonduktørbuksebæltespændeemblempoleringsmiddelshylde€'"
            v_max = "'Minoritetsladningsbærerdiffusjonskoeffisientmålingsapparatur'"
            insert_sttm = f"insert into test(id, f01) select row_number()over(),iif(mod(row_number()over(), 100) = 0, {v_chk}, {v_max}) from rdb$types,rdb$types rows 1000"
        elif dtype == 'varbinary(16)':
            idx_partial_name = f'test_f01_vbin_partial'.upper()
            idx_common_name = f'test_f02_vbin_common'.upper()
            v_chk = "x'0A'"
            v_max = "gen_uuid()"
            insert_sttm = f"insert into test(id, f01) select row_number()over(),iif(mod(row_number()over(), 100) = 0, {v_chk}, {v_max}) from rdb$types,rdb$types rows 1000"
        elif dtype == 'boolean':
            v_chk = "false"
            v_max = "true"
            insert_sttm = f"insert into test(id, f01) select row_number()over(),iif(mod(row_number()over(), 100) = 0, {v_chk}, {v_max}) from rdb$types,rdb$types rows 1000"
        else:
            insert_sttm = f"insert into test(id, f01) select row_number()over(), iif(mod(row_number()over(), 100) = 0, cast({v_chk} as {dtype}), cast(rand()*{v_max} as {dtype})) from rdb$types,rdb$types rows 1000"
        ddl = f"""
            recreate table test(id int primary key, f01 {dtype}, f02 {dtype}) ^
            {insert_sttm} ^
            update test set f02 = f01 ^
            create index {idx_partial_name} on test computed by (f01) where f01 = {v_chk} ^
            create index {idx_common_name} on test(f02) ^
            set statistics index {idx_partial_name} ^
            set statistics index {idx_common_name} ^
        """

        dml = f"""
            select count(*) from test where f01 = {v_chk} ^
            select count(*) from test where f02 = {v_chk} ^
        """

        for x in [p for p in ddl.split('^') if p.strip()]:
            if x.startswith('--'):
                pass
            else:
                con.execute_immediate(x)
                con.commit()

        for x in [p for p in dml.split('^') if p.strip()]:
            ps = cur.prepare(x)
            for s in ps.detailed_plan.split('\n'):
                print( replace_leading(s) )

            cur.execute(ps)
            cur_cols = cur.description
            for r in cur:
                for i in range(0,len(cur_cols)):
                    print( cur_cols[i][0], ':', r[i] )
            con.commit()

        act.expected_stdout = f"""
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "{idx_partial_name}" Full Scan
            COUNT : 10
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "{idx_common_name}" Range Scan (full match)
            COUNT : 10
        """
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()

#-----------------------------------------------------------

@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):
    
    run_ddl_dml(act, capsys, 'smallint', -32768, 32767, True)
    run_ddl_dml(act, capsys, 'bigint', -9223372036854775808, 9223372036854775807, True)
    run_ddl_dml(act, capsys, 'double precision', -2.2250738585072014e-308, 1.7976931348623158e+308, True)
    run_ddl_dml(act, capsys, 'int128', Decimal(-170141183460469231731687303715884105728), Decimal(170141183460469231731687303715884105727), True)
    run_ddl_dml(act, capsys, 'decfloat', 0, Decimal(1.7976931348623158e+308), True)
    run_ddl_dml(act, capsys, 'date', None, None)
    run_ddl_dml(act, capsys, 'time with time zone', None, None)
    run_ddl_dml(act, capsys, 'varchar(80) character set utf8', None, None)
    run_ddl_dml(act, capsys, 'varbinary(16)', None, None)
    run_ddl_dml(act, capsys, 'boolean', None, None)
