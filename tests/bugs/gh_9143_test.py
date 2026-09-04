#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9143
TITLE:       Cannot insert data into package table with fully qualified name
DESCRIPTION:
    Test verifies ability to run DML against public packaged table 'T_PUB' in case wheh
    appropriate package is created in different schemas ('public', 'custom' and '"dépôt"').
    Queries to that table should return data that have been just inserted in it.
    Datatype of column 'T_PUB.ID' differs depending on schema.
NOTES:
    [04.09.2026] pzotov
    Confirmed bug on 6.0.0.2164-2d371e2
    Checked on 6.0.0.2169-6a5c761.
"""

import pytest
from firebird.qa import *

db = db_factory(charset = 'utf8')

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6')
def test_1(act: Action, capsys):
    
    schemas_map = {
        'public'  :  ('int',         '1', '2')
        ,'custom'  : ('boolean',     'false', 'true')
        ,'"dépôt"' : ('varchar(10)', "q'#bâtiment#'", "q'#étagère#'")
    }

    test_sql_lst = [ 'set autoterm on;', 'set list on;' ]
    with act.db.connect() as con:
        cur = con.cursor()
        for k, v in schemas_map.items():
            s_name = k
            d_type = v[0]
            d_pair = v[1:3]

            create_schema_sttm = '' if s_name.upper() == 'PUBLIC'.upper() else f'create schema {s_name};'
            schema_search_path = '' if s_name.upper() == 'PUBLIC'.upper() else f'set search_path to {s_name};'
            test_sql_lst.append(
                f"""
                {create_schema_sttm}
                {schema_search_path}
                create package pg_test as
                begin
                    temporary table t_pub(id {d_type}) on commit preserve rows index t_pub_id (id);
                end;

                insert into pg_test.t_pub values ({d_pair[0]});
                insert into {s_name}.pg_test.t_pub values ({d_pair[1]});

                select * from pg_test.t_pub;
                select * from {s_name}.pg_test.t_pub;
                """,
            )

    act.expected_stdout = """
        ID 1
        ID 2
        ID 1
        ID 2
        
        ID <false>
        ID <true>
        ID <false>
        ID <true>
        
        ID bâtiment
        ID étagère
        ID bâtiment
        ID étagère
    """
    act.isql(switches = ['-q'], input = '\n'.join(test_sql_lst), combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
