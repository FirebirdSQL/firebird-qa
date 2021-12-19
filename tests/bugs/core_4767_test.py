#coding:utf-8
#
# id:           bugs.core_4767
# title:        CREATE USER ... TAGS ( attr = 'prefix #suffix' ): suffix will be removed from storage because of character '#' in the value of attribute
# decription:
#                   Checked on:
#                       FB30SS, build 3.0.4.32985: OK, 0.985s.
#                       FB40SS, build 4.0.0.1000: OK, 1.281s.
#
# tracker_id:   CORE-4767
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, user_factory, User

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    create or alter view v_user_tags as
    select
         a.sec$key tag
        ,a.sec$value val
    from sec$users u
    left join sec$user_attributes a on u.sec$user_name = a.sec$user_name
    where upper(u.sec$user_name) = upper('tmp$c4767') and upper(u.sec$plugin) = upper('Srp')
    ;
    commit;

    create or alter user tmp$c4767 password '123' using plugin Srp  tags (
        attr00001='attr #00001'
       ,attr00002='#'
       ,attr00003='##'
       ,attr00004='$'
       ,attr00005='$$'
    );
    commit;

    select * from v_user_tags;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TAG                             ATTR00001
    VAL                             attr #00001

    TAG                             ATTR00002
    VAL                             #

    TAG                             ATTR00003
    VAL                             ##

    TAG                             ATTR00004
    VAL                             $

    TAG                             ATTR00005
    VAL                             $$
"""

# cleanup fixture
user_1=user_factory('db_1', name='tmp$c4767', password='123', plugin='Srp',
                    do_not_create=True)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, user_1: User):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

