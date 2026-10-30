# agg_resulting_datatype

QA tests for `doc/sql.extensions/README.data_type_results_of_aggregations.txt`
("result data type of the result of an aggregation over values of compatible data
types, such as case expressions and columns at the same position in a union query
expression", Arno Brinkman).

The old README is extended here with the cases it does not cover:

1. types introduced after the document was written: **INT128, DECFLOAT(16/34),
   BOOLEAN, TIME WITH TIME ZONE, TIMESTAMP WITH TIME ZONE**;
2. **non-ascii strings that belong to different character sets** (win1251, koi8r,
   utf8, unicode_fss, iso8859_1, octets, none) - the README only says "the character
   set and collation are used from the first character string data type in DTS";
3. the special **SQL_NULL type** (langref 3.9.1) and untyped NULL literals, and how
   they are merged with non-null values.

## How to run

`firebird.qa` must be importable (on this machine it is installed in editable mode
from `C:\FBTESTING\qa\firebird-qa`). Typical launch:

    pytest C:\FBTESTING\qa\zcode\probe01\agg_resulting_datatype -vv ^
        --driver-config C:\FBTESTING\qa\firebird-qa\FBDRV-IMAGE_PC1.conf ^
        --server 60ss

Checked on WI-T6.0.0.2424 (60ss), WI-V5.0.5.1906 (50ss), WI-V4.0.8.3328 (40ss).
Behaviour is identical on all three; the only difference is that FB 6.x prepends
`SYSTEM.` to charset names in `set sqlda_display on` output, which is stripped by a
substitution.

Note: `@pytest.mark.intl` is registered by the firebird-qa repo's own pytest.ini;
when these tests are run from this standalone folder pytest emits a harmless
`PytestUnknownMarkWarning` for it.

## Technique

* Most tests use isql `set sqlda_display on` with `rows 0` (no data transfer): the
  XSQLVAR descriptor shows sqltype, scale, subtype, length and charset of the merged
  type. Substitutions keep only descriptor and error lines.
* `charset_collation_merging_test.py` persists aggregation results into VIEWs and
  dumps `RDB$FIELDS` (charset id, collation id, storage type, precision, scale) -
  the only way to check collation and precision of the result.

## Files

| file | covers |
|------|--------|
| `char_types_merging_test.py` | README 3a: fixed/variable merging, max length, charset resolution (first / NONE loses / OCTETS wins), non-ascii charsets, transliteration; numeric-vs-string |
| `charset_collation_merging_test.py` | collation from the FIRST member (persisted in RDB$FIELDS), NONE/OCTETS precedence, blob charset, numeric storage precision/scale |
| `exact_numeric_merging_test.py` | README 3b: smallint..int128 chain, scales, numeric/decimal storage subtypes, hex literals, DECODE |
| `approximate_decfloat_merging_test.py` | README 3c: FLOAT/DOUBLE mixing; DECFLOAT(16/34) vs everything |
| `datetime_merging_test.py` | README 3d: date/time/timestamp, WITH TIME ZONE dominance, not-comparable errors |
| `boolean_merging_test.py` | BOOLEAN: +boolean, +null, +numeric (error), +string |
| `blob_merging_test.py` | README 3e: subtypes, text blob charsets, blob vs non-blob |
| `sql_null_merging_test.py` | NULL literal and SQL_NULL (32766): merging with every type, `? IS NULL`, driver-level semantics |
| `list_aggregate_merging_test.py` | LIST() over all types (blob sub_type text, charset preserved); MIN/MAX keep argument type |
| `mixing_numeric_types_test.py` | full matrix: 1184 combinations of 3 pairwise-different numeric types (960 from the `is_exact` generator + 224 with max-scale `numeric(p,p)`/`decimal(p,p)` in the 1st record) x {union all, union distinct} = 2368 statements, boundary literals; expected types are built by an explicit merge model that was verified against the engine on every statement |

## UNION numeric matrix (mixing_numeric_types_test.py)

Combinations are produced by the `is_exact` cross-join generator (see test docstring):
records 1..3 have pairwise-different types, with at least one integer type
(smallint/int/bigint/int128) and at least one other; literals are close to the type
boundaries (pos 1 -> min, pos 2 -> max, pos 3 -> min). Additional matrix puts
`numeric(4,4) / decimal(4,4) / numeric(18,18) / numeric(38,38)` into the 1st record
with records 2-3 from the eight non-integer types.

Findings: none of the 2368 statements raises an error (neither at prepare nor at
execution), `union all` and `union distinct` always give the same resulting type,
and the result is exactly the left-to-right pairwise merge:

1. decfloat dominates any other numeric (decfloat(16) + bigint -> decfloat(16));
   decfloat(16) + decfloat(34) -> decfloat(34);
2. double beats float, float beats any exact numeric (bigint + float -> float, no
   widening to double);
3. all-exact: widest storage wins (short < long < int64 < int128), scale = max
   scale, subtype = decimal(2) if any member is decimal, else numeric(1) if any
   member is numeric/decimal, else 0.

## Deviations of the actual engine behaviour from the old README

Documented in the tests' expected output and docstrings (behaviour is the same on
4.0 / 5.0 / 6.0):

| # | README says | engine (4.0-6.0) does |
|---|-------------|----------------------|
| 1 | 3a-2 charset+collation from the FIRST char type | charset: FIRST only when it is not NONE; **NONE always loses**, **OCTETS always wins**; collation is taken from the first member and silently ignored if it belongs to another charset |
| 2 | 3a-1 length = max length in characters | true; sqlda shows it in BYTES of the result charset (utf8 x4) |
| 3 | 2 "All of the data types in DTS shall be comparable" | numeric **is** comparable with string: integer + varchar(5) -> varchar(11); boolean + varchar(5) -> varchar(5); BLOB dominates over any non-blob member |
| 4 | 3c "any approximate numeric: each data type shall be numeric, else error" | DECFLOAT + DOUBLE/FLOAT/exact-numeric -> that DECFLOAT (no error, no widening); BIGINT + FLOAT -> FLOAT (not double) |
| 5 | 3d datetime members must have "the same datetime type" | TIME + TIME WITH TIME ZONE -> TIME WITH TIME ZONE; TIMESTAMP + TIMESTAMP WITH TIME ZONE -> TIMESTAMP WITH TIME ZONE (no error); DATE can not be merged with any other datetime type (error) |
| 6 | 3e BLOB members "shall be ... all with the same sub-type" | blob sub_type 0 + sub_type 1 -> sub_type 0, no error |
| 7 | (nothing about NULL / SQL_NULL) | untyped NULL is merged as the "NULL literal" placeholder char(1) charset NONE; NULL + T -> T; `? IS NULL` param is typed SQL_NULL (32766) and ignores its value; `?` can not be merged in UNION output position (-804) but IS accepted in CASE/COALESCE |
