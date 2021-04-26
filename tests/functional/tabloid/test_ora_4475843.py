#coding:utf-8
#
# id:           functional.tabloid.ora_4475843
# title:        Wrong (empty) result of query in Oracle 19
# decription:   
#                  Original issue:
#                  https://community.oracle.com/tech/developers/discussion/4475843/wrong-result-on-a-simple-sql-statement
#                  According to message, Oracle return no rows for the query that follows.
#                  Could not check because of problems with install Oracle XE.
#               
#                  Checked on 4.0.0.2416, 3.0.8.33445 - results OK (one row).
#                  Checked also on SQL Server XE and Postgres 13
#                
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
        p_c_id   int,
        v_id     int,
        r_m_i_id int not null,
        r_m_s_id int,
        constraint pk_test primary key (p_c_id, v_id)
    );
    insert into test(p_c_id, v_id, r_m_i_id, r_m_s_id) values(102, 646, 318, 1089);
    insert into test(p_c_id, v_id, r_m_i_id, r_m_s_id) values(102, 647, 317, 1089);
    insert into test(p_c_id, v_id, r_m_i_id, r_m_s_id) values(102, 648, 316, 1363);
    insert into test(p_c_id, v_id, r_m_i_id, r_m_s_id) values(102, 649, 315, null);
    commit;

    set list on;
    set count on;
    select
        (
            select rmis.s_id
            from (
                select
                  316 as r_m_i_id
                  ,1089      as s_id
                  ,'true'    as i_d_s
                from rdb$database
                union all
                select
                  316 as r_m_i_id
                  ,1363     as s_id
                  ,'false'  as i_d_s
                from rdb$database
            ) rmis
            where rmis.r_m_i_id = pm.r_m_i_id
            and (
                pm.r_m_s_id    is null and rmis.i_d_s   = 'true'
                or
                pm.r_m_s_id is not null and rmis.s_id = pm.r_m_s_id
            )
            fetch first 1 rows only
        ) as supplier
        ,pm.r_m_s_id
        ,pc.m_c_id
        ,pc.id
    from test pm
    inner join (select 102 as id, 10 as m_c_id from rdb$database ) pc on pc.id = pm.p_c_id
    where
        pm.p_c_id = 102
        and pm.v_id = 648;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SUPPLIER                        1363
    R_M_S_ID                        1363
    M_C_ID                          10
    ID                              102
    Records affected: 1
  """

@pytest.mark.version('>=3.0')
def test_ora_4475843_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

