#coding:utf-8
#
# id:           bugs.core_6358
# title:        Adding NOT NULL column with DEFAULT value may cause default values to update when selecting or have the wrong charset
# decription:   
#                   Confirmed bug on 4.0.0.2089
#                   Checked on 4.0.0.2090  - all OK.
#                   (intermediate snapshot with timestamps: 07-JUL-2020, 18:06)
#               
#                   Checked on 3.0.7.33340 - all OK
#                   (intermediate snapshot with timestamps: 10-JUL-2020, 15:50)
#                
# tracker_id:   CORE-6358
# min_versions: ['3.0.7']
# versions:     3.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.7
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
	
    -- Part 1: adding field of timestamp datatype with default value = 'now'
    -- #######

    create table tdelay(id int primary key);
    create sequence g;
    set term ^;
    create procedure sp_delay returns( dts1 timestamp, dts2 timestamp, elap_ms int ) as
        declare c int;
        declare v_id int;
    begin
        execute statement 'select count(*) from rdb$database /* do you really think that i am in work now ? */' into c;
        v_id = gen_id(g,1);
        dts1 = cast('now' as timestamp);
        insert into tdelay(id) values( :v_id );
        in autonomous transaction do
        begin
            execute statement ('insert into tdelay(id) values(?)') ( :v_id );
            when any do
            begin
                -- nop --
            end
        end
        delete from tdelay where id = :v_id;
        dts2 = cast('now' as timestamp);
        elap_ms = datediff( millisecond from dts1 to dts2);
        suspend;
    end
    ^
    set term ;^
    commit;

    -----------------------------
    recreate table t (n integer);
    insert into t values (1);
    commit;
    alter table t add dts timestamp default 'now' not null;
    commit;
    -----------------------------

    set transaction lock timeout 1;
	--                          ^^^ ### DELAY ###
    set term ^;
    execute block returns( diff_ms int ) as
        declare c int;
        declare t1 timestamp;
        declare t2 timestamp;
    begin
        select dts from t into t1;

		-- HERE WE MAKE DELAY:
		-- ###################
        select count(*) from sp_delay p into c;
		
        select dts from t into t2;
        diff_ms = datediff(millisecond from t1 to t2);
        suspend;
    end^
    set term ;^


    -- Part 2: adding field with charset that differs from current client connection charset.
    --##################################

    recreate table t2 (n integer);
    insert into t2 values (1);
    commit;
    alter table t2 add c1 varchar(10) character set win1252 default '123áé456' not null;
    insert into t2 (n) values (2);
    select * from t2;
  
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	DIFF_MS                         0

	N                               1
	C1                              123áé456
	N                               2
	C1                              123áé456
  """

@pytest.mark.version('>=3.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

