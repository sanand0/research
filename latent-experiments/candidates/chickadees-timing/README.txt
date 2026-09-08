This file contains the meta-data information for the 3 data files called required to reproduce analyses presented in: Exploring sources of (co-)variation in the timing and intensity rate of foraging in a wild population of Black-capped chickadees (Poecile atricapillus)



#############################
File name: "2022-2023data.csv"
#############################
Project: Exploring sources of (co-)variation in the timing and intensity rate of foraging in a wild population of Black-capped chickadees (Poecile atricapillus)
Authors: Nathan Hobbs, Deborah M. Hawkshaw, Jan J. Wijmenga and Kimberley J. Mathot
Institution: University of Alberta 
Location: University of Alberta Botanic Garden
Study period: Winter 2022-2023 field season

Description:
Data regarding RFID (Radio Frequency Identification) detections at 8 bird feeders located in the University of Alberta Botanical Garden during the 2022-2023 field season. 


Variables:
Column 1 (no name): Column indicates the row number 
Date_Time: Date and time the passive integrated transponder (PIT) tag was detected (PIT tag visited the feeder).
VisitDate: Date the PIT tag was detected (PIT tag visited the feeder).
Time: Time the PIT tag was detected. Note. All detections that occurred within 12 sec were condensed into a single visit, where the time was the first detection in the visit.
Feeder: ID of the feeder that was visited. Could be one of eight possible values. 
TransponderHexCode: The hexadecimal code of the PIT tag that was detected at the feeder. 
IVI: Intervisit interval. Calculated as the time between the current visits and the previous visit. NAs indicate when IVI was not calculated. 
IVIc: Intervisit interval as a continous number. Calculated as the time between the current visits and the previous visit. NAs indicate when IVI was not calculated. 
type: Type of visit/transponder tag, either bird or observer. Bird indicates when the Transponder HEX code belonged to a bird (chickadee), while observer indicates when the Transponder HEX code belonged to a human observer (used to indicate when the feeder was visit by a human to download data, change batteries, refill feeders with sunflower seeds etc.)



###########################
File name: "Age_Sex_V2.csv"
###########################
Project: Exploring sources of (co-)variation in the timing and intensity rate of foraging in a wild population of Black-capped chickadees (Poecile atricapillus)
Authors: Nathan Hobbs, Deborah M. Hawkshaw, Jan J. Wijmenga and Kimberley J. Mathot
Institution: University of Alberta 
Location: University of Alberta Botanic Garden
Study period: Winter 2022-2023 field season
Complied by: Nathan Hobbs

Description:
Data regarding the Transponder HEX code, sex and maximum year of every chickadee recorded in the study sites history. 

Variables:
TransponderHexCode**: Unique individual identifier for each individual chickadee 
SexConclusion: Sex of each individual chickadee. Unknown cells represent chickadees that were unable to be accurately sexed, whereas blank cells were never sexed. 
MaxHatchYear: Maximum possible hatching year of each individual chickadee.


**Some individuals in the datafile had their Transponder HEX codes improperly extracted. However, these individuals did not use the feeders during our study period. 
The row numbers containing improperly extracted HEX codes are listed below:
206
207
246
249
342
343


############################
File name: "TempDay2023.csv"
############################
Project: Exploring sources of (co-)variation in the timing and intensity rate of foraging in a wild population of Black-capped chickadees (Poecile atricapillus)
Authors: Nathan Hobbs, Deborah M. Hawkshaw, Jan J. Wijmenga and Kimberley J. Mathot
Institution: University of Alberta 
Location: University of Alberta Botanic Garden
Study period: Winter 2022-2023 field season
Data sources: Agriculture and Irrigation Alberta Climate Information Service; Sunrise/Sunset Calculator National Research Council Canada
Complied by: Nathan Hobbs

Description:
Compiled data on daily mean ambient temperature and daylength from 2022/12/01 to 2023/02/28 (study period data was analyzed for). Data on daily mean ambient temperature was obtained via the Agriculture and Irrigation Alberta Climate Information Service (https://agriculture.alberta.ca/acis/weather-data-viewer.jsp) and reflects data collected from a weather station located at the Edmonton International Airport (YEG). Data on daylength was obtained via the National Research Council Canada's sunrise/sunset calculator (https://nrc.canada.ca/en/research-development/products-services/software-applications/sun-calculator/) and reflects the daylength (hours of illumination - day) in the city of Edmonton.


Variables:
date: Date presented in YYYY-MM-DD.
Temperature: Average ambient temperature in degrees celcius (C) for the given day.
Precipitation: Amount of precipitation in millimeters for the given day 
Daylength: Daylength in hours (Hr) for the given day. 
Sunrise: Timing of sunrise in Mountain Standard Time on the 24 hour clock
Sunset: Timing of sunset in Mountain Standard Time on the 24 hour clock