#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8974
TITLE:       Temporary tables in packages (#8974) - access rights
DESCRIPTION:
    Test verifies assertions from doc/sql.extensions/README.packaged_temporary_tables.md, particularly that:
        * Unqualified references to a matching declared table name inside package routines resolve to the package table.
        * Header tables can be accessed externally as `package_name.table_name` or `package_name%package.table_name`.
        * Body tables cannot be accessed externally and are only valid inside routines of the same package body.
        * Direct access to public header tables requires the appropriate package privilege for the requested operation,
          such as `SELECT`, `INSERT`, `UPDATE` or `DELETE`.
        * A package table name may also match a regular table name in the same schema.
NOTES:
    [30.05.2026] pzotov
    Checked on 6.0.0.1976.
"""
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

tmp_user = user_factory('db', name = 'tmp_pg_tabs_john', password='123')
tmp_role = role_factory('db', name = 'tmp_pg_tabs_role')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_user: User, tmp_role: Role, capsys):

    for sec_type in ('invoker', 'definer'):

        init_script = f"""
            set autoterm on;
            recreate table t_pub(id int);  -- regular non-packaged table with name that is the same to packaged table
            recreate table t_priv(id int); -- regular non-packaged table with name that is the same to packaged table
            create sequence g start with 1000000;
            create or alter package pg_test
            sql security {sec_type}
            as
            begin
                temporary table t_pub(id int, f01 int, u_name rdb$user, u_role rdb$user) on commit preserve rows unique index t_pub_unq(id);
                procedure sp_add_data(a_id int = null, a_f01 int = null);
                procedure sp_get_data returns(src varchar(20), id int, f01 int, u_name rdb$user, u_role rdb$user);
            end
            ;
            recreate package body pg_test as
            begin
                temporary table t_priv(id int, f01 int, u_name rdb$user, u_role rdb$user) on commit preserve rows unique index t_priv_unq(id);
                procedure sp_add_data(a_id int, a_f01 int) as
                    declare v int;
                begin
                    -- ::: NOTE ::: UNQUALIFIED NAMES must be resolved to the PACKAGED tables:
                    if (a_id is null) then
                        begin
                            v = -gen_id(g,1);
                            insert into t_pub(id, f01, u_name, u_role) values(:v, :v, current_user, current_role);
                            insert into t_priv(id, f01, u_name, u_role) values(-1000 - :v, -1000 - :v, current_user, current_role);
                        end
                    else
                        insert into t_pub(id, f01, u_name, u_role) values(:a_id, :a_f01, current_user, current_role);
                        insert into t_priv(id, f01, u_name, u_role) values(1000 + :a_id, 1000 + :a_f01, current_user, current_role);
                end

                procedure sp_get_data returns(src varchar(20), id int, f01 int, u_name rdb$user, u_role rdb$user) as
                begin
                    for
                        select src, id, f01, u_name, u_role
                        from (
                            -- ::: NOTE ::: UNQUALIFIED NAMES must be resolved to the PACKAGED tables:
                            select 't_pub' as src, id, f01, u_name, u_role from t_pub
                            UNION ALL
                            select 't_priv' as src, id, f01, u_name, u_role from t_priv
                        )
                        order by src, id
                    into
                        src, id, f01, u_name, u_role
                    do
                        suspend;
                end
            end
            ;
            commit;
        """
        act.isql(switches = ['-q'], input = init_script, combine_output = True)
        assert act.clean_stdout == '' and act.return_code == 0
        act.reset()

        if sec_type == 'invoker':
            # [doc]: Direct access to public header tables requires the appropriate package privilege
            # for the requested operation, such as `SELECT`, `INSERT`, `UPDATE` or `DELETE`.
            #
            grants_lst = f"""
                grant {tmp_role.name} to {tmp_user.name} ^
                grant execute on package pg_test to role {tmp_role.name} ^
                grant usage on sequence g to package pg_test ^
                grant select, insert on package pg_test to role {tmp_role.name} ^
            """
        else:
            grants_lst = f"""
                grant {tmp_role.name} to {tmp_user.name} ^
                grant execute on package pg_test to role {tmp_role.name} ^
            """

        print(f'Checked {sec_type=}')
        with act.db.connect() as con_dba:
            for x in grants_lst.split('^'):
                if ( s:= x.strip() ):
                    if s.lower() == 'commit':
                        con_dba.commit()
                    else:
                        con_dba.execute_immediate(s)
            con_dba.commit()

            with act.db.connect(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name) as con_usr:

                cur_dba = con_dba.cursor()
                cur_dba.callproc('pg_test.sp_add_data(1, 1)')
                cur_dba.execute('select * from pg_test.sp_get_data')
                ccol=cur_dba.description
                for r in cur_dba:
                    for i in range(0,len(ccol)):
                        print( ccol[i][0],':', r[i])

                cur_usr = con_usr.cursor()
                cur_usr.callproc('pg_test.sp_add_data(1, 1)')
                cur_usr.execute('select * from pg_test.sp_get_data')
                ccol=cur_usr.description
                for r in cur_usr:
                    for i in range(0,len(ccol)):
                        print( ccol[i][0],':', r[i])
            
            try:
                # must PASS because we query table in the package HEAD:
                #
                cur_dba.execute('select count(*) as t_pub_cnt from pg_test.t_pub')
                ccol = cur_dba.description
                for r in cur_dba:
                    for i in range(0,len(ccol)):
                        print( ccol[i][0],':', r[i])

                # Private body tables cannot be made externally accessible with package grants.
                # must FAIL because we query table in the package BODY,
                # with gds = 335545335 / Table ... is private to package ...
                #
                cur_dba.execute('select count(*) as t_priv_cnt from pg_test.t_priv')
                ccol = cur_dba.description
                for r in cur_dba:
                    for i in range(0,len(ccol)):
                        print( ccol[i][0],':', r[i])

            except DatabaseError as e:
                print( e.__str__() )
                print(e.gds_codes)

            con_dba.execute_immediate('drop package pg_test')
            con_dba.execute_immediate('drop sequence g')
            con_dba.commit()

    act.expected_stdout = f"""
        Checked sec_type='invoker'
        SRC : t_priv
        ID : 1001
        F01 : 1001
        U_NAME : SYSDBA
        U_ROLE : NONE
        SRC : t_pub
        ID : 1
        F01 : 1
        U_NAME : SYSDBA
        U_ROLE : NONE
        SRC : t_priv
        ID : 1001
        F01 : 1001
        U_NAME : TMP_PG_TABS_JOHN
        U_ROLE : TMP_PG_TABS_ROLE
        SRC : t_pub
        ID : 1
        F01 : 1
        U_NAME : TMP_PG_TABS_JOHN
        U_ROLE : TMP_PG_TABS_ROLE

        T_PUB_CNT : 1
        Table "T_PRIV" is private to package "PUBLIC"."PG_TEST"
        (335545335,)

        Checked sec_type='definer'
        SRC : t_priv
        ID : 1001
        F01 : 1001
        U_NAME : SYSDBA
        U_ROLE : NONE
        SRC : t_pub
        ID : 1
        F01 : 1
        U_NAME : SYSDBA
        U_ROLE : NONE
        SRC : t_priv
        ID : 1001
        F01 : 1001
        U_NAME : TMP_PG_TABS_JOHN
        U_ROLE : TMP_PG_TABS_ROLE
        SRC : t_pub
        ID : 1
        F01 : 1
        U_NAME : TMP_PG_TABS_JOHN
        U_ROLE : TMP_PG_TABS_ROLE

        T_PUB_CNT : 1
        Table "T_PRIV" is private to package "PUBLIC"."PG_TEST"
        (335545335,)
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
