#coding:utf-8
#
# id:           bugs.core_1373
# title:        Incorrect result of recursive CTE query when recursive member's SELECT list contains expression using self-referenced fields
# decription:   
# tracker_id:   CORE-1373
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1373

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """RECREATE TABLE Phases
(Id INT NOT NULL PRIMARY KEY, ParentPhaseId INT);

CREATE GENERATOR GenPhases;
COMMIT;

INSERT INTO Phases VALUES(491, NULL);
INSERT INTO Phases VALUES(494, 491);
INSERT INTO Phases VALUES(495, 491);
INSERT INTO Phases VALUES(497, 494);
INSERT INTO Phases VALUES(498, NULL);

-- below i want to renumber Phases table and keep parent-child relation
SET GENERATOR GenPhases to 0;
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """WITH RECURSIVE
  Tree (OldPhaseId, OldParentPhaseId, NewPhaseId, NewParentPhaseId) AS
  (
    SELECT P.Id, P.ParentPhaseId, GEN_ID(GenPhases, 1), CAST(NULL AS INTEGER)
      FROM Phases P
     WHERE P.ParentPhaseId IS NULL

    UNION ALL

    SELECT P.Id, P.ParentPhaseId, GEN_ID(GenPhases, 1), T.NewPhaseId
      FROM Phases P, Tree T
     WHERE P.ParentPhaseId = T.OldPhaseId
  )
SELECT * FROM Tree;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  OLDPHASEID OLDPARENTPHASEID            NEWPHASEID NEWPARENTPHASEID
============ ================ ===================== ================
         491           <null>                     1           <null>
         494              491                     2                1
         497              494                     3                2
         495              491                     4                1
         498           <null>                     5           <null>

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

