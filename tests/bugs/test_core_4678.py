#coding:utf-8
#
# id:           bugs.core_4678
# title:        Regression: incorrect calculation of byte-length for view columns
# decription:   
# tracker_id:   CORE-4678
# min_versions: ['2.5.4']
# versions:     2.5.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.4
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test(id int);
    commit;
    
    set term ^;
    execute block as
    begin
        execute statement 'drop sequence gen_memo_id';
        when any do begin end
    end ^
    set term ;^
    commit;
    
    create generator gen_memo_id;
    
    recreate table test (
        id int not null,
        memo blob sub_type 1 segment size 100 character set ascii
    );
    create index memo_idx1 on test computed by (upper(trim(cast(substring(memo from 1 for 128) as varchar(128)))));
    
    set term ^ ;
    create or alter trigger test_bi for test
    active before insert position 0
    as
    begin
      if (new.id is null) then
        new.id = gen_id(gen_memo_id,1);
    end
    ^
    set term ; ^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    insert into test(memo) values( 'foo-rio-bar' );
    rollback;
    -- Confirmed on WI-V2.5.2.26540 (official release): 
    -- exception on ROLLBACK raises with text:
    -- ===
    -- Statement failed, SQLSTATE = HY000
    -- BLOB not found
    -- ===
    -- No reconnect is required, all can be done in one ISQL attachment.
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.4')
def test_core_4678_1(act_1: Action):
    act_1.execute()

