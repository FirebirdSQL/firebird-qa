#coding:utf-8

"""
ID:          issue-8223
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8223
TITLE:       SubQueryConversion = true: error "no current record for fetch operation" with complex joins
DESCRIPTION:
NOTES:
    [27.08.2024] pzotov
    1. Confirmed bug on 5.0.1.1469-1d792e4 (Release (15.08.2024), got for SubQueryConversion=true:
       no current record for fetch operation / gdscode = 335544348.

    2. Parameter 'SubQueryConversion' currently presents only in FB 5.x and _NOT_ in FB 6.x.
       Because of that, testing version are limited only for 5.0.2. FB 6.x currently is NOT tested.
    3. Custom driver config objects are created here, one with SubQueryConversion = true and second with false.
    
    Checked on 5.0.2.1483-0bf2de0 -- all ok.
    Thanks to dimitr for the advice on implementing the test.
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, DatabaseError

init_script = """
    create table t1(id int);
    create table t2(id int);
    create table t3(id int);
    create table t4(id int);
    create table t5(id int);

    insert into t1(id) values(1);
    insert into t2(id) values(1);
    insert into t3(id) values(1);
    insert into t4(id) values(1);
    insert into t5(id) values(1);
    commit;

    create view v as
    select a.id as a_id, b.id as b_id, c.id as c_id
    from t1 a
    left join t2 b on a.id = b.id
    left join t3 c on b.id = c.id;
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
        select v.a_id, v.b_id, v.c_id
        from v 
        join t4 d on v.c_id = d.id
        where exists (
            select 1
            from t5 e where e.id = d.id
        )
    """

    for sq_conv in ('true','false',):
        srv_cfg = driver_config.register_server(name = f'srv_cfg_8223_{sq_conv}', config = '')
        db_cfg_name = f'db_cfg_8223_{sq_conv}'
        db_cfg_object = driver_config.register_database(name = db_cfg_name)
        db_cfg_object.server.value = srv_cfg.name
        db_cfg_object.database.value = str(act.db.db_path)
        db_cfg_object.config.value = f"""
            SubQueryConversion = {sq_conv}
        """

        with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
            try:
                cur = con.cursor()
                cur.execute("select g.rdb$config_name, g.rdb$config_value from rdb$database r left join rdb$config g on g.rdb$config_name = 'SubQueryConversion'")
                for r in cur:
                    print(r[0],r[1])

                ps = cur.prepare(test_sql)

                # Print explained plan with padding eash line by dots in order to see indentations:
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

                # Print data:
                for r in cur.execute(ps):
                    print(r[0], r[1], r[2])
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)

    act.expected_stdout = f"""
        SubQueryConversion true
        Select Expression
        ....-> Filter
        ........-> Hash Join (semi)
        ............-> Filter
        ................-> Hash Join (inner)
        ....................-> Nested Loop Join (outer)
        ........................-> Nested Loop Join (outer)
        ............................-> Table "T1" as "V A" Full Scan
        ............................-> Filter
        ................................-> Table "T2" as "V B" Full Scan
        ........................-> Filter
        ............................-> Table "T3" as "V C" Full Scan
        ....................-> Record Buffer (record length: 25)
        ........................-> Table "T4" as "D" Full Scan
        ............-> Record Buffer (record length: 25)
        ................-> Table "T5" as "E" Full Scan
        1 1 1
        SubQueryConversion false
        Sub-query
        ....-> Filter
        ........-> Table "T5" as "E" Full Scan
        Select Expression
        ....-> Filter
        ........-> Hash Join (inner)
        ............-> Nested Loop Join (outer)
        ................-> Nested Loop Join (outer)
        ....................-> Table "T1" as "V A" Full Scan
        ....................-> Filter
        ........................-> Table "T2" as "V B" Full Scan
        ................-> Filter
        ....................-> Table "T3" as "V C" Full Scan
        ............-> Record Buffer (record length: 25)
        ................-> Filter
        ....................-> Table "T4" as "D" Full Scan
        1 1 1
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
