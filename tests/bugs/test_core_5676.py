#coding:utf-8
#
# id:           bugs.core_5676
# title:        Consider equivalence classes for index navigation
# decription:   
#                   Confirmed inefficiense on:
#                       3.0.3.32837
#                       4.0.0.800
#                   Checked on:
#                       3.0.3.32852: OK, 1.250s.
#                       4.0.0.830: OK, 1.375s.
#                
# tracker_id:   CORE-5676
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
    PLAN JOIN (DOC_IP_DOC ORDER PK_DOC_IP_DOC, DOCUMENT INDEX (PK_DOCUMENT))
  """

@pytest.mark.version('>=3.0.3')
def test_core_5676_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

