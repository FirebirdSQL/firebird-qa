#coding:utf-8
#
# id:           bugs.core_2274
# title:        MERGE non-standard behaviour, accepts multiple matches
# decription:   
#                  Confirmed bug on 4.0.0.2011
#                  Checked on 4.0.0.2022 - works fine.
#                
# tracker_id:   CORE-2274
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t_payment_details(operation_id int primary key, person_id int, payment_sum int);
    recreate table t_payment_totals(person_id int primary key, payment_sum int);
    commit;
    insert into t_payment_details(operation_id, person_id, payment_sum) values(0, 10, 0);
    insert into t_payment_details(operation_id, person_id, payment_sum) values(1, 11, 11);
    insert into t_payment_details(operation_id, person_id, payment_sum) values(2, 22, 222);
    insert into t_payment_details(operation_id, person_id, payment_sum) values(3, 11, 3333);
    insert into t_payment_details(operation_id, person_id, payment_sum) values(7, 17, 77777);

    insert into t_payment_totals(person_id, payment_sum) values(10, 100);
    insert into t_payment_totals(person_id, payment_sum) values(11, 111);
    insert into t_payment_totals(person_id, payment_sum) values(22, 222);

    set list on;
    select 'before merge' as msg, e.* from t_payment_totals e order by person_id;

    merge into t_payment_totals t 
    using t_payment_details s on s.person_id = t.person_id
    when NOT matched then
        insert(person_id, payment_sum) values( s.person_id, s.payment_sum )
    when MATCHED then
        update set t.payment_sum = t.payment_sum + s.payment_sum
    ;

    select 'after merge' as msg, e.* from t_payment_totals e order by person_id;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             before merge
    PERSON_ID                       10
    PAYMENT_SUM                     100

    MSG                             before merge
    PERSON_ID                       11
    PAYMENT_SUM                     111

    MSG                             before merge
    PERSON_ID                       22
    PAYMENT_SUM                     222



    MSG                             after merge
    PERSON_ID                       10
    PAYMENT_SUM                     100

    MSG                             after merge
    PERSON_ID                       11
    PAYMENT_SUM                     111

    MSG                             after merge
    PERSON_ID                       22
    PAYMENT_SUM                     222
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 21000
    Multiple source records cannot match the same target during MERGE
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

