#coding:utf-8
#
# id:           bugs.core_6532
# title:        Results of concatenation with blob has no info about collation of source columns (which are declared with such info)
# decription:   
#                   Confirmed bug on 4.0.0.2394, 3.0.8.33426
#                   Checked on intermediate builds 4.0.0.2401 (03-apr-2021 09:36), 3.0.8.33435 (03-apr-2021 09:35) -- all OK.
#                 
# tracker_id:   CORE-6532
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

    --create domain dm_name_ci as varchar(10) character set utf8 collate name_coll;
    create domain dm_name_ci as blob sub_type text character set utf8 collate name_coll;
    commit;

    recreate table test(
        id int
       ,c1 varchar(10) character set utf8 collate name_coll
       ,b1 dm_name_ci
       --,b1 blob sub_type text character set utf8 collate name_coll -- same result
    );

    insert into test(id, c1, b1) values(1,'qWE','qWE');
    insert into test(id, c1, b1) values(2,'QWe','QWe');
    insert into test(id, c1, b1) values(3,'qwE','qwE');
    commit;

    set count on;
    -- set echo on;
    set list on;

    ---------------------------------------------

    select id from test
    where
        b1 starting with 'qwe' -- Records affected: 3 // OK
    order by id
    ;


    ---------------------------------------------

    select id from test
    where
        b1 || b1 starting with 'qwe' -- Was wrong: "Records affected: 0"
    order by id
    ;

    --------------------------------------------

    select id from test
    where
        c1 || cast(c1 as blob sub_type text character set utf8) collate name_coll starting with 'qwe' -- Was wrong: "Records affected: 0"
    order by id
    ; 
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

