#coding:utf-8
#
# id:           bugs.core_5600
# title:        Invalid blob id when add a new blob column of type text and update another field
# decription:   
#                    Reproduced bug on WI-V3.0.3.32813, WI-T4.0.0.767.
#                    All fine on WI-T4.0.0.778.
#                
# tracker_id:   CORE-5600
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = [('BLOB_ID_.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    recreate table operation (
        id bigint not null,
        name blob sub_type text character set utf8 default '' not null,
        d_value double precision default 0 not null
    );

    alter table operation add constraint operation_pk_1 primary key ( id );

    insert into operation(id, name, d_value )
    select row_number()over() , 'foo', 1
    from rdb$types 
    rows 3
    ;
    commit;

    alter table operation add surname blob sub_type text character set utf8 default 'bar' not null;

    update operation set id=-id where id=2;

    -- NB: do _not_ put "COMMIT;" here!

    set blob all;
    set list on;
    select
         id
        ,name as blob_id_1
        ,surname as blob_id_2
    from operation where abs(id) in (1,2,3);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    foo
    bar

    ID                              -2
    foo
    bar

    ID                              3
    foo
    bar
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

