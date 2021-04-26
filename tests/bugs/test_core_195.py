#coding:utf-8
#
# id:           bugs.core_195
# title:        Bugcheck 291
# decription:   
# tracker_id:   CORE-195
# min_versions: ['1.5.0']
# versions:     1.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 1.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table tbl_bugcheck291
(
 ID integer NOT NULL PRIMARY KEY,
 DATA integer
);

commit;

insert into tbl_bugcheck291 (id, data) values (1,100);

commit;

SET TERM ^ ;

create trigger bu_tbl_bugcheck291 for tbl_bugcheck291
 before update
as
begin
 if (new.data is not null) then
 begin
  if(new.data<110)then
  begin
   update tbl_bugcheck291 x set x.data=new.data+1 where x.id=new.id;
  end
 end
end
^
COMMIT WORK ^
SET TERM ;^

CREATE TABLE T1

(

  DATA	INTEGER,

  FLAG	INTEGER

);



SET TERM ^ ;



CREATE TRIGGER TRIG1 FOR T1

ACTIVE BEFORE UPDATE POSITION 1

as

begin

if (new.Flag = 16 and new.Data = 1) then begin

  update t1 set Data = 2 where Flag = 46;

  update t1 set Data = 3 where Flag = 46;

end

if (new.Flag = 46 and new.Data = 2) then begin

  update t1 set Data = 4 where Flag = 14;

  update t1 set Data = 5 where Flag = 15;

end

if (new.Flag = 14 and new.Data = 4) then begin

  update t1 set Data = 6 where Flag = 46;

end

if (new.Flag = 15 and new.Data = 5) then begin

  update t1 set Data = 7 where Flag = 46;

end

if (new.Flag = 46 and new.Data = 3) then begin

  update t1 set Data = 8 where Flag = 46;

end

end

 ^



COMMIT ^

SET TERM ;^



insert into t1(Flag) values(14);

insert into t1(Flag) values(15);

insert into t1(Flag) values(16);

insert into t1(Flag) values(46);

commit;

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """update tbl_bugcheck291 set data=105 where id=1;
commit;
update tbl_bugcheck291 set data=105 where id=1;
commit;
update t1 set Data=1 where Flag = 16;
commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=1.5.0')
def test_core_195_1(act_1: Action):
    act_1.execute()

