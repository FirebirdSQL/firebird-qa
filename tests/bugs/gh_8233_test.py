#coding:utf-8

"""
ID:          issue-8233
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8233
TITLE:       SubQueryConversion = true --multiple rows in singleton select
DESCRIPTION:
NOTES:
    [27.08.2024] pzotov
    1. Confirmed bug on 5.0.1.1485-274af35 (26.08.2024), got for SubQueryConversion=true:
       "multiple rows in singleton select", gdscodes: (335544652, 335544842)
    2. Parameter 'SubQueryConversion' currently presents only in FB 5.x and _NOT_ in FB 6.x.
       Because of that, testing version are limited only for 5.0.2. FB 6.x currently is NOT tested.
    3. Table 't1' must have more than one row for bug reproducing. Query must be enclosed in execute block.
    4. Custom driver config objects are created here, one with SubQueryConversion = true and second with false.
    
    Checked on 5.0.2.1487-6934878 -- all ok.
    Thanks to dimitr for the advice on implementing the test.
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect, DatabaseError

init_script = """
create table t1(id int, fld int);
create table t2(id int, fld int);

insert into t1(id, fld) values(1, 111);
insert into t1(id, fld) values(2, 222);
insert into t1(id, fld) values(3, 333);
insert into t2(id, fld) values(3, 999);
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
        execute block returns (res int)
        as
        begin
           select first 1 id from t1
             where exists (select 1 from t2 where t1.id = t2.id)
             order by t1.id
             into :res;
           suspend;
        end
    """

    for sq_conv in ('true','false',):
        srv_cfg = driver_config.register_server(name = f'srv_cfg_8233_{sq_conv}', config = '')
        db_cfg_name = f'db_cfg_8233_{sq_conv}'
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
                    print(r[0])
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)

    act.expected_stdout = f"""
        SubQueryConversion true
        Select Expression (line 5, column 12)
        ....-> Singularity Check
        ........-> First N Records
        ............-> Filter
        ................-> Hash Join (semi)
        ....................-> Sort (record length: 28, key length: 8)
        ........................-> Table "T1" Full Scan
        ....................-> Record Buffer (record length: 25)
        ........................-> Table "T2" Full Scan
        3
        SubQueryConversion false
        Sub-query
        ....-> Filter
        ........-> Table "T2" Full Scan
        Select Expression (line 5, column 12)
        ....-> Singularity Check
        ........-> First N Records
        ............-> Sort (record length: 28, key length: 8)
        ................-> Filter
        ....................-> Table "T1" Full Scan
        3
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
