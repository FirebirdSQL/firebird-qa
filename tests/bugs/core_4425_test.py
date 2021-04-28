#coding:utf-8
#
# id:           bugs.core_4425
# title:        User-collations based on UNICODE are not upgrade to newer ICU version on restore
# decription:   
#                  Test uses .fbk which was created on linux host and has collation with following DDL:
#                  create collation nums_coll for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
#               
#                  SHOW COLLATION on linux host did show: COLL-VERSION=49.192.5.41.
#               
#                  We restore this database and try to use existing collation again.
#                  Checked on WI-V3.0.1.32573, WI-T4.0.0.331.
#                
# tracker_id:   CORE-4425
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core4425.fbk', init=init_script_1)

test_script_1 = """
    create domain dm_nums2 as varchar(20) character set utf8 collate nums_coll;
    commit;
    create table test2(s1 dm_nums2, s2 dm_nums2);
    commit;

    insert into test2 values('123qWe', '123QwE');
    insert into test2 values('1zXcvU', '1ZXcvu');
    insert into test2 values('12XcvU', '12xCVu');

    commit;
    set list on; 
    select 'old table:' as msg, s1,s2,s1=s2 from test order by s1;
    select 'new table:' as msg, s1,s2,s1=s2 from test2 order by s2;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             old table:
    S1                              1zXcvU
    S2                              1ZXcvu
    <true>
    MSG                             old table:
    S1                              12XcvU
    S2                              12xCVu
    <true>
    MSG                             old table:
    S1                              123qWe
    S2                              123QwE
    <true>

    MSG                             new table:
    S1                              1zXcvU
    S2                              1ZXcvu
    <true>
    MSG                             new table:
    S1                              12XcvU
    S2                              12xCVu
    <true>
    MSG                             new table:
    S1                              123qWe
    S2                              123QwE
    <true>
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

