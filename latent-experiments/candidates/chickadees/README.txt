Descriptions of data files used in: "Age, sex and temperature shape off-territory feeder use in black-capped chickadees"
Author Names redacted for review


#----------------#
data_AllDates.csv
#----------------#
description: this file contains all data collected from January 9 to February 28, 2023 (inclusive), but excudes February 15 to February 23, 2023 (inclusive). 

column name: description
VisitDate: date of observation (YYYY-MM-DD)
TransponderHexCode: unique 10-digit hexadecimal PIT tag code
UniqueFeederCount: the number of unique feeders visited by the bird on the given VisitDate
AvgTemp: mean daily temperature in degrees Celcius
Temp_stnd: the standardized temperature used in analysis. Temperature was standardized by dividing values by 2 standard deviations so that the estimated effect of temperature reflects the effect of 1 s.d. change in temperature (i.e., 5.74°C). 
Sex: determined molecularly or by discriminant function score. Male or Female
AgeBin: the binned age of birds (0 = birds hatched in 2022, “juveniles”; 1 = birds hatched in 2021 or earlier, “adults”)
Age_Sex: a composite variable specifying the age (0 = juvenile or 1 = adult) and sex (male or female) of each individual, resulting in four levels (0Male, 0Female, 1Male, 1Female).
VisitCount: the number of visits the bird made to feeders throughout the study site on the given VisitDate (i.e., daily feeding rate)
Age: the minimum age of a bird with reference to their hatch year. The birds present in our study ranged in minimum age from 0 years (i.e., hatched in spring 2022) to 6 years (i.e., hatched in spring 2016 or earlier). 


#---------------#
data_FeedersVisits.csv
#---------------#
description: this file contains each bird's visit recording to the feeders from January 9 to February 28, 2023 (inclusive), but excudes February 15 to February 23, 2023 (inclusive). 

column name: description
VisitDate: date of observation (YYYY-MM-DD)
TransponderHexCode: unique 10-digit hexadecimal PIT tag code
Time: time of visit
Feeder: location of feeder visited (02A, 04A, 09A, 11A, 12A, 16A)
UniqueFeederCount_Total: the number of unique feeders visited by the bird calculated across the entire study period
UniqueFeederCount_Day: the number of unique feeders visited by the bird on the given VisitDate


#---------------#
THC_Survival.csv
#---------------#
description: this file contains data on the annaul survival of birds that used the feeders in Winter 2023.

column name: description
TransponderHexCode: unique 10-digit hexadecimal PIT tag code
Survived: was a bird detected at our RFID equipped feeders in Fall 2023 (i.e., did it survive?) (0 = no, 1 = yes)
