| Group | Features (computed only from the building's own h days of history, divided by the scale s) |
|:--|:--|
| Calendar | hour of day, day of week, weekend flag, month |
| History length | min(h, 28) |
| Lagged load | same hour 1, 2, 7 and 14 days earlier (missing if h is too short) |
| Previous day | mean, maximum and minimum of the previous day's normalised load |
| Profiles | hour-of-day mean over ≤ 28 days; same day-type (weekday/weekend) hour mean; same day-of-week hour mean (≤ 4 weeks, h ≥ 7) |
| Variability | mean absolute day-to-day change of the normalised hourly profile |
| Weather (BDG2 only) | air temperature at the target hour; daily mean; difference to the mean of the scale window and to the previous day |
| Target | y / s (point model: squared error; quantile models: pinball loss at α/2 and 1 − α/2) |
