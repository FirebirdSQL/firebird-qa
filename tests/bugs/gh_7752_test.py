#coding:utf-8

"""
ID:          issue-7752
ISSUE:       7752
TITLE:       The access path information is truncated to 255 characters in the PLG$PROF_RECORD_SOURCES table
NOTES:
    [02.10.2023] pzotov
    Confirmed problem (truncating of profiler data) on 5.0.0.1219, date of build: 17-sep-2023.
    Checked on 5.0.0.1235, 6.0.0.65 -- all fine.
"""

import os
import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

test_sql = """
    select count(*)
    from (
        select 1 i from
        rdb$relations r
        where 
          (r.rdb$relation_name = 'RDB$RELATIONS') OR
          (r.rdb$relation_name = 'RDB$DATABASE') OR
          (r.rdb$relation_name = 'RDB$COLLATIONS') OR
          (r.rdb$relation_name = 'RDB$CONFIG') OR
          (r.rdb$relation_name = 'RDB$EXCEPTIONS') OR
          (r.rdb$relation_name = 'RDB$FIELDS') OR
          (r.rdb$relation_name = 'RDB$FUNCTIONS') OR
          (r.rdb$relation_name = 'RDB$PROCEDURES')
          rows 1
    )
"""

profiler_sql = """
    select p.access_path
    from  plg$prof_record_sources p
    order by p.record_source_id desc rows 1
"""

expected_stdout = """
    -> Table "RDB$RELATIONS" as "R" Access By ID
    ....-> Bitmap Or
    ........-> Bitmap Or
    ............-> Bitmap Or
    ................-> Bitmap Or
    ....................-> Bitmap Or
    ........................-> Bitmap Or
    ............................-> Bitmap Or
    ................................-> Bitmap
    ....................................-> Index "RDB$INDEX_0" Unique Scan
    ................................-> Bitmap
    ....................................-> Index "RDB$INDEX_0" Unique Scan
    ............................-> Bitmap
    ................................-> Index "RDB$INDEX_0" Unique Scan
    ........................-> Bitmap
    ............................-> Index "RDB$INDEX_0" Unique Scan
    ....................-> Bitmap
    ........................-> Index "RDB$INDEX_0" Unique Scan
    ................-> Bitmap
    ....................-> Index "RDB$INDEX_0" Unique Scan
    ............-> Bitmap
    ................-> Index "RDB$INDEX_0" Unique Scan
    ........-> Bitmap
    ............-> Index "RDB$INDEX_0" Unique Scan
"""

#---------------------------------------------------------

def replace_leading(source, char="#"):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#---------------------------------------------------------

@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):
    
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute("select rdb$profiler.start_session('profile session 1') from rdb$database")
        for r in cur:
            pass

        cur.execute(test_sql)
        cur.callproc('rdb$profiler.finish_session', (True,))
        con.commit()

        cur.execute(profiler_sql)
        for r in cur:
            print( '\n'.join([replace_leading(s, char='.') for s in r[0].split('\n')])  )

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
