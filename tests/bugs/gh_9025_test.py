#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9025
TITLE:       UDF compact div overflow
DESCRIPTION:
NOTES:
    [09.06.2026] pzotov
    Confirmed crash on 6.0.0.1963-f41a8da.
    Checked on 6.0.0.1965-f9a8d1a.
"""
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

init_script = """
    -- See declaration examples in plugins\\udr\\UdfBackwardCompatibility.sql:
    create function UDR40_div (
        n1 integer,
        n2 integer
    ) returns double precision
    external name 'udf_compat!UC_div'
    engine udr;
    commit;
"""

db = db_factory(init = init_script)
act = python_act('db')

@pytest.mark.version('>=6.0')
def test(act: Action, capsys):
    with  act.db.connect() as con:
        cur = con.cursor()
        try:
            cur.execute("select 'OK' from rdb$database where UDR40_div(?, ?) is not null", (-2147483648, -1))
            for r in cur:
                print(r[0])
        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)

    act.expected_stdout = 'OK'
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
