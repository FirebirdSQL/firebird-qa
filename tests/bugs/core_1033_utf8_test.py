#coding:utf-8

"""
ID:          issue-1450
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/1450
TITLE:       LIKE doesn't work for computed values (at least in a view)
DESCRIPTION:
JIRA:        CORE-1033
NOTES:
    [29.09.2025] pzotov
    Refactored: show SQLDA, changed table output to the list, added substitutions.
    ::: NB ::: Column 'v_test.part_descr' which is evaluated as
    "x.part_descr || ' (' || x.part_id || ')'" has diff len in SQLDA in FB versions
    prior/since 6.x: 224 vs 236.

    Checked on 6.0.0.1280; 5.0.4.1715; 4.0.7.3235; 3.0.14.33826.
"""
import sys
import time
import locale
from pathlib import Path
import pytest
from firebird.qa import *

#sys.stdout.reconfigure(encoding='utf-8')

db = db_factory(charset = 'utf8')

tmp_sql = temp_file('tmp_core_1033_utf8.sql')
tmp_log = temp_file('tmp_core_1033_utf8.log')

substitutions = [ ('^((?!(SQLSTATE|sqltype|PART_ID|PART_DESCR|Records)).)*$', ''), ('[ \t]+', ' '), ('charset:.*', '') ]

act = python_act('db', substitutions = substitutions, )

@pytest.mark.version('>=3')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path):

    test_script = """
        create table test (
           part_id smallint primary key
          ,part_descr varchar(50)
        );

        create view v_test (part_id, part_descr) as
        select
            part_id
           ,x.part_descr || ' (' || x.part_id || ')'
        from test as x
        ;
        commit;

        insert into test(part_id, part_descr) values (1,'æýþ');
        insert into test(part_id, part_descr) values (2,'æýþxýþ');
        insert into test(part_id, part_descr) values (3,'æýþ012');
        insert into test(part_id, part_descr) values (4,'æ%þxýþ'); -- pattern character '%' presents in data
        insert into test(part_id, part_descr) values (5,'æýþ_ýþ'); -- pattern character '_' presents in data

        set list on;
        set count on;
        set sqlda_display on;
        set planonly;
        select * from v_test;
        set planonly;
        set sqlda_display off;
        
        select * from v_test where part_descr like 'æýþ (1)' ;
        select * from v_test where part_descr like 'æýþ (%)' ;
        select * from v_test where part_descr like 'æýþ%' ;
        select * from v_test where part_descr like 'æ#%þ%(%' escape '#' ;
        select * from v_test where part_descr like 'æ_þ#_ýþ%(_%' escape '#' ;

    """
    tmp_sql.write_text(test_script, encoding='utf8')

    expected_stdout_5x = """
        01: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
        : name: PART_ID alias: PART_ID
        02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 224
        : name: PART_DESCR alias: PART_DESCR
        PART_ID 1
        PART_DESCR æýþ (1)
        Records affected: 1
        PART_ID 1
        PART_DESCR æýþ (1)
        Records affected: 1
        PART_ID 1
        PART_DESCR æýþ (1)
        PART_ID 2
        PART_DESCR æýþxýþ (2)
        PART_ID 3
        PART_DESCR æýþ012 (3)
        PART_ID 5
        PART_DESCR æýþ_ýþ (5)
        Records affected: 4
        PART_ID 4
        PART_DESCR æ%þxýþ (4)
        Records affected: 1
        PART_ID 5
        PART_DESCR æýþ_ýþ (5)
        Records affected: 1
    """

    expected_stdout_6x = """
        01: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
        : name: PART_ID alias: PART_ID
        02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 236
        : name: PART_DESCR alias: PART_DESCR
        PART_ID 1
        PART_DESCR æýþ (1)
        Records affected: 1

        PART_ID 1
        PART_DESCR æýþ (1)
        Records affected: 1

        PART_ID 1
        PART_DESCR æýþ (1)
        PART_ID 2
        PART_DESCR æýþxýþ (2)
        PART_ID 3
        PART_DESCR æýþ012 (3)
        PART_ID 5
        PART_DESCR æýþ_ýþ (5)
        Records affected: 4

        PART_ID 4
        PART_DESCR æ%þxýþ (4)
        Records affected: 1

        PART_ID 5
        PART_DESCR æýþ_ýþ (5)
        Records affected: 1
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.isql(switches = ['-q'], charset = 'utf8', input_file = tmp_sql, combine_output = True, io_enc = 'utf-8' )
    #tmp_log.write_text(act.clean_stdout, encoding='utf8')
    assert act.clean_stdout == act.clean_expected_stdout
