#coding:utf-8

"""
ID:          issue-5864
ISSUE:       5864
TITLE:       Error "block size exceeds implementation restriction" while inner joining large datasets with a long key using the HASH JOIN plan
DESCRIPTION:
  Hash join have to operate with keys of total length >= 1 Gb if we want to reproduce runtime error
  "Statement failed, SQLSTATE = HY001 / unable to allocate memory from operating system"
  If test table that serves as the source for HJ has record length about 65 Kb than not less than 16K records must be added there.
  If we use charset UTF8 than record length in bytes will be 8 times of declared field_len, so we declare field with len = 8191 charactyer
  (and this is current implementation limit).
  Than we add into this table >= 16Kb rows of unicode (NON-ascii!) characters.
  Finally, we launch query against this table and this query will use hash join because of missed indices.
  We have to check that NO errors occured during this query.

  Discuss with dimitr: letters 08-jan-2018 .. 06-feb-2018.
JIRA:        CORE-5598
"""

import pytest
from firebird.qa import *

substitutions = [('[ \t]+', ' '), ('.*RECORD LENGTH:[ \t]+[\\d]+[ \t]*\\)', ''),
                 ('.*COUNT[ \t]+[\\d]+', ''), ('(?m)DATABASE:.*\\n?', '')]

db = db_factory(charset='UTF8')

act = python_act('db', substitutions=substitutions)

expected_stdout = """
    SELECT EXPRESSION
     -> AGGREGATE
     -> FILTER
     -> HASH JOIN (INNER)
     -> TABLE "TEST" AS "B" FULL SCAN
     -> RECORD BUFFER (RECORD LENGTH: 32793)
     -> TABLE "TEST" AS "A" FULL SCAN
    COUNT 17000
"""

MIN_RECS_TO_ADD = 17000

test_script = """
    set list on;
    --show version;
    set explain on;
    select count(*) from test a join test b using(id, s);
    set explain off;
    quit;
    select
         m.MON$STAT_ID
        ,m.MON$STAT_GROUP
        ,m.MON$MEMORY_USED
        ,m.MON$MEMORY_ALLOCATED
        ,m.MON$MAX_MEMORY_USED
        ,m.MON$MAX_MEMORY_ALLOCATED
    from mon$database d join mon$memory_usage m using (MON$STAT_ID);
"""

@pytest.mark.version('>=3.0.3')
def test_1(act: Action):
    with act.db.connect(charset='utf8') as con:
        con.execute_immediate('create table test(id int, s varchar(8191))')
        con.commit()
        c = con.cursor()
        c.execute(f"insert into test(id, s) select row_number()over(), lpad('', 8191, 'Алексей, Łukasz, Máté, François, Jørgen, Νικόλαος') from rdb$types,rdb$types rows {MIN_RECS_TO_ADD}")
        con.commit()
    #
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=test_script)
    act.stdout = act.stdout.upper()
    assert act.clean_stdout == act.clean_expected_stdout
