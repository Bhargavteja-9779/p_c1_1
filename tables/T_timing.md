**Isolated timing benchmark** (x86_64, 4 logical CPUs, OMP_NUM_THREADS=1, no concurrent jobs; median and IQR over repetitions; 'store' row in MB)

| dataset   | method                   | operation                                |       median_ms | iqr_ms                 |   reps |   n_cal |   n_tgt |
|:----------|:-------------------------|:-----------------------------------------|----------------:|:-----------------------|-------:|--------:|--------:|
| BDG2      | HSC-CQR simple (primary) | LOBO tuning (9 kappa)                    |  1634           | [1552, 1646]           |      5 |     208 |     303 |
| BDG2      | HSC-CQR full             | LOBO tuning (5 K x 9 kappa)              | 27171.5         | [2.707e+04, 2.727e+04] |      2 |     208 |     303 |
| BDG2      | QShrink-CQR              | LOBO tuning                              |  1502.01        | [1479, 1510]           |      5 |     208 |     303 |
| BDG2      | Self-CQR-fb              | LOBO tuning                              |   699.171       | [690.7, 707.7]         |      5 |     208 |     303 |
| BDG2      | ACI-CQR                  | LOBO tuning                              |  1229.03        | [1207, 1243]           |      5 |     208 |     303 |
| BDG2      | HSC-CQR simple (primary) | apply, per building-day (batch)          |     0.0141627   | [0.01388, 0.01455]     |     20 |     208 |     303 |
| BDG2      | CQR                      | apply, per building-day (batch)          |     0.000661512 | [0.0006406, 0.0006835] |     20 |     208 |     303 |
| BDG2      | QShrink-CQR              | apply, per building-day (batch)          |     0.0104794   | [0.01041, 0.0107]      |     20 |     208 |     303 |
| BDG2      | ACI-CQR                  | apply, per building-day (batch)          |     0.0070565   | [0.007006, 0.007337]   |     20 |     208 |     303 |
| BDG2      | HSC-CQR simple (primary) | incremental update, one building-day     |     0.0232845   | [0.02313, 0.02365]     |    200 |     208 |     303 |
| BDG2      | forecaster               | feature construction, one building-day   |     0.592575    | [0.5517, 0.6703]       |     50 |     208 |     303 |
| BDG2      | forecaster               | 3 LightGBM predictions, one building-day |     4.73885     | [4.557, 4.869]         |     50 |     208 |     303 |
| BDG2      | store                    | pooled score CDF (MB, float32)           |    23.296       |                        |      0 |     208 |     303 |
| UCI       | HSC-CQR simple (primary) | LOBO tuning (9 kappa)                    |   376.83        | [375.1, 390.5]         |      5 |      63 |      95 |
| UCI       | HSC-CQR full             | LOBO tuning (5 K x 9 kappa)              |  5499.07        | [5465, 5534]           |      2 |      63 |      95 |
| UCI       | QShrink-CQR              | LOBO tuning                              |   378.94        | [365.1, 392.4]         |      5 |      63 |      95 |
| UCI       | Self-CQR-fb              | LOBO tuning                              |   180.732       | [179.9, 181.8]         |      5 |      63 |      95 |
| UCI       | ACI-CQR                  | LOBO tuning                              |   307.149       | [305.8, 311]           |      5 |      63 |      95 |
| UCI       | HSC-CQR simple (primary) | apply, per building-day (batch)          |     0.0108854   | [0.01079, 0.0112]      |     20 |      63 |      95 |
| UCI       | CQR                      | apply, per building-day (batch)          |     0.000276086 | [0.0002707, 0.0002796] |     20 |      63 |      95 |
| UCI       | QShrink-CQR              | apply, per building-day (batch)          |     0.0102083   | [0.00895, 0.01343]     |     20 |      63 |      95 |
| UCI       | ACI-CQR                  | apply, per building-day (batch)          |     0.00806898  | [0.008031, 0.008143]   |     20 |      63 |      95 |
| UCI       | HSC-CQR simple (primary) | incremental update, one building-day     |     0.023543    | [0.02336, 0.02374]     |    200 |      63 |      95 |
| UCI       | forecaster               | feature construction, one building-day   |     0.314424    | [0.3071, 0.3455]       |     50 |      63 |      95 |
| UCI       | forecaster               | 3 LightGBM predictions, one building-day |     3.18665     | [3.126, 3.289]         |     50 |      63 |      95 |
| UCI       | store                    | pooled score CDF (MB, float32)           |     7.056       |                        |      0 |      63 |      95 |
