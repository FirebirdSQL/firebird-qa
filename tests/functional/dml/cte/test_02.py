#coding:utf-8

"""
ID:          dml.cte-02
TITLE:       Recursive CTEs
FBTEST:      functional.dml.cte.02
DESCRIPTION:
  Rules for Recursive CTEs
    A recursive CTE is self-referencing (has a reference to itself)
    A recursive CTE is a UNION of recursive and non-recursive members:
    At least one non-recursive member (anchor) must be present
    Non-recursive members are placed first in the UNION
    Recursive members are separated from anchor members and from one another with UNION ALL clauses, i.e.,
       non-recursive member (anchor)
        UNION [ALL | DISTINCT]
        non-recursive member (anchor)
        UNION [ALL | DISTINCT]
        non-recursive member (anchor)
        UNION ALL
        recursive member
        UNION ALL
        recursive member

    References between CTEs should not have loops
    Aggregates (DISTINCT, GROUP BY, HAVING) and aggregate functions (SUM, COUNT, MAX etc) are not allowed in recursive members
    A recursive member can have only one reference to itself and only in a FROM clause
    A recursive reference cannot participate in an outer join
"""

import pytest
from firebird.qa import *

init_script = """
    CREATE TABLE product( id_product INTEGER , name VARCHAR(20) ,id_type_product INTEGER,  PRIMARY KEY(id_product));
    CREATE TABLE type_product(id_type_product INTEGER, name VARCHAR(20),id_sub_type INTEGER);
    INSERT INTO type_product(id_type_product,name,id_sub_type) values(1,'DVD',NULL);
    INSERT INTO type_product(id_type_product,name,id_sub_type) values(2,'BOOK',NULL);
    INSERT INTO type_product(id_type_product,name,id_sub_type) values(3,'FILM SF',1);
    INSERT INTO type_product(id_type_product,name,id_sub_type) values(4,'FILM ACTION',1);
    INSERT INTO type_product(id_type_product,name,id_sub_type) values(5,'FILM ROMANCE',1);
    INSERT INTO product(id_product, name,id_type_product) VALUES (1,'Harry Potter 8',3  );
    INSERT INTO product(id_product, name,id_type_product) VALUES (2,'Total Recall',3  );
    INSERT INTO product(id_product, name,id_type_product) VALUES (3,'Kingdom of Heaven',3  );
    INSERT INTO product(id_product, name,id_type_product) VALUES (4,'Desperate Housewives',5  );
    INSERT INTO product(id_product, name,id_type_product) VALUES (5,'Reign over me',5  );
    INSERT INTO product(id_product, name,id_type_product) VALUES (6,'Prison Break',4  );
"""

db = db_factory(init=init_script)

test_script = """WITH RECURSIVE
TYPE_PRODUCT_RECUR (id_type_product,name,father) AS
(
SELECT id_type_product ,'+ ' || name as name  , id_type_product as father
FROM type_product
WHERE type_product.id_sub_type is null
UNION ALL
SELECT T.id_type_product ,' - ' || T.name , TR.id_type_product as father
FROM type_product T
JOIN TYPE_PRODUCT_RECUR TR on TR.id_type_product = T.id_sub_type
),
COUNT_BY_TYPE AS
(
SELECT P.ID_TYPE_PRODUCT,count(ID_PRODUCT) as count_p from PRODUCT P
group by P.ID_TYPE_PRODUCT
union
SELECT TP.FATHER,count(ID_PRODUCT) as count_p from
TYPE_PRODUCT_RECUR TP , PRODUCT P
where TP.ID_TYPE_PRODUCT = P.id_type_product
group by TP.FATHER
)
SELECT  T.id_type_product , T.name ,C.count_p
FROM TYPE_PRODUCT_RECUR T
left join  COUNT_BY_TYPE C
on C.ID_TYPE_PRODUCT = T.id_type_product;

"""

act = isql_act('db', test_script)

expected_stdout = """
ID_TYPE_PRODUCT NAME                                 COUNT_P
=============== ====================== =====================
              1 + DVD                                      6
              3  - FILM SF                                 3
              4  - FILM ACTION                             1
              5  - FILM ROMANCE                            2
              2 + BOOK                                <null>
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
