#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8914
TITLE:       SELECT with multiple EXISTS sub-queries fails in case of SubQueryConversion = true
DESCRIPTION:
NOTES:
    [24.02.2026] pzotov
    Custom driver config objects are created here.
    For FB 5.x we *change* SubQueryConversion: set it 'true' while default value is 'false'.
    In FB 6.x this parameter no more exists and conversion is performed always, i.e. in effect it is also 'true'.

    Confirmed bug on 5.0.4.1767 (no current record for fetch operation).
    Checked on 5.0.4.1770-aec782c; 6.0.0.1465-3bbe725.
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, DatabaseError

db = db_factory()
act = python_act('db')

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.4')
def test_1(act: Action, capsys):

    test_sql = """
        -- expected: 1 row (ok with subqueryconversion = false)
        -- before fix: error when subqueryconversion = true:
        -- no current record for fetch operation / gdscode = 335544348
        select 1 as x -- a.rdb$index_name
        from rdb$relation_constraints a
        where
            a.rdb$relation_name = 'RDB$FUNCTIONS' and
            a.rdb$constraint_type in ('UNIQUE', 'PRIMARY KEY') and
            exists(select 1
                   from rdb$index_segments b1
                   where b1.rdb$index_name = a.rdb$index_name and
                         b1.rdb$field_name = 'RDB$PACKAGE_NAME') and
            exists(select 1
                   from rdb$index_segments b2
                   where b2.rdb$index_name = a.rdb$index_name and
                         b2.rdb$field_name = 'RDB$FUNCTION_NAME')
        rows 1
        ;
    """

    srv_cfg = driver_config.register_server(name = f'srv_cfg_8914', config = '')
    db_cfg_name = f'db_cfg_8914'
    db_cfg_object = driver_config.register_database(name = db_cfg_name)
    db_cfg_object.server.value = srv_cfg.name
    db_cfg_object.database.value = str(act.db.db_path)
    if act.is_version('<6'):
        db_cfg_object.config.value = f"""
            SubQueryConversion = true
        """

    with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
        try:
            cur = con.cursor()
            cur.execute(test_sql)
            cur_cols = cur.description
            for r in cur:
                for i in range(0,len(cur_cols)):
                    print( cur_cols[i][0], ':', r[i] )
        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)


    expected_stdout = """
        X : 1
    """

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
