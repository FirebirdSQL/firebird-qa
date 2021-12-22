#coding:utf-8
#
# id:           bugs.core_6531
# title:        COMPUTED BY column looses charset and collate of source field <F> when <F> is either of type BLOB or VARCHAR casted to BLOB
# decription:   
#                   Confirmed bug on 4.0.0.2394, 3.0.8.33426
#                   Checked on intermediate builds 4.0.0.2401 (03-apr-2021 09:36), 3.0.8.33435 (03-apr-2021 09:35) -- all OK.
#                 
# tracker_id:   CORE-6531
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create collation name_coll for utf8 from unicode case insensitive;
    commit;

    create domain dm_name_ci as blob sub_type text character set utf8 collate name_coll;
    commit;

    recreate table test(
        id int
       ,b1 dm_name_ci
       ,calc_b1 computed by ( b1 )
       -----------------------------------------------------
       ,c1 varchar(10) character set utf8 collate name_coll
       ,calc_c1 computed by ( cast(c1 as blob sub_type text character set utf8) collate name_coll ) -- ==> SQLDA: "charset: 0 NONE"
       --,calc_c1 computed by ( (select list(x.c1) from test x where x.id = test.id) ) -- ==> SQLDA: "charset: 0 NONE"
       --,calc_c1 computed by ( cast(c1 as varchar(10) character set utf8) collate name_coll ) -- ==> SQLDA: "charset: 32260 UTF8" // OK
    );

    insert into test(id, b1, c1) values(1,'qWE','qWE');
    insert into test(id, b1, c1) values(2,'QWe','QWe');
    insert into test(id, b1, c1) values(3,'qwE','qwE');
    commit;

    set list on;
    set count on;
    -- set echo on;

    ---------------------------------------------

    select id
    from test where calc_c1 starting with 'qwe'
    order by id;

    ---------------------------------------------

    select id
    from test where calc_b1 starting with 'qwe'
    order by id;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    ID                              2
    ID                              3
    Records affected: 3

    ID                              1
    ID                              2
    ID                              3
    Records affected: 3
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

