#coding:utf-8
#
# id:           bugs.core_6044
# title:        ISQL issues with increased identifier length
# decription:   
#                   Confirmed problem on WI-T4.0.0.1421: FB crashed when we create sequence 
#               	with name = 63 on-ascii characters and then ask it using 'show sequ' command.
#               	Also, FB crashe when we created a table with column which name contains 63 
#               	non-ascii characters and then this table metadata is queried by 'show table <T>' command.
#                   Checked on 4.0.0.1485: OK, 1.576s. 
#               	
#               	18.08.2020: added filter for 'current value: ...' of sequence. FB 4.x became incompatible
#               	with previous versions since 06-aug-2020.
#                   See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d
#               	
#                
# tracker_id:   CORE-6044
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('current value.*', 'current value')]

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
	set bail on;
	create  exception "ИсключениеДляСообщенияПользователюОНевозможностиПреобразованияя" 'Ваша строка не может быть преобразована в число.';
	create collation  "КоллацияДляСортировкиСтроковыхДанныхКоторыеПредставимыКакЧислаа" for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
	create domain     "ДоменДляХраненияСтроковыхДанныхКоторыеПредставимыДляСортировкии" as varchar(160) character set utf8 collate "КоллацияДляСортировкиСтроковыхДанныхКоторыеПредставимыКакЧислаа";
	create sequence   "ГенераторКоторыйДолженСодержатьНомераПоследнихУдаленнДокументов";
	create table      "ТаблицаКотораяВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю"(
					  "СтолбецКоторыйВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю"
					  "ДоменДляХраненияСтроковыхДанныхКоторыеПредставимыДляСортировкии"
					  ,constraint 
					  "ПервичныйКлючНаТаблицуКотораяВсегдаДолжнаСодержатьСвежайшуюИнфу"
					  primary key
					 ("СтолбецКоторыйВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю")
	);
	set bail off;

	show domain;    -- this passed OK
	show exception; -- this passed OK
	show collation; -- this passed OK
	show table;     -- this passed OK
	show sequ;      -- this led to crash
	show table "ТаблицаКотораяВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю"; -- this also led to crash
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	ДоменДляХраненияСтроковыхДанныхКоторыеПредставимыДляСортировкии
	ИсключениеДляСообщенияПользователюОНевозможностиПреобразованияя; Msg: Ваша строка не может быть преобразована в число.
	КоллацияДляСортировкиСтроковыхДанныхКоторыеПредставимыКакЧислаа, CHARACTER SET UTF8, FROM EXTERNAL ('UNICODE'), PAD SPACE, CASE INSENSITIVE, 'COLL-VERSION=153.88;NUMERIC-SORT=1'
	ТаблицаКотораяВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю
	Generator ГенераторКоторыйДолженСодержатьНомераПоследнихУдаленнДокументов, current value: 0, initial value: 0, increment: 1
	СтолбецКоторыйВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю (ДоменДляХраненияСтроковыхДанныхКоторыеПредставимыДляСортировкии) VARCHAR(160) CHARACTER SET UTF8 Not Null
	COLLATE КоллацияДляСортировкиСтроковыхДанныхКоторыеПредставимыКакЧислаа
	CONSTRAINT ПервичныйКлючНаТаблицуКотораяВсегдаДолжнаСодержатьСвежайшуюИнфу:
	Primary key (СтолбецКоторыйВсегдаДолжнаСодержатьТолькоСамуюСвежуюИнформациюю)
  """

@pytest.mark.version('>=4.0')
def test_core_6044_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

