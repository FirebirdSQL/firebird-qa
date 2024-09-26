#coding:utf-8

"""
ID:          issue-8252
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8252
TITLE:       Incorrect subquery unnesting with complex dependencies (SubQueryConversion = true)
DESCRIPTION:
NOTES:
    [14.09.2024] pzotov
    1. Parameter 'SubQueryConversion' currently presents only in FB 5.x and _NOT_ in FB 6.x.
       Because of that, testing version are limited only for 5.0.2. FB 6.x currently is NOT tested.
    2. Custom driver config object is created here for using 'SubQueryConversion = true'.
    3. Additional test was made for this issue: tests/functional/tabloid/test_aae2ae32.py

    Confirmed bug on 5.0.2.1497.
    Checked on 5.0.2.1499-5fa4ae6.
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, NetProtocol

db = db_factory()

act = python_act('db', substitutions = [ ('[ \t]+',' ') ])

test_sql = """
    select /* TRACE_ME */ first 5 1 x
    from sales s
    where exists (
        select 1 from customer c
        where
            s.cust_no = c.cust_no
            and ( s.cust_no = c.cust_no
                  or
                  s.cust_no = c.cust_no
                )
    );
"""

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.2,<6')
def test_1(act: Action, capsys):

    srv_cfg = driver_config.register_server(name = 'test_srv_gh_8252', config = '')
    db_cfg_name = f'db_cfg_8252'
    db_cfg_object = driver_config.register_database(name = db_cfg_name)
    db_cfg_object.server.value = srv_cfg.name
    db_cfg_object.database.value = 'employee'
    db_cfg_object.config.value = f"""
        SubQueryConversion = true
    """

    with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
        cur = con.cursor()
        cur.execute("select g.rdb$config_name, g.rdb$config_value from rdb$database r left join rdb$config g on g.rdb$config_name = 'SubQueryConversion'")
        for r in cur:
            print(r[0],r[1])

        ps = cur.prepare(test_sql)
        print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
        for r in cur.execute(ps):
            print(r[0])
        con.rollback()


    act.expected_stdout = """
        SubQueryConversion true
        Sub-query
        ....-> Filter
        ........-> Table "CUSTOMER" as "C" Access By ID
        ............-> Bitmap
        ................-> Index "RDB$PRIMARY22" Unique Scan
        Select Expression
        ....-> First N Records
        ........-> Filter
        ............-> Table "SALES" as "S" Full Scan
        1
        1
        1
        1
        1
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
