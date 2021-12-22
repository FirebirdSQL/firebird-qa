#coding:utf-8
#
# id:           bugs.core_4544
# title:        Allow hiding source code of procedures and triggers in FB 3
# decription:   
# tracker_id:   CORE-4544
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('SOURCE_BLOB.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(id int primary key, x int);
    recreate table tlog(id int, x int);
    
    recreate sequence g;
    
    set term ^;
    create or alter procedure sp_test1 as
        declare c int;
    begin
        select count(*) from rdb$types into c;
    end
    ^
    
    create or alter function fn_test1 returns int as
    begin
      return 111;
    end
    ^
    
    create or alter trigger trg_test_1 active before insert on test as
    begin
        new.id = gen_id(g,1);
    end
    ^
    
    create or alter package pkg_test1 as
    begin
        procedure sp_test1;
        function fn_test1 returns int;
    end
    ^
    
    recreate package body pkg_test1 as
    begin
        procedure sp_test1 as
            declare c int;
        begin
            select count(*) from rdb$types into c;
        end
    
        function fn_test1 returns int as
        begin
           return 111;
        end
    end
    ^
    
    set term ;^
    commit;
    
    set blob all;
    set list on;
    
    select rdb$procedure_name, rdb$procedure_source as source_blob
    from rdb$procedures where rdb$system_flag is distinct from 1;
    
    select rdb$function_name, rdb$function_source as source_blob
    from rdb$functions where rdb$system_flag is distinct from 1;
    
    select rdb$trigger_name, rdb$trigger_source as source_blob
    from rdb$triggers where rdb$system_flag is distinct from 1;
    
    select rdb$package_name, rdb$package_body_source as source_blob
    from rdb$packages where rdb$system_flag is distinct from 1;
    
    set count on;
    set echo on;
    
    update rdb$procedures set rdb$procedure_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$procedure_source is not null
    ;
    
    update rdb$functions set rdb$function_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$function_source is not null
    ;
    
    update rdb$triggers set rdb$trigger_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$trigger_source is not null
    ;
    
    update rdb$packages set rdb$package_body_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$package_body_source is not null
    ;
    
    set echo off;
    commit;
    
    
    select rdb$procedure_name, rdb$procedure_source as source_blob
    from rdb$procedures
    where rdb$system_flag is distinct from 1 and rdb$procedure_source is not null;
    
    select rdb$function_name, rdb$function_source as source_blob
    from rdb$functions
    where rdb$system_flag is distinct from 1 and rdb$function_source is not null;
    
    select rdb$trigger_name, rdb$trigger_source as source_blob
    from rdb$triggers
    where rdb$system_flag is distinct from 1 and rdb$trigger_source is not null;
    
    select rdb$package_name, rdb$package_body_source as source_blob
    from rdb$packages where rdb$system_flag is distinct from 1 and rdb$package_body_source is not null;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$PROCEDURE_NAME              SP_TEST1                                                                                     
    SOURCE_BLOB                     1a:1e0
    declare c int;
    begin
        select count(*) from rdb$types into c;
    end
    
    RDB$PROCEDURE_NAME              SP_TEST1                                                                                     
    SOURCE_BLOB                     <null>
    
    
    
    RDB$FUNCTION_NAME               FN_TEST1                                                                                     
    SOURCE_BLOB                     e:1e0
    begin
      return 111;
    end
    
    RDB$FUNCTION_NAME               FN_TEST1                                                                                     
    SOURCE_BLOB                     <null>
    
    
    
    RDB$TRIGGER_NAME                TRG_TEST_1                                                                                   
    SOURCE_BLOB                     c:3d0
    as
    begin
        new.id = gen_id(g,1);
    end
    
    
    
    RDB$PACKAGE_NAME                PKG_TEST1                                                                                    
    SOURCE_BLOB                     2a:1
    begin
        procedure sp_test1 as
            declare c int;
        begin
            select count(*) from rdb$types into c;
        end
    
        function fn_test1 returns int as
        begin
           return 111;
        end
    end
    
    
    
    update rdb$procedures set rdb$procedure_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$procedure_source is not null
    ;
    Records affected: 1
    
    update rdb$functions set rdb$function_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$function_source is not null
    ;
    Records affected: 1
    
    update rdb$triggers set rdb$trigger_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$trigger_source is not null
    ;
    Records affected: 1
    
    update rdb$packages set rdb$package_body_source = null
    where
        rdb$system_flag is distinct from 1
        and rdb$package_body_source is not null
    ;
    Records affected: 1
    
    set echo off;
    Records affected: 0
    Records affected: 0
    Records affected: 0
    Records affected: 0
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

