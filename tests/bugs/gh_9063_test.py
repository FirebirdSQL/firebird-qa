#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9063
TITLE:       Incorrect results for DISTINCT used together with IN/EXISTS which is converted into a semi-join
DESCRIPTION:
NOTES:
    [17.06.2026] pzotov
    Custom driver config objects are created here for 5.x (because SubQueryConversion = true must be used).
    Test verifies that there is no difference in results returning by queries that uses DISTINCT vs GROUP BY.
    Confirmed bug on 6.0.0.2009; 5.0.5.1833.
    Checked on 6.0.0.2012; 5.0.5.1837.
"""
from firebird.driver import DatabaseError, driver_config, connect

import pytest
from firebird.qa import *

init_script = """
    create table employee (
        emp_no       smallint not null
       ,first_name   varchar(15) not null
    );

    create table employee_project (
        emp_no   smallint not null
       ,proj_id  char(5) not null
    );

    create table project (
        proj_id char(5) not null
    );
    commit;

    insert into employee (emp_no, first_name) values (2, 'robert');
    insert into employee (emp_no, first_name) values (4, 'bruce');
    insert into employee (emp_no, first_name) values (5, 'kim');
    insert into employee (emp_no, first_name) values (8, 'leslie');
    insert into employee (emp_no, first_name) values (9, 'phil');
    insert into employee (emp_no, first_name) values (11, 'k. j.');
    insert into employee (emp_no, first_name) values (12, 'terri');
    insert into employee (emp_no, first_name) values (14, 'stewart');
    insert into employee (emp_no, first_name) values (15, 'katherine');
    insert into employee (emp_no, first_name) values (20, 'chris');
    insert into employee (emp_no, first_name) values (24, 'pete');
    insert into employee (emp_no, first_name) values (28, 'ann');
    insert into employee (emp_no, first_name) values (29, 'roger');
    insert into employee (emp_no, first_name) values (34, 'janet');
    insert into employee (emp_no, first_name) values (36, 'roger');
    insert into employee (emp_no, first_name) values (37, 'willie');
    insert into employee (emp_no, first_name) values (44, 'leslie');
    insert into employee (emp_no, first_name) values (45, 'ashok');
    insert into employee (emp_no, first_name) values (46, 'walter');
    insert into employee (emp_no, first_name) values (52, 'carol');
    insert into employee (emp_no, first_name) values (61, 'luke');
    insert into employee (emp_no, first_name) values (65, 'sue anne');
    insert into employee (emp_no, first_name) values (71, 'jennifer m.');
    insert into employee (emp_no, first_name) values (72, 'claudia');
    insert into employee (emp_no, first_name) values (83, 'dana');
    insert into employee (emp_no, first_name) values (85, 'mary s.');
    insert into employee (emp_no, first_name) values (94, 'randy');
    insert into employee (emp_no, first_name) values (105, 'oliver h.');
    insert into employee (emp_no, first_name) values (107, 'kevin');
    insert into employee (emp_no, first_name) values (109, 'kelly');
    insert into employee (emp_no, first_name) values (110, 'yuki');
    insert into employee (emp_no, first_name) values (113, 'mary');
    insert into employee (emp_no, first_name) values (114, 'bill');
    insert into employee (emp_no, first_name) values (118, 'takashi');
    insert into employee (emp_no, first_name) values (121, 'roberto');
    insert into employee (emp_no, first_name) values (127, 'michael');
    insert into employee (emp_no, first_name) values (134, 'jacques');
    insert into employee (emp_no, first_name) values (136, 'scott');
    insert into employee (emp_no, first_name) values (138, 't.j.');
    insert into employee (emp_no, first_name) values (141, 'pierre');
    insert into employee (emp_no, first_name) values (144, 'john');
    insert into employee (emp_no, first_name) values (145, 'mark');

    insert into employee_project (emp_no, proj_id) values (144, 'dgpii');
    insert into employee_project (emp_no, proj_id) values (113, 'dgpii');
    insert into employee_project (emp_no, proj_id) values (24, 'dgpii');
    insert into employee_project (emp_no, proj_id) values (8, 'vbase');
    insert into employee_project (emp_no, proj_id) values (136, 'vbase');
    insert into employee_project (emp_no, proj_id) values (15, 'vbase');
    insert into employee_project (emp_no, proj_id) values (71, 'vbase');
    insert into employee_project (emp_no, proj_id) values (145, 'vbase');
    insert into employee_project (emp_no, proj_id) values (44, 'vbase');
    insert into employee_project (emp_no, proj_id) values (4, 'vbase');
    insert into employee_project (emp_no, proj_id) values (83, 'vbase');
    insert into employee_project (emp_no, proj_id) values (138, 'vbase');
    insert into employee_project (emp_no, proj_id) values (45, 'vbase');
    insert into employee_project (emp_no, proj_id) values (20, 'guide');
    insert into employee_project (emp_no, proj_id) values (24, 'guide');
    insert into employee_project (emp_no, proj_id) values (113, 'guide');
    insert into employee_project (emp_no, proj_id) values (8, 'guide');
    insert into employee_project (emp_no, proj_id) values (4, 'mapdb');
    insert into employee_project (emp_no, proj_id) values (71, 'mapdb');
    insert into employee_project (emp_no, proj_id) values (46, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (105, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (12, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (85, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (110, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (34, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (8, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (14, 'mktpr');
    insert into employee_project (emp_no, proj_id) values (52, 'mktpr');

    insert into project (proj_id) values ('vbase');
    insert into project (proj_id) values ('dgpii');
    insert into project (proj_id) values ('guide');
    insert into project (proj_id) values ('mapdb');
    insert into project (proj_id) values ('hwrii');
    insert into project (proj_id) values ('mktpr');

    commit;

    alter table employee add primary key (emp_no);
    alter table employee_project add primary key (emp_no, proj_id);
    alter table project add primary key (proj_id);

    alter table employee_project add foreign key (emp_no) references employee (emp_no);
    alter table employee_project add foreign key (proj_id) references project (proj_id);
    commit;
"""
db = db_factory(init = init_script)
act = python_act('db')

query_map = {
    1000 : (
              """
                with
                d as (
                    select distinct e.first_name
                    from employee e join employee_project ep on e.emp_no = ep.emp_no
                    where ep.proj_id in (select first 5 p.proj_id from project p order by 1)
                )
                ,g as (
                    select e.first_name
                    from employee e join employee_project ep on e.emp_no = ep.emp_no
                    where ep.proj_id in (select first 5 p.proj_id from project p order by 1)
                    group by 1
                )
                select d.first_name as name_via_distinct, g.first_name as name_via_group_by
                from d
                full join g using(first_name)
                where d.first_name is distinct from g.first_name
                ;
              """
             ,'Based on test from the ticket. NO records must be issued.'
           )
}

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=5.0.5')
def test_1(act: Action, capsys):

    srv_cfg = driver_config.register_server(name = f'srv_cfg_9063', config = '')
    db_cfg_name = f'db_cfg_9063'
    db_cfg_object = driver_config.register_database(name = db_cfg_name)
    db_cfg_object.server.value = srv_cfg.name
    db_cfg_object.database.value = str(act.db.db_path)
    if act.is_version('<6'):
        db_cfg_object.config.value = f"""
            SubQueryConversion = true
        """

    with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
        cur = con.cursor()
        for q_idx, q_tuple in query_map.items():
            test_sql, qry_comment = q_tuple[:2]
            print(q_idx)
            print(test_sql)
            print(qry_comment)
            try:
                ps = cur.prepare(test_sql)
                cur.execute(ps)
                ccol=cur.description
                for r in cur:
                    for i in range(0,len(ccol)):
                        print( 'UNEXPECTED ' + ccol[i][0],':', r[i])
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)

    act.expected_stdout = f"""
        1000
        {query_map[1000][0]}
        {query_map[1000][1]}
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
