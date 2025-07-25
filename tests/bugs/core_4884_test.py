#coding:utf-8

"""
ID:          issue-5178
ISSUE:       5178
TITLE:       Crash on pasring of script containing `execute block` with lot of nested begin..end statements
DESCRIPTION:
NOTES:
  Batch file that generates .sql with arbitrary level of begin..end statements can be seen in the traker.
JIRA:        CORE-4884
FBTEST:      bugs.core_4884
NOTES:
    [30.06.2025] pzotov
    Added 'SQL_SCHEMA_PREFIX' to be substituted in expected_* on FB 6.x
    Checked on 6.0.0.876; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate exception ex_test 'Hi from Mariana Trench, depth=@1, time=@2';
    recreate sequence g;
    commit;
    set list on;
    set term ^;
    execute block as
    declare n int = 0;
    begin
    begin -- level = 1
    n = gen_id(g, 1);
    begin -- level = 2
    n = gen_id(g, 1);
    begin -- level = 3
    n = gen_id(g, 1);
    begin -- level = 4
    n = gen_id(g, 1);
    begin -- level = 5
    n = gen_id(g, 1);
    begin -- level = 6
    n = gen_id(g, 1);
    begin -- level = 7
    n = gen_id(g, 1);
    begin -- level = 8
    n = gen_id(g, 1);
    begin -- level = 9
    n = gen_id(g, 1);
    begin -- level = 10
    n = gen_id(g, 1);
    begin -- level = 11
    n = gen_id(g, 1);
    begin -- level = 12
    n = gen_id(g, 1);
    begin -- level = 13
    n = gen_id(g, 1);
    begin -- level = 14
    n = gen_id(g, 1);
    begin -- level = 15
    n = gen_id(g, 1);
    begin -- level = 16
    n = gen_id(g, 1);
    begin -- level = 17
    n = gen_id(g, 1);
    begin -- level = 18
    n = gen_id(g, 1);
    begin -- level = 19
    n = gen_id(g, 1);
    begin -- level = 20
    n = gen_id(g, 1);
    begin -- level = 21
    n = gen_id(g, 1);
    begin -- level = 22
    n = gen_id(g, 1);
    begin -- level = 23
    n = gen_id(g, 1);
    begin -- level = 24
    n = gen_id(g, 1);
    begin -- level = 25
    n = gen_id(g, 1);
    begin -- level = 26
    n = gen_id(g, 1);
    begin -- level = 27
    n = gen_id(g, 1);
    begin -- level = 28
    n = gen_id(g, 1);
    begin -- level = 29
    n = gen_id(g, 1);
    begin -- level = 30
    n = gen_id(g, 1);
    begin -- level = 31
    n = gen_id(g, 1);
    begin -- level = 32
    n = gen_id(g, 1);
    begin -- level = 33
    n = gen_id(g, 1);
    begin -- level = 34
    n = gen_id(g, 1);
    begin -- level = 35
    n = gen_id(g, 1);
    begin -- level = 36
    n = gen_id(g, 1);
    begin -- level = 37
    n = gen_id(g, 1);
    begin -- level = 38
    n = gen_id(g, 1);
    begin -- level = 39
    n = gen_id(g, 1);
    begin -- level = 40
    n = gen_id(g, 1);
    begin -- level = 41
    n = gen_id(g, 1);
    begin -- level = 42
    n = gen_id(g, 1);
    begin -- level = 43
    n = gen_id(g, 1);
    begin -- level = 44
    n = gen_id(g, 1);
    begin -- level = 45
    n = gen_id(g, 1);
    begin -- level = 46
    n = gen_id(g, 1);
    begin -- level = 47
    n = gen_id(g, 1);
    begin -- level = 48
    n = gen_id(g, 1);
    begin -- level = 49
    n = gen_id(g, 1);
    begin -- level = 50
    n = gen_id(g, 1);
    begin -- level = 51
    n = gen_id(g, 1);
    begin -- level = 52
    n = gen_id(g, 1);
    begin -- level = 53
    n = gen_id(g, 1);
    begin -- level = 54
    n = gen_id(g, 1);
    begin -- level = 55
    n = gen_id(g, 1);
    begin -- level = 56
    n = gen_id(g, 1);
    begin -- level = 57
    n = gen_id(g, 1);
    begin -- level = 58
    n = gen_id(g, 1);
    begin -- level = 59
    n = gen_id(g, 1);
    begin -- level = 60
    n = gen_id(g, 1);
    begin -- level = 61
    n = gen_id(g, 1);
    begin -- level = 62
    n = gen_id(g, 1);
    begin -- level = 63
    n = gen_id(g, 1);
    begin -- level = 64
    n = gen_id(g, 1);
    begin -- level = 65
    n = gen_id(g, 1);
    begin -- level = 66
    n = gen_id(g, 1);
    begin -- level = 67
    n = gen_id(g, 1);
    begin -- level = 68
    n = gen_id(g, 1);
    begin -- level = 69
    n = gen_id(g, 1);
    begin -- level = 70
    n = gen_id(g, 1);
    begin -- level = 71
    n = gen_id(g, 1);
    begin -- level = 72
    n = gen_id(g, 1);
    begin -- level = 73
    n = gen_id(g, 1);
    begin -- level = 74
    n = gen_id(g, 1);
    begin -- level = 75
    n = gen_id(g, 1);
    begin -- level = 76
    n = gen_id(g, 1);
    begin -- level = 77
    n = gen_id(g, 1);
    begin -- level = 78
    n = gen_id(g, 1);
    begin -- level = 79
    n = gen_id(g, 1);
    begin -- level = 80
    n = gen_id(g, 1);
    begin -- level = 81
    n = gen_id(g, 1);
    begin -- level = 82
    n = gen_id(g, 1);
    begin -- level = 83
    n = gen_id(g, 1);
    begin -- level = 84
    n = gen_id(g, 1);
    begin -- level = 85
    n = gen_id(g, 1);
    begin -- level = 86
    n = gen_id(g, 1);
    begin -- level = 87
    n = gen_id(g, 1);
    begin -- level = 88
    n = gen_id(g, 1);
    begin -- level = 89
    n = gen_id(g, 1);
    begin -- level = 90
    n = gen_id(g, 1);
    begin -- level = 91
    n = gen_id(g, 1);
    begin -- level = 92
    n = gen_id(g, 1);
    begin -- level = 93
    n = gen_id(g, 1);
    begin -- level = 94
    n = gen_id(g, 1);
    begin -- level = 95
    n = gen_id(g, 1);
    begin -- level = 96
    n = gen_id(g, 1);
    begin -- level = 97
    n = gen_id(g, 1);
    begin -- level = 98
    n = gen_id(g, 1);
    begin -- level = 99
    n = gen_id(g, 1);
    begin -- level = 100
    n = gen_id(g, 1);
    begin -- level = 101
    n = gen_id(g, 1);
    begin -- level = 102
    n = gen_id(g, 1);
    begin -- level = 103
    n = gen_id(g, 1);
    begin -- level = 104
    n = gen_id(g, 1);
    begin -- level = 105
    n = gen_id(g, 1);
    begin -- level = 106
    n = gen_id(g, 1);
    begin -- level = 107
    n = gen_id(g, 1);
    begin -- level = 108
    n = gen_id(g, 1);
    begin -- level = 109
    n = gen_id(g, 1);
    begin -- level = 110
    n = gen_id(g, 1);
    begin -- level = 111
    n = gen_id(g, 1);
    begin -- level = 112
    n = gen_id(g, 1);
    begin -- level = 113
    n = gen_id(g, 1);
    begin -- level = 114
    n = gen_id(g, 1);
    begin -- level = 115
    n = gen_id(g, 1);
    begin -- level = 116
    n = gen_id(g, 1);
    begin -- level = 117
    n = gen_id(g, 1);
    begin -- level = 118
    n = gen_id(g, 1);
    begin -- level = 119
    n = gen_id(g, 1);
    begin -- level = 120
    n = gen_id(g, 1);
    begin -- level = 121
    n = gen_id(g, 1);
    begin -- level = 122
    n = gen_id(g, 1);
    begin -- level = 123
    n = gen_id(g, 1);
    begin -- level = 124
    n = gen_id(g, 1);
    begin -- level = 125
    n = gen_id(g, 1);
    begin -- level = 126
    n = gen_id(g, 1);
    begin -- level = 127
    n = gen_id(g, 1);
    begin -- level = 128
    n = gen_id(g, 1);
    begin -- level = 129
    n = gen_id(g, 1);
    begin -- level = 130
    n = gen_id(g, 1);
    begin -- level = 131
    n = gen_id(g, 1);
    begin -- level = 132
    n = gen_id(g, 1);
    begin -- level = 133
    n = gen_id(g, 1);
    begin -- level = 134
    n = gen_id(g, 1);
    begin -- level = 135
    n = gen_id(g, 1);
    begin -- level = 136
    n = gen_id(g, 1);
    begin -- level = 137
    n = gen_id(g, 1);
    begin -- level = 138
    n = gen_id(g, 1);
    begin -- level = 139
    n = gen_id(g, 1);
    begin -- level = 140
    n = gen_id(g, 1);
    begin -- level = 141
    n = gen_id(g, 1);
    begin -- level = 142
    n = gen_id(g, 1);
    begin -- level = 143
    n = gen_id(g, 1);
    begin -- level = 144
    n = gen_id(g, 1);
    begin -- level = 145
    n = gen_id(g, 1);
    begin -- level = 146
    n = gen_id(g, 1);
    begin -- level = 147
    n = gen_id(g, 1);
    begin -- level = 148
    n = gen_id(g, 1);
    begin -- level = 149
    n = gen_id(g, 1);
    begin -- level = 150
    n = gen_id(g, 1);
    begin -- level = 151
    n = gen_id(g, 1);
    begin -- level = 152
    n = gen_id(g, 1);
    begin -- level = 153
    n = gen_id(g, 1);
    begin -- level = 154
    n = gen_id(g, 1);
    begin -- level = 155
    n = gen_id(g, 1);
    begin -- level = 156
    n = gen_id(g, 1);
    begin -- level = 157
    n = gen_id(g, 1);
    begin -- level = 158
    n = gen_id(g, 1);
    begin -- level = 159
    n = gen_id(g, 1);
    begin -- level = 160
    n = gen_id(g, 1);
    begin -- level = 161
    n = gen_id(g, 1);
    begin -- level = 162
    n = gen_id(g, 1);
    begin -- level = 163
    n = gen_id(g, 1);
    begin -- level = 164
    n = gen_id(g, 1);
    begin -- level = 165
    n = gen_id(g, 1);
    begin -- level = 166
    n = gen_id(g, 1);
    begin -- level = 167
    n = gen_id(g, 1);
    begin -- level = 168
    n = gen_id(g, 1);
    begin -- level = 169
    n = gen_id(g, 1);
    begin -- level = 170
    n = gen_id(g, 1);
    begin -- level = 171
    n = gen_id(g, 1);
    begin -- level = 172
    n = gen_id(g, 1);
    begin -- level = 173
    n = gen_id(g, 1);
    begin -- level = 174
    n = gen_id(g, 1);
    begin -- level = 175
    n = gen_id(g, 1);
    begin -- level = 176
    n = gen_id(g, 1);
    begin -- level = 177
    n = gen_id(g, 1);
    begin -- level = 178
    n = gen_id(g, 1);
    begin -- level = 179
    n = gen_id(g, 1);
    begin -- level = 180
    n = gen_id(g, 1);
    begin -- level = 181
    n = gen_id(g, 1);
    begin -- level = 182
    n = gen_id(g, 1);
    begin -- level = 183
    n = gen_id(g, 1);
    begin -- level = 184
    n = gen_id(g, 1);
    begin -- level = 185
    n = gen_id(g, 1);
    begin -- level = 186
    n = gen_id(g, 1);
    begin -- level = 187
    n = gen_id(g, 1);
    begin -- level = 188
    n = gen_id(g, 1);
    begin -- level = 189
    n = gen_id(g, 1);
    begin -- level = 190
    n = gen_id(g, 1);
    begin -- level = 191
    n = gen_id(g, 1);
    begin -- level = 192
    n = gen_id(g, 1);
    begin -- level = 193
    n = gen_id(g, 1);
    begin -- level = 194
    n = gen_id(g, 1);
    begin -- level = 195
    n = gen_id(g, 1);
    begin -- level = 196
    n = gen_id(g, 1);
    begin -- level = 197
    n = gen_id(g, 1);
    begin -- level = 198
    n = gen_id(g, 1);
    begin -- level = 199
    n = gen_id(g, 1);
    begin -- level = 200
    n = gen_id(g, 1);
    begin -- level = 201
    n = gen_id(g, 1);
    begin -- level = 202
    n = gen_id(g, 1);
    begin -- level = 203
    n = gen_id(g, 1);
    begin -- level = 204
    n = gen_id(g, 1);
    begin -- level = 205
    n = gen_id(g, 1);
    begin -- level = 206
    n = gen_id(g, 1);
    begin -- level = 207
    n = gen_id(g, 1);
    begin -- level = 208
    n = gen_id(g, 1);
    begin -- level = 209
    n = gen_id(g, 1);
    begin -- level = 210
    n = gen_id(g, 1);
    begin -- level = 211
    n = gen_id(g, 1);
    begin -- level = 212
    n = gen_id(g, 1);
    begin -- level = 213
    n = gen_id(g, 1);
    begin -- level = 214
    n = gen_id(g, 1);
    begin -- level = 215
    n = gen_id(g, 1);
    begin -- level = 216
    n = gen_id(g, 1);
    begin -- level = 217
    n = gen_id(g, 1);
    begin -- level = 218
    n = gen_id(g, 1);
    begin -- level = 219
    n = gen_id(g, 1);
    begin -- level = 220
    n = gen_id(g, 1);
    begin -- level = 221
    n = gen_id(g, 1);
    begin -- level = 222
    n = gen_id(g, 1);
    begin -- level = 223
    n = gen_id(g, 1);
    begin -- level = 224
    n = gen_id(g, 1);
    begin -- level = 225
    n = gen_id(g, 1);
    begin -- level = 226
    n = gen_id(g, 1);
    begin -- level = 227
    n = gen_id(g, 1);
    begin -- level = 228
    n = gen_id(g, 1);
    begin -- level = 229
    n = gen_id(g, 1);
    begin -- level = 230
    n = gen_id(g, 1);
    begin -- level = 231
    n = gen_id(g, 1);
    begin -- level = 232
    n = gen_id(g, 1);
    begin -- level = 233
    n = gen_id(g, 1);
    begin -- level = 234
    n = gen_id(g, 1);
    begin -- level = 235
    n = gen_id(g, 1);
    begin -- level = 236
    n = gen_id(g, 1);
    begin -- level = 237
    n = gen_id(g, 1);
    begin -- level = 238
    n = gen_id(g, 1);
    begin -- level = 239
    n = gen_id(g, 1);
    begin -- level = 240
    n = gen_id(g, 1);
    begin -- level = 241
    n = gen_id(g, 1);
    begin -- level = 242
    n = gen_id(g, 1);
    begin -- level = 243
    n = gen_id(g, 1);
    begin -- level = 244
    n = gen_id(g, 1);
    begin -- level = 245
    n = gen_id(g, 1);
    begin -- level = 246
    n = gen_id(g, 1);
    begin -- level = 247
    n = gen_id(g, 1);
    begin -- level = 248
    n = gen_id(g, 1);
    begin -- level = 249
    n = gen_id(g, 1);
    begin -- level = 250
    n = gen_id(g, 1);
    begin -- level = 251
    n = gen_id(g, 1);
    begin -- level = 252
    n = gen_id(g, 1);
    begin -- level = 253
    n = gen_id(g, 1);
    begin -- level = 254
    n = gen_id(g, 1);
    begin -- level = 255
    n = gen_id(g, 1);
    begin -- level = 256
    n = gen_id(g, 1);
    begin -- level = 257
    n = gen_id(g, 1);
    begin -- level = 258
    n = gen_id(g, 1);
    begin -- level = 259
    n = gen_id(g, 1);
    begin -- level = 260
    n = gen_id(g, 1);
    begin -- level = 261
    n = gen_id(g, 1);
    begin -- level = 262
    n = gen_id(g, 1);
    begin -- level = 263
    n = gen_id(g, 1);
    begin -- level = 264
    n = gen_id(g, 1);
    begin -- level = 265
    n = gen_id(g, 1);
    begin -- level = 266
    n = gen_id(g, 1);
    begin -- level = 267
    n = gen_id(g, 1);
    begin -- level = 268
    n = gen_id(g, 1);
    begin -- level = 269
    n = gen_id(g, 1);
    begin -- level = 270
    n = gen_id(g, 1);
    begin -- level = 271
    n = gen_id(g, 1);
    begin -- level = 272
    n = gen_id(g, 1);
    begin -- level = 273
    n = gen_id(g, 1);
    begin -- level = 274
    n = gen_id(g, 1);
    begin -- level = 275
    n = gen_id(g, 1);
    begin -- level = 276
    n = gen_id(g, 1);
    begin -- level = 277
    n = gen_id(g, 1);
    begin -- level = 278
    n = gen_id(g, 1);
    begin -- level = 279
    n = gen_id(g, 1);
    begin -- level = 280
    n = gen_id(g, 1);
    begin -- level = 281
    n = gen_id(g, 1);
    begin -- level = 282
    n = gen_id(g, 1);
    begin -- level = 283
    n = gen_id(g, 1);
    begin -- level = 284
    n = gen_id(g, 1);
    begin -- level = 285
    n = gen_id(g, 1);
    begin -- level = 286
    n = gen_id(g, 1);
    begin -- level = 287
    n = gen_id(g, 1);
    begin -- level = 288
    n = gen_id(g, 1);
    begin -- level = 289
    n = gen_id(g, 1);
    begin -- level = 290
    n = gen_id(g, 1);
    begin -- level = 291
    n = gen_id(g, 1);
    begin -- level = 292
    n = gen_id(g, 1);
    begin -- level = 293
    n = gen_id(g, 1);
    begin -- level = 294
    n = gen_id(g, 1);
    begin -- level = 295
    n = gen_id(g, 1);
    begin -- level = 296
    n = gen_id(g, 1);
    begin -- level = 297
    n = gen_id(g, 1);
    begin -- level = 298
    n = gen_id(g, 1);
    begin -- level = 299
    n = gen_id(g, 1);
    begin -- level = 300
    n = gen_id(g, 1);
    begin -- level = 301
    n = gen_id(g, 1);
    begin -- level = 302
    n = gen_id(g, 1);
    begin -- level = 303
    n = gen_id(g, 1);
    begin -- level = 304
    n = gen_id(g, 1);
    begin -- level = 305
    n = gen_id(g, 1);
    begin -- level = 306
    n = gen_id(g, 1);
    begin -- level = 307
    n = gen_id(g, 1);
    begin -- level = 308
    n = gen_id(g, 1);
    begin -- level = 309
    n = gen_id(g, 1);
    begin -- level = 310
    n = gen_id(g, 1);
    begin -- level = 311
    n = gen_id(g, 1);
    begin -- level = 312
    n = gen_id(g, 1);
    begin -- level = 313
    n = gen_id(g, 1);
    begin -- level = 314
    n = gen_id(g, 1);
    begin -- level = 315
    n = gen_id(g, 1);
    begin -- level = 316
    n = gen_id(g, 1);
    begin -- level = 317
    n = gen_id(g, 1);
    begin -- level = 318
    n = gen_id(g, 1);
    begin -- level = 319
    n = gen_id(g, 1);
    begin -- level = 320
    n = gen_id(g, 1);
    begin -- level = 321
    n = gen_id(g, 1);
    begin -- level = 322
    n = gen_id(g, 1);
    begin -- level = 323
    n = gen_id(g, 1);
    begin -- level = 324
    n = gen_id(g, 1);
    begin -- level = 325
    n = gen_id(g, 1);
    begin -- level = 326
    n = gen_id(g, 1);
    begin -- level = 327
    n = gen_id(g, 1);
    begin -- level = 328
    n = gen_id(g, 1);
    begin -- level = 329
    n = gen_id(g, 1);
    begin -- level = 330
    n = gen_id(g, 1);
    begin -- level = 331
    n = gen_id(g, 1);
    begin -- level = 332
    n = gen_id(g, 1);
    begin -- level = 333
    n = gen_id(g, 1);
    begin -- level = 334
    n = gen_id(g, 1);
    begin -- level = 335
    n = gen_id(g, 1);
    begin -- level = 336
    n = gen_id(g, 1);
    begin -- level = 337
    n = gen_id(g, 1);
    begin -- level = 338
    n = gen_id(g, 1);
    begin -- level = 339
    n = gen_id(g, 1);
    begin -- level = 340
    n = gen_id(g, 1);
    begin -- level = 341
    n = gen_id(g, 1);
    begin -- level = 342
    n = gen_id(g, 1);
    begin -- level = 343
    n = gen_id(g, 1);
    begin -- level = 344
    n = gen_id(g, 1);
    begin -- level = 345
    n = gen_id(g, 1);
    begin -- level = 346
    n = gen_id(g, 1);
    begin -- level = 347
    n = gen_id(g, 1);
    begin -- level = 348
    n = gen_id(g, 1);
    begin -- level = 349
    n = gen_id(g, 1);
    begin -- level = 350
    n = gen_id(g, 1);
    begin -- level = 351
    n = gen_id(g, 1);
    begin -- level = 352
    n = gen_id(g, 1);
    begin -- level = 353
    n = gen_id(g, 1);
    begin -- level = 354
    n = gen_id(g, 1);
    begin -- level = 355
    n = gen_id(g, 1);
    begin -- level = 356
    n = gen_id(g, 1);
    begin -- level = 357
    n = gen_id(g, 1);
    begin -- level = 358
    n = gen_id(g, 1);
    begin -- level = 359
    n = gen_id(g, 1);
    begin -- level = 360
    n = gen_id(g, 1);
    begin -- level = 361
    n = gen_id(g, 1);
    begin -- level = 362
    n = gen_id(g, 1);
    begin -- level = 363
    n = gen_id(g, 1);
    begin -- level = 364
    n = gen_id(g, 1);
    begin -- level = 365
    n = gen_id(g, 1);
    begin -- level = 366
    n = gen_id(g, 1);
    begin -- level = 367
    n = gen_id(g, 1);
    begin -- level = 368
    n = gen_id(g, 1);
    begin -- level = 369
    n = gen_id(g, 1);
    begin -- level = 370
    n = gen_id(g, 1);
    begin -- level = 371
    n = gen_id(g, 1);
    begin -- level = 372
    n = gen_id(g, 1);
    begin -- level = 373
    n = gen_id(g, 1);
    begin -- level = 374
    n = gen_id(g, 1);
    begin -- level = 375
    n = gen_id(g, 1);
    begin -- level = 376
    n = gen_id(g, 1);
    begin -- level = 377
    n = gen_id(g, 1);
    begin -- level = 378
    n = gen_id(g, 1);
    begin -- level = 379
    n = gen_id(g, 1);
    begin -- level = 380
    n = gen_id(g, 1);
    begin -- level = 381
    n = gen_id(g, 1);
    begin -- level = 382
    n = gen_id(g, 1);
    begin -- level = 383
    n = gen_id(g, 1);
    begin -- level = 384
    n = gen_id(g, 1);
    begin -- level = 385
    n = gen_id(g, 1);
    begin -- level = 386
    n = gen_id(g, 1);
    begin -- level = 387
    n = gen_id(g, 1);
    begin -- level = 388
    n = gen_id(g, 1);
    begin -- level = 389
    n = gen_id(g, 1);
    begin -- level = 390
    n = gen_id(g, 1);
    begin -- level = 391
    n = gen_id(g, 1);
    begin -- level = 392
    n = gen_id(g, 1);
    begin -- level = 393
    n = gen_id(g, 1);
    begin -- level = 394
    n = gen_id(g, 1);
    begin -- level = 395
    n = gen_id(g, 1);
    begin -- level = 396
    n = gen_id(g, 1);
    begin -- level = 397
    n = gen_id(g, 1);
    begin -- level = 398
    n = gen_id(g, 1);
    begin -- level = 399
    n = gen_id(g, 1);
    begin -- level = 400
    n = gen_id(g, 1);
    begin -- level = 401
    n = gen_id(g, 1);
    begin -- level = 402
    n = gen_id(g, 1);
    begin -- level = 403
    n = gen_id(g, 1);
    begin -- level = 404
    n = gen_id(g, 1);
    begin -- level = 405
    n = gen_id(g, 1);
    begin -- level = 406
    n = gen_id(g, 1);
    begin -- level = 407
    n = gen_id(g, 1);
    begin -- level = 408
    n = gen_id(g, 1);
    begin -- level = 409
    n = gen_id(g, 1);
    begin -- level = 410
    n = gen_id(g, 1);
    begin -- level = 411
    n = gen_id(g, 1);
    begin -- level = 412
    n = gen_id(g, 1);
    begin -- level = 413
    n = gen_id(g, 1);
    begin -- level = 414
    n = gen_id(g, 1);
    begin -- level = 415
    n = gen_id(g, 1);
    begin -- level = 416
    n = gen_id(g, 1);
    begin -- level = 417
    n = gen_id(g, 1);
    begin -- level = 418
    n = gen_id(g, 1);
    begin -- level = 419
    n = gen_id(g, 1);
    begin -- level = 420
    n = gen_id(g, 1);
    begin -- level = 421
    n = gen_id(g, 1);
    begin -- level = 422
    n = gen_id(g, 1);
    begin -- level = 423
    n = gen_id(g, 1);
    begin -- level = 424
    n = gen_id(g, 1);
    begin -- level = 425
    n = gen_id(g, 1);
    begin -- level = 426
    n = gen_id(g, 1);
    begin -- level = 427
    n = gen_id(g, 1);
    begin -- level = 428
    n = gen_id(g, 1);
    begin -- level = 429
    n = gen_id(g, 1);
    begin -- level = 430
    n = gen_id(g, 1);
    begin -- level = 431
    n = gen_id(g, 1);
    begin -- level = 432
    n = gen_id(g, 1);
    begin -- level = 433
    n = gen_id(g, 1);
    begin -- level = 434
    n = gen_id(g, 1);
    begin -- level = 435
    n = gen_id(g, 1);
    begin -- level = 436
    n = gen_id(g, 1);
    begin -- level = 437
    n = gen_id(g, 1);
    begin -- level = 438
    n = gen_id(g, 1);
    begin -- level = 439
    n = gen_id(g, 1);
    begin -- level = 440
    n = gen_id(g, 1);
    begin -- level = 441
    n = gen_id(g, 1);
    begin -- level = 442
    n = gen_id(g, 1);
    begin -- level = 443
    n = gen_id(g, 1);
    begin -- level = 444
    n = gen_id(g, 1);
    begin -- level = 445
    n = gen_id(g, 1);
    begin -- level = 446
    n = gen_id(g, 1);
    begin -- level = 447
    n = gen_id(g, 1);
    begin -- level = 448
    n = gen_id(g, 1);
    begin -- level = 449
    n = gen_id(g, 1);
    begin -- level = 450
    n = gen_id(g, 1);
    begin -- level = 451
    n = gen_id(g, 1);
    begin -- level = 452
    n = gen_id(g, 1);
    begin -- level = 453
    n = gen_id(g, 1);
    begin -- level = 454
    n = gen_id(g, 1);
    begin -- level = 455
    n = gen_id(g, 1);
    begin -- level = 456
    n = gen_id(g, 1);
    begin -- level = 457
    n = gen_id(g, 1);
    begin -- level = 458
    n = gen_id(g, 1);
    begin -- level = 459
    n = gen_id(g, 1);
    begin -- level = 460
    n = gen_id(g, 1);
    begin -- level = 461
    n = gen_id(g, 1);
    begin -- level = 462
    n = gen_id(g, 1);
    begin -- level = 463
    n = gen_id(g, 1);
    begin -- level = 464
    n = gen_id(g, 1);
    begin -- level = 465
    n = gen_id(g, 1);
    begin -- level = 466
    n = gen_id(g, 1);
    begin -- level = 467
    n = gen_id(g, 1);
    begin -- level = 468
    n = gen_id(g, 1);
    begin -- level = 469
    n = gen_id(g, 1);
    begin -- level = 470
    n = gen_id(g, 1);
    begin -- level = 471
    n = gen_id(g, 1);
    begin -- level = 472
    n = gen_id(g, 1);
    begin -- level = 473
    n = gen_id(g, 1);
    begin -- level = 474
    n = gen_id(g, 1);
    begin -- level = 475
    n = gen_id(g, 1);
    begin -- level = 476
    n = gen_id(g, 1);
    begin -- level = 477
    n = gen_id(g, 1);
    begin -- level = 478
    n = gen_id(g, 1);
    begin -- level = 479
    n = gen_id(g, 1);
    begin -- level = 480
    n = gen_id(g, 1);
    begin -- level = 481
    n = gen_id(g, 1);
    begin -- level = 482
    n = gen_id(g, 1);
    begin -- level = 483
    n = gen_id(g, 1);
    begin -- level = 484
    n = gen_id(g, 1);
    begin -- level = 485
    n = gen_id(g, 1);
    begin -- level = 486
    n = gen_id(g, 1);
    begin -- level = 487
    n = gen_id(g, 1);
    begin -- level = 488
    n = gen_id(g, 1);
    begin -- level = 489
    n = gen_id(g, 1);
    begin -- level = 490
    n = gen_id(g, 1);
    begin -- level = 491
    n = gen_id(g, 1);
    begin -- level = 492
    n = gen_id(g, 1);
    begin -- level = 493
    n = gen_id(g, 1);
    begin -- level = 494
    n = gen_id(g, 1);
    begin -- level = 495
    n = gen_id(g, 1);
    begin -- level = 496
    n = gen_id(g, 1);
    begin -- level = 497
    n = gen_id(g, 1);
    begin -- level = 498
    n = gen_id(g, 1);
    begin -- level = 499
    n = gen_id(g, 1);
    begin -- level = 500
    n = gen_id(g, 1);
    begin -- level = 501
    n = gen_id(g, 1);
    begin -- level = 502
    n = gen_id(g, 1);
    begin -- level = 503
    n = gen_id(g, 1);
    begin -- level = 504
    n = gen_id(g, 1);
    begin -- level = 505
    n = gen_id(g, 1);
    begin -- level = 506
    n = gen_id(g, 1);
    begin -- level = 507
    n = gen_id(g, 1);
    begin -- level = 508
    n = gen_id(g, 1);
    begin -- level = 509
    n = gen_id(g, 1);
    begin -- level = 510
    n = gen_id(g, 1);
    begin -- level = 511
    n = gen_id(g, 1);
    exception ex_test using( n, cast('now' as timestamp) );
    end -- level = 511
    end -- level = 510
    end -- level = 509
    end -- level = 508
    end -- level = 507
    end -- level = 506
    end -- level = 505
    end -- level = 504
    end -- level = 503
    end -- level = 502
    end -- level = 501
    end -- level = 500
    end -- level = 499
    end -- level = 498
    end -- level = 497
    end -- level = 496
    end -- level = 495
    end -- level = 494
    end -- level = 493
    end -- level = 492
    end -- level = 491
    end -- level = 490
    end -- level = 489
    end -- level = 488
    end -- level = 487
    end -- level = 486
    end -- level = 485
    end -- level = 484
    end -- level = 483
    end -- level = 482
    end -- level = 481
    end -- level = 480
    end -- level = 479
    end -- level = 478
    end -- level = 477
    end -- level = 476
    end -- level = 475
    end -- level = 474
    end -- level = 473
    end -- level = 472
    end -- level = 471
    end -- level = 470
    end -- level = 469
    end -- level = 468
    end -- level = 467
    end -- level = 466
    end -- level = 465
    end -- level = 464
    end -- level = 463
    end -- level = 462
    end -- level = 461
    end -- level = 460
    end -- level = 459
    end -- level = 458
    end -- level = 457
    end -- level = 456
    end -- level = 455
    end -- level = 454
    end -- level = 453
    end -- level = 452
    end -- level = 451
    end -- level = 450
    end -- level = 449
    end -- level = 448
    end -- level = 447
    end -- level = 446
    end -- level = 445
    end -- level = 444
    end -- level = 443
    end -- level = 442
    end -- level = 441
    end -- level = 440
    end -- level = 439
    end -- level = 438
    end -- level = 437
    end -- level = 436
    end -- level = 435
    end -- level = 434
    end -- level = 433
    end -- level = 432
    end -- level = 431
    end -- level = 430
    end -- level = 429
    end -- level = 428
    end -- level = 427
    end -- level = 426
    end -- level = 425
    end -- level = 424
    end -- level = 423
    end -- level = 422
    end -- level = 421
    end -- level = 420
    end -- level = 419
    end -- level = 418
    end -- level = 417
    end -- level = 416
    end -- level = 415
    end -- level = 414
    end -- level = 413
    end -- level = 412
    end -- level = 411
    end -- level = 410
    end -- level = 409
    end -- level = 408
    end -- level = 407
    end -- level = 406
    end -- level = 405
    end -- level = 404
    end -- level = 403
    end -- level = 402
    end -- level = 401
    end -- level = 400
    end -- level = 399
    end -- level = 398
    end -- level = 397
    end -- level = 396
    end -- level = 395
    end -- level = 394
    end -- level = 393
    end -- level = 392
    end -- level = 391
    end -- level = 390
    end -- level = 389
    end -- level = 388
    end -- level = 387
    end -- level = 386
    end -- level = 385
    end -- level = 384
    end -- level = 383
    end -- level = 382
    end -- level = 381
    end -- level = 380
    end -- level = 379
    end -- level = 378
    end -- level = 377
    end -- level = 376
    end -- level = 375
    end -- level = 374
    end -- level = 373
    end -- level = 372
    end -- level = 371
    end -- level = 370
    end -- level = 369
    end -- level = 368
    end -- level = 367
    end -- level = 366
    end -- level = 365
    end -- level = 364
    end -- level = 363
    end -- level = 362
    end -- level = 361
    end -- level = 360
    end -- level = 359
    end -- level = 358
    end -- level = 357
    end -- level = 356
    end -- level = 355
    end -- level = 354
    end -- level = 353
    end -- level = 352
    end -- level = 351
    end -- level = 350
    end -- level = 349
    end -- level = 348
    end -- level = 347
    end -- level = 346
    end -- level = 345
    end -- level = 344
    end -- level = 343
    end -- level = 342
    end -- level = 341
    end -- level = 340
    end -- level = 339
    end -- level = 338
    end -- level = 337
    end -- level = 336
    end -- level = 335
    end -- level = 334
    end -- level = 333
    end -- level = 332
    end -- level = 331
    end -- level = 330
    end -- level = 329
    end -- level = 328
    end -- level = 327
    end -- level = 326
    end -- level = 325
    end -- level = 324
    end -- level = 323
    end -- level = 322
    end -- level = 321
    end -- level = 320
    end -- level = 319
    end -- level = 318
    end -- level = 317
    end -- level = 316
    end -- level = 315
    end -- level = 314
    end -- level = 313
    end -- level = 312
    end -- level = 311
    end -- level = 310
    end -- level = 309
    end -- level = 308
    end -- level = 307
    end -- level = 306
    end -- level = 305
    end -- level = 304
    end -- level = 303
    end -- level = 302
    end -- level = 301
    end -- level = 300
    end -- level = 299
    end -- level = 298
    end -- level = 297
    end -- level = 296
    end -- level = 295
    end -- level = 294
    end -- level = 293
    end -- level = 292
    end -- level = 291
    end -- level = 290
    end -- level = 289
    end -- level = 288
    end -- level = 287
    end -- level = 286
    end -- level = 285
    end -- level = 284
    end -- level = 283
    end -- level = 282
    end -- level = 281
    end -- level = 280
    end -- level = 279
    end -- level = 278
    end -- level = 277
    end -- level = 276
    end -- level = 275
    end -- level = 274
    end -- level = 273
    end -- level = 272
    end -- level = 271
    end -- level = 270
    end -- level = 269
    end -- level = 268
    end -- level = 267
    end -- level = 266
    end -- level = 265
    end -- level = 264
    end -- level = 263
    end -- level = 262
    end -- level = 261
    end -- level = 260
    end -- level = 259
    end -- level = 258
    end -- level = 257
    end -- level = 256
    end -- level = 255
    end -- level = 254
    end -- level = 253
    end -- level = 252
    end -- level = 251
    end -- level = 250
    end -- level = 249
    end -- level = 248
    end -- level = 247
    end -- level = 246
    end -- level = 245
    end -- level = 244
    end -- level = 243
    end -- level = 242
    end -- level = 241
    end -- level = 240
    end -- level = 239
    end -- level = 238
    end -- level = 237
    end -- level = 236
    end -- level = 235
    end -- level = 234
    end -- level = 233
    end -- level = 232
    end -- level = 231
    end -- level = 230
    end -- level = 229
    end -- level = 228
    end -- level = 227
    end -- level = 226
    end -- level = 225
    end -- level = 224
    end -- level = 223
    end -- level = 222
    end -- level = 221
    end -- level = 220
    end -- level = 219
    end -- level = 218
    end -- level = 217
    end -- level = 216
    end -- level = 215
    end -- level = 214
    end -- level = 213
    end -- level = 212
    end -- level = 211
    end -- level = 210
    end -- level = 209
    end -- level = 208
    end -- level = 207
    end -- level = 206
    end -- level = 205
    end -- level = 204
    end -- level = 203
    end -- level = 202
    end -- level = 201
    end -- level = 200
    end -- level = 199
    end -- level = 198
    end -- level = 197
    end -- level = 196
    end -- level = 195
    end -- level = 194
    end -- level = 193
    end -- level = 192
    end -- level = 191
    end -- level = 190
    end -- level = 189
    end -- level = 188
    end -- level = 187
    end -- level = 186
    end -- level = 185
    end -- level = 184
    end -- level = 183
    end -- level = 182
    end -- level = 181
    end -- level = 180
    end -- level = 179
    end -- level = 178
    end -- level = 177
    end -- level = 176
    end -- level = 175
    end -- level = 174
    end -- level = 173
    end -- level = 172
    end -- level = 171
    end -- level = 170
    end -- level = 169
    end -- level = 168
    end -- level = 167
    end -- level = 166
    end -- level = 165
    end -- level = 164
    end -- level = 163
    end -- level = 162
    end -- level = 161
    end -- level = 160
    end -- level = 159
    end -- level = 158
    end -- level = 157
    end -- level = 156
    end -- level = 155
    end -- level = 154
    end -- level = 153
    end -- level = 152
    end -- level = 151
    end -- level = 150
    end -- level = 149
    end -- level = 148
    end -- level = 147
    end -- level = 146
    end -- level = 145
    end -- level = 144
    end -- level = 143
    end -- level = 142
    end -- level = 141
    end -- level = 140
    end -- level = 139
    end -- level = 138
    end -- level = 137
    end -- level = 136
    end -- level = 135
    end -- level = 134
    end -- level = 133
    end -- level = 132
    end -- level = 131
    end -- level = 130
    end -- level = 129
    end -- level = 128
    end -- level = 127
    end -- level = 126
    end -- level = 125
    end -- level = 124
    end -- level = 123
    end -- level = 122
    end -- level = 121
    end -- level = 120
    end -- level = 119
    end -- level = 118
    end -- level = 117
    end -- level = 116
    end -- level = 115
    end -- level = 114
    end -- level = 113
    end -- level = 112
    end -- level = 111
    end -- level = 110
    end -- level = 109
    end -- level = 108
    end -- level = 107
    end -- level = 106
    end -- level = 105
    end -- level = 104
    end -- level = 103
    end -- level = 102
    end -- level = 101
    end -- level = 100
    end -- level = 99
    end -- level = 98
    end -- level = 97
    end -- level = 96
    end -- level = 95
    end -- level = 94
    end -- level = 93
    end -- level = 92
    end -- level = 91
    end -- level = 90
    end -- level = 89
    end -- level = 88
    end -- level = 87
    end -- level = 86
    end -- level = 85
    end -- level = 84
    end -- level = 83
    end -- level = 82
    end -- level = 81
    end -- level = 80
    end -- level = 79
    end -- level = 78
    end -- level = 77
    end -- level = 76
    end -- level = 75
    end -- level = 74
    end -- level = 73
    end -- level = 72
    end -- level = 71
    end -- level = 70
    end -- level = 69
    end -- level = 68
    end -- level = 67
    end -- level = 66
    end -- level = 65
    end -- level = 64
    end -- level = 63
    end -- level = 62
    end -- level = 61
    end -- level = 60
    end -- level = 59
    end -- level = 58
    end -- level = 57
    end -- level = 56
    end -- level = 55
    end -- level = 54
    end -- level = 53
    end -- level = 52
    end -- level = 51
    end -- level = 50
    end -- level = 49
    end -- level = 48
    end -- level = 47
    end -- level = 46
    end -- level = 45
    end -- level = 44
    end -- level = 43
    end -- level = 42
    end -- level = 41
    end -- level = 40
    end -- level = 39
    end -- level = 38
    end -- level = 37
    end -- level = 36
    end -- level = 35
    end -- level = 34
    end -- level = 33
    end -- level = 32
    end -- level = 31
    end -- level = 30
    end -- level = 29
    end -- level = 28
    end -- level = 27
    end -- level = 26
    end -- level = 25
    end -- level = 24
    end -- level = 23
    end -- level = 22
    end -- level = 21
    end -- level = 20
    end -- level = 19
    end -- level = 18
    end -- level = 17
    end -- level = 16
    end -- level = 15
    end -- level = 14
    end -- level = 13
    end -- level = 12
    end -- level = 11
    end -- level = 10
    end -- level = 9
    end -- level = 8
    end -- level = 7
    end -- level = 6
    end -- level = 5
    end -- level = 4
    end -- level = 3
    end -- level = 2
    end -- level = 1
    end^
    set term ;^
    commit;
"""

act = isql_act('db', test_script,
               substitutions=[('exception [0-9]+', 'exception'), ('time=.*', ''),
                              ('-At block line: [\\d]+, col: [\\d]+', '-At block line')])

@pytest.mark.version('>=3.0')
def test_1(act: Action):

    SQL_SCHEMA_PREFIX = '' if act.is_version('<6') else  '"PUBLIC".'
    EXCEPTION_NAME = 'EX_TEST' if act.is_version('<6') else f'{SQL_SCHEMA_PREFIX}"EX_TEST"'
    expected_stderr = f"""
        Statement failed, SQLSTATE = HY000
        exception 4
        -{EXCEPTION_NAME}
        -Hi from Mariana Trench, depth=511, time=2015-08-24 13:47:25.1330
        -At block line: 1026, col: 5
    """

    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

