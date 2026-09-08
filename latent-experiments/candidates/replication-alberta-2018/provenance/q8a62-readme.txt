Descriptions of data files used in: "An investigation of recapture bias in black-capped chickadees (Poecile atricapillus)"
Authors: LaRocque, Arteaga-Torres, Haave-Audet, Sridharan, Wijmenga and Mathot


#-------------#
recap_data.csv
#-------------#
description: this file provides a list of the birds that were detected at feeders in the 5 days preceeding catching attempts in 2019 and 2020. Within a year, individuals received a single recapture score.

column name: description
Year: year bird was present for recapture (2019 or 2020)
Recap: was the individual recaptured in that year? (0 = no, 1 = yes)
CatchRingNumber: unique aluminun ring band number
TransponderHexCode: unique 10 digit PIT tag code
sex: determined molecuarly. Male, Female or NA. NS = blood sample was not obtained for sexing.


#-------------#
feeding_recap.csv
#-------------#
description: this file contains data on feeding rates for birds detected at feeders in the five days preceeting catching attempts at those feeders in 2019 and 2020.

column name: description
Year: year bird was detected at feeder (2019 or 2020)
VisitDate: day of feeder visit (mm-dd-yyyy)w
Feeder: FeederID (8 different feeder locations)
TransponderHexCode: unique 10 digit PIT tag code
DailyVisits: Total daily visits to feeder
DaysPreCatch: days prior to catching attemp (1, 2, 3, 4, or 5)


#-------------#
latency_data.csv
#-------------#
description: this file contains all data collected during the winter 2018/2019 experiments looking at latency to resume feeding after different manipulations of perceived predation risk

column name: description
Year: year of the observation (2018 or 2019)
Month: month of the observation (12 = December, 1 = January, 2 = February)
Day: day of observation (day within month)
Rep: replicate (1, 2, 3, or 4)
Feeder: Feeder identity
Mount: identity of merlin mount. 0 if no mount present.
Track: identity of mobbing call track. 0 if no track used.
TempDay: mean daily temperature in degrees Celcius
Treatment: 1 = Control, 2 = Acoustic, 3 = Visual, 4 = Acoustic + Visual
ID: unique 10 digit TransponderHexCode
StartTime: start time of treatment (continuous time from 0-1)
VisitTime: time of first visit following treatment (continuous time from 0-1)
LatencyTime: VisitTime-StartTime (on scale from 0-1, where 1 = 24hrs)
Sec: Latecy converted to seconds
Return: did the bird return to the feeder on the same day following the treatment (0 = no, 1 = yes). Birds that did not return were assignedVisitTimes equal to sunset on the day of treatment.


#-------------#
cage_test.csv
#-------------#
description: this file contains all cage exploration scores collected in the population
column name: description

CatchYear: Year the bird was caught for a cage exploration test
CatchMonth: Month the bird was caught for a cage exploration test
CatchDay: Day of the month that the bird was caught for a cage exploration test
CatchRingNumber: unique aluminun ring band number
FormNumber: unique ID given to each cage exploration test
CageTestScore: sum of all movements during cage exploration test


#-------------#
aggression_test.csv
#-------------#
description: this file contains all handling aggression test scores colelcted in the population

column name: description
CatchYear: Year the bird was caught for a cage exploration test
CatchMonth: Month the bird was caught for a cage exploration test
CatchDay: Day of the month that the bird was caught for a cage exploration test
CatchRingNumber: unique aluminun ring band number
AggressivenessScore: handling aggresssion score on a 4 point scale (0 = least aggression, 3 = most aggression)


#-------------#
sampling.csv
#-------------#
description: this file contains all data collected during the winter 2019/2020 experiments looking at sampling behaviour

column name: description
TransponderHexCode: unique 10 digit PIT tag code
Feeder: FeederID (8 different feeder locations)
Round: replicate number (1, 2, 3, or 4)
Treatment: Status of pair of feeders at a site. (empty-empty, empty-full, or full-empty). Note, at least one feeder had to be empty for us to assess sampling given the operational definition.
Sampled: Did the bird sample? (1 = yes, 0 = no). Sampling is defined as returning to a feeder that was previously experienced as unrewarding.
Adjacent: Status of the adjacent feeder
AvgTemp: Daily average temperature in degrees Celcius
