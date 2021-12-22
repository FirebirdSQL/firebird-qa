#coding:utf-8
#
# id:           bugs.core_4752
# title:        EXECUTE STATEMENT using BLOB parameters results in "Invalid BLOB ID" error
# decription:   
# tracker_id:   CORE-4752
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tb(id int, b1 blob);
    commit;
    insert into tb(id) values(1);
    insert into tb(id) values(2);
    insert into tb(id) values(3);
    commit;
    
    set term ^;
    execute block as
        declare v_stt varchar(255);
        declare v_blob_a blob = 'qwertyuioplkjhgfdsazxcvbnm';
        declare v_blob_b blob = '1234567890asdfghjklmnbvcxz';
    begin
        v_stt = 'update tb set b1 = case when id in (1,2) then cast(? as blob) else cast(? as blob) end';
        execute statement ( v_stt ) ( v_blob_a, v_blob_b );
    end
    ^
    set term ;^ 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.5')
def test_1(act_1: Action):
    act_1.execute()

