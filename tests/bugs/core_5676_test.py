#coding:utf-8

"""
ID:          issue-5942
ISSUE:       5942
TITLE:       Consider equivalence classes for index navigation
DESCRIPTION:
JIRA:        CORE-5676
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table document(id int primary key using index pk_document);
    recreate table doc_ip_doc(id int primary key using index pk_doc_ip_doc, name varchar(100));

    insert into document (id) select row_number() over() from rdb$types,(select 1 i from rdb$types rows 10);
    insert into doc_ip_doc (id) select row_number() over() from rdb$types;
    commit;

    set planonly;

    select document.id, doc_ip_doc.name
    from doc_ip_doc
    join document on document.id=doc_ip_doc.id
    order by doc_ip_doc.id;
    --PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))

    select document.id, doc_ip_doc.name
    from doc_ip_doc
    join document on document.id=doc_ip_doc.id
    order by document.id;
    -- OLD: PLAN SORT (JOIN (DOC_IP_DOC NATURAL, DOCUMENT INDEX (PK_DOCUMENT)))

    select doc_ip_doc.id, doc_ip_doc.name
    from doc_ip_doc
    join document on document.id=doc_ip_doc.id
    order by id;
    --PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))

    select document.id, doc_ip_doc.name
    from doc_ip_doc
    join document on document.id=doc_ip_doc.id
    order by id;
    -- OLD: PLAN SORT (JOIN (DOC_IP_DOC NATURAL, DOCUMENT INDEX (PK_DOCUMENT)))
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
"""

@pytest.mark.version('>=3.0.3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

