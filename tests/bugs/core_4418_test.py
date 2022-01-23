#coding:utf-8

"""
ID:          issue-4740
ISSUE:       4740
TITLE:       Regression: Can not run ALTER TABLE DROP CONSTRAINT <FK_name> after recent changes in svn
DESCRIPTION: Added some extra DDL statements to be run within single Tx and then to be rollbacked.
JIRA:        CORE-4418
"""

import pytest
from firebird.qa import *

substitutions = [('COLL-VERSION=\\d{2,}.\\d{2,}', 'COLL-VERSION=111.222'),
                 ('COLL-VERSION=\\d+\\.\\d+\\.\\d+\\.\\d+', 'COLL-VERSION=111.222')]

init_script = """
recreate table td(id int);
recreate table tm(id int);
commit;

set term ^;
execute block as
begin
  begin
    execute statement 'drop domain dm_ids';
  when any do begin end
  end
  begin
    execute statement 'drop domain dm_nums';
  when any do begin end
  end
  begin
    execute statement 'drop collation nums_coll';
  when any do begin end
  end
end
^set term ;^
commit;

create collation nums_coll for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
commit;
create domain dm_nums as varchar(20) character set utf8 collate nums_coll;
commit;
create domain dm_ids as bigint;
commit;

recreate table tm(
  id dm_ids,
  nm dm_nums,
  constraint tm_pk primary key(id)
);

recreate table td(
  id dm_ids,
  pid dm_ids,
  nm dm_nums,
  constraint td_pk primary key(id),
  constraint td_fk foreign key(pid) references tm
);

set autoddl off;
commit;

alter table td drop constraint td_fk;
alter table td drop constraint td_pk;
alter table tm drop constraint tm_pk;
drop table td;
drop table tm;
drop domain dm_nums;
drop domain dm_ids;
drop collation nums_coll;

rollback;
"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """
show table tm;
show table td;
show domain dm_ids;
show domain dm_nums;
show collation nums_coll;
-- oel64: coll-version=49.192.5.41
-- winxp: coll-version=58.0.6.50
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
ID                              (DM_IDS) BIGINT Not Null
NM                              (DM_NUMS) VARCHAR(20) CHARACTER SET UTF8 Nullable
                                 COLLATE NUMS_COLL
CONSTRAINT TM_PK:
  Primary key (ID)
ID                              (DM_IDS) BIGINT Not Null
PID                             (DM_IDS) BIGINT Nullable
NM                              (DM_NUMS) VARCHAR(20) CHARACTER SET UTF8 Nullable
                                 COLLATE NUMS_COLL
CONSTRAINT TD_FK:
  Foreign key (PID)    References TM (ID)
CONSTRAINT TD_PK:
  Primary key (ID)
DM_IDS                          BIGINT Nullable
DM_NUMS                         VARCHAR(20) CHARACTER SET UTF8 Nullable
                                 COLLATE NUMS_COLL
NUMS_COLL, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88;NUMERIC-SORT=1'
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

