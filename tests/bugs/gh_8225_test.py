#coding:utf-8

"""
ID:          issue-8225
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8225
TITLE:       Problematic queries when SubQueryConversion = true
DESCRIPTION:
NOTES:
    [03.09.2024] pzotov
    Parameter 'SubQueryConversion' currently presents only in FB 5.x and _NOT_ in FB 6.x.
    Because of that, testing version are limited only for 5.0.2. FB 6.x currently is NOT tested.

    Confirmed bug on 5.0.2.1479-adfe97a.
    Checked on 5.0.2.1482-604555f.
"""

import pytest
from firebird.qa import *
from firebird.driver import driver_config, connect

init_script = """
    create domain dm_emp_id smallint;
    create domain dm_dep_id smallint;
    create domain dm_name varchar(20);

    create table department (
         dept_no dm_dep_id not null
        ,dept_name dm_name not null
    );

    create table employee (
        emp_no dm_emp_id not null
        ,last_name dm_name not null
        ,dept_no dm_dep_id not null
        ,constraint emp_key primary key (emp_no)
    );
    commit;
    insert into department( dept_no, dept_name) values (1, 'd1');
    insert into department( dept_no, dept_name) values (2, 'd2');
    insert into department( dept_no, dept_name) values (3, 'd3');
    insert into employee( emp_no, last_name, dept_no) values (1, 'e1', 1);
    insert into employee( emp_no, last_name, dept_no) values (2, 'e2', 2);
    insert into employee( emp_no, last_name, dept_no) values (3, 'e3', 3);
    insert into employee( emp_no, last_name, dept_no) values (4, 'e4', 1);
    insert into employee( emp_no, last_name, dept_no) values (5, 'e5', 1);
    insert into employee( emp_no, last_name, dept_no) values (6, 'e6', 1);
    insert into employee( emp_no, last_name, dept_no) values (7, 'e7', 2);
    insert into employee( emp_no, last_name, dept_no) values (8, 'e8', 3);
    insert into employee( emp_no, last_name, dept_no) values (9, 'e9', 3);
    commit;

    update department d set dept_no = -dept_no where exists(select * from employee e where e.dept_no = d.dept_no) rows 1;
    insert into employee( emp_no, last_name, dept_no) values (12, 'e12', -(select max(dept_no)+1 from department) );
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
        select d.dept_no, d.dept_name from department d
        where exists(select * from employee e where e.dept_no = d.dept_no)
        order by dept_no rows 1
    """

    for sq_conv in ('true','false',):
        srv_cfg = driver_config.register_server(name = f'srv_cfg_8225_{sq_conv}', config = '')
        db_cfg_name = f'db_cfg_8225_{sq_conv}'
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

            ps = cur.prepare(test_sql)
            print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )
            for r in cur.execute(ps):
                print(r[0],r[1])
            con.rollback()

    act.expected_stdout = f"""
        SubQueryConversion true

        Select Expression
        ....-> First N Records
        ........-> Filter
        ............-> Hash Join (semi)
        ................-> Refetch
        ....................-> Sort (record length: 28, key length: 8)
        ........................-> Table "DEPARTMENT" as "D" Full Scan
        ................-> Record Buffer (record length: 25)
        ....................-> Table "EMPLOYEE" as "E" Full Scan
        2 d2

        SubQueryConversion false

        Sub-query
        ....-> Filter
        ........-> Table "EMPLOYEE" as "E" Full Scan
        Select Expression
        ....-> First N Records
        ........-> Refetch
        ............-> Sort (record length: 28, key length: 8)
        ................-> Filter
        ....................-> Table "DEPARTMENT" as "D" Full Scan
        2 d2
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

