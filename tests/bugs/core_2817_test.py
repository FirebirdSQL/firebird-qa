#coding:utf-8
#
# id:           bugs.core_2817
# title:        If stored procedure or trigger contains query with PLAN ORDER it could fail after disconnect of attachment where procedure	rigger executed first time
# decription:   
#                
# tracker_id:   CORE-2817
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    create sequence g;
    create or alter procedure sp_test returns(cnt int) as begin end;
    recreate table test(
        x int,
        s varchar(1000)
    );
    commit;

    insert into test(x, s)
    select gen_id(g,1), rpad('', 1000, uuid_to_char(gen_uuid()))
    from rdb$types, rdb$types
    rows 1000;
    commit;

    create index test_x on test(x);
    create index test_s on test(s);
    commit;

    set term ^;
    create or alter procedure sp_test(a_odd smallint) as
        declare c_ord cursor for (
            select s 
            from test 
            where mod(x, 2) = :a_odd 
            order by x
        );
        declare v_s type of column test.s;
    begin
        open c_ord;
        while (1=1) do
        begin
            fetch c_ord into v_s;
            if (row_count = 0) then leave;
            update test set s = uuid_to_char(gen_uuid()) where current of c_ord;
        end
        close c_ord;
    end
    ^ -- sp_test
    set term ;^
    commit; 
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import fdb
#  
#  db_conn.close()
#  att1 = kdb.connect(dsn=dsn.encode(),user='SYSDBA',password='masterkey')
#  att2 = kdb.connect(dsn=dsn.encode(),user='SYSDBA',password='masterkey')
#  
#  cur1 = att1.cursor()
#  cur2 = att2.cursor()
#  
#  sp_run='execute procedure sp_test'
#  
#  cur1.execute('execute procedure sp_test(0)')
#  cur2.execute('execute procedure sp_test(1)')
#  
#  att1.commit()
#  att1.close()
#  
#  cur2.execute('execute procedure sp_test(1)')
#  att2.close()
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


