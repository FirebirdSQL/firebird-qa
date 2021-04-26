#coding:utf-8
#
# id:           bugs.core_3650
# title:        recreation of collation for utf8 from unicode with option NUMERIC-SORT=1 leads to FB death
# decription:   
# tracker_id:   CORE-3650
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tns(f int); -- drop dependencies if any
    commit;
    set term ^;
    execute block as
    begin
      execute statement 'drop collation ns_coll;';
      when any do begin end
    end^
    set term ;^
    commit;
    create collation ns_coll for utf8 from unicode 'NUMERIC-SORT=1';
    recreate table tns(s varchar(50) character set utf8 collate ns_coll);
    commit;
    
    recreate table tns(f int); -- drop dependencies if any
    commit;
    set term ^;
    execute block as
    begin
      execute statement 'drop collation ns_coll;';
      when any do begin end
    end^
    set term ;^
    commit;
    create collation ns_coll for utf8 from unicode 'NUMERIC-SORT=1';
    rollback; -- !!NB!!
    
    set term ^;
    execute block as
    begin
      execute statement 'drop collation ns_coll;';
      when any do begin end
    end^
    set term ;^
    commit; -- this commit kills FB service 
    show collation;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
  There are no user-defined collations in this database
  """

@pytest.mark.version('>=2.5.2')
def test_core_3650_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

