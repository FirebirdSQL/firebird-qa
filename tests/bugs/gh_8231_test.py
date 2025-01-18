#coding:utf-8

"""
ID:          issue-8231
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8231
TITLE:       SubQueryConversion = true --request size limit exceeded / Unsuccessful execution caused by an unavailable resource. unable to allocate memory from operating system
DESCRIPTION:
NOTES:
    [26.08.2024] pzotov
    Two tables must be joined by columns which has different charset or collates.
    Confirmed bug on 5.0.2.1484-3cdfd38 (25.08.2024), got:
        Statement failed, SQLSTATE = HY000
        request size limit exceeded
    Checked on 5.0.2.1485-274af35 -- all ok.

    [18.01.2025] pzotov
    Resultset of cursor that executes using instance of selectable PreparedStatement must be stored
    in some variable in order to have ability close it EXPLICITLY (before PS will be freed).
    Otherwise access violation raises during Python GC and pytest hangs at final point (does not return control to OS).
    This occurs at least for: Python 3.11.2 / pytest: 7.4.4 / firebird.driver: 1.10.6 / Firebird.Qa: 0.19.3
    The reason of that was explained by Vlad, 26.10.24 17:42 ("oddities when use instances of selective statements").
    
    Thanks to dimitr for the advice on implementing the test.
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, DatabaseError

init_script = """
    create table t1(fld varchar(10) character set win1252);
    create table t2(fld varchar(10) character set utf8);

    insert into t1(fld) values('Ð');
    insert into t2(fld) values('Ð');
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.2,<6')
def test_1(act: Action, capsys):

    test_sql = """
        select 1 as x
        from t1
        where exists (select 1 from t2 where t1.fld = t2.fld)
    """

    for sq_conv in ('true','false',):
        srv_cfg = driver_config.register_server(name = f'srv_cfg_8231_{sq_conv}', config = '')
        db_cfg_name = f'db_cfg_8231_{sq_conv}'
        db_cfg_object = driver_config.register_database(name = db_cfg_name)
        db_cfg_object.server.value = srv_cfg.name
        db_cfg_object.database.value = str(act.db.db_path)
        db_cfg_object.config.value = f"""
            SubQueryConversion = {sq_conv}
        """

        with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
            cur = con.cursor()
            cur.execute("select g.rdb$config_name, g.rdb$config_value from rdb$database r left join rdb$config g on g.rdb$config_name = 'SubQueryConversion'")
            for r in cur:
                print(r[0],r[1])

            ps, rs = None, None
            try:
                ps = cur.prepare(test_sql)

                # Print explained plan with padding eash line by dots in order to see indentations:
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

                # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
                # We have to store result of cur.execute(<psInstance>) in order to
                # close it explicitly.
                # Otherwise AV can occur during Python garbage collection and this
                # causes pytest to hang on its final point.
                # Explained by hvlad, email 26.10.24 17:42
                rs = cur.execute(ps)
                for r in rs:
                    print(r[0])
            except:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()

            con.rollback()

    act.expected_stdout = f"""
        SubQueryConversion true
        Select Expression
        ....-> Nested Loop Join (semi)
        ........-> Table "T1" Full Scan
        ........-> Filter
        ............-> Table "T2" Full Scan
        1

        SubQueryConversion false
        Sub-query
        ....-> Filter
        ........-> Table "T2" Full Scan
        Select Expression
        ....-> Filter
        ........-> Table "T1" Full Scan
        1
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
