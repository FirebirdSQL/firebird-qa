#coding:utf-8

"""
ID:          issue-1362
ISSUE:       1362
TITLE:       GSTAT does not work using the localhost connection string
DESCRIPTION:
JIRA:        CORE-959
FBTEST:      bugs.core_0959
"""

import pytest
from firebird.qa import *
import re

init_script = """
      create sequence g;
      create table test(id int primary key using index test_id_pk);
      commit;
      insert into test(id) select gen_id(g,1) from rdb$types,rdb$types rows 1000;
      commit;
"""

db = db_factory(init=init_script)

substitutions = [('Database ".*', 'Database'),
                 ('Gstat execution time .*', 'Gstat execution time'),
                 ('Attributes .*', 'Attributes'),
                 ('Primary pointer page: \\d+, Index root page: \\d+\\s*', 'Primary pointer page, Index root page'),
                 ('Data pages: \\d+, average fill: \\d+[percent_sign]', 'Data pages, average fill'),
                 ('Root page: \\d+, depth: \\d+, leaf buckets: \\d+, nodes: \\d+\\s*', 'Root page, depth, leaf buckets, nodes'),
                 ('Gstat completion time .*', 'Gstat completion time')]

act = python_act('db', substitutions=substitutions)

expected_stdout = """
    Database "C:\\MIX\\FIREBIRD\\QA\\FBT-REPO\\TMP\\BUGS.CORE_0959.FDB"
    Gstat execution time Fri Nov 17 12:37:29 2017
    Attributes force write
    Primary pointer page: 193, Index root page: 194
    Data pages: 7, average fill: 45[percent_sign]
    Root page: 197, depth: 1, leaf buckets: 1, nodes: 1000
    Gstat completion time Fri Nov 17 12:37:29 2017
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    hdr_dbname_ptn = re.compile('Database\\s+"', re.IGNORECASE)
    hdr_dbattr_ptn = re.compile('Attributes\\s+\\.*', re.IGNORECASE)
    table_ppip_ptn = re.compile('Primary\\s+pointer\\s+page:\\s+\\d+,\\s+Index root page:\\s+\\d+\\s*', re.IGNORECASE)
    table_dpaf_ptn = re.compile('Data\\s+pages:\\s+\\d+,\\s+average\\s+fill:\\s+\\d+%\\s*', re.IGNORECASE)
    index_root_ptn = re.compile('Root\\s+page:\\s+\\d+,\\s+depth:\\s+\\d+,\\s+leaf\\s+buckets:\\s+\\d+,\\s+nodes:\\s+\\d+\\s*', re.IGNORECASE)
    #
    gstat_init_ptn = re.compile('Gstat\\s+execution\\s+time\\s+', re.IGNORECASE)
    gstat_fini_ptn = re.compile('Gstat\\s+completion\\s+time\\s+', re.IGNORECASE)
    #
    watched_ptn_list = [hdr_dbname_ptn, hdr_dbattr_ptn, table_ppip_ptn, table_dpaf_ptn,
                        index_root_ptn, gstat_init_ptn, gstat_fini_ptn]
    #
    act.expected_stdout = expected_stdout
    act.gstat(switches=['-d', '-i', '-r'])
    #
    matched = []
    for line in act.stdout.splitlines():
        for p in watched_ptn_list:
            if p.search(line):
                matched.append(' '.join(line.replace('%','[percent_sign]').split()))
    #
    actual = '\n'.join(matched)
    actual = act.string_strip(actual, act.substitutions)
    assert ('localhost' in act.db.dsn and act.clean_expected_stdout == actual)


