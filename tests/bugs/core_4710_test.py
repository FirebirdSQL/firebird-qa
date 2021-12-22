#coding:utf-8
#
# id:           bugs.core_4710
# title:        invalid request BLR at offset 361 context already in use (BLR error)
# decription:   
# tracker_id:   CORE-4710
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select
        (select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        --,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1) /* #2 */
        --,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1) /* #1 */
    from
    rdb$database;
    
    select
        (select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1) /* #2 */
        --,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1) /* #1 */
    from
    rdb$database;
    
    
    select
        (select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1)
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1) /* #2 */
        ,(select row_number() over() from rdb$database r full join rdb$database r2 on r2.rdb$relation_id=r.rdb$relation_id group by r.rdb$relation_id having count(*)>0 order by r.rdb$relation_id rows 1 to 1) /* #1 */
    from
    rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN SORT (SORT (JOIN (JOIN (R2 NATURAL, R NATURAL), JOIN (R NATURAL, R2 NATURAL))))
    PLAN (RDB$DATABASE NATURAL)
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 54001
    Dynamic SQL Error
    -Too many Contexts of Relation/Procedure/Views. Maximum allowed is 256
    
    Statement failed, SQLSTATE = 54001
    Dynamic SQL Error
    -Too many Contexts of Relation/Procedure/Views. Maximum allowed is 256
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

