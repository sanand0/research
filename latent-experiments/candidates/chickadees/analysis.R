# Data analysis for:
# Age, sex and temperature shape off-territory feeder use in black-capped chickadees
# Megan LaRocque, Jan Wijmenga, Kimberley Mathot. 2024. Behavioral Ecology



#=============================#
#----Set working directory----
#=============================#

setwd("C:/Users/megan/OneDrive/Desktop/Summer 2023 NSERC USRA Project/MS Submission/Behavioral Ecology/Submission_202409XX/Clean Data + R Scripts") ##please set your working directory



#==================================#
#----Load libraries + functions----
#==================================#

#R.version.string v. 4.3.3
library(lme4) #v. 1.1-35.3
library(stringr) #v. 1.5.1
library(MCMCglmm) #v. 2.35
library(arm) #v. 1.14.4
library(ggplot2) #v. 3.5.0
library(tidyr) #v. 1.3.1
library(rptR) #v. 0.9.22
library(tidyverse) #v. 2.0.0
library(data.table) #v. 1.15.4
library(ggeffects) #v. 1.5.2
library(DHARMa) #v. 0.4.6
library(broom.mixed) #v. 2.9.5
library(gridExtra) #v. 2.3


##Overdispersion function----
  #Used to test for overdisperson of binomial models
overdisp_fun<-function(model) {
  rdf <- df.residual(model)
  rp <- residuals(model,type="pearson")
  Pearson.chisq <- sum(rp^2)
  prat <- Pearson.chisq/rdf
  pval <- pchisq(Pearson.chisq, df=rdf, lower.tail=FALSE)
  c(chisq=Pearson.chisq,ratio=prat,rdf=rdf,p=pval)
}

##Two max sum function----
  #Used for determining core feeders
sum_two_max_columns <- function(row) {
  sorted_values <- sort(row, decreasing = TRUE)  
  sum(sorted_values[1:2])
}

##P-value difference function----
  #Used to calculate the percent overlap (Bayesian p-value) of pairwise estimates/CrIs
p_difference <- function(simulation, param_index1, param_index2) {
  difference <- simulation@fixef[, param_index1] - simulation@fixef[, param_index2]
  difference_mcmc <- as.mcmc(difference)
  mode <- posterior.mode(difference_mcmc)
  CrI <- HPDinterval(difference_mcmc)
  pos_values <- ifelse(difference_mcmc > 0, 1, 0)
  neg_values <- ifelse(difference_mcmc < 0, 1, 0)
  if(mode<0){pvalue<-sum(pos_values)/(sum(pos_values)+sum(neg_values))}
  else{pvalue<-sum(neg_values)/(sum(pos_values)+sum(neg_values))}
  return(list(Pvalue=pvalue, PostMode=mode["var1"], LowCrI=CrI[,"lower"], HighCrI=CrI[,"upper"]))}

##P-value overlap of 0 function----
  #Used to calculate overlap of 0 for one estimate's CrI
p_zero <- function(simulation, param_index) {
  estimate <- simulation@fixef[, param_index]
  estimate_mcmc <- as.mcmc(estimate)
  mode <- posterior.mode(estimate_mcmc)
  pos_values <- ifelse(estimate_mcmc > 0, 1, 0)
  neg_values <- ifelse(estimate_mcmc < 0, 1, 0)
  if(mode<0){pvalue<-sum(pos_values)/(sum(pos_values)+sum(neg_values))}
  else{pvalue<-sum(neg_values)/(sum(pos_values)+sum(neg_values))}
  return(pvalue)
  print(pvalue)}



#=====================#
#----Load Datasets----
#=====================#

data_FeederVisits <- read.csv("data_FeederVisits.csv")
data_full <- read.csv("data_AllDates.csv")
data <- data_full %>% filter(UniqueFeederCount >= 1) #remove rows with 0s or NAs for unique feeder count
survival <- read.csv("THC_Survival.csv")



#===================#
#----Core Feeder----
#===================#

Feeder_THC <- data_FeederVisits %>% subset(select=c(Feeder, TransponderHexCode)) %>% na.omit()
CoreFeeder <- Feeder_THC %>% group_by(TransponderHexCode) %>% transmute("02A"=sum(Feeder=="02A"), 
                                                                        "04A"=sum(Feeder=="04A"),
                                                                        "09A"=sum(Feeder=="09A"),
                                                                        "10A"=sum(Feeder=="10A"),
                                                                        "11A"=sum(Feeder=="11A"),
                                                                        "12A"=sum(Feeder=="12A"),
                                                                        "14A"=sum(Feeder=="14A"),
                                                                        "16A"=sum(Feeder=="16A")) %>% distinct()


#What is the visit value of the 'Core Feeder'
CoreFeeder$CoreFeederVisits <- apply(CoreFeeder[,-1], 1, max, na.rm=TRUE)
#Which feeder was visited the most by each bird (i.e., their 'Core Feeder')
CoreFeeder$CoreFeeder <- colnames(CoreFeeder[, -1])[max.col(CoreFeeder[, -1], ties.method='first')]
#What is the total visits made across all feeders
CoreFeeder$TotalFeederSums <- rowSums(CoreFeeder[c(2, 3, 4, 5, 6, 7, 8, 9)])
#Sum of visits to the most and second most visited feeder
CoreFeeder$TwoMaxSum <- apply(CoreFeeder[, c("02A", "04A", "09A", "10A", "11A", "12A", "14A", "16A")], 1, sum_two_max_columns)
#Percentage of visits made to 'Core Feeder' (relative to other most visited feeder)
CoreFeeder$PercentCoreFeeder <- (CoreFeeder$CoreFeederVisits / CoreFeeder$TwoMaxSum)*100

#Birds with two core feeders (09A, 11A):
#"3B001878E9", "3B0018A4C3"
CoreFeeder <- CoreFeeder %>%
  mutate(CoreFeeder = ifelse(PercentCoreFeeder < 60, "09A, 11A", CoreFeeder))

##Define On/Off Territory----
  #If a bird visit only their core feeder on a given day = on territory
  #If a bird visits another feeder (in addition to or other than their core feeder) on a given day = off territory
data_CF <- left_join(data_FeederVisits, CoreFeeder)
data_CF <- data_CF %>% group_by(VisitDate, TransponderHexCode) %>%
  mutate(
    CoreList = strsplit(as.character(CoreFeeder), ","),
    onT = as.integer(Feeder %in% unlist(CoreList)) #1=fed at core feeder; 0=fed not at core feeder
  )
data_CF <- data_CF %>% filter(UniqueFeederCount_Day>0) %>% #remove non-visits
  mutate(offT = ifelse(onT == 0, 1, 0)) #1=does not feed at core feeder; 0=fed at core feeder

###Each bird should only get one offT score per day----
#i.e., only offT=1 if they visited at least one non-core feeder on a given day
data_CF_sum <- data_CF %>%
  group_by(VisitDate, TransponderHexCode, CoreFeeder) %>%
  summarize(offT = max(offT), .groups = 'drop')

##Add CoreFeeder to dataset----
data_offT <- left_join(data, data_CF_sum)



#==========================================#
#----Filter data for main text analysis----
#==========================================#

#Only include Jan 9, 2023 to Feb 14, 2023 (inclusive)
data_MS <- data_offT %>% filter(VisitDate >= as.Date("2023-01-09"), VisitDate <= as.Date("2023-02-14"))
data_MS$TempL0<-data_MS$Temp_stnd+1.2082479 #left-zero temperature data



#=====================#
#----Summary Stats----
#=====================#

data_MSdates <- data_full %>% filter(VisitDate >= as.Date("2023-01-09"), VisitDate <= as.Date("2023-02-14"))
data_NoNAs <- data_MSdates[complete.cases(data_MSdates),]#remove rows with NAs for feeder visits

##VisitCount by temperature----
ggplot(data_NoNAs, aes(x=AvgTemp, y=VisitCount)) +
  geom_point(colour="black", stat="identity")+
  scale_x_continuous(name='Average Daily Temperature') +
  scale_y_continuous(name='Daily Visit Count')
data_VC200 <- data_NoNAs %>% filter(VisitCount>=200) #number of visit counts >200; N=27 out of a total of 4990 observations

##Average number of visit dates by bird---- 
#i.e., where birds had Unique_Feeder_Count > 0 
ReplicateCount<-data_NoNAs %>% 
  group_by(TransponderHexCode) %>% 
  summarise(Count = n())
H_ReplicateCount <- hist(ReplicateCount$Count)
mean(ReplicateCount$Count) #36.15942 out of 37 VisitDate
sd(ReplicateCount$Count) #4.673651
summary(ReplicateCount$Count)#Ranges from 2 to 37 (i.e., individuals visited feeders at 2 to 37 days out of a total possible 37 days)

##Histograms of unique feeder count---- 
###Seasonally----
UFC_Total <- data_FeederVisits %>% subset(select=c(TransponderHexCode, UniqueFeederCount_Total)) %>% na.omit() %>% distinct()
THC.UFC_Total <- UFC_Total %>% group_by(UniqueFeederCount_Total) %>% summarise(THC_Count = n_distinct(TransponderHexCode)) %>% distinct()
#Add zeros into data
zeros <- data.table("UniqueFeederCount_Total" = 0, "THC_Count" = 0)
THC.UFC_Total0 <- rbindlist(list(THC.UFC_Total, zeros))

theme_update(legend.title=element_text(size = 28),legend.position="right",legend.text = element_text(size = 28),
             axis.title = element_text(size=28), axis.text = element_text(size=28))
Fig.2a = ggplot(THC.UFC_Total0, aes(x=as.factor(UniqueFeederCount_Total), y=THC_Count)) +
  geom_bar(colour="black", stat="identity") +
  scale_x_discrete(drop = FALSE, name='Seasonal unique feeder count') +
  scale_y_continuous(name='Number of Birds', limit=c(0,80)) +
  ggtitle("a)") +
  theme_classic()  

median(UFC_Total$UniqueFeederCount_Total, na.rm = TRUE) #1 out of 7 UniqueFeeders throughout entire study period
sd(UFC_Total$UniqueFeederCount_Total, na.rm = TRUE) #1.113376
summary(as.factor(UFC_Total$UniqueFeederCount_Total))
#Ranges from 1 to 6 (i.e., individuals visited 1-6 feeders out of a total possible 7 feeders throughout the study period)
#N=70 birds visit only max of 1 feeder; N=68 birds visit >1 max feeders; N=0 visits visited no feeders

###Daily----
THC.UFC_Day <- data_NoNAs %>% group_by(UniqueFeederCount) %>% count(name = "THC_Count")

theme_update(legend.title=element_text(size = 28),legend.position="right",legend.text = element_text(size = 28),
             axis.title = element_text(size=28), axis.text = element_text(size=28))
Fig.2b = ggplot(THC.UFC_Day, aes(x=as.factor(UniqueFeederCount), y=THC_Count)) +
  geom_bar(colour="black", stat="identity") +
  scale_x_discrete(drop = FALSE, name=' Daily unique feeder count') +
  scale_y_continuous(name='Frequency') +
  ggtitle("b)") +
  theme_classic()

median(data_NoNAs$UniqueFeederCount, na.rm = TRUE) #1 out of 7 UniqueFeeders throughout entire study period
sd(data_NoNAs$UniqueFeederCount, na.rm = TRUE) #0.4586303
summary(data_NoNAs$UniqueFeederCount)
summary(as.factor(data_NoNAs$UniqueFeederCount))
#Ranges from 0 to 5 (i.e., individuals visited 0-5 feeders out of a total possible 7 feeders on any given visit date)
#N=4033 birds visit only 1 feeder; N=936 birds visit >1 feeders; N=21 never visited a feeder on a given day

#Figure saved at 575x510 pixels
Fig.2 = grid.arrange(Fig.2a, Fig.2b, nrow = 2, ncol = 1) 
Fig.2

##Age distributions----
Ages <- subset(data_NoNAs, select = c(TransponderHexCode, Age)) %>% distinct()
H_Age_ESM <- hist(Ages$Age)
summary(as.factor(Ages$Age))



#===================#
#****Results****----
#===================#

#*Off-Territory Use*----

##Model----
m1 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_MS, family=binomial, 
            control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1) #m1 is not overdispersed
#DHARMa assumptions test
sim_results_m1 <- simulateResiduals(m1)
plot(sim_results_m1)
test_results_m1 <- testResiduals(sim_results_m1)
print(test_results_m1)

summary(m1)

sm1<-sim(m1, 1000)
mode1<-posterior.mode(as.mcmc(sm1@fixef))
HPD1<-HPDinterval(as.mcmc(sm1@fixef))
mode1 #estimates
HPD1 #CrIs

#between Bird ID variance
var_THC1 <- sm1@ranef$TransponderHexCode
bvar_THC1<-as.vector(apply(var_THC1, 1, var))
bvar_THC1<-as.mcmc(bvar_THC1)
posterior.mode(bvar_THC1) #4.431184       
HPDinterval(bvar_THC1)  #(3.764433, 5.720619)

#between CoreFeeder variance
var_CF1 <- sm1@ranef$CoreFeeder
bvar_CF1<-as.vector(apply(var_CF1, 1, var))
bvar_CF1<-as.mcmc(bvar_CF1)
posterior.mode(bvar_CF1) #11.69592        
HPDinterval(bvar_CF1)  #(2.522028, 24.08959)

##Repeatability----
rep1<-bvar_THC1 / (bvar_THC1 + (pi^2)/3)
posterior.mode(rep1) #0.5740497      
HPDinterval(rep1) #(0.5336365, 0.6348845)


##Effect Size Significance----
  #only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA (intercept)
FA_int1 <- p_zero(sm1,3) #0.036
#MJ (intercept)
MJ_int1 <- p_zero(sm1,2) #0.028
#FJ (slope)
FJ_slope1 <- p_zero(sm1,5) #0.026
#MJ (slope)
MJ_slope1 <- p_zero(sm1,6) #0.275
#MA (slope)
MA_slope1 <- p_zero(sm1,8) #0.334

##Pairwise Contrasts----
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1 <- p_difference(sm1,3,1)
FJFA_int1 
#MJ-FJ (intercept)
FJMJ_int1 <- p_difference(sm1,2,1)
FJMJ_int1 
#MJ-FA (intercept)
FAMJ_int1 <- p_difference(sm1,2,3)
FAMJ_int1 
#MA-FJ (intercept)
FJMA_int1 <- p_difference(sm1,4,1)
FJMA_int1
#MA-FA (intercept)
FAMA_int1 <- p_difference(sm1,4,3)
FAMA_int1 
#MA-MJ (intercept)
MJMA_int1 <- p_difference(sm1,4,2)
MJMA_int1 
#FJ-FA (slope)
FJFA_slope1 <- p_difference(sm1,5,7)
FJFA_slope1 
#FJ-MJ (slope)
FJMJ_slope1 <- p_difference(sm1,5,6)
FJMJ_slope1
#FJ-MA (slope)
FJMA_slope1 <- p_difference(sm1,5,8)
FJMA_slope1 
#FA-MJ (slope)
FAMJ_slope1 <- p_difference(sm1,7,6)
FAMJ_slope1 
#FA-MA (slope)
FAMA_slope1 <- p_difference(sm1,7,8)
FAMA_slope1
#MJ-MA (slope)
MJMA_slope1 <- p_difference(sm1,6,8)
MJMA_slope1

###Table----
m1_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                    "MJ-FJ (int)",
                                    "MJ-FA (int)", 
                                    "MA-FJ (int)", 
                                    "MA-FA (int)", 
                                    "MA-MJ (int)", 
                                    "FJ-FA (slope)",
                                    "FJ-MJ (slope)",
                                    "FJ-MA (slope)", 
                                    "FA-MJ (slope)", 
                                    "FA-MA (slope)", 
                                    "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1$Pvalue, 2),
                                      round(FJMA_int1$Pvalue, 2),
                                      round(FJMJ_int1$Pvalue, 2), 
                                      round(FAMJ_int1$Pvalue, 2), 
                                      round(FAMA_int1$Pvalue, 2),
                                      round(MJMA_int1$Pvalue, 2),
                                      round(FJFA_slope1$Pvalue, 2),
                                      round(FJMA_slope1$Pvalue, 2),
                                      round(FJMJ_slope1$Pvalue, 2), 
                                      round(FAMJ_slope1$Pvalue, 2), 
                                      round(FAMA_slope1$Pvalue, 2),
                                      round(MJMA_slope1$Pvalue, 2)), 
                       PostMode = c(round(FJFA_int1$PostMode, 2),
                                  round(FJMA_int1$PostMode, 2),
                                  round(FJMJ_int1$PostMode, 2), 
                                  round(FAMJ_int1$PostMode, 2), 
                                  round(FAMA_int1$PostMode, 2),
                                  round(MJMA_int1$PostMode, 2),
                                  round(FJFA_slope1$PostMode, 2),
                                  round(FJMA_slope1$PostMode, 2),
                                  round(FJMJ_slope1$PostMode, 2), 
                                  round(FAMJ_slope1$PostMode, 2), 
                                  round(FAMA_slope1$PostMode, 2),
                                  round(MJMA_slope1$PostMode, 2)), 
                       LowCrI = c(round(FJFA_int1$LowCrI, 2),
                                    round(FJMA_int1$LowCrI, 2),
                                    round(FJMJ_int1$LowCrI, 2), 
                                    round(FAMJ_int1$LowCrI, 2), 
                                    round(FAMA_int1$LowCrI, 2),
                                    round(MJMA_int1$LowCrI, 2),
                                    round(FJFA_slope1$LowCrI, 2),
                                    round(FJMA_slope1$LowCrI, 2),
                                    round(FJMJ_slope1$LowCrI, 2), 
                                    round(FAMJ_slope1$LowCrI, 2), 
                                    round(FAMA_slope1$LowCrI, 2),
                                    round(MJMA_slope1$LowCrI, 2)), 
                       HighCrI = c(round(FJFA_int1$HighCrI, 2),
                                  round(FJMA_int1$HighCrI, 2),
                                  round(FJMJ_int1$HighCrI, 2), 
                                  round(FAMJ_int1$HighCrI, 2), 
                                  round(FAMA_int1$HighCrI, 2),
                                  round(MJMA_int1$HighCrI, 2),
                                  round(FJFA_slope1$HighCrI, 2),
                                  round(FJMA_slope1$HighCrI, 2),
                                  round(FJMJ_slope1$HighCrI, 2), 
                                  round(FAMJ_slope1$HighCrI, 2), 
                                  round(FAMA_slope1$HighCrI, 2),
                                  round(MJMA_slope1$HighCrI, 2)), )


##----Figure 5----
####create temperature bins in 5C intervals
data_MS$TempBin<-round(data_MS$AvgTemp/5)*5

####summarize mean and se by age_sex for each temperature bin
rawplot<-data_MS %>%
  group_by(Age_Sex, TempBin) %>%
  summarise(
    Mean = mean (offT),
    SE = sd(offT)/sqrt(n())
  )


#Prediction for model response
m1_pred<-augment(m1, type.predict="response", se_fit=TRUE)

#Get a column with the average daily temperature for figure purposes
AvgTemp_TempL0 <- subset(data_MS, select = c("AvgTemp", "TempL0")) %>% distinct()
m1_pred2 <- left_join(m1_pred, AvgTemp_TempL0, by=c("TempL0"))

#plot figure with raw data and prediction curves
#Figure saved at 1200x800 pixels
theme_set(theme_classic())
theme_update(legend.title=element_text(size = 28),legend.position="right",legend.text = element_text(size = 28),
             axis.title = element_text(size=28), axis.text = element_text(size=28))
Fig.5 <- ggplot(rawplot, aes(x= TempBin, y = Mean, color = Age_Sex, shape = Age_Sex)) +
  geom_point(position = position_dodge(width = 0.5), size=3)+
  geom_errorbar(
    aes(ymin=Mean-SE, ymax= Mean+SE),
    width = 0.2,
    position=position_dodge(width=0.5))+
  stat_smooth(data=m1_pred2, aes(x=AvgTemp, y=.fitted, colour=Age_Sex, linetype = Age_Sex), method="glm", se=TRUE, method.args = list(family=binomial))+
  xlab(expression("\n Average daily temperature (°C)"))+ 
  ylab("Probability of foraging off territory\n")+
  labs(linetype="Age & Sex Groups", colour="Age & Sex Groups", shape="Age & Sex Groups") +
  scale_linetype_manual(labels = c("Juvenile Female", "Juvenile Male", "Adult Female", "Adult Male"), values = c("0Female"=1, "0Male"=2,"1Female"=3, "1Male"=4)) +
  scale_colour_manual(labels = c("Juvenile Female", "Juvenile Male", "Adult Female", "Adult Male"), values = c("brown3", "#1874CD", "#458B00", "orange3")) +
  scale_shape_manual(labels = c("Juvenile Female", "Juvenile Male", "Adult Female", "Adult Male"), values = c("0Female"=15, "0Male"=19,"1Female"=17, "1Male"=18))

Fig.5


#*Daily Feeder Visits*----

##Model----
m2_sqrt <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_MS)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_sqrt)
hist(resid(m2_sqrt))
#DHARMa assumptions test
sim_results_m2_sqrt <- simulateResiduals(m2_sqrt)
plot(sim_results_m2_sqrt)
test_results_m2_sqrt <- testResiduals(sim_results_m2_sqrt)
print(test_results_m2_sqrt)

summary(m2_sqrt)

sm2_sqrt<-sim(m2_sqrt, 1000)
mode2_m2_sqrt<-posterior.mode(as.mcmc(sm2_sqrt@fixef))
HPD2_m2_sqrt<-HPDinterval(as.mcmc(sm2_sqrt@fixef))
mode2_m2_sqrt #estimates
HPD2_m2_sqrt #CrIs

#between Bird ID variance
var_THC2_sqrt <- sm2_sqrt@ranef$TransponderHexCode
bvar_THC2_sqrt<-as.vector(apply(var_THC2_sqrt, 1, var))
bvar_THC2_sqrt<-as.mcmc(bvar_THC2_sqrt)
posterior.mode(bvar_THC2_sqrt) #2.086561     
HPDinterval(bvar_THC2_sqrt)  #(1.879986, 2.326911)

#between CoreFeeder variance
var_CF2_sqrt <- sm2_sqrt@ranef$CoreFeeder
bvar_CF2_sqrt<-as.vector(apply(var_CF2_sqrt, 1, var))
bvar_CF2_sqrt<-as.mcmc(bvar_CF2_sqrt)
posterior.mode(bvar_CF2_sqrt) #0.04783623      
HPDinterval(bvar_CF2_sqrt)  #(0.02639084, 0.09318278)

#between Residual variance
rvar2_sqrt<-sm2_sqrt@sigma^2
rvar2_sqrt<-as.mcmc(rvar2_sqrt)
posterior.mode(rvar2_sqrt) #1.8588      
HPDinterval(rvar2_sqrt) #(1.799955, 1.942778)

##Repeatability----
rep2_sqrt <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_MS, 
            datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_sqrt) # 0.509 (0.427, 0.569)

##Pairwise Contrasts----
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_sqrt <- p_difference(sm2_sqrt,3,1)
FJFA_int2_sqrt 
#MJ-FJ (intercept)
FJMJ_int2_sqrt <- p_difference(sm2_sqrt,2,1)
FJMJ_int2_sqrt 
#MJ-FA (intercept)
FAMJ_int2_sqrt <- p_difference(sm2_sqrt,2,3)
FAMJ_int2_sqrt 
#MA-FJ (intercept)
FJMA_int2_sqrt <- p_difference(sm2_sqrt,4,1)
FJMA_int2_sqrt
#MA-FA (intercept)
FAMA_int2_sqrt <- p_difference(sm2_sqrt,4,3)
FAMA_int2_sqrt 
#MA-MJ (intercept)
MJMA_int2_sqrt <- p_difference(sm2_sqrt,4,2)
MJMA_int2_sqrt 
#FJ-FA (slope)
FJFA_slope2_sqrt <- p_difference(sm2_sqrt,5,7)
FJFA_slope2_sqrt 
#FJ-MJ (slope)
FJMJ_slope2_sqrt <- p_difference(sm2_sqrt,5,6)
FJMJ_slope2_sqrt
#FJ-MA (slope)
FJMA_slope2_sqrt <- p_difference(sm2_sqrt,5,8)
FJMA_slope2_sqrt 
#FA-MJ (slope)
FAMJ_slope2_sqrt <- p_difference(sm2_sqrt,7,6)
FAMJ_slope2_sqrt 
#FA-MA (slope)
FAMA_slope2_sqrt <- p_difference(sm2_sqrt,7,8)
FAMA_slope2_sqrt
#MJ-MA (slope)
MJMA_slope2_sqrt <- p_difference(sm2_sqrt,6,8)
MJMA_slope2_sqrt

###Table----
m2_sqrt_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                    "MJ-FJ (int)",
                                    "MJ-FA (int)", 
                                    "MA-FJ (int)", 
                                    "MA-FA (int)", 
                                    "MA-MJ (int)", 
                                    "FJ-FA (slope)",
                                    "FJ-MJ (slope)",
                                    "FJ-MA (slope)", 
                                    "FA-MJ (slope)", 
                                    "FA-MA (slope)", 
                                    "MJ-MA (slope)"),
                       Pvalue = c(round(FJFA_int2_sqrt$Pvalue, 2),
                                  round(FJMA_int2_sqrt$Pvalue, 2),
                                  round(FJMJ_int2_sqrt$Pvalue, 2), 
                                  round(FAMJ_int2_sqrt$Pvalue, 2), 
                                  round(FAMA_int2_sqrt$Pvalue, 2),
                                  round(MJMA_int2_sqrt$Pvalue, 2),
                                  round(FJFA_slope2_sqrt$Pvalue, 2),
                                  round(FJMA_slope2_sqrt$Pvalue, 2),
                                  round(FJMJ_slope2_sqrt$Pvalue, 2), 
                                  round(FAMJ_slope2_sqrt$Pvalue, 2), 
                                  round(FAMA_slope2_sqrt$Pvalue, 2),
                                  round(MJMA_slope2_sqrt$Pvalue, 2)), 
                       PostMode = c(round(FJFA_int2_sqrt$PostMode, 2),
                                    round(FJMA_int2_sqrt$PostMode, 2),
                                    round(FJMJ_int2_sqrt$PostMode, 2), 
                                    round(FAMJ_int2_sqrt$PostMode, 2), 
                                    round(FAMA_int2_sqrt$PostMode, 2),
                                    round(MJMA_int2_sqrt$PostMode, 2),
                                    round(FJFA_slope2_sqrt$PostMode, 2),
                                    round(FJMA_slope2_sqrt$PostMode, 2),
                                    round(FJMJ_slope2_sqrt$PostMode, 2), 
                                    round(FAMJ_slope2_sqrt$PostMode, 2), 
                                    round(FAMA_slope2_sqrt$PostMode, 2),
                                    round(MJMA_slope2_sqrt$PostMode, 2)), 
                       LowCrI = c(round(FJFA_int2_sqrt$LowCrI, 2),
                                  round(FJMA_int2_sqrt$LowCrI, 2),
                                  round(FJMJ_int2_sqrt$LowCrI, 2), 
                                  round(FAMJ_int2_sqrt$LowCrI, 2), 
                                  round(FAMA_int2_sqrt$LowCrI, 2),
                                  round(MJMA_int2_sqrt$LowCrI, 2),
                                  round(FJFA_slope2_sqrt$LowCrI, 2),
                                  round(FJMA_slope2_sqrt$LowCrI, 2),
                                  round(FJMJ_slope2_sqrt$LowCrI, 2), 
                                  round(FAMJ_slope2_sqrt$LowCrI, 2), 
                                  round(FAMA_slope2_sqrt$LowCrI, 2),
                                  round(MJMA_slope2_sqrt$LowCrI, 2)), 
                       HighCrI = c(round(FJFA_int2_sqrt$HighCrI, 2),
                                   round(FJMA_int2_sqrt$HighCrI, 2),
                                   round(FJMJ_int2_sqrt$HighCrI, 2), 
                                   round(FAMJ_int2_sqrt$HighCrI, 2), 
                                   round(FAMA_int2_sqrt$HighCrI, 2),
                                   round(MJMA_int2_sqrt$HighCrI, 2),
                                   round(FJFA_slope2_sqrt$HighCrI, 2),
                                   round(FJMA_slope2_sqrt$HighCrI, 2),
                                   round(FJMJ_slope2_sqrt$HighCrI, 2), 
                                   round(FAMJ_slope2_sqrt$HighCrI, 2), 
                                   round(FAMA_slope2_sqrt$HighCrI, 2),
                                   round(MJMA_slope2_sqrt$HighCrI, 2)), )


##Figure 4----
#Prediction necessary to plot figure
m2_pred <- ggeffect(m2_sqrt, terms = c("TempL0", "Age_Sex"), ci.level = 0.95)

#Figure saved at 1200x800 pixels
theme_set(theme_classic())
theme_update(legend.title=element_text(size = 28),legend.position="right",legend.text = element_text(size = 28),
             axis.title = element_text(size=28), axis.text = element_text(size=28))

Fig.4 <- ggplot(m2_pred, aes(y = (predicted)^2, x = x, col = group, linetype = group))+
  geom_line(linewidth=1)  +
  geom_ribbon(aes(ymin = (conf.low)^2, ymax = (conf.high)^2, colour = NULL),  alpha = .15, show.legend = FALSE)+  
  xlab(expression("Average daily temperature (°C)"))+ 
  ylab("Number of daily feeder visits")+
  theme(legend.key = element_rect(fill = "lightgrey", colour = FALSE))+ 
  labs(linetype="Age & Sex Groups", colour="Age & Sex Groups") +
  scale_linetype_manual(labels = c("Juvenile Female", "Juvenile Male", "Adult Female", "Adult Male"), values = c("0Female"=1, "0Male"=2,"1Female"=3, "1Male"=4)) +
  scale_colour_manual(labels = c("Juvenile Female", "Juvenile Male", "Adult Female", "Adult Male"), values = c("brown3", "#1874CD", "#458B00", "orange3")) +
  scale_x_continuous(breaks=seq(-0.2,1.6,by=0.3), labels = c("-25","-20", "-15", "-10", "-5", "0", "5"))

Fig.4


#*Survival*----
##Off-Territory Use----
offT_lm_list <- list()
for (iter in seq_len(nrow(sm1@ranef$TransponderHexCode))) {
  blups_offT2 <- select(
    as_tibble(sm1@ranef$TransponderHexCode),
    contains(".(Intercept)")
  )[iter, ] 
  blups_offT <- tibble(
    TransponderHexCode = str_sub(colnames(blups_offT2), end = -13),
    blups_offT = as.numeric(blups_offT2))
  
  data_offT_lm <- merge(blups_offT, survival, by = "TransponderHexCode")
  offT_lm_list[[iter]] <- glm(Survived ~ scale(blups_offT), data = data_offT_lm, family = binomial)
}

summary(offT_lm_list[[iter]])

coef_SurvoffT <- as.mcmc(
  sapply(
    offT_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)

#estimate + CrI
posterior.mode(coef_SurvoffT) #-0.2449067     
HPDinterval(coef_SurvoffT) #(-0.5029151 -0.04976171)
#bayesian p-value
pos_SurvoffT<-ifelse(coef_SurvoffT>0,1,0)
neg_SurvoffT<-ifelse(coef_SurvoffT<0,1,0)
p_SurvoffT<-sum(pos_SurvoffT)/(sum(pos_SurvoffT)+sum(neg_SurvoffT))
p_SurvoffT #0.007

##Daily Feeder Visits----
FR_lm_list <- list()
for (iter in seq_len(nrow(sm2_sqrt@ranef$TransponderHexCode))) {
  blups_FR2 <- select(
    as_tibble(sm2_sqrt@ranef$TransponderHexCode),
    contains(".(Intercept)")
  )[iter, ] 
  blups_FR <- tibble(
    TransponderHexCode = str_sub(colnames(blups_FR2), end = -13),
    blups_FR = as.numeric(blups_FR2))
  
  data_FR_lm <- merge(blups_FR, survival, by = "TransponderHexCode")
  FR_lm_list[[iter]] <- glm(Survived ~ scale(blups_FR), data = data_FR_lm, family = binomial)
}

summary(FR_lm_list[[iter]])

coef_SurvFR <- as.mcmc(
  sapply(
    FR_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)

#estimate + CrI
posterior.mode(coef_SurvFR) #0.1166302       
HPDinterval(coef_SurvFR) #(-0.01504541, 0.1984903)
#bayesian p-value
pos_SurvFR<-ifelse(coef_SurvFR>0,1,0)
neg_SurvFR<-ifelse(coef_SurvFR<0,1,0)
p_SurvFR<-sum(neg_SurvFR)/(sum(pos_SurvFR)+sum(neg_SurvFR))
p_SurvFR #0.041

##Age-Sex differences----
#number of birds (n) that survived by Age_Sex group
THC_AgeSex <- subset(data_MS, select = c(TransponderHexCode, Age_Sex)) %>% distinct()
survival2 <- left_join(survival, THC_AgeSex, by = 'TransponderHexCode')

Survived_by_AgeSex <- survival2 %>% 
  group_by(Age_Sex, Survived) %>% count() 



#=======================================#
#----****Supplementary Analyses****----
#=======================================#

#*Survival trivariate analysis*----
  #Both priors resulted in models that did not converge

#Combine Survival data with data_MS without repeated measures for 'survived' column
data_MS_surv <- left_join(data_MS, survival, by = c('TransponderHexCode'))
data_MS_surv <- data_MS_surv %>%
  group_by(TransponderHexCode) %>%
  mutate(Survived = if_else(row_number() == 1, Survived, NA)) %>%
  ungroup()

#priors:
prior1_3var = list(R = list(V = diag(c(1,1,0.0001),3,3), nu = 1.002, fix = 3),
                   G = list(G1 = list(V = diag(3), nu = 3,
                                      alpha.mu = rep(0,3),
                                      alpha.V = diag(25^2,3,3))))
prior2_3var<-list(R = list(V = diag(c(1,1,0.0001),3,3), nu = 1.002, fix = 3),
                  G = list(G1 = list(V = diag(3), nu = 3, fixed = 3)))

#Models:
modelSurv1 <- MCMCglmm(
  cbind(offT, VisitCount, Survived) ~trait-1 +
    trait:Age_Sex +
    at.level(trait, 1):Age_Sex:Temp_stnd +
    at.level(trait, 2):Age_Sex:Temp_stnd,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("categorical", "gaussian", "categorical"),
  data = data_MS_surv,
  prior = prior1_3var,
  verbose = TRUE,
  singular.ok=TRUE,
  pr = TRUE, #saves posterior distribution of BLUPS
  nitt=103000,
  burnin=3000,
  thin=100
)

par(mar = c(1, 1, 1, 1))
plot(modelSurv1)
summary(modelSurv1)

modelSurv2 <- MCMCglmm(
  cbind(offT, VisitCount, Survived) ~trait-1 +
    trait:Age_Sex +
    at.level(trait, 1):Age_Sex:Temp_stnd +
    at.level(trait, 2):Age_Sex:Temp_stnd,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("categorical", "gaussian", "categorical"),
  data = data_MS_surv,
  prior = prior2_3var,
  verbose = TRUE,
  singular.ok=TRUE,
  pr = TRUE, #saves posterior distribution of BLUPS
  nitt=103000,
  burnin=3000,
  thin=100
)

par(mar = c(1, 1, 1, 1))
plot(modelSurv2)
summary(modelSurv2)

#*All dates analysis*----
data_AllDates <- data_offT
data_AllDates$TempL0<-data_AllDates$Temp_stnd+1.893628 #left-zero to new minimum temperature

##Off-Territory Use----
m1_AllDates<-glmer(offT ~ -1 + Age_Sex+Age_Sex:TempL0 + (1|CoreFeeder) + (1|TransponderHexCode), data=data_AllDates, family=binomial, 
                   control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1_AllDates) #not overdispersed

#DHARMa assumptions test
sim_results_m1_AllDates <- simulateResiduals(m1_AllDates)
plot(sim_results_m1_AllDates)
test_results_m1_AllDates <- testResiduals(sim_results_m1_AllDates)
print(test_results_m1_AllDates)

summary(m1_AllDates)

sm1_AllDates<-sim(m1_AllDates)
mode1_AllDates<-posterior.mode(as.mcmc(sm1_AllDates@fixef))
HPD1_AllDates<-HPDinterval(as.mcmc(sm1_AllDates@fixef))
mode1_AllDates
HPD1_AllDates

#between Bird ID variance
var_THC1_AllDates <- sm1_AllDates@ranef$TransponderHexCode
bvar_THC1_AllDates<-as.vector(apply(var_THC1_AllDates, 1, var))
bvar_THC1_AllDates<-as.mcmc(bvar_THC1_AllDates)
posterior.mode(bvar_THC1_AllDates) #4.050627       
HPDinterval(bvar_THC1_AllDates)  #( 3.284877, 4.916334)

#between CoreFeeder variance
var_CF1_AllDates <- sm1_AllDates@ranef$CoreFeeder
bvar_CF1_AllDates<-as.vector(apply(var_CF1_AllDates, 1, var))
bvar_CF1_AllDates<-as.mcmc(bvar_CF1_AllDates)
posterior.mode(bvar_CF1_AllDates) #11.6165         
HPDinterval(bvar_CF1_AllDates)  #(2.87721, 20.60671)

#Repeatability
rep1_AllDates<-bvar_THC1_AllDates / (bvar_THC1_AllDates + (pi^2)/3)
posterior.mode(rep1_AllDates) #0.5518425     
HPDinterval(rep1_AllDates) #(0.5083505, 0.6048229)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (slope)
FJ_int1_AllDates <- p_zero(sm1_AllDates,5) #0.18
#FA (slope)
FA_slope1_AllDates <- p_zero(sm1_AllDates,7) #0.18
#MA (slope)
MA_slope1_AllDates <- p_zero(sm1_AllDates,8) #0.11


##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_AllDates <- p_difference(sm1_AllDates,3,1)
FJFA_int1_AllDates 
#MJ-FJ (intercept)
FJMJ_int1_AllDates <- p_difference(sm1_AllDates,2,1)
FJMJ_int1_AllDates 
#MJ-FA (intercept)
FAMJ_int1_AllDates <- p_difference(sm1_AllDates,2,3)
FAMJ_int1_AllDates 
#MA-FJ (intercept)
FJMA_int1_AllDates <- p_difference(sm1_AllDates,4,1)
FJMA_int1_AllDates
#MA-FA (intercept)
FAMA_int1_AllDates <- p_difference(sm1_AllDates,4,3)
FAMA_int1_AllDates 
#MA-MJ (intercept)
MJMA_int1_AllDates <- p_difference(sm1_AllDates,4,2)
MJMA_int1_AllDates 
#FJ-FA (slope)
FJFA_slope1_AllDates <- p_difference(sm1_AllDates,5,7)
FJFA_slope1_AllDates 
#FJ-MJ (slope)
FJMJ_slope1_AllDates <- p_difference(sm1_AllDates,5,6)
FJMJ_slope1_AllDates
#FJ-MA (slope)
FJMA_slope1_AllDates <- p_difference(sm1_AllDates,5,8)
FJMA_slope1_AllDates 
#FA-MJ (slope)
FAMJ_slope1_AllDates <- p_difference(sm1_AllDates,7,6)
FAMJ_slope1_AllDates 
#FA-MA (slope)
FAMA_slope1_AllDates <- p_difference(sm1_AllDates,7,8)
FAMA_slope1_AllDates
#MJ-MA (slope)
MJMA_slope1_AllDates <- p_difference(sm1_AllDates,6,8)
MJMA_slope1_AllDates

###Table
m1_AllDates_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                    "MJ-FJ (int)",
                                    "MJ-FA (int)", 
                                    "MA-FJ (int)", 
                                    "MA-FA (int)", 
                                    "MA-MJ (int)", 
                                    "FJ-FA (slope)",
                                    "FJ-MJ (slope)",
                                    "FJ-MA (slope)", 
                                    "FA-MJ (slope)", 
                                    "FA-MA (slope)", 
                                    "MJ-MA (slope)"),
                       Pvalue = c(round(FJFA_int1_AllDates$Pvalue, 2),
                                  round(FJMA_int1_AllDates$Pvalue, 2),
                                  round(FJMJ_int1_AllDates$Pvalue, 2), 
                                  round(FAMJ_int1_AllDates$Pvalue, 2), 
                                  round(FAMA_int1_AllDates$Pvalue, 2),
                                  round(MJMA_int1_AllDates$Pvalue, 2),
                                  round(FJFA_slope1_AllDates$Pvalue, 2),
                                  round(FJMA_slope1_AllDates$Pvalue, 2),
                                  round(FJMJ_slope1_AllDates$Pvalue, 2), 
                                  round(FAMJ_slope1_AllDates$Pvalue, 2), 
                                  round(FAMA_slope1_AllDates$Pvalue, 2),
                                  round(MJMA_slope1_AllDates$Pvalue, 2)), 
                       PostMode = c(round(FJFA_int1_AllDates$PostMode, 2),
                                    round(FJMA_int1_AllDates$PostMode, 2),
                                    round(FJMJ_int1_AllDates$PostMode, 2), 
                                    round(FAMJ_int1_AllDates$PostMode, 2), 
                                    round(FAMA_int1_AllDates$PostMode, 2),
                                    round(MJMA_int1_AllDates$PostMode, 2),
                                    round(FJFA_slope1_AllDates$PostMode, 2),
                                    round(FJMA_slope1_AllDates$PostMode, 2),
                                    round(FJMJ_slope1_AllDates$PostMode, 2), 
                                    round(FAMJ_slope1_AllDates$PostMode, 2), 
                                    round(FAMA_slope1_AllDates$PostMode, 2),
                                    round(MJMA_slope1_AllDates$PostMode, 2)), 
                       LowCrI = c(round(FJFA_int1_AllDates$LowCrI, 2),
                                  round(FJMA_int1_AllDates$LowCrI, 2),
                                  round(FJMJ_int1_AllDates$LowCrI, 2), 
                                  round(FAMJ_int1_AllDates$LowCrI, 2), 
                                  round(FAMA_int1_AllDates$LowCrI, 2),
                                  round(MJMA_int1_AllDates$LowCrI, 2),
                                  round(FJFA_slope1_AllDates$LowCrI, 2),
                                  round(FJMA_slope1_AllDates$LowCrI, 2),
                                  round(FJMJ_slope1_AllDates$LowCrI, 2), 
                                  round(FAMJ_slope1_AllDates$LowCrI, 2), 
                                  round(FAMA_slope1_AllDates$LowCrI, 2),
                                  round(MJMA_slope1_AllDates$LowCrI, 2)), 
                       HighCrI = c(round(FJFA_int1_AllDates$HighCrI, 2),
                                   round(FJMA_int1_AllDates$HighCrI, 2),
                                   round(FJMJ_int1_AllDates$HighCrI, 2), 
                                   round(FAMJ_int1_AllDates$HighCrI, 2), 
                                   round(FAMA_int1_AllDates$HighCrI, 2),
                                   round(MJMA_int1_AllDates$HighCrI, 2),
                                   round(FJFA_slope1_AllDates$HighCrI, 2),
                                   round(FJMA_slope1_AllDates$HighCrI, 2),
                                   round(FJMJ_slope1_AllDates$HighCrI, 2), 
                                   round(FAMJ_slope1_AllDates$HighCrI, 2), 
                                   round(FAMA_slope1_AllDates$HighCrI, 2),
                                   round(MJMA_slope1_AllDates$HighCrI, 2)), )



##Daily Feeder Visits----
m2_AllDates<-lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|CoreFeeder) + (1|TransponderHexCode), data = data_AllDates)

#Test assumptions
hist(resid(m2_AllDates))
plot(m2_AllDates)
#DHARMa assumptions test
sim_results_m2_AllDates <- simulateResiduals(m2_AllDates)
plot(sim_results_m2_AllDates)
test_results_m2_AllDates <- testResiduals(sim_results_m2_AllDates)
print(test_results_m2_AllDates)

summary(m2_AllDates)

sm2_AllDates<-sim(m2_AllDates, 1000)
mode2_AllDates<-posterior.mode(as.mcmc(sm2_AllDates@fixef))
HPD2_AllDates<-HPDinterval(as.mcmc(sm2_AllDates@fixef))
mode2_AllDates
HPD2_AllDates

#between THC variance
var_THC2_AllDates <- sm2_AllDates@ranef$TransponderHexCode
bvar_THC2_AllDates<-as.vector(apply(var_THC2_AllDates, 1, var))
bvar_THC2_AllDates<-as.mcmc(bvar_THC2_AllDates)
posterior.mode(bvar_THC2_AllDates) #1.961188       
HPDinterval(bvar_THC2_AllDates)  #(1.773369, 2.216626)

#between CoreFeeder variance
var_CF2_AllDates <- sm2_AllDates@ranef$CoreFeeder
bvar_CF2_AllDates<-as.vector(apply(var_CF2_AllDates, 1, var))
bvar_CF2_AllDates<-as.mcmc(bvar_CF2_AllDates)
posterior.mode(bvar_CF2_AllDates) #0.04887979         
HPDinterval(bvar_CF2_AllDates)  #(0.02223299, 0.0949385)

#between Residual variance
rvar2_AllDates<-sm2_AllDates@sigma^2
rvar2_AllDates<-as.mcmc(rvar2_AllDates)
posterior.mode(rvar2_AllDates) #2.47617       
HPDinterval(rvar2_AllDates) #(2.413479, 2.58774)


###Repeatability
rep2_AllDates <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|CoreFeeder) + (1|TransponderHexCode), grname = "TransponderHexCode", data = data_AllDates, 
                     datatype = "Gaussian", nboot = 1000, npermut = 0)
print(rep2_AllDates) # 0.504 (0.425, 0.567)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA (slope)
FA_slope2_AllDates <- p_zero(sm2_AllDates,7) #0.377

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_AllDates <- p_difference(sm2_AllDates,3,1)
FJFA_int2_AllDates 
#MJ-FJ (intercept)
FJMJ_int2_AllDates <- p_difference(sm2_AllDates,2,1)
FJMJ_int2_AllDates 
#MJ-FA (intercept)
FAMJ_int2_AllDates <- p_difference(sm2_AllDates,2,3)
FAMJ_int2_AllDates 
#MA-FJ (intercept)
FJMA_int2_AllDates <- p_difference(sm2_AllDates,4,1)
FJMA_int2_AllDates
#MA-FA (intercept)
FAMA_int2_AllDates <- p_difference(sm2_AllDates,4,3)
FAMA_int2_AllDates 
#MA-MJ (intercept)
MJMA_int2_AllDates <- p_difference(sm2_AllDates,4,2)
MJMA_int2_AllDates 
#FJ-FA (slope)
FJFA_slope2_AllDates <- p_difference(sm2_AllDates,5,7)
FJFA_slope2_AllDates 
#FJ-MJ (slope)
FJMJ_slope2_AllDates <- p_difference(sm2_AllDates,5,6)
FJMJ_slope2_AllDates
#FJ-MA (slope)
FJMA_slope2_AllDates <- p_difference(sm2_AllDates,5,8)
FJMA_slope2_AllDates 
#FA-MJ (slope)
FAMJ_slope2_AllDates <- p_difference(sm2_AllDates,7,6)
FAMJ_slope2_AllDates 
#FA-MA (slope)
FAMA_slope2_AllDates <- p_difference(sm2_AllDates,7,8)
FAMA_slope2_AllDates
#MJ-MA (slope)
MJMA_slope2_AllDates <- p_difference(sm2_AllDates,6,8)
MJMA_slope2_AllDates

###Table
m2_AllDates_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                             "MJ-FJ (int)",
                                             "MJ-FA (int)", 
                                             "MA-FJ (int)", 
                                             "MA-FA (int)", 
                                             "MA-MJ (int)", 
                                             "FJ-FA (slope)",
                                             "FJ-MJ (slope)",
                                             "FJ-MA (slope)", 
                                             "FA-MJ (slope)", 
                                             "FA-MA (slope)", 
                                             "MJ-MA (slope)"),
                                Pvalue = c(round(FJFA_int2_AllDates$Pvalue, 2),
                                           round(FJMA_int2_AllDates$Pvalue, 2),
                                           round(FJMJ_int2_AllDates$Pvalue, 2), 
                                           round(FAMJ_int2_AllDates$Pvalue, 2), 
                                           round(FAMA_int2_AllDates$Pvalue, 2),
                                           round(MJMA_int2_AllDates$Pvalue, 2),
                                           round(FJFA_slope2_AllDates$Pvalue, 2),
                                           round(FJMA_slope2_AllDates$Pvalue, 2),
                                           round(FJMJ_slope2_AllDates$Pvalue, 2), 
                                           round(FAMJ_slope2_AllDates$Pvalue, 2), 
                                           round(FAMA_slope2_AllDates$Pvalue, 2),
                                           round(MJMA_slope2_AllDates$Pvalue, 2)), 
                                PostMode = c(round(FJFA_int2_AllDates$PostMode, 2),
                                             round(FJMA_int2_AllDates$PostMode, 2),
                                             round(FJMJ_int2_AllDates$PostMode, 2), 
                                             round(FAMJ_int2_AllDates$PostMode, 2), 
                                             round(FAMA_int2_AllDates$PostMode, 2),
                                             round(MJMA_int2_AllDates$PostMode, 2),
                                             round(FJFA_slope2_AllDates$PostMode, 2),
                                             round(FJMA_slope2_AllDates$PostMode, 2),
                                             round(FJMJ_slope2_AllDates$PostMode, 2), 
                                             round(FAMJ_slope2_AllDates$PostMode, 2), 
                                             round(FAMA_slope2_AllDates$PostMode, 2),
                                             round(MJMA_slope2_AllDates$PostMode, 2)), 
                                LowCrI = c(round(FJFA_int2_AllDates$LowCrI, 2),
                                           round(FJMA_int2_AllDates$LowCrI, 2),
                                           round(FJMJ_int2_AllDates$LowCrI, 2), 
                                           round(FAMJ_int2_AllDates$LowCrI, 2), 
                                           round(FAMA_int2_AllDates$LowCrI, 2),
                                           round(MJMA_int2_AllDates$LowCrI, 2),
                                           round(FJFA_slope2_AllDates$LowCrI, 2),
                                           round(FJMA_slope2_AllDates$LowCrI, 2),
                                           round(FJMJ_slope2_AllDates$LowCrI, 2), 
                                           round(FAMJ_slope2_AllDates$LowCrI, 2), 
                                           round(FAMA_slope2_AllDates$LowCrI, 2),
                                           round(MJMA_slope2_AllDates$LowCrI, 2)), 
                                HighCrI = c(round(FJFA_int2_AllDates$HighCrI, 2),
                                            round(FJMA_int2_AllDates$HighCrI, 2),
                                            round(FJMJ_int2_AllDates$HighCrI, 2), 
                                            round(FAMJ_int2_AllDates$HighCrI, 2), 
                                            round(FAMA_int2_AllDates$HighCrI, 2),
                                            round(MJMA_int2_AllDates$HighCrI, 2),
                                            round(FJFA_slope2_AllDates$HighCrI, 2),
                                            round(FJMA_slope2_AllDates$HighCrI, 2),
                                            round(FJMJ_slope2_AllDates$HighCrI, 2), 
                                            round(FAMJ_slope2_AllDates$HighCrI, 2), 
                                            round(FAMA_slope2_AllDates$HighCrI, 2),
                                            round(MJMA_slope2_AllDates$HighCrI, 2)), )

##Figure S1----
data_AllDates2 <- subset(data_AllDates, select = c(Age_Sex, VisitDate, AvgTemp, VisitCount))
data_AllDates2_sumVC.AgeSex<-aggregate(.~ Age_Sex + VisitDate + AvgTemp, data_AllDates2, FUN= sum)
colnames(data_AllDates2_sumVC.AgeSex)[colnames(data_AllDates2_sumVC.AgeSex) == 'VisitCount'] <- 'TotalVisitCount'

data_AllDates2_sumVC <- subset(data_AllDates2_sumVC.AgeSex, select = -c(Age_Sex)) %>% distinct()

#Add in the missing dates (Feb 15-23)
ExtraDates <- data.table(VisitDate = c(as.character("2023-02-15"), as.character("2023-02-16"), as.character("2023-02-17"), 
                                       as.character("2023-02-18"), as.character("2023-02-19"), as.character("2023-02-20"), 
                                       as.character("2023-02-21"), as.character("2023-02-22"), as.character("2023-02-23")),
                         TotalVisitCount = c(NA,NA,NA,NA,NA,NA,NA,NA,NA),
                         AvgTemp = c(NA,NA,NA,NA,NA,NA,NA,NA,NA))

FeedingRateAllDays <- full_join(data_AllDates2_sumVC, ExtraDates, by= c('VisitDate', 'TotalVisitCount', 'AvgTemp')) 

#Create the graph scale for AvgTemp
ylim.tvc <- c(0, 12000)
ylim.temp <- c(-30, 10)
b <- diff(ylim.tvc)/diff(ylim.temp)
a <- ylim.tvc[1] - b*ylim.temp[1]

#Create plot with two y-axes
## Figure saved at 2000x800 pixels 
theme_set(theme_classic())
theme_update(legend.title=element_text(size = 32),legend.position="right",legend.text = element_text(size = 32),
             axis.title = element_text(size=32), axis.text = element_text(size=28))

FeedingRateAllDays$VisitDate <- as.Date(FeedingRateAllDays$VisitDate, format = "%Y-%m-%d")

Fig.S1 = ggplot(FeedingRateAllDays) +
  geom_col(aes(VisitDate, TotalVisitCount), fill = "grey") +
  geom_point(aes(x=VisitDate, y = a + AvgTemp*b), color = "black", size = 4) +
  scale_y_continuous("Total Visit Count\n", limits = c(0,12000), expand = c(0, 0), breaks=seq(0,12000,by=1500), sec.axis = sec_axis(~ (. - a)/b, name = "Average \nTemperature (°C)\n", breaks=seq(-30,10,by=5))) +
  scale_x_date(name = '\nVisit Date', date_breaks = '1 week', expand = c(0,0))+
  labs(title = "\n")+
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))

Fig.S1


#*Off-Territory Model Comparison*----
##IxE----
m1_IE0<-glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (0+TempL0|TransponderHexCode) + (1|CoreFeeder), data = data_MS, family=binomial,
              control=glmerControl(optimizer="bobyqa")) #uncorrelated random slopes/intercepts
m1_IE1<-glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1+TempL0|TransponderHexCode) + (1|CoreFeeder), data = data_MS, family=binomial,
              control=glmerControl(optimizer="bobyqa")) #correlated random slopes/intercepts

anova(m1, m1_IE0, m1_IE1) #support for IxE correlated random slopes/intercepts as final model

overdisp_fun(m1_IE1) #model is not overdispersed

#DHARMa assumption tests
sim_results_m1_IE <- simulateResiduals(m1_IE1)
plot(sim_results_m1_IE)
test_results_m1_IE <- testResiduals(sim_results_m1_IE)
print(test_results_m1_IE)

summary(m1_IE1) 

sm1_IE<-sim(m1_IE1, 1000)
mode1_IE<-posterior.mode(as.mcmc(sm1_IE@fixef))
HPD1_IE<-HPDinterval(as.mcmc(sm1_IE@fixef))
mode1_IE #estimates
HPD1_IE #CrIs

#between Bird ID variance
var_THC1_IE <- sm1_IE@ranef$TransponderHexCode
bvar_THC1_IE<-as.vector(apply(var_THC1_IE, 1, var))
bvar_THC1_IE<-as.mcmc(bvar_THC1_IE)
posterior.mode(bvar_THC1_IE) #0.641498         
HPDinterval(bvar_THC1_IE)  #(0.3194087, 4.860113)

#between CoreFeeder variance
var_CF1_IE <- sm1_IE@ranef$CoreFeeder
bvar_CF1_IE<-as.vector(apply(var_CF1_IE, 1, var))
bvar_CF1_IE<-as.mcmc(bvar_CF1_IE)
posterior.mode(bvar_CF1_IE) #12.68205          
HPDinterval(bvar_CF1_IE)  #(3.180593 31.21683)

#Repeatability
rep1<-bvar_THC1_IE / (bvar_THC1_IE + (pi^2)/3)
posterior.mode(rep1) #0.1814486      
HPDinterval(rep1) #(0.1051981, 0.6043666)

####Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (intercept)
FJ_int1_IE <- p_zero(sm1_IE,1) #0.038
#FA (intercept)
FA_int1_IE <- p_zero(sm1_IE,3) #0.057
#MJ (intercept)
MJ_int1_IE <- p_zero(sm1_IE,2) #0.084
#MJ (slope)
MJ_slope1_IE <- p_zero(sm1_IE,6) #0.165
#MA (slope)
MA_slope1_IE <- p_zero(sm1_IE,8) #0.238


###Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_IE <- p_difference(sm1_IE,3,1)
FJFA_int1_IE 
#MJ-FJ (intercept)
FJMJ_int1_IE <- p_difference(sm1_IE,2,1)
FJMJ_int1_IE 
#MJ-FA (intercept)
FAMJ_int1_IE <- p_difference(sm1_IE,2,3)
FAMJ_int1_IE 
#MA-FJ (intercept)
FJMA_int1_IE <- p_difference(sm1_IE,4,1)
FJMA_int1_IE
#MA-FA (intercept)
FAMA_int1_IE <- p_difference(sm1_IE,4,3)
FAMA_int1_IE 
#MA-MJ (intercept)
MJMA_int1_IE <- p_difference(sm1_IE,4,2)
MJMA_int1_IE 
#FJ-FA (slope)
FJFA_slope1_IE <- p_difference(sm1_IE,5,7)
FJFA_slope1_IE 
#FJ-MJ (slope)
FJMJ_slope1_IE <- p_difference(sm1_IE,5,6)
FJMJ_slope1_IE
#FJ-MA (slope)
FJMA_slope1_IE <- p_difference(sm1_IE,5,8)
FJMA_slope1_IE 
#FA-MJ (slope)
FAMJ_slope1_IE <- p_difference(sm1_IE,7,6)
FAMJ_slope1_IE 
#FA-MA (slope)
FAMA_slope1_IE <- p_difference(sm1_IE,7,8)
FAMA_slope1_IE
#MJ-MA (slope)
MJMA_slope1_IE <- p_difference(sm1_IE,6,8)
MJMA_slope1_IE

###Table
m1_IE_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_IE$Pvalue, 2),
                                     round(FJMA_int1_IE$Pvalue, 2),
                                     round(FJMJ_int1_IE$Pvalue, 2), 
                                     round(FAMJ_int1_IE$Pvalue, 2), 
                                     round(FAMA_int1_IE$Pvalue, 2),
                                     round(MJMA_int1_IE$Pvalue, 2),
                                     round(FJFA_slope1_IE$Pvalue, 2),
                                     round(FJMA_slope1_IE$Pvalue, 2),
                                     round(FJMJ_slope1_IE$Pvalue, 2), 
                                     round(FAMJ_slope1_IE$Pvalue, 2), 
                                     round(FAMA_slope1_IE$Pvalue, 2),
                                     round(MJMA_slope1_IE$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_IE$PostMode, 2),
                                       round(FJMA_int1_IE$PostMode, 2),
                                       round(FJMJ_int1_IE$PostMode, 2), 
                                       round(FAMJ_int1_IE$PostMode, 2), 
                                       round(FAMA_int1_IE$PostMode, 2),
                                       round(MJMA_int1_IE$PostMode, 2),
                                       round(FJFA_slope1_IE$PostMode, 2),
                                       round(FJMA_slope1_IE$PostMode, 2),
                                       round(FJMJ_slope1_IE$PostMode, 2), 
                                       round(FAMJ_slope1_IE$PostMode, 2), 
                                       round(FAMA_slope1_IE$PostMode, 2),
                                       round(MJMA_slope1_IE$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_IE$LowCrI, 2),
                                     round(FJMA_int1_IE$LowCrI, 2),
                                     round(FJMJ_int1_IE$LowCrI, 2), 
                                     round(FAMJ_int1_IE$LowCrI, 2), 
                                     round(FAMA_int1_IE$LowCrI, 2),
                                     round(MJMA_int1_IE$LowCrI, 2),
                                     round(FJFA_slope1_IE$LowCrI, 2),
                                     round(FJMA_slope1_IE$LowCrI, 2),
                                     round(FJMJ_slope1_IE$LowCrI, 2), 
                                     round(FAMJ_slope1_IE$LowCrI, 2), 
                                     round(FAMA_slope1_IE$LowCrI, 2),
                                     round(MJMA_slope1_IE$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_IE$HighCrI, 2),
                                      round(FJMA_int1_IE$HighCrI, 2),
                                      round(FJMJ_int1_IE$HighCrI, 2), 
                                      round(FAMJ_int1_IE$HighCrI, 2), 
                                      round(FAMA_int1_IE$HighCrI, 2),
                                      round(MJMA_int1_IE$HighCrI, 2),
                                      round(FJFA_slope1_IE$HighCrI, 2),
                                      round(FJMA_slope1_IE$HighCrI, 2),
                                      round(FJMJ_slope1_IE$HighCrI, 2), 
                                      round(FAMJ_slope1_IE$HighCrI, 2), 
                                      round(FAMA_slope1_IE$HighCrI, 2),
                                      round(MJMA_slope1_IE$HighCrI, 2)), )

#*Daily Feeder Visit Model Comparisons*----
##Non-transformed LMM----
m2<-lmer(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|CoreFeeder) + (1|TransponderHexCode), data = data_MS)
summary(m2)

#DHARMa assumption tests
sim_results_m2 <- simulateResiduals(m2)
plot(sim_results_m2)
test_results_m2 <- testResiduals(sim_results_m2)
print(test_results_m2)

sm2<-sim(m2, 1000)
mode2<-posterior.mode(as.mcmc(sm2@fixef))
HPD2<-HPDinterval(as.mcmc(sm2@fixef))
mode2 #estimates
HPD2 #CrIs

#between Bird ID variance
var_THC2 <- sm2@ranef$TransponderHexCode
bvar_THC2<-as.vector(apply(var_THC2, 1, var))
bvar_THC2<-as.mcmc(bvar_THC2)
posterior.mode(bvar_THC2) #568.6905    
HPDinterval(bvar_THC2)  #(518.6291, 651.3315)

#between CoreFeeder variance
var_CF2 <- sm2@ranef$CoreFeeder
bvar_CF2<-as.vector(apply(var_CF2, 1, var))
bvar_CF2<-as.mcmc(bvar_CF2)
posterior.mode(bvar_CF2) #21.34174     
HPDinterval(bvar_CF2)  #(11.50437, 35.24662)

#between Residual variance
rvar2<-sm2@sigma^2
rvar2<-as.mcmc(rvar2)
posterior.mode(rvar2) #511.1889     
HPDinterval(rvar2) #(489.9393, 529.4586)

#Repeatability
rep2 <- rpt(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_MS, 
            datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2) #0.51 (0.426, 0.575)


###Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2 <- p_difference(sm2,3,1)
FJFA_int2 
#MJ-FJ (intercept)
FJMJ_int2 <- p_difference(sm2,2,1)
FJMJ_int2 
#MJ-FA (intercept)
FAMJ_int2 <- p_difference(sm2,2,3)
FAMJ_int2 
#MA-FJ (intercept)
FJMA_int2 <- p_difference(sm2,4,1)
FJMA_int2
#MA-FA (intercept)
FAMA_int2 <- p_difference(sm2,4,3)
FAMA_int2 
#MA-MJ (intercept)
MJMA_int2 <- p_difference(sm2,4,2)
MJMA_int2 
#FJ-FA (slope)
FJFA_slope2 <- p_difference(sm2,5,7)
FJFA_slope2 
#FJ-MJ (slope)
FJMJ_slope2 <- p_difference(sm2,5,6)
FJMJ_slope2
#FJ-MA (slope)
FJMA_slope2 <- p_difference(sm2,5,8)
FJMA_slope2 
#FA-MJ (slope)
FAMJ_slope2 <- p_difference(sm2,7,6)
FAMJ_slope2 
#FA-MA (slope)
FAMA_slope2 <- p_difference(sm2,7,8)
FAMA_slope2
#MJ-MA (slope)
MJMA_slope2 <- p_difference(sm2,6,8)
MJMA_slope2

###Table
m2_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                    "MJ-FJ (int)",
                                    "MJ-FA (int)", 
                                    "MA-FJ (int)", 
                                    "MA-FA (int)", 
                                    "MA-MJ (int)", 
                                    "FJ-FA (slope)",
                                    "FJ-MJ (slope)",
                                    "FJ-MA (slope)", 
                                    "FA-MJ (slope)", 
                                    "FA-MA (slope)", 
                                    "MJ-MA (slope)"),
                       Pvalue = c(round(FJFA_int2$Pvalue, 2),
                                  round(FJMA_int2$Pvalue, 2),
                                  round(FJMJ_int2$Pvalue, 2), 
                                  round(FAMJ_int2$Pvalue, 2), 
                                  round(FAMA_int2$Pvalue, 2),
                                  round(MJMA_int2$Pvalue, 2),
                                  round(FJFA_slope2$Pvalue, 2),
                                  round(FJMA_slope2$Pvalue, 2),
                                  round(FJMJ_slope2$Pvalue, 2), 
                                  round(FAMJ_slope2$Pvalue, 2), 
                                  round(FAMA_slope2$Pvalue, 2),
                                  round(MJMA_slope2$Pvalue, 2)), 
                       PostMode = c(round(FJFA_int2$PostMode, 2),
                                    round(FJMA_int2$PostMode, 2),
                                    round(FJMJ_int2$PostMode, 2), 
                                    round(FAMJ_int2$PostMode, 2), 
                                    round(FAMA_int2$PostMode, 2),
                                    round(MJMA_int2$PostMode, 2),
                                    round(FJFA_slope2$PostMode, 2),
                                    round(FJMA_slope2$PostMode, 2),
                                    round(FJMJ_slope2$PostMode, 2), 
                                    round(FAMJ_slope2$PostMode, 2), 
                                    round(FAMA_slope2$PostMode, 2),
                                    round(MJMA_slope2$PostMode, 2)), 
                       LowCrI = c(round(FJFA_int2$LowCrI, 2),
                                  round(FJMA_int2$LowCrI, 2),
                                  round(FJMJ_int2$LowCrI, 2), 
                                  round(FAMJ_int2$LowCrI, 2), 
                                  round(FAMA_int2$LowCrI, 2),
                                  round(MJMA_int2$LowCrI, 2),
                                  round(FJFA_slope2$LowCrI, 2),
                                  round(FJMA_slope2$LowCrI, 2),
                                  round(FJMJ_slope2$LowCrI, 2), 
                                  round(FAMJ_slope2$LowCrI, 2), 
                                  round(FAMA_slope2$LowCrI, 2),
                                  round(MJMA_slope2$LowCrI, 2)), 
                       HighCrI = c(round(FJFA_int2$HighCrI, 2),
                                   round(FJMA_int2$HighCrI, 2),
                                   round(FJMJ_int2$HighCrI, 2), 
                                   round(FAMJ_int2$HighCrI, 2), 
                                   round(FAMA_int2$HighCrI, 2),
                                   round(MJMA_int2$HighCrI, 2),
                                   round(FJFA_slope2$HighCrI, 2),
                                   round(FJMA_slope2$HighCrI, 2),
                                   round(FJMJ_slope2$HighCrI, 2), 
                                   round(FAMJ_slope2$HighCrI, 2), 
                                   round(FAMA_slope2$HighCrI, 2),
                                   round(MJMA_slope2$HighCrI, 2)), )

##Non-transformed LMM IxE----
m2_IE1<-lmer(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + (1+TempL0|TransponderHexCode) + (1|CoreFeeder), data = data_MS) #correlated random slopes/intercepts
summary(m2_IE1)

m2_IE0<-lmer(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + (0+TempL0|TransponderHexCode) + (1|CoreFeeder), data = data_MS) #correlated random slopes/intercepts
summary(m2_IE0)

anova(m2, m2_IE1, m2_IE0) #support for the correlated IxE model

#DHARMa assumption tests
sim_results_m2_IE <- simulateResiduals(m2_IE1)
plot(sim_results_m2_IE) 
test_results_m2_IE <- testResiduals(sim_results_m1_IE)
print(test_results_m2_IE)

sm2_IE<-sim(m2_IE1, 1000)
mode2_IE<-posterior.mode(as.mcmc(sm2_IE@fixef))
HPD2_IE<-HPDinterval(as.mcmc(sm2_IE@fixef))
mode2_IE #estimates
HPD2_IE #CrIs

#between Bird ID variance
var_THC2_IE <- sm2_IE@ranef$TransponderHexCode
bvar_THC2_IE<-as.vector(apply(var_THC2_IE, 1, var))
bvar_THC2_IE<-as.mcmc(bvar_THC2_IE)
posterior.mode(bvar_THC2_IE) #-66.42056    
HPDinterval(bvar_THC2_IE)  #(-118.1958, 552.5511)

#between CoreFeeder variance
var_CF2_IE <- sm2_IE@ranef$CoreFeeder
bvar_CF2_IE<-as.vector(apply(var_CF2_IE, 1, var))
bvar_CF2_IE<-as.mcmc(bvar_CF2_IE)
posterior.mode(bvar_CF2_IE) #1.668238      
HPDinterval(bvar_CF2_IE)  #(0.5009383, 5.885729)

#between Residual variance
rvar2_IE<-sm2_IE@sigma^2
rvar2_IE<-as.mcmc(rvar2_IE)
posterior.mode(rvar2_IE) #439.4082      
HPDinterval(rvar2_IE) #(428.6462, 460.9707)

#Repeatability
rep2_IE<-bvar_THC2_IE / (bvar_THC2_IE + rvar2_IE)
posterior.mode(rep2_IE) #0.4833257     
HPDinterval(rep2_IE) #(-0.3075033, 0.5695643)

###Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_IE <- p_difference(sm2_IE,3,1)
FJFA_int2_IE 
#MJ-FJ (intercept)
FJMJ_int2_IE <- p_difference(sm2_IE,2,1)
FJMJ_int2_IE 
#MJ-FA (intercept)
FAMJ_int2_IE <- p_difference(sm2_IE,2,3)
FAMJ_int2_IE 
#MA-FJ (intercept)
FJMA_int2_IE <- p_difference(sm2_IE,4,1)
FJMA_int2_IE
#MA-FA (intercept)
FAMA_int2_IE <- p_difference(sm2_IE,4,3)
FAMA_int2_IE 
#MA-MJ (intercept)
MJMA_int2_IE <- p_difference(sm2_IE,4,2)
MJMA_int2_IE 
#FJ-FA (slope)
FJFA_slope2_IE <- p_difference(sm2_IE,5,7)
FJFA_slope2_IE 
#FJ-MJ (slope)
FJMJ_slope2_IE <- p_difference(sm2_IE,5,6)
FJMJ_slope2_IE
#FJ-MA (slope)
FJMA_slope2_IE <- p_difference(sm2_IE,5,8)
FJMA_slope2_IE 
#FA-MJ (slope)
FAMJ_slope2_IE <- p_difference(sm2_IE,7,6)
FAMJ_slope2_IE 
#FA-MA (slope)
FAMA_slope2_IE <- p_difference(sm2_IE,7,8)
FAMA_slope2_IE
#MJ-MA (slope)
MJMA_slope2_IE <- p_difference(sm2_IE,6,8)
MJMA_slope2_IE

###Table
m2_IE_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_IE$Pvalue, 2),
                                     round(FJMA_int2_IE$Pvalue, 2),
                                     round(FJMJ_int2_IE$Pvalue, 2), 
                                     round(FAMJ_int2_IE$Pvalue, 2), 
                                     round(FAMA_int2_IE$Pvalue, 2),
                                     round(MJMA_int2_IE$Pvalue, 2),
                                     round(FJFA_slope2_IE$Pvalue, 2),
                                     round(FJMA_slope2_IE$Pvalue, 2),
                                     round(FJMJ_slope2_IE$Pvalue, 2), 
                                     round(FAMJ_slope2_IE$Pvalue, 2), 
                                     round(FAMA_slope2_IE$Pvalue, 2),
                                     round(MJMA_slope2_IE$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_IE$PostMode, 2),
                                       round(FJMA_int2_IE$PostMode, 2),
                                       round(FJMJ_int2_IE$PostMode, 2), 
                                       round(FAMJ_int2_IE$PostMode, 2), 
                                       round(FAMA_int2_IE$PostMode, 2),
                                       round(MJMA_int2_IE$PostMode, 2),
                                       round(FJFA_slope2_IE$PostMode, 2),
                                       round(FJMA_slope2_IE$PostMode, 2),
                                       round(FJMJ_slope2_IE$PostMode, 2), 
                                       round(FAMJ_slope2_IE$PostMode, 2), 
                                       round(FAMA_slope2_IE$PostMode, 2),
                                       round(MJMA_slope2_IE$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_IE$LowCrI, 2),
                                     round(FJMA_int2_IE$LowCrI, 2),
                                     round(FJMJ_int2_IE$LowCrI, 2), 
                                     round(FAMJ_int2_IE$LowCrI, 2), 
                                     round(FAMA_int2_IE$LowCrI, 2),
                                     round(MJMA_int2_IE$LowCrI, 2),
                                     round(FJFA_slope2_IE$LowCrI, 2),
                                     round(FJMA_slope2_IE$LowCrI, 2),
                                     round(FJMJ_slope2_IE$LowCrI, 2), 
                                     round(FAMJ_slope2_IE$LowCrI, 2), 
                                     round(FAMA_slope2_IE$LowCrI, 2),
                                     round(MJMA_slope2_IE$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_IE$HighCrI, 2),
                                      round(FJMA_int2_IE$HighCrI, 2),
                                      round(FJMJ_int2_IE$HighCrI, 2), 
                                      round(FAMJ_int2_IE$HighCrI, 2), 
                                      round(FAMA_int2_IE$HighCrI, 2),
                                      round(MJMA_int2_IE$HighCrI, 2),
                                      round(FJFA_slope2_IE$HighCrI, 2),
                                      round(FJMA_slope2_IE$HighCrI, 2),
                                      round(FJMJ_slope2_IE$HighCrI, 2), 
                                      round(FAMJ_slope2_IE$HighCrI, 2), 
                                      round(FAMA_slope2_IE$HighCrI, 2),
                                      round(MJMA_slope2_IE$HighCrI, 2)), )

##Negative binomial----
m2_nb<-glmer.nb(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|CoreFeeder) + (1|TransponderHexCode), data = data_MS)
summary(m2_nb)

#DHARMa assumption tests
sim_results_m2_nb <- simulateResiduals(m2_nb)
plot(sim_results_m2_nb) 
test_results_m2_nb <- testResiduals(sim_results_m2_nb)
print(test_results_m2_nb)

sm2_nb<-sim(m2_nb, 1000)
mode2_nb<-posterior.mode(as.mcmc(sm2_nb@fixef))
HPD2_nb<-HPDinterval(as.mcmc(sm2_nb@fixef))
mode2_nb
HPD2_nb

#between Bird ID variance
var_THC2_nb <- sm2_nb@ranef$TransponderHexCode
bvar_THC2_nb<-as.vector(apply(var_THC2_nb, 1, var))
bvar_THC2_nb<-as.mcmc(bvar_THC2_nb)
posterior.mode(bvar_THC2_nb) #0.1272741     
HPDinterval(bvar_THC2_nb)  #(0.1152456, 0.1424917)

#between CoreFeeder variance
var_CF2_nb <- sm2_nb@ranef$CoreFeeder
bvar_CF2_nb<-as.vector(apply(var_CF2_nb, 1, var))
bvar_CF2_nb<-as.mcmc(bvar_CF2_nb)
posterior.mode(bvar_CF2_nb) #0.002606813      
HPDinterval(bvar_CF2_nb)  #(0.00133815, 0.005047965)

#Repeatability
rep2_nb<-bvar_THC2_nb / (bvar_THC2_nb + (pi^2)/3)
posterior.mode(rep2_nb) #0.03725722
HPDinterval(rep2_nb) #(0.03384487, 0.0415142)

###Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_nb <- p_difference(sm2_nb,3,1)
FJFA_int2_nb 
#MJ-FJ (intercept)
FJMJ_int2_nb <- p_difference(sm2_nb,2,1)
FJMJ_int2_nb 
#MJ-FA (intercept)
FAMJ_int2_nb <- p_difference(sm2_nb,2,3)
FAMJ_int2_nb 
#MA-FJ (intercept)
FJMA_int2_nb <- p_difference(sm2_nb,4,1)
FJMA_int2_nb
#MA-FA (intercept)
FAMA_int2_nb <- p_difference(sm2_nb,4,3)
FAMA_int2_nb 
#MA-MJ (intercept)
MJMA_int2_nb <- p_difference(sm2_nb,4,2)
MJMA_int2_nb 
#FJ-FA (slope)
FJFA_slope2_nb <- p_difference(sm2_nb,5,7)
FJFA_slope2_nb 
#FJ-MJ (slope)
FJMJ_slope2_nb <- p_difference(sm2_nb,5,6)
FJMJ_slope2_nb
#FJ-MA (slope)
FJMA_slope2_nb <- p_difference(sm2_nb,5,8)
FJMA_slope2_nb 
#FA-MJ (slope)
FAMJ_slope2_nb <- p_difference(sm2_nb,7,6)
FAMJ_slope2_nb 
#FA-MA (slope)
FAMA_slope2_nb <- p_difference(sm2_nb,7,8)
FAMA_slope2_nb
#MJ-MA (slope)
MJMA_slope2_nb <- p_difference(sm2_nb,6,8)
MJMA_slope2_nb

###Table
m2_nb_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_nb$Pvalue, 2),
                                     round(FJMA_int2_nb$Pvalue, 2),
                                     round(FJMJ_int2_nb$Pvalue, 2), 
                                     round(FAMJ_int2_nb$Pvalue, 2), 
                                     round(FAMA_int2_nb$Pvalue, 2),
                                     round(MJMA_int2_nb$Pvalue, 2),
                                     round(FJFA_slope2_nb$Pvalue, 2),
                                     round(FJMA_slope2_nb$Pvalue, 2),
                                     round(FJMJ_slope2_nb$Pvalue, 2), 
                                     round(FAMJ_slope2_nb$Pvalue, 2), 
                                     round(FAMA_slope2_nb$Pvalue, 2),
                                     round(MJMA_slope2_nb$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_nb$PostMode, 2),
                                       round(FJMA_int2_nb$PostMode, 2),
                                       round(FJMJ_int2_nb$PostMode, 2), 
                                       round(FAMJ_int2_nb$PostMode, 2), 
                                       round(FAMA_int2_nb$PostMode, 2),
                                       round(MJMA_int2_nb$PostMode, 2),
                                       round(FJFA_slope2_nb$PostMode, 2),
                                       round(FJMA_slope2_nb$PostMode, 2),
                                       round(FJMJ_slope2_nb$PostMode, 2), 
                                       round(FAMJ_slope2_nb$PostMode, 2), 
                                       round(FAMA_slope2_nb$PostMode, 2),
                                       round(MJMA_slope2_nb$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_nb$LowCrI, 2),
                                     round(FJMA_int2_nb$LowCrI, 2),
                                     round(FJMJ_int2_nb$LowCrI, 2), 
                                     round(FAMJ_int2_nb$LowCrI, 2), 
                                     round(FAMA_int2_nb$LowCrI, 2),
                                     round(MJMA_int2_nb$LowCrI, 2),
                                     round(FJFA_slope2_nb$LowCrI, 2),
                                     round(FJMA_slope2_nb$LowCrI, 2),
                                     round(FJMJ_slope2_nb$LowCrI, 2), 
                                     round(FAMJ_slope2_nb$LowCrI, 2), 
                                     round(FAMA_slope2_nb$LowCrI, 2),
                                     round(MJMA_slope2_nb$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_nb$HighCrI, 2),
                                      round(FJMA_int2_nb$HighCrI, 2),
                                      round(FJMJ_int2_nb$HighCrI, 2), 
                                      round(FAMJ_int2_nb$HighCrI, 2), 
                                      round(FAMA_int2_nb$HighCrI, 2),
                                      round(MJMA_int2_nb$HighCrI, 2),
                                      round(FJFA_slope2_nb$HighCrI, 2),
                                      round(FJMA_slope2_nb$HighCrI, 2),
                                      round(FJMJ_slope2_nb$HighCrI, 2), 
                                      round(FAMJ_slope2_nb$HighCrI, 2), 
                                      round(FAMA_slope2_nb$HighCrI, 2),
                                      round(MJMA_slope2_nb$HighCrI, 2)), )


##Quadratic----
data_MS$TempC <- data_MS$AvgTemp-mean(data_MS$AvgTemp)
data_MS$TempC_sqd <- data_MS$TempC^2
data_MS$Temp_std <- data_MS$TempC_sqd/(2*sd(data_MS$TempC_sqd)) #squared and standardized temperature

m2_quad <- lmer(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + Age_Sex:Temp_std + (1|TransponderHexCode) + (1|CoreFeeder), data = data_MS)
summary(m2_quad)

#DHARMa assumption tests
sim_results_m2_quad <- simulateResiduals(m2_quad)
plot(sim_results_m2_quad)
test_results_m2_quad <- testResiduals(sim_results_m2_quad)
print(test_results_m2_quad)

sm2_quad<-sim(m2_quad, 1000)
mode2_m2_quad<-posterior.mode(as.mcmc(sm2_quad@fixef))
HPD2_m2_quad<-HPDinterval(as.mcmc(sm2_quad@fixef))
mode2_m2_quad #estimates
HPD2_m2_quad #CrIs

#between Bird ID variance
var_THC2_quad <- sm2_quad@ranef$TransponderHexCode
bvar_THC2_quad<-as.vector(apply(var_THC2_quad, 1, var))
bvar_THC2_quad<-as.mcmc(bvar_THC2_quad)
posterior.mode(bvar_THC2_quad) #586.5286     
HPDinterval(bvar_THC2_quad)  #(525.0584, 650.1364)

#between CoreFeeder variance
var_CF2_quad <- sm2_quad@ranef$CoreFeeder
bvar_CF2_quad<-as.vector(apply(var_CF2_quad, 1, var))
bvar_CF2_quad<-as.mcmc(bvar_CF2_quad)
posterior.mode(bvar_CF2_quad) #19.91527       
HPDinterval(bvar_CF2_quad)  #(11.48957, 36.84433)

#between Residual variance
rvar2_quad<-sm2_quad@sigma^2
rvar2_quad<-as.mcmc(rvar2_quad)
posterior.mode(rvar2_quad) #482.3876       
HPDinterval(rvar2_quad) #(464.343, 500.5306)

#Repeatability
rep2_quad <- rpt(VisitCount ~ -1 + Age_Sex + Age_Sex:TempL0 + Age_Sex:Temp_std + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_MS, 
                 datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_quad) #0.52 (0.44, 0.59)

###Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_quad <- p_difference(sm2_quad,3,1)
FJFA_int2_quad 
#MJ-FJ (intercept)
FJMJ_int2_quad <- p_difference(sm2_quad,2,1)
FJMJ_int2_quad 
#MJ-FA (intercept)
FAMJ_int2_quad <- p_difference(sm2_quad,2,3)
FAMJ_int2_quad 
#MA-FJ (intercept)
FJMA_int2_quad <- p_difference(sm2_quad,4,1)
FJMA_int2_quad
#MA-FA (intercept)
FAMA_int2_quad <- p_difference(sm2_quad,4,3)
FAMA_int2_quad 
#MA-MJ (intercept)
MJMA_int2_quad <- p_difference(sm2_quad,4,2)
MJMA_int2_quad 
#FJ-FA (slope)
FJFA_slope2_quad <- p_difference(sm2_quad,5,7)
FJFA_slope2_quad 
#FJ-MJ (slope)
FJMJ_slope2_quad <- p_difference(sm2_quad,5,6)
FJMJ_slope2_quad
#FJ-MA (slope)
FJMA_slope2_quad <- p_difference(sm2_quad,5,8)
FJMA_slope2_quad 
#FA-MJ (slope)
FAMJ_slope2_quad <- p_difference(sm2_quad,7,6)
FAMJ_slope2_quad 
#FA-MA (slope)
FAMA_slope2_quad <- p_difference(sm2_quad,7,8)
FAMA_slope2_quad
#MJ-MA (slope)
MJMA_slope2_quad <- p_difference(sm2_quad,6,8)
MJMA_slope2_quad

###Table
m2_quad_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                         "MJ-FJ (int)",
                                         "MJ-FA (int)", 
                                         "MA-FJ (int)", 
                                         "MA-FA (int)", 
                                         "MA-MJ (int)", 
                                         "FJ-FA (slope)",
                                         "FJ-MJ (slope)",
                                         "FJ-MA (slope)", 
                                         "FA-MJ (slope)", 
                                         "FA-MA (slope)", 
                                         "MJ-MA (slope)"),
                            Pvalue = c(round(FJFA_int2_quad$Pvalue, 2),
                                       round(FJMA_int2_quad$Pvalue, 2),
                                       round(FJMJ_int2_quad$Pvalue, 2), 
                                       round(FAMJ_int2_quad$Pvalue, 2), 
                                       round(FAMA_int2_quad$Pvalue, 2),
                                       round(MJMA_int2_quad$Pvalue, 2),
                                       round(FJFA_slope2_quad$Pvalue, 2),
                                       round(FJMA_slope2_quad$Pvalue, 2),
                                       round(FJMJ_slope2_quad$Pvalue, 2), 
                                       round(FAMJ_slope2_quad$Pvalue, 2), 
                                       round(FAMA_slope2_quad$Pvalue, 2),
                                       round(MJMA_slope2_quad$Pvalue, 2)), 
                            PostMode = c(round(FJFA_int2_quad$PostMode, 2),
                                         round(FJMA_int2_quad$PostMode, 2),
                                         round(FJMJ_int2_quad$PostMode, 2), 
                                         round(FAMJ_int2_quad$PostMode, 2), 
                                         round(FAMA_int2_quad$PostMode, 2),
                                         round(MJMA_int2_quad$PostMode, 2),
                                         round(FJFA_slope2_quad$PostMode, 2),
                                         round(FJMA_slope2_quad$PostMode, 2),
                                         round(FJMJ_slope2_quad$PostMode, 2), 
                                         round(FAMJ_slope2_quad$PostMode, 2), 
                                         round(FAMA_slope2_quad$PostMode, 2),
                                         round(MJMA_slope2_quad$PostMode, 2)), 
                            LowCrI = c(round(FJFA_int2_quad$LowCrI, 2),
                                       round(FJMA_int2_quad$LowCrI, 2),
                                       round(FJMJ_int2_quad$LowCrI, 2), 
                                       round(FAMJ_int2_quad$LowCrI, 2), 
                                       round(FAMA_int2_quad$LowCrI, 2),
                                       round(MJMA_int2_quad$LowCrI, 2),
                                       round(FJFA_slope2_quad$LowCrI, 2),
                                       round(FJMA_slope2_quad$LowCrI, 2),
                                       round(FJMJ_slope2_quad$LowCrI, 2), 
                                       round(FAMJ_slope2_quad$LowCrI, 2), 
                                       round(FAMA_slope2_quad$LowCrI, 2),
                                       round(MJMA_slope2_quad$LowCrI, 2)), 
                            HighCrI = c(round(FJFA_int2_quad$HighCrI, 2),
                                        round(FJMA_int2_quad$HighCrI, 2),
                                        round(FJMJ_int2_quad$HighCrI, 2), 
                                        round(FAMJ_int2_quad$HighCrI, 2), 
                                        round(FAMA_int2_quad$HighCrI, 2),
                                        round(MJMA_int2_quad$HighCrI, 2),
                                        round(FJFA_slope2_quad$HighCrI, 2),
                                        round(FJMA_slope2_quad$HighCrI, 2),
                                        round(FJMJ_slope2_quad$HighCrI, 2), 
                                        round(FAMJ_slope2_quad$HighCrI, 2), 
                                        round(FAMA_slope2_quad$HighCrI, 2),
                                        round(MJMA_slope2_quad$HighCrI, 2)), )


#*Rarefaction Analysis*----
##Remove CoreFeeder=02A----
data_R02 <- data_MS %>% filter(CoreFeeder!="02A")

###Off-Territory Use----
m1_R02 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R02, family=binomial, 
            control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1_R02) #model is not overdispersed

#DHARMa assumptions test
sim_results_m1_R02 <- simulateResiduals(m1_R02)
plot(sim_results_m1_R02)
test_results_m1_R02 <- testResiduals(sim_results_m1_R02)
print(test_results_m1_R02)

summary(m1_R02)

sm1_R02<-sim(m1_R02, 1000)
mode1_R02<-posterior.mode(as.mcmc(sm1_R02@fixef))
HPD1_R02<-HPDinterval(as.mcmc(sm1_R02@fixef))
mode1_R02 #estimates
HPD1_R02 #CrIs

#between Bird ID variance
var_THC1_R02 <- sm1_R02@ranef$TransponderHexCode
bvar_THC1_R02<-as.vector(apply(var_THC1_R02, 1, var))
bvar_THC1_R02<-as.mcmc(bvar_THC1_R02)
posterior.mode(bvar_THC1_R02) #3.615796         
HPDinterval(bvar_THC1_R02)  #(2.756834, 4.453446)

#between CoreFeeder variance
var_CF1_R02 <- sm1_R02@ranef$CoreFeeder
bvar_CF1_R02<-as.vector(apply(var_CF1_R02, 1, var))
bvar_CF1_R02<-as.mcmc(bvar_CF1_R02)
posterior.mode(bvar_CF1_R02) #12.14           
HPDinterval(bvar_CF1_R02)  #(2.101864, 23.48113)

#Repeatability
rep1_R02<-bvar_THC1_R02 / (bvar_THC1_R02 + (pi^2)/3)
posterior.mode(rep1_R02) #0.5238036        
HPDinterval(rep1_R02) #(0.4676702, 0.5829044)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (intercept)
FJ_int1_R02 <- p_zero(sm1_R02,1) #0.071
#FA (intercept)
FA_int1_R02 <- p_zero(sm1_R02,3) #0.082
#MJ (intercept)
MJ_int1_R02 <- p_zero(sm1_R02,2) #0.053
#MJ (slope)
MJ_slope1_R02 <- p_zero(sm1_R02,6) #0.135
#MA (slope)
MA_slope1_R02 <- p_zero(sm1_R02,8) #0.355


##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R02 <- p_difference(sm1_R02,3,1)
FJFA_int1_R02 
#MJ-FJ (intercept)
FJMJ_int1_R02 <- p_difference(sm1_R02,2,1)
FJMJ_int1_R02 
#MJ-FA (intercept)
FAMJ_int1_R02 <- p_difference(sm1_R02,2,3)
FAMJ_int1_R02 
#MA-FJ (intercept)
FJMA_int1_R02 <- p_difference(sm1_R02,4,1)
FJMA_int1_R02
#MA-FA (intercept)
FAMA_int1_R02 <- p_difference(sm1_R02,4,3)
FAMA_int1_R02 
#MA-MJ (intercept)
MJMA_int1_R02 <- p_difference(sm1_R02,4,2)
MJMA_int1_R02 
#FJ-FA (slope)
FJFA_slope1_R02 <- p_difference(sm1_R02,5,7)
FJFA_slope1_R02 
#FJ-MJ (slope)
FJMJ_slope1_R02 <- p_difference(sm1_R02,5,6)
FJMJ_slope1_R02
#FJ-MA (slope)
FJMA_slope1_R02 <- p_difference(sm1_R02,5,8)
FJMA_slope1_R02 
#FA-MJ (slope)
FAMJ_slope1_R02 <- p_difference(sm1_R02,7,6)
FAMJ_slope1_R02 
#FA-MA (slope)
FAMA_slope1_R02 <- p_difference(sm1_R02,7,8)
FAMA_slope1_R02
#MJ-MA (slope)
MJMA_slope1_R02 <- p_difference(sm1_R02,6,8)
MJMA_slope1_R02

###Table
m1_R02_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R02$Pvalue, 2),
                                     round(FJMA_int1_R02$Pvalue, 2),
                                     round(FJMJ_int1_R02$Pvalue, 2), 
                                     round(FAMJ_int1_R02$Pvalue, 2), 
                                     round(FAMA_int1_R02$Pvalue, 2),
                                     round(MJMA_int1_R02$Pvalue, 2),
                                     round(FJFA_slope1_R02$Pvalue, 2),
                                     round(FJMA_slope1_R02$Pvalue, 2),
                                     round(FJMJ_slope1_R02$Pvalue, 2), 
                                     round(FAMJ_slope1_R02$Pvalue, 2), 
                                     round(FAMA_slope1_R02$Pvalue, 2),
                                     round(MJMA_slope1_R02$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R02$PostMode, 2),
                                       round(FJMA_int1_R02$PostMode, 2),
                                       round(FJMJ_int1_R02$PostMode, 2), 
                                       round(FAMJ_int1_R02$PostMode, 2), 
                                       round(FAMA_int1_R02$PostMode, 2),
                                       round(MJMA_int1_R02$PostMode, 2),
                                       round(FJFA_slope1_R02$PostMode, 2),
                                       round(FJMA_slope1_R02$PostMode, 2),
                                       round(FJMJ_slope1_R02$PostMode, 2), 
                                       round(FAMJ_slope1_R02$PostMode, 2), 
                                       round(FAMA_slope1_R02$PostMode, 2),
                                       round(MJMA_slope1_R02$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R02$LowCrI, 2),
                                     round(FJMA_int1_R02$LowCrI, 2),
                                     round(FJMJ_int1_R02$LowCrI, 2), 
                                     round(FAMJ_int1_R02$LowCrI, 2), 
                                     round(FAMA_int1_R02$LowCrI, 2),
                                     round(MJMA_int1_R02$LowCrI, 2),
                                     round(FJFA_slope1_R02$LowCrI, 2),
                                     round(FJMA_slope1_R02$LowCrI, 2),
                                     round(FJMJ_slope1_R02$LowCrI, 2), 
                                     round(FAMJ_slope1_R02$LowCrI, 2), 
                                     round(FAMA_slope1_R02$LowCrI, 2),
                                     round(MJMA_slope1_R02$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R02$HighCrI, 2),
                                      round(FJMA_int1_R02$HighCrI, 2),
                                      round(FJMJ_int1_R02$HighCrI, 2), 
                                      round(FAMJ_int1_R02$HighCrI, 2), 
                                      round(FAMA_int1_R02$HighCrI, 2),
                                      round(MJMA_int1_R02$HighCrI, 2),
                                      round(FJFA_slope1_R02$HighCrI, 2),
                                      round(FJMA_slope1_R02$HighCrI, 2),
                                      round(FJMJ_slope1_R02$HighCrI, 2), 
                                      round(FAMJ_slope1_R02$HighCrI, 2), 
                                      round(FAMA_slope1_R02$HighCrI, 2),
                                      round(MJMA_slope1_R02$HighCrI, 2)), )

###Daily Feeder Visits----
m2_R02 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R02)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R02)
hist(resid(m2_R02))
#DHARMa assumptions test
sim_results_m2_R02 <- simulateResiduals(m2_R02)
plot(sim_results_m2_R02)
test_results_m2_R02 <- testResiduals(sim_results_m2_R02)
print(test_results_m2_R02)

summary(m2_R02)

sm2_R02<-sim(m2_R02, 1000)
mode2_m2_R02<-posterior.mode(as.mcmc(sm2_R02@fixef))
HPD2_m2_R02<-HPDinterval(as.mcmc(sm2_R02@fixef))
mode2_m2_R02 #estimates
HPD2_m2_R02 #CrIs

#between Bird ID variance
var_THC2_R02 <- sm2_R02@ranef$TransponderHexCode
bvar_THC2_R02<-as.vector(apply(var_THC2_R02, 1, var))
bvar_THC2_R02<-as.mcmc(bvar_THC2_R02)
posterior.mode(bvar_THC2_R02) #2.489374     
HPDinterval(bvar_THC2_R02)  #(2.138251, 2.819617)

#between CoreFeeder variance
var_CF2_R02 <- sm2_R02@ranef$CoreFeeder
bvar_CF2_R02<-as.vector(apply(var_CF2_R02, 1, var))
bvar_CF2_R02<-as.mcmc(bvar_CF2_R02)
posterior.mode(bvar_CF2_R02) #0.05194137      
HPDinterval(bvar_CF2_R02)  #(0.03037517, 0.122893)

#between Residual variance
rvar2_R02<-sm2_R02@sigma^2
rvar2_R02<-as.mcmc(rvar2_R02)
posterior.mode(rvar2_R02) #2.081523      
HPDinterval(rvar2_R02) #(2.024438, 2.210351)

#Repeatability
rep2_R02 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R02, 
            datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R02) # 0.518 (0.43, 0.592)


##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R02 <- p_difference(sm2_R02,3,1)
FJFA_int2_R02 
#MJ-FJ (intercept)
FJMJ_int2_R02 <- p_difference(sm2_R02,2,1)
FJMJ_int2_R02 
#MJ-FA (intercept)
FAMJ_int2_R02 <- p_difference(sm2_R02,2,3)
FAMJ_int2_R02 
#MA-FJ (intercept)
FJMA_int2_R02 <- p_difference(sm2_R02,4,1)
FJMA_int2_R02
#MA-FA (intercept)
FAMA_int2_R02 <- p_difference(sm2_R02,4,3)
FAMA_int2_R02 
#MA-MJ (intercept)
MJMA_int2_R02 <- p_difference(sm2_R02,4,2)
MJMA_int2_R02 
#FJ-FA (slope)
FJFA_slope2_R02 <- p_difference(sm2_R02,5,7)
FJFA_slope2_R02 
#FJ-MJ (slope)
FJMJ_slope2_R02 <- p_difference(sm2_R02,5,6)
FJMJ_slope2_R02
#FJ-MA (slope)
FJMA_slope2_R02 <- p_difference(sm2_R02,5,8)
FJMA_slope2_R02 
#FA-MJ (slope)
FAMJ_slope2_R02 <- p_difference(sm2_R02,7,6)
FAMJ_slope2_R02 
#FA-MA (slope)
FAMA_slope2_R02 <- p_difference(sm2_R02,7,8)
FAMA_slope2_R02
#MJ-MA (slope)
MJMA_slope2_R02 <- p_difference(sm2_R02,6,8)
MJMA_slope2_R02

###Table
m2_R02_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R02$Pvalue, 2),
                                     round(FJMA_int2_R02$Pvalue, 2),
                                     round(FJMJ_int2_R02$Pvalue, 2), 
                                     round(FAMJ_int2_R02$Pvalue, 2), 
                                     round(FAMA_int2_R02$Pvalue, 2),
                                     round(MJMA_int2_R02$Pvalue, 2),
                                     round(FJFA_slope2_R02$Pvalue, 2),
                                     round(FJMA_slope2_R02$Pvalue, 2),
                                     round(FJMJ_slope2_R02$Pvalue, 2), 
                                     round(FAMJ_slope2_R02$Pvalue, 2), 
                                     round(FAMA_slope2_R02$Pvalue, 2),
                                     round(MJMA_slope2_R02$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R02$PostMode, 2),
                                       round(FJMA_int2_R02$PostMode, 2),
                                       round(FJMJ_int2_R02$PostMode, 2), 
                                       round(FAMJ_int2_R02$PostMode, 2), 
                                       round(FAMA_int2_R02$PostMode, 2),
                                       round(MJMA_int2_R02$PostMode, 2),
                                       round(FJFA_slope2_R02$PostMode, 2),
                                       round(FJMA_slope2_R02$PostMode, 2),
                                       round(FJMJ_slope2_R02$PostMode, 2), 
                                       round(FAMJ_slope2_R02$PostMode, 2), 
                                       round(FAMA_slope2_R02$PostMode, 2),
                                       round(MJMA_slope2_R02$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R02$LowCrI, 2),
                                     round(FJMA_int2_R02$LowCrI, 2),
                                     round(FJMJ_int2_R02$LowCrI, 2), 
                                     round(FAMJ_int2_R02$LowCrI, 2), 
                                     round(FAMA_int2_R02$LowCrI, 2),
                                     round(MJMA_int2_R02$LowCrI, 2),
                                     round(FJFA_slope2_R02$LowCrI, 2),
                                     round(FJMA_slope2_R02$LowCrI, 2),
                                     round(FJMJ_slope2_R02$LowCrI, 2), 
                                     round(FAMJ_slope2_R02$LowCrI, 2), 
                                     round(FAMA_slope2_R02$LowCrI, 2),
                                     round(MJMA_slope2_R02$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R02$HighCrI, 2),
                                      round(FJMA_int2_R02$HighCrI, 2),
                                      round(FJMJ_int2_R02$HighCrI, 2), 
                                      round(FAMJ_int2_R02$HighCrI, 2), 
                                      round(FAMA_int2_R02$HighCrI, 2),
                                      round(MJMA_int2_R02$HighCrI, 2),
                                      round(FJFA_slope2_R02$HighCrI, 2),
                                      round(FJMA_slope2_R02$HighCrI, 2),
                                      round(FJMJ_slope2_R02$HighCrI, 2), 
                                      round(FAMJ_slope2_R02$HighCrI, 2), 
                                      round(FAMA_slope2_R02$HighCrI, 2),
                                      round(MJMA_slope2_R02$HighCrI, 2)), )

##Remove CoreFeeder=04A
data_R04 <- data_MS %>% filter(CoreFeeder!="04A")

###Off-Territory Use
m1_R04 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R04, family=binomial, 
                control=glmerControl(optimizer="bobyqa"))
overdisp_fun(m1_R04) #model is not overdispersed
summary(m1_R04)

sm1_R04<-sim(m1_R04, 1000)
mode1_R04<-posterior.mode(as.mcmc(sm1_R04@fixef))
HPD1_R04<-HPDinterval(as.mcmc(sm1_R04@fixef))
mode1_R04 #estimates
HPD1_R04 #CrIs

#between Bird ID variance
var_THC1_R04 <- sm1_R04@ranef$TransponderHexCode
bvar_THC1_R04<-as.vector(apply(var_THC1_R04, 1, var))
bvar_THC1_R04<-as.mcmc(bvar_THC1_R04)
posterior.mode(bvar_THC1_R04) #4.87002        
HPDinterval(bvar_THC1_R04)  #(3.71336, 6.166394)

#between CoreFeeder variance
var_CF1_R04 <- sm1_R04@ranef$CoreFeeder
bvar_CF1_R04<-as.vector(apply(var_CF1_R04, 1, var))
bvar_CF1_R04<-as.mcmc(bvar_CF1_R04)
posterior.mode(bvar_CF1_R04) #15.38734          
HPDinterval(bvar_CF1_R04)  #(3.058978, 29.50568)

#Repeatability
rep1_R04<-bvar_THC1_R04 / (bvar_THC1_R04 + (pi^2)/3)
posterior.mode(rep1_R04) #0.5969849       
HPDinterval(rep1_R04) #(0.5336701, 0.6545059)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (intercept)
FJ_int1_R04 <- p_zero(sm1_R04,1) #0.047
#FA (intercept)
FA_int1_R04 <- p_zero(sm1_R04,3) #0.059
#MJ (intercept)
MJ_int1_R04 <- p_zero(sm1_R04,2) #0.152


##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R04 <- p_difference(sm1_R04,3,1)
FJFA_int1_R04 
#MJ-FJ (intercept)
FJMJ_int1_R04 <- p_difference(sm1_R04,2,1)
FJMJ_int1_R04 
#MJ-FA (intercept)
FAMJ_int1_R04 <- p_difference(sm1_R04,2,3)
FAMJ_int1_R04 
#MA-FJ (intercept)
FJMA_int1_R04 <- p_difference(sm1_R04,4,1)
FJMA_int1_R04
#MA-FA (intercept)
FAMA_int1_R04 <- p_difference(sm1_R04,4,3)
FAMA_int1_R04 
#MA-MJ (intercept)
MJMA_int1_R04 <- p_difference(sm1_R04,4,2)
MJMA_int1_R04 
#FJ-FA (slope)
FJFA_slope1_R04 <- p_difference(sm1_R04,5,7)
FJFA_slope1_R04 
#FJ-MJ (slope)
FJMJ_slope1_R04 <- p_difference(sm1_R04,5,6)
FJMJ_slope1_R04
#FJ-MA (slope)
FJMA_slope1_R04 <- p_difference(sm1_R04,5,8)
FJMA_slope1_R04 
#FA-MJ (slope)
FAMJ_slope1_R04 <- p_difference(sm1_R04,7,6)
FAMJ_slope1_R04 
#FA-MA (slope)
FAMA_slope1_R04 <- p_difference(sm1_R04,7,8)
FAMA_slope1_R04
#MJ-MA (slope)
MJMA_slope1_R04 <- p_difference(sm1_R04,6,8)
MJMA_slope1_R04

###Table
m1_R04_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R04$Pvalue, 2),
                                     round(FJMA_int1_R04$Pvalue, 2),
                                     round(FJMJ_int1_R04$Pvalue, 2), 
                                     round(FAMJ_int1_R04$Pvalue, 2), 
                                     round(FAMA_int1_R04$Pvalue, 2),
                                     round(MJMA_int1_R04$Pvalue, 2),
                                     round(FJFA_slope1_R04$Pvalue, 2),
                                     round(FJMA_slope1_R04$Pvalue, 2),
                                     round(FJMJ_slope1_R04$Pvalue, 2), 
                                     round(FAMJ_slope1_R04$Pvalue, 2), 
                                     round(FAMA_slope1_R04$Pvalue, 2),
                                     round(MJMA_slope1_R04$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R04$PostMode, 2),
                                       round(FJMA_int1_R04$PostMode, 2),
                                       round(FJMJ_int1_R04$PostMode, 2), 
                                       round(FAMJ_int1_R04$PostMode, 2), 
                                       round(FAMA_int1_R04$PostMode, 2),
                                       round(MJMA_int1_R04$PostMode, 2),
                                       round(FJFA_slope1_R04$PostMode, 2),
                                       round(FJMA_slope1_R04$PostMode, 2),
                                       round(FJMJ_slope1_R04$PostMode, 2), 
                                       round(FAMJ_slope1_R04$PostMode, 2), 
                                       round(FAMA_slope1_R04$PostMode, 2),
                                       round(MJMA_slope1_R04$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R04$LowCrI, 2),
                                     round(FJMA_int1_R04$LowCrI, 2),
                                     round(FJMJ_int1_R04$LowCrI, 2), 
                                     round(FAMJ_int1_R04$LowCrI, 2), 
                                     round(FAMA_int1_R04$LowCrI, 2),
                                     round(MJMA_int1_R04$LowCrI, 2),
                                     round(FJFA_slope1_R04$LowCrI, 2),
                                     round(FJMA_slope1_R04$LowCrI, 2),
                                     round(FJMJ_slope1_R04$LowCrI, 2), 
                                     round(FAMJ_slope1_R04$LowCrI, 2), 
                                     round(FAMA_slope1_R04$LowCrI, 2),
                                     round(MJMA_slope1_R04$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R04$HighCrI, 2),
                                      round(FJMA_int1_R04$HighCrI, 2),
                                      round(FJMJ_int1_R04$HighCrI, 2), 
                                      round(FAMJ_int1_R04$HighCrI, 2), 
                                      round(FAMA_int1_R04$HighCrI, 2),
                                      round(MJMA_int1_R04$HighCrI, 2),
                                      round(FJFA_slope1_R04$HighCrI, 2),
                                      round(FJMA_slope1_R04$HighCrI, 2),
                                      round(FJMJ_slope1_R04$HighCrI, 2), 
                                      round(FAMJ_slope1_R04$HighCrI, 2), 
                                      round(FAMA_slope1_R04$HighCrI, 2),
                                      round(MJMA_slope1_R04$HighCrI, 2)), )

###Daily Feeder Visits
m2_R04 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R04)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R04)
hist(resid(m2_R04))

summary(m2_R04)

sm2_R04<-sim(m2_R04, 1000)
mode2_m2_R04<-posterior.mode(as.mcmc(sm2_R04@fixef))
HPD2_m2_R04<-HPDinterval(as.mcmc(sm2_R04@fixef))
mode2_m2_R04 #estimates
HPD2_m2_R04 #CrIs

#between Bird ID variance
var_THC2_R04 <- sm2_R04@ranef$TransponderHexCode
bvar_THC2_R04<-as.vector(apply(var_THC2_R04, 1, var))
bvar_THC2_R04<-as.mcmc(bvar_THC2_R04)
posterior.mode(bvar_THC2_R04) #2.11543     
HPDinterval(bvar_THC2_R04)  #(1.848347, 2.429469)

#between CoreFeeder variance
var_CF2_R04 <- sm2_R04@ranef$CoreFeeder
bvar_CF2_R04<-as.vector(apply(var_CF2_R04, 1, var))
bvar_CF2_R04<-as.mcmc(bvar_CF2_R04)
posterior.mode(bvar_CF2_R04) #-0.000132722     
HPDinterval(bvar_CF2_R04)  #(0, 0)

#between Residual variance
rvar2_R04<-sm2_R04@sigma^2
rvar2_R04<-as.mcmc(rvar2_R04)
posterior.mode(rvar2_R04) #1.799937      
HPDinterval(rvar2_R04) #(1.728675, 1.886581)

#Repeatability
rep2_R04 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R04, 
                datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R04) # 0.528 (0.456, 0.594)

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R04 <- p_difference(sm2_R04,3,1)
FJFA_int2_R04 
#MJ-FJ (intercept)
FJMJ_int2_R04 <- p_difference(sm2_R04,2,1)
FJMJ_int2_R04 
#MJ-FA (intercept)
FAMJ_int2_R04 <- p_difference(sm2_R04,2,3)
FAMJ_int2_R04 
#MA-FJ (intercept)
FJMA_int2_R04 <- p_difference(sm2_R04,4,1)
FJMA_int2_R04
#MA-FA (intercept)
FAMA_int2_R04 <- p_difference(sm2_R04,4,3)
FAMA_int2_R04 
#MA-MJ (intercept)
MJMA_int2_R04 <- p_difference(sm2_R04,4,2)
MJMA_int2_R04 
#FJ-FA (slope)
FJFA_slope2_R04 <- p_difference(sm2_R04,5,7)
FJFA_slope2_R04 
#FJ-MJ (slope)
FJMJ_slope2_R04 <- p_difference(sm2_R04,5,6)
FJMJ_slope2_R04
#FJ-MA (slope)
FJMA_slope2_R04 <- p_difference(sm2_R04,5,8)
FJMA_slope2_R04 
#FA-MJ (slope)
FAMJ_slope2_R04 <- p_difference(sm2_R04,7,6)
FAMJ_slope2_R04 
#FA-MA (slope)
FAMA_slope2_R04 <- p_difference(sm2_R04,7,8)
FAMA_slope2_R04
#MJ-MA (slope)
MJMA_slope2_R04 <- p_difference(sm2_R04,6,8)
MJMA_slope2_R04

###Table
m2_R04_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R04$Pvalue, 2),
                                     round(FJMA_int2_R04$Pvalue, 2),
                                     round(FJMJ_int2_R04$Pvalue, 2), 
                                     round(FAMJ_int2_R04$Pvalue, 2), 
                                     round(FAMA_int2_R04$Pvalue, 2),
                                     round(MJMA_int2_R04$Pvalue, 2),
                                     round(FJFA_slope2_R04$Pvalue, 2),
                                     round(FJMA_slope2_R04$Pvalue, 2),
                                     round(FJMJ_slope2_R04$Pvalue, 2), 
                                     round(FAMJ_slope2_R04$Pvalue, 2), 
                                     round(FAMA_slope2_R04$Pvalue, 2),
                                     round(MJMA_slope2_R04$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R04$PostMode, 2),
                                       round(FJMA_int2_R04$PostMode, 2),
                                       round(FJMJ_int2_R04$PostMode, 2), 
                                       round(FAMJ_int2_R04$PostMode, 2), 
                                       round(FAMA_int2_R04$PostMode, 2),
                                       round(MJMA_int2_R04$PostMode, 2),
                                       round(FJFA_slope2_R04$PostMode, 2),
                                       round(FJMA_slope2_R04$PostMode, 2),
                                       round(FJMJ_slope2_R04$PostMode, 2), 
                                       round(FAMJ_slope2_R04$PostMode, 2), 
                                       round(FAMA_slope2_R04$PostMode, 2),
                                       round(MJMA_slope2_R04$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R04$LowCrI, 2),
                                     round(FJMA_int2_R04$LowCrI, 2),
                                     round(FJMJ_int2_R04$LowCrI, 2), 
                                     round(FAMJ_int2_R04$LowCrI, 2), 
                                     round(FAMA_int2_R04$LowCrI, 2),
                                     round(MJMA_int2_R04$LowCrI, 2),
                                     round(FJFA_slope2_R04$LowCrI, 2),
                                     round(FJMA_slope2_R04$LowCrI, 2),
                                     round(FJMJ_slope2_R04$LowCrI, 2), 
                                     round(FAMJ_slope2_R04$LowCrI, 2), 
                                     round(FAMA_slope2_R04$LowCrI, 2),
                                     round(MJMA_slope2_R04$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R04$HighCrI, 2),
                                      round(FJMA_int2_R04$HighCrI, 2),
                                      round(FJMJ_int2_R04$HighCrI, 2), 
                                      round(FAMJ_int2_R04$HighCrI, 2), 
                                      round(FAMA_int2_R04$HighCrI, 2),
                                      round(MJMA_int2_R04$HighCrI, 2),
                                      round(FJFA_slope2_R04$HighCrI, 2),
                                      round(FJMA_slope2_R04$HighCrI, 2),
                                      round(FJMJ_slope2_R04$HighCrI, 2), 
                                      round(FAMJ_slope2_R04$HighCrI, 2), 
                                      round(FAMA_slope2_R04$HighCrI, 2),
                                      round(MJMA_slope2_R04$HighCrI, 2)), )


##Remove CoreFeeder=09A----
data_R09 <- data_MS %>% filter(CoreFeeder!="09A")

###Off-Territory Use----
m1_R09 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R09, family=binomial, 
                control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1_R09) #model is not overdispersed

#DHARMa assumptions test
sim_results_m1_R09 <- simulateResiduals(m1_R09)
plot(sim_results_m1_R09)
test_results_m1_R09 <- testResiduals(sim_results_m1_R09)
print(test_results_m1_R09)

summary(m1_R09)

sm1_R09<-sim(m1_R09, 1000)
mode1_R09<-posterior.mode(as.mcmc(sm1_R09@fixef))
HPD1_R09<-HPDinterval(as.mcmc(sm1_R09@fixef))
mode1_R09 #estimates
HPD1_R09 #CrIs

#between Bird ID variance
var_THC1_R09 <- sm1_R09@ranef$TransponderHexCode
bvar_THC1_R09<-as.vector(apply(var_THC1_R09, 1, var))
bvar_THC1_R09<-as.mcmc(bvar_THC1_R09)
posterior.mode(bvar_THC1_R09) #5.833893        
HPDinterval(bvar_THC1_R09)  #(4.525566, 7.076016)

#between CoreFeeder variance
var_CF1_R09 <- sm1_R09@ranef$CoreFeeder
bvar_CF1_R09<-as.vector(apply(var_CF1_R09, 1, var))
bvar_CF1_R09<-as.mcmc(bvar_CF1_R09)
posterior.mode(bvar_CF1_R09) #6.783862          
HPDinterval(bvar_CF1_R09)  #(1.974665, 20.01748)

#Repeatability
rep1_R09<-bvar_THC1_R09 / (bvar_THC1_R09 + (pi^2)/3)
posterior.mode(rep1_R09) #0.6394946       
HPDinterval(rep1_R09) #(0.5837653, 0.6855804)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (slope)
FJ_slope1_R09 <- p_zero(sm1_R09,5) #0.578
#FA (slope)
FA_slope1_R09 <- p_zero(sm1_R09,7) #0.271

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R09 <- p_difference(sm1_R09,3,1)
FJFA_int1_R09 
#MJ-FJ (intercept)
FJMJ_int1_R09 <- p_difference(sm1_R09,2,1)
FJMJ_int1_R09 
#MJ-FA (intercept)
FAMJ_int1_R09 <- p_difference(sm1_R09,2,3)
FAMJ_int1_R09 
#MA-FJ (intercept)
FJMA_int1_R09 <- p_difference(sm1_R09,4,1)
FJMA_int1_R09
#MA-FA (intercept)
FAMA_int1_R09 <- p_difference(sm1_R09,4,3)
FAMA_int1_R09 
#MA-MJ (intercept)
MJMA_int1_R09 <- p_difference(sm1_R09,4,2)
MJMA_int1_R09 
#FJ-FA (slope)
FJFA_slope1_R09 <- p_difference(sm1_R09,5,7)
FJFA_slope1_R09 
#FJ-MJ (slope)
FJMJ_slope1_R09 <- p_difference(sm1_R09,5,6)
FJMJ_slope1_R09
#FJ-MA (slope)
FJMA_slope1_R09 <- p_difference(sm1_R09,5,8)
FJMA_slope1_R09 
#FA-MJ (slope)
FAMJ_slope1_R09 <- p_difference(sm1_R09,7,6)
FAMJ_slope1_R09 
#FA-MA (slope)
FAMA_slope1_R09 <- p_difference(sm1_R09,7,8)
FAMA_slope1_R09
#MJ-MA (slope)
MJMA_slope1_R09 <- p_difference(sm1_R09,6,8)
MJMA_slope1_R09

###Table
m1_R09_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R09$Pvalue, 2),
                                     round(FJMA_int1_R09$Pvalue, 2),
                                     round(FJMJ_int1_R09$Pvalue, 2), 
                                     round(FAMJ_int1_R09$Pvalue, 2), 
                                     round(FAMA_int1_R09$Pvalue, 2),
                                     round(MJMA_int1_R09$Pvalue, 2),
                                     round(FJFA_slope1_R09$Pvalue, 2),
                                     round(FJMA_slope1_R09$Pvalue, 2),
                                     round(FJMJ_slope1_R09$Pvalue, 2), 
                                     round(FAMJ_slope1_R09$Pvalue, 2), 
                                     round(FAMA_slope1_R09$Pvalue, 2),
                                     round(MJMA_slope1_R09$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R09$PostMode, 2),
                                       round(FJMA_int1_R09$PostMode, 2),
                                       round(FJMJ_int1_R09$PostMode, 2), 
                                       round(FAMJ_int1_R09$PostMode, 2), 
                                       round(FAMA_int1_R09$PostMode, 2),
                                       round(MJMA_int1_R09$PostMode, 2),
                                       round(FJFA_slope1_R09$PostMode, 2),
                                       round(FJMA_slope1_R09$PostMode, 2),
                                       round(FJMJ_slope1_R09$PostMode, 2), 
                                       round(FAMJ_slope1_R09$PostMode, 2), 
                                       round(FAMA_slope1_R09$PostMode, 2),
                                       round(MJMA_slope1_R09$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R09$LowCrI, 2),
                                     round(FJMA_int1_R09$LowCrI, 2),
                                     round(FJMJ_int1_R09$LowCrI, 2), 
                                     round(FAMJ_int1_R09$LowCrI, 2), 
                                     round(FAMA_int1_R09$LowCrI, 2),
                                     round(MJMA_int1_R09$LowCrI, 2),
                                     round(FJFA_slope1_R09$LowCrI, 2),
                                     round(FJMA_slope1_R09$LowCrI, 2),
                                     round(FJMJ_slope1_R09$LowCrI, 2), 
                                     round(FAMJ_slope1_R09$LowCrI, 2), 
                                     round(FAMA_slope1_R09$LowCrI, 2),
                                     round(MJMA_slope1_R09$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R09$HighCrI, 2),
                                      round(FJMA_int1_R09$HighCrI, 2),
                                      round(FJMJ_int1_R09$HighCrI, 2), 
                                      round(FAMJ_int1_R09$HighCrI, 2), 
                                      round(FAMA_int1_R09$HighCrI, 2),
                                      round(MJMA_int1_R09$HighCrI, 2),
                                      round(FJFA_slope1_R09$HighCrI, 2),
                                      round(FJMA_slope1_R09$HighCrI, 2),
                                      round(FJMJ_slope1_R09$HighCrI, 2), 
                                      round(FAMJ_slope1_R09$HighCrI, 2), 
                                      round(FAMA_slope1_R09$HighCrI, 2),
                                      round(MJMA_slope1_R09$HighCrI, 2)), )

###Daily Feeder Visits----
m2_R09 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R09)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R09)
hist(resid(m2_R09))
#DHARMa assumptions test
sim_results_m2_R09 <- simulateResiduals(m2_R09)
plot(sim_results_m2_R09)
test_results_m2_R09 <- testResiduals(sim_results_m2_R09)
print(test_results_m2_R09)

summary(m2_R09)

sm2_R09<-sim(m2_R09, 1000)
mode2_m2_R09<-posterior.mode(as.mcmc(sm2_R09@fixef))
HPD2_m2_R09<-HPDinterval(as.mcmc(sm2_R09@fixef))
mode2_m2_R09 #estimates
HPD2_m2_R09 #CrIs

#between Bird ID variance
var_THC2_R09 <- sm2_R09@ranef$TransponderHexCode
bvar_THC2_R09<-as.vector(apply(var_THC2_R09, 1, var))
bvar_THC2_R09<-as.mcmc(bvar_THC2_R09)
posterior.mode(bvar_THC2_R09) #2.049052     
HPDinterval(bvar_THC2_R09)  #(1.862337, 2.438132)

#between CoreFeeder variance
var_CF2_R09 <- sm2_R09@ranef$CoreFeeder
bvar_CF2_R09<-as.vector(apply(var_CF2_R09, 1, var))
bvar_CF2_R09<-as.mcmc(bvar_CF2_R09)
posterior.mode(bvar_CF2_R09) #0.0479604      
HPDinterval(bvar_CF2_R09)  #(0.01957787, 0.09692821)

#between Residual variance
rvar2_R09<-sm2_R09@sigma^2
rvar2_R09<-as.mcmc(rvar2_R09)
posterior.mode(rvar2_R09) #1.863704      
HPDinterval(rvar2_R09) #(1.781554, 1.935564)

#Repeatability
rep2_R09 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R09, 
                datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R09) # 0.516 (0.44, 0.584)

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R09 <- p_difference(sm2_R09,3,1)
FJFA_int2_R09 
#MJ-FJ (intercept)
FJMJ_int2_R09 <- p_difference(sm2_R09,2,1)
FJMJ_int2_R09 
#MJ-FA (intercept)
FAMJ_int2_R09 <- p_difference(sm2_R09,2,3)
FAMJ_int2_R09 
#MA-FJ (intercept)
FJMA_int2_R09 <- p_difference(sm2_R09,4,1)
FJMA_int2_R09
#MA-FA (intercept)
FAMA_int2_R09 <- p_difference(sm2_R09,4,3)
FAMA_int2_R09 
#MA-MJ (intercept)
MJMA_int2_R09 <- p_difference(sm2_R09,4,2)
MJMA_int2_R09 
#FJ-FA (slope)
FJFA_slope2_R09 <- p_difference(sm2_R09,5,7)
FJFA_slope2_R09 
#FJ-MJ (slope)
FJMJ_slope2_R09 <- p_difference(sm2_R09,5,6)
FJMJ_slope2_R09
#FJ-MA (slope)
FJMA_slope2_R09 <- p_difference(sm2_R09,5,8)
FJMA_slope2_R09 
#FA-MJ (slope)
FAMJ_slope2_R09 <- p_difference(sm2_R09,7,6)
FAMJ_slope2_R09 
#FA-MA (slope)
FAMA_slope2_R09 <- p_difference(sm2_R09,7,8)
FAMA_slope2_R09
#MJ-MA (slope)
MJMA_slope2_R09 <- p_difference(sm2_R09,6,8)
MJMA_slope2_R09

###Table
m2_R09_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R09$Pvalue, 2),
                                     round(FJMA_int2_R09$Pvalue, 2),
                                     round(FJMJ_int2_R09$Pvalue, 2), 
                                     round(FAMJ_int2_R09$Pvalue, 2), 
                                     round(FAMA_int2_R09$Pvalue, 2),
                                     round(MJMA_int2_R09$Pvalue, 2),
                                     round(FJFA_slope2_R09$Pvalue, 2),
                                     round(FJMA_slope2_R09$Pvalue, 2),
                                     round(FJMJ_slope2_R09$Pvalue, 2), 
                                     round(FAMJ_slope2_R09$Pvalue, 2), 
                                     round(FAMA_slope2_R09$Pvalue, 2),
                                     round(MJMA_slope2_R09$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R09$PostMode, 2),
                                       round(FJMA_int2_R09$PostMode, 2),
                                       round(FJMJ_int2_R09$PostMode, 2), 
                                       round(FAMJ_int2_R09$PostMode, 2), 
                                       round(FAMA_int2_R09$PostMode, 2),
                                       round(MJMA_int2_R09$PostMode, 2),
                                       round(FJFA_slope2_R09$PostMode, 2),
                                       round(FJMA_slope2_R09$PostMode, 2),
                                       round(FJMJ_slope2_R09$PostMode, 2), 
                                       round(FAMJ_slope2_R09$PostMode, 2), 
                                       round(FAMA_slope2_R09$PostMode, 2),
                                       round(MJMA_slope2_R09$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R09$LowCrI, 2),
                                     round(FJMA_int2_R09$LowCrI, 2),
                                     round(FJMJ_int2_R09$LowCrI, 2), 
                                     round(FAMJ_int2_R09$LowCrI, 2), 
                                     round(FAMA_int2_R09$LowCrI, 2),
                                     round(MJMA_int2_R09$LowCrI, 2),
                                     round(FJFA_slope2_R09$LowCrI, 2),
                                     round(FJMA_slope2_R09$LowCrI, 2),
                                     round(FJMJ_slope2_R09$LowCrI, 2), 
                                     round(FAMJ_slope2_R09$LowCrI, 2), 
                                     round(FAMA_slope2_R09$LowCrI, 2),
                                     round(MJMA_slope2_R09$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R09$HighCrI, 2),
                                      round(FJMA_int2_R09$HighCrI, 2),
                                      round(FJMJ_int2_R09$HighCrI, 2), 
                                      round(FAMJ_int2_R09$HighCrI, 2), 
                                      round(FAMA_int2_R09$HighCrI, 2),
                                      round(MJMA_int2_R09$HighCrI, 2),
                                      round(FJFA_slope2_R09$HighCrI, 2),
                                      round(FJMA_slope2_R09$HighCrI, 2),
                                      round(FJMJ_slope2_R09$HighCrI, 2), 
                                      round(FAMJ_slope2_R09$HighCrI, 2), 
                                      round(FAMA_slope2_R09$HighCrI, 2),
                                      round(MJMA_slope2_R09$HighCrI, 2)), )

##Remove CoreFeeder=10A----
data_R10 <- data_MS %>% filter(CoreFeeder!="10A")

###Off-Territory Use----
m1_R10 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R10, family=binomial, 
                control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1_R10) #model is not overdispersed

#DHARMa assumptions test
sim_results_m1_R10 <- simulateResiduals(m1_R10)
plot(sim_results_m1_R10)
test_results_m1_R10 <- testResiduals(sim_results_m1_R10)
print(test_results_m1_R10)

summary(m1_R10)

sm1_R10<-sim(m1_R10, 1000)
mode1_R10<-posterior.mode(as.mcmc(sm1_R10@fixef))
HPD1_R10<-HPDinterval(as.mcmc(sm1_R10@fixef))
mode1_R10 #estimates
HPD1_R10 #CrIs

#between Bird ID variance
var_THC1_R10 <- sm1_R10@ranef$TransponderHexCode
bvar_THC1_R10<-as.vector(apply(var_THC1_R10, 1, var))
bvar_THC1_R10<-as.mcmc(bvar_THC1_R10)
posterior.mode(bvar_THC1_R10) #4.624805        
HPDinterval(bvar_THC1_R10)  #(3.701081, 5.856327)

#between CoreFeeder variance
var_CF1_R10 <- sm1_R10@ranef$CoreFeeder
bvar_CF1_R10<-as.vector(apply(var_CF1_R10, 1, var))
bvar_CF1_R10<-as.mcmc(bvar_CF1_R10)
posterior.mode(bvar_CF1_R10) #10.83402          
HPDinterval(bvar_CF1_R10)  #(3.547351, 29.81617)

#Repeatability
rep1_R10<-bvar_THC1_R10 / (bvar_THC1_R10 + (pi^2)/3)
posterior.mode(rep1_R10) #0.5997945       
HPDinterval(rep1_R10) #(0.533411, 0.6435537)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (intercept)
FJ_int1_R10 <- p_zero(sm1_R10,1) #0.039
#FA (intercept)
FA_int1_R10 <- p_zero(sm1_R10,3) #0.082
#MJ (intercept)
MJ_int1_R10 <- p_zero(sm1_R10,2) #0.066
#FJ (slope)
FJ_slope1_R10 <- p_zero(sm1_R10,5) #0.079
#MJ (slope)
MJ_slope1_R10 <- p_zero(sm1_R10,6) #0.242
#MA (slope)
MA_slope1_R10 <- p_zero(sm1_R10,8) #0.336

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R10 <- p_difference(sm1_R10,3,1)
FJFA_int1_R10 
#MJ-FJ (intercept)
FJMJ_int1_R10 <- p_difference(sm1_R10,2,1)
FJMJ_int1_R10 
#MJ-FA (intercept)
FAMJ_int1_R10 <- p_difference(sm1_R10,2,3)
FAMJ_int1_R10 
#MA-FJ (intercept)
FJMA_int1_R10 <- p_difference(sm1_R10,4,1)
FJMA_int1_R10
#MA-FA (intercept)
FAMA_int1_R10 <- p_difference(sm1_R10,4,3)
FAMA_int1_R10 
#MA-MJ (intercept)
MJMA_int1_R10 <- p_difference(sm1_R10,4,2)
MJMA_int1_R10 
#FJ-FA (slope)
FJFA_slope1_R10 <- p_difference(sm1_R10,5,7)
FJFA_slope1_R10 
#FJ-MJ (slope)
FJMJ_slope1_R10 <- p_difference(sm1_R10,5,6)
FJMJ_slope1_R10
#FJ-MA (slope)
FJMA_slope1_R10 <- p_difference(sm1_R10,5,8)
FJMA_slope1_R10 
#FA-MJ (slope)
FAMJ_slope1_R10 <- p_difference(sm1_R10,7,6)
FAMJ_slope1_R10 
#FA-MA (slope)
FAMA_slope1_R10 <- p_difference(sm1_R10,7,8)
FAMA_slope1_R10
#MJ-MA (slope)
MJMA_slope1_R10 <- p_difference(sm1_R10,6,8)
MJMA_slope1_R10

###Table
m1_R10_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R10$Pvalue, 2),
                                     round(FJMA_int1_R10$Pvalue, 2),
                                     round(FJMJ_int1_R10$Pvalue, 2), 
                                     round(FAMJ_int1_R10$Pvalue, 2), 
                                     round(FAMA_int1_R10$Pvalue, 2),
                                     round(MJMA_int1_R10$Pvalue, 2),
                                     round(FJFA_slope1_R10$Pvalue, 2),
                                     round(FJMA_slope1_R10$Pvalue, 2),
                                     round(FJMJ_slope1_R10$Pvalue, 2), 
                                     round(FAMJ_slope1_R10$Pvalue, 2), 
                                     round(FAMA_slope1_R10$Pvalue, 2),
                                     round(MJMA_slope1_R10$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R10$PostMode, 2),
                                       round(FJMA_int1_R10$PostMode, 2),
                                       round(FJMJ_int1_R10$PostMode, 2), 
                                       round(FAMJ_int1_R10$PostMode, 2), 
                                       round(FAMA_int1_R10$PostMode, 2),
                                       round(MJMA_int1_R10$PostMode, 2),
                                       round(FJFA_slope1_R10$PostMode, 2),
                                       round(FJMA_slope1_R10$PostMode, 2),
                                       round(FJMJ_slope1_R10$PostMode, 2), 
                                       round(FAMJ_slope1_R10$PostMode, 2), 
                                       round(FAMA_slope1_R10$PostMode, 2),
                                       round(MJMA_slope1_R10$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R10$LowCrI, 2),
                                     round(FJMA_int1_R10$LowCrI, 2),
                                     round(FJMJ_int1_R10$LowCrI, 2), 
                                     round(FAMJ_int1_R10$LowCrI, 2), 
                                     round(FAMA_int1_R10$LowCrI, 2),
                                     round(MJMA_int1_R10$LowCrI, 2),
                                     round(FJFA_slope1_R10$LowCrI, 2),
                                     round(FJMA_slope1_R10$LowCrI, 2),
                                     round(FJMJ_slope1_R10$LowCrI, 2), 
                                     round(FAMJ_slope1_R10$LowCrI, 2), 
                                     round(FAMA_slope1_R10$LowCrI, 2),
                                     round(MJMA_slope1_R10$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R10$HighCrI, 2),
                                      round(FJMA_int1_R10$HighCrI, 2),
                                      round(FJMJ_int1_R10$HighCrI, 2), 
                                      round(FAMJ_int1_R10$HighCrI, 2), 
                                      round(FAMA_int1_R10$HighCrI, 2),
                                      round(MJMA_int1_R10$HighCrI, 2),
                                      round(FJFA_slope1_R10$HighCrI, 2),
                                      round(FJMA_slope1_R10$HighCrI, 2),
                                      round(FJMJ_slope1_R10$HighCrI, 2), 
                                      round(FAMJ_slope1_R10$HighCrI, 2), 
                                      round(FAMA_slope1_R10$HighCrI, 2),
                                      round(MJMA_slope1_R10$HighCrI, 2)), )

###Daily Feeder Visits----
m2_R10 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R10)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R10)
hist(resid(m2_R10))
#DHARMa assumptions test
sim_results_m2_R10 <- simulateResiduals(m2_R10)
plot(sim_results_m2_R10)
test_results_m2_R10 <- testResiduals(sim_results_m2_R10)
print(test_results_m2_R10)

summary(m2_R10)

sm2_R10<-sim(m2_R10, 1000)
mode2_m2_R10<-posterior.mode(as.mcmc(sm2_R10@fixef))
HPD2_m2_R10<-HPDinterval(as.mcmc(sm2_R10@fixef))
mode2_m2_R10 #estimates
HPD2_m2_R10 #CrIs

#between Bird ID variance
var_THC2_R10 <- sm2_R10@ranef$TransponderHexCode
bvar_THC2_R10<-as.vector(apply(var_THC2_R10, 1, var))
bvar_THC2_R10<-as.mcmc(bvar_THC2_R10)
posterior.mode(bvar_THC2_R10) #2.118173     
HPDinterval(bvar_THC2_R10)  #(1.884675, 2.330498)

#between CoreFeeder variance
var_CF2_R10 <- sm2_R10@ranef$CoreFeeder
bvar_CF2_R10<-as.vector(apply(var_CF2_R10, 1, var))
bvar_CF2_R10<-as.mcmc(bvar_CF2_R10)
posterior.mode(bvar_CF2_R10) #0.05103491      
HPDinterval(bvar_CF2_R10)  #(0.02855829 0.1096809)

#between Residual variance
rvar2_R10<-sm2_R10@sigma^2
rvar2_R10<-as.mcmc(rvar2_R10)
posterior.mode(rvar2_R10) #1.810786      
HPDinterval(rvar2_R10) #(1.726982, 1.875156)

#Repeatability
rep2_R10 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R10, 
                datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R10) # 0.512 (0.428, 0.582)

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R10 <- p_difference(sm2_R10,3,1)
FJFA_int2_R10 
#MJ-FJ (intercept)
FJMJ_int2_R10 <- p_difference(sm2_R10,2,1)
FJMJ_int2_R10 
#MJ-FA (intercept)
FAMJ_int2_R10 <- p_difference(sm2_R10,2,3)
FAMJ_int2_R10 
#MA-FJ (intercept)
FJMA_int2_R10 <- p_difference(sm2_R10,4,1)
FJMA_int2_R10
#MA-FA (intercept)
FAMA_int2_R10 <- p_difference(sm2_R10,4,3)
FAMA_int2_R10 
#MA-MJ (intercept)
MJMA_int2_R10 <- p_difference(sm2_R10,4,2)
MJMA_int2_R10 
#FJ-FA (slope)
FJFA_slope2_R10 <- p_difference(sm2_R10,5,7)
FJFA_slope2_R10 
#FJ-MJ (slope)
FJMJ_slope2_R10 <- p_difference(sm2_R10,5,6)
FJMJ_slope2_R10
#FJ-MA (slope)
FJMA_slope2_R10 <- p_difference(sm2_R10,5,8)
FJMA_slope2_R10 
#FA-MJ (slope)
FAMJ_slope2_R10 <- p_difference(sm2_R10,7,6)
FAMJ_slope2_R10 
#FA-MA (slope)
FAMA_slope2_R10 <- p_difference(sm2_R10,7,8)
FAMA_slope2_R10
#MJ-MA (slope)
MJMA_slope2_R10 <- p_difference(sm2_R10,6,8)
MJMA_slope2_R10

###Table
m2_R10_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R10$Pvalue, 2),
                                     round(FJMA_int2_R10$Pvalue, 2),
                                     round(FJMJ_int2_R10$Pvalue, 2), 
                                     round(FAMJ_int2_R10$Pvalue, 2), 
                                     round(FAMA_int2_R10$Pvalue, 2),
                                     round(MJMA_int2_R10$Pvalue, 2),
                                     round(FJFA_slope2_R10$Pvalue, 2),
                                     round(FJMA_slope2_R10$Pvalue, 2),
                                     round(FJMJ_slope2_R10$Pvalue, 2), 
                                     round(FAMJ_slope2_R10$Pvalue, 2), 
                                     round(FAMA_slope2_R10$Pvalue, 2),
                                     round(MJMA_slope2_R10$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R10$PostMode, 2),
                                       round(FJMA_int2_R10$PostMode, 2),
                                       round(FJMJ_int2_R10$PostMode, 2), 
                                       round(FAMJ_int2_R10$PostMode, 2), 
                                       round(FAMA_int2_R10$PostMode, 2),
                                       round(MJMA_int2_R10$PostMode, 2),
                                       round(FJFA_slope2_R10$PostMode, 2),
                                       round(FJMA_slope2_R10$PostMode, 2),
                                       round(FJMJ_slope2_R10$PostMode, 2), 
                                       round(FAMJ_slope2_R10$PostMode, 2), 
                                       round(FAMA_slope2_R10$PostMode, 2),
                                       round(MJMA_slope2_R10$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R10$LowCrI, 2),
                                     round(FJMA_int2_R10$LowCrI, 2),
                                     round(FJMJ_int2_R10$LowCrI, 2), 
                                     round(FAMJ_int2_R10$LowCrI, 2), 
                                     round(FAMA_int2_R10$LowCrI, 2),
                                     round(MJMA_int2_R10$LowCrI, 2),
                                     round(FJFA_slope2_R10$LowCrI, 2),
                                     round(FJMA_slope2_R10$LowCrI, 2),
                                     round(FJMJ_slope2_R10$LowCrI, 2), 
                                     round(FAMJ_slope2_R10$LowCrI, 2), 
                                     round(FAMA_slope2_R10$LowCrI, 2),
                                     round(MJMA_slope2_R10$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R10$HighCrI, 2),
                                      round(FJMA_int2_R10$HighCrI, 2),
                                      round(FJMJ_int2_R10$HighCrI, 2), 
                                      round(FAMJ_int2_R10$HighCrI, 2), 
                                      round(FAMA_int2_R10$HighCrI, 2),
                                      round(MJMA_int2_R10$HighCrI, 2),
                                      round(FJFA_slope2_R10$HighCrI, 2),
                                      round(FJMA_slope2_R10$HighCrI, 2),
                                      round(FJMJ_slope2_R10$HighCrI, 2), 
                                      round(FAMJ_slope2_R10$HighCrI, 2), 
                                      round(FAMA_slope2_R10$HighCrI, 2),
                                      round(MJMA_slope2_R10$HighCrI, 2)), )

##Remove CoreFeeder=11A----
data_R11 <- data_MS %>% filter(CoreFeeder!="11A")

###Off-Territory Use----
m1_R11 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R11, family=binomial, 
                control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1_R11) #model is not overdispersed

#DHARMa assumptions test
sim_results_m1_R11 <- simulateResiduals(m1_R11)
plot(sim_results_m1_R11)
test_results_m1_R11 <- testResiduals(sim_results_m1_R11)
print(test_results_m1_R11)

summary(m1_R11)

sm1_R11<-sim(m1_R11, 1000)
mode1_R11<-posterior.mode(as.mcmc(sm1_R11@fixef))
HPD1_R11<-HPDinterval(as.mcmc(sm1_R11@fixef))
mode1_R11 #estimates
HPD1_R11 #CrIs

#between Bird ID variance
var_THC1_R11 <- sm1_R11@ranef$TransponderHexCode
bvar_THC1_R11<-as.vector(apply(var_THC1_R11, 1, var))
bvar_THC1_R11<-as.mcmc(bvar_THC1_R11)
posterior.mode(bvar_THC1_R11) #5.326673        
HPDinterval(bvar_THC1_R11)  #(4.232656, 6.892394)

#between CoreFeeder variance
var_CF1_R11 <- sm1_R11@ranef$CoreFeeder
bvar_CF1_R11<-as.vector(apply(var_CF1_R11, 1, var))
bvar_CF1_R11<-as.mcmc(bvar_CF1_R11)
posterior.mode(bvar_CF1_R11) #11.61477          
HPDinterval(bvar_CF1_R11)  #(3.258871, 29.98047)

#Repeatability
rep1_R11<-bvar_THC1_R11 / (bvar_THC1_R11 + (pi^2)/3)
posterior.mode(rep1_R11) #0.6183292       
HPDinterval(rep1_R11) #(0.5695497, 0.6837276)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA (intercept)
FA_int1_R11 <- p_zero(sm1_R11,3) #0.022
#MJ (intercept)
MJ_int1_R11 <- p_zero(sm1_R11,2) #0.026
#FJ (slope)
FJ_slope1_R11 <- p_zero(sm1_R11,5) #0.029
#MJ (slope)
MJ_slope1_R11 <- p_zero(sm1_R11,6) #0.034
#MA (slope)
MA_slope1_R11 <- p_zero(sm1_R11,8) #0.351

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R11 <- p_difference(sm1_R11,3,1)
FJFA_int1_R11 
#MJ-FJ (intercept)
FJMJ_int1_R11 <- p_difference(sm1_R11,2,1)
FJMJ_int1_R11 
#MJ-FA (intercept)
FAMJ_int1_R11 <- p_difference(sm1_R11,2,3)
FAMJ_int1_R11 
#MA-FJ (intercept)
FJMA_int1_R11 <- p_difference(sm1_R11,4,1)
FJMA_int1_R11
#MA-FA (intercept)
FAMA_int1_R11 <- p_difference(sm1_R11,4,3)
FAMA_int1_R11 
#MA-MJ (intercept)
MJMA_int1_R11 <- p_difference(sm1_R11,4,2)
MJMA_int1_R11 
#FJ-FA (slope)
FJFA_slope1_R11 <- p_difference(sm1_R11,5,7)
FJFA_slope1_R11 
#FJ-MJ (slope)
FJMJ_slope1_R11 <- p_difference(sm1_R11,5,6)
FJMJ_slope1_R11
#FJ-MA (slope)
FJMA_slope1_R11 <- p_difference(sm1_R11,5,8)
FJMA_slope1_R11 
#FA-MJ (slope)
FAMJ_slope1_R11 <- p_difference(sm1_R11,7,6)
FAMJ_slope1_R11 
#FA-MA (slope)
FAMA_slope1_R11 <- p_difference(sm1_R11,7,8)
FAMA_slope1_R11
#MJ-MA (slope)
MJMA_slope1_R11 <- p_difference(sm1_R11,6,8)
MJMA_slope1_R11

###Table
m1_R11_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R11$Pvalue, 2),
                                     round(FJMA_int1_R11$Pvalue, 2),
                                     round(FJMJ_int1_R11$Pvalue, 2), 
                                     round(FAMJ_int1_R11$Pvalue, 2), 
                                     round(FAMA_int1_R11$Pvalue, 2),
                                     round(MJMA_int1_R11$Pvalue, 2),
                                     round(FJFA_slope1_R11$Pvalue, 2),
                                     round(FJMA_slope1_R11$Pvalue, 2),
                                     round(FJMJ_slope1_R11$Pvalue, 2), 
                                     round(FAMJ_slope1_R11$Pvalue, 2), 
                                     round(FAMA_slope1_R11$Pvalue, 2),
                                     round(MJMA_slope1_R11$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R11$PostMode, 2),
                                       round(FJMA_int1_R11$PostMode, 2),
                                       round(FJMJ_int1_R11$PostMode, 2), 
                                       round(FAMJ_int1_R11$PostMode, 2), 
                                       round(FAMA_int1_R11$PostMode, 2),
                                       round(MJMA_int1_R11$PostMode, 2),
                                       round(FJFA_slope1_R11$PostMode, 2),
                                       round(FJMA_slope1_R11$PostMode, 2),
                                       round(FJMJ_slope1_R11$PostMode, 2), 
                                       round(FAMJ_slope1_R11$PostMode, 2), 
                                       round(FAMA_slope1_R11$PostMode, 2),
                                       round(MJMA_slope1_R11$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R11$LowCrI, 2),
                                     round(FJMA_int1_R11$LowCrI, 2),
                                     round(FJMJ_int1_R11$LowCrI, 2), 
                                     round(FAMJ_int1_R11$LowCrI, 2), 
                                     round(FAMA_int1_R11$LowCrI, 2),
                                     round(MJMA_int1_R11$LowCrI, 2),
                                     round(FJFA_slope1_R11$LowCrI, 2),
                                     round(FJMA_slope1_R11$LowCrI, 2),
                                     round(FJMJ_slope1_R11$LowCrI, 2), 
                                     round(FAMJ_slope1_R11$LowCrI, 2), 
                                     round(FAMA_slope1_R11$LowCrI, 2),
                                     round(MJMA_slope1_R11$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R11$HighCrI, 2),
                                      round(FJMA_int1_R11$HighCrI, 2),
                                      round(FJMJ_int1_R11$HighCrI, 2), 
                                      round(FAMJ_int1_R11$HighCrI, 2), 
                                      round(FAMA_int1_R11$HighCrI, 2),
                                      round(MJMA_int1_R11$HighCrI, 2),
                                      round(FJFA_slope1_R11$HighCrI, 2),
                                      round(FJMA_slope1_R11$HighCrI, 2),
                                      round(FJMJ_slope1_R11$HighCrI, 2), 
                                      round(FAMJ_slope1_R11$HighCrI, 2), 
                                      round(FAMA_slope1_R11$HighCrI, 2),
                                      round(MJMA_slope1_R11$HighCrI, 2)), )

###Daily Feeder Visits----
m2_R11 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R11)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R11)
hist(resid(m2_R11))
#DHARMa assumptions test
sim_results_m2_R11 <- simulateResiduals(m2_R11)
plot(sim_results_m2_R11)
test_results_m2_R11 <- testResiduals(sim_results_m2_R11)
print(test_results_m2_R11)

summary(m2_R11)

sm2_R11<-sim(m2_R11, 1000)
mode2_m2_R11<-posterior.mode(as.mcmc(sm2_R11@fixef))
HPD2_m2_R11<-HPDinterval(as.mcmc(sm2_R11@fixef))
mode2_m2_R11 #estimates
HPD2_m2_R11 #CrIs

#between Bird ID variance
var_THC2_R11 <- sm2_R11@ranef$TransponderHexCode
bvar_THC2_R11<-as.vector(apply(var_THC2_R11, 1, var))
bvar_THC2_R11<-as.mcmc(bvar_THC2_R11)
posterior.mode(bvar_THC2_R11) #1.890605     
HPDinterval(bvar_THC2_R11)  #(1.728966, 2.244716)

#between CoreFeeder variance
var_CF2_R11 <- sm2_R11@ranef$CoreFeeder
bvar_CF2_R11<-as.vector(apply(var_CF2_R11, 1, var))
bvar_CF2_R11<-as.mcmc(bvar_CF2_R11)
posterior.mode(bvar_CF2_R11) #0.09748735      
HPDinterval(bvar_CF2_R11)  #(0.04079759, 0.1612401)

#between Residual variance
rvar2_R11<-sm2_R11@sigma^2
rvar2_R11<-as.mcmc(rvar2_R11)
posterior.mode(rvar2_R11) #1.92012      
HPDinterval(rvar2_R11) #(1.852065, 2.023663)

#Repeatability
rep2_R11 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R11, 
                datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R11) # 0.472 (0.381, 0.554)

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R11 <- p_difference(sm2_R11,3,1)
FJFA_int2_R11 
#MJ-FJ (intercept)
FJMJ_int2_R11 <- p_difference(sm2_R11,2,1)
FJMJ_int2_R11 
#MJ-FA (intercept)
FAMJ_int2_R11 <- p_difference(sm2_R11,2,3)
FAMJ_int2_R11 
#MA-FJ (intercept)
FJMA_int2_R11 <- p_difference(sm2_R11,4,1)
FJMA_int2_R11
#MA-FA (intercept)
FAMA_int2_R11 <- p_difference(sm2_R11,4,3)
FAMA_int2_R11 
#MA-MJ (intercept)
MJMA_int2_R11 <- p_difference(sm2_R11,4,2)
MJMA_int2_R11 
#FJ-FA (slope)
FJFA_slope2_R11 <- p_difference(sm2_R11,5,7)
FJFA_slope2_R11 
#FJ-MJ (slope)
FJMJ_slope2_R11 <- p_difference(sm2_R11,5,6)
FJMJ_slope2_R11
#FJ-MA (slope)
FJMA_slope2_R11 <- p_difference(sm2_R11,5,8)
FJMA_slope2_R11 
#FA-MJ (slope)
FAMJ_slope2_R11 <- p_difference(sm2_R11,7,6)
FAMJ_slope2_R11 
#FA-MA (slope)
FAMA_slope2_R11 <- p_difference(sm2_R11,7,8)
FAMA_slope2_R11
#MJ-MA (slope)
MJMA_slope2_R11 <- p_difference(sm2_R11,6,8)
MJMA_slope2_R11

###Table
m2_R11_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R11$Pvalue, 2),
                                     round(FJMA_int2_R11$Pvalue, 2),
                                     round(FJMJ_int2_R11$Pvalue, 2), 
                                     round(FAMJ_int2_R11$Pvalue, 2), 
                                     round(FAMA_int2_R11$Pvalue, 2),
                                     round(MJMA_int2_R11$Pvalue, 2),
                                     round(FJFA_slope2_R11$Pvalue, 2),
                                     round(FJMA_slope2_R11$Pvalue, 2),
                                     round(FJMJ_slope2_R11$Pvalue, 2), 
                                     round(FAMJ_slope2_R11$Pvalue, 2), 
                                     round(FAMA_slope2_R11$Pvalue, 2),
                                     round(MJMA_slope2_R11$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R11$PostMode, 2),
                                       round(FJMA_int2_R11$PostMode, 2),
                                       round(FJMJ_int2_R11$PostMode, 2), 
                                       round(FAMJ_int2_R11$PostMode, 2), 
                                       round(FAMA_int2_R11$PostMode, 2),
                                       round(MJMA_int2_R11$PostMode, 2),
                                       round(FJFA_slope2_R11$PostMode, 2),
                                       round(FJMA_slope2_R11$PostMode, 2),
                                       round(FJMJ_slope2_R11$PostMode, 2), 
                                       round(FAMJ_slope2_R11$PostMode, 2), 
                                       round(FAMA_slope2_R11$PostMode, 2),
                                       round(MJMA_slope2_R11$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R11$LowCrI, 2),
                                     round(FJMA_int2_R11$LowCrI, 2),
                                     round(FJMJ_int2_R11$LowCrI, 2), 
                                     round(FAMJ_int2_R11$LowCrI, 2), 
                                     round(FAMA_int2_R11$LowCrI, 2),
                                     round(MJMA_int2_R11$LowCrI, 2),
                                     round(FJFA_slope2_R11$LowCrI, 2),
                                     round(FJMA_slope2_R11$LowCrI, 2),
                                     round(FJMJ_slope2_R11$LowCrI, 2), 
                                     round(FAMJ_slope2_R11$LowCrI, 2), 
                                     round(FAMA_slope2_R11$LowCrI, 2),
                                     round(MJMA_slope2_R11$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R11$HighCrI, 2),
                                      round(FJMA_int2_R11$HighCrI, 2),
                                      round(FJMJ_int2_R11$HighCrI, 2), 
                                      round(FAMJ_int2_R11$HighCrI, 2), 
                                      round(FAMA_int2_R11$HighCrI, 2),
                                      round(MJMA_int2_R11$HighCrI, 2),
                                      round(FJFA_slope2_R11$HighCrI, 2),
                                      round(FJMA_slope2_R11$HighCrI, 2),
                                      round(FJMJ_slope2_R11$HighCrI, 2), 
                                      round(FAMJ_slope2_R11$HighCrI, 2), 
                                      round(FAMA_slope2_R11$HighCrI, 2),
                                      round(MJMA_slope2_R11$HighCrI, 2)), )

##Remove CoreFeeder=12A----
data_R12 <- data_MS %>% filter(CoreFeeder!="12A")

###Off-Territory Use----
m1_R12 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R12, family=binomial, 
                control=glmerControl(optimizer="bobyqa"))
overdisp_fun(m1_R12) #model is not overdispersed
#DHARMa assumptions test
sim_results_m1_R12 <- simulateResiduals(m1_R12)
plot(sim_results_m1_R12)
test_results_m1_R12 <- testResiduals(sim_results_m1_R12)
print(test_results_m1_R12)

summary(m1_R12)

sm1_R12<-sim(m1_R12, 1000)
mode1_R12<-posterior.mode(as.mcmc(sm1_R12@fixef))
HPD1_R12<-HPDinterval(as.mcmc(sm1_R12@fixef))
mode1_R12 #estimates
HPD1_R12 #CrIs

#between Bird ID variance
var_THC1_R12 <- sm1_R12@ranef$TransponderHexCode
bvar_THC1_R12<-as.vector(apply(var_THC1_R12, 1, var))
bvar_THC1_R12<-as.mcmc(bvar_THC1_R12)
posterior.mode(bvar_THC1_R12) #4.482465        
HPDinterval(bvar_THC1_R12)  #(3.658125, 5.735958)

#between CoreFeeder variance
var_CF1_R12 <- sm1_R12@ranef$CoreFeeder
bvar_CF1_R12<-as.vector(apply(var_CF1_R12, 1, var))
bvar_CF1_R12<-as.mcmc(bvar_CF1_R12)
posterior.mode(bvar_CF1_R12) #13.0697          
HPDinterval(bvar_CF1_R12)  #(2.719215, 28.2292)

#Repeatability
rep1_R12<-bvar_THC1_R12 / (bvar_THC1_R12 + (pi^2)/3)
posterior.mode(rep1_R12) #0.576781       
HPDinterval(rep1_R12) #(0.5296276, 0.6379412)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (intercept)
FJ_int1_R12 <- p_zero(sm1_R12,1) #0.069
#FA (intercept)
FA_int1_R12 <- p_zero(sm1_R12,3) #0.045
#MJ (intercept)
MJ_int1_R12 <- p_zero(sm1_R12,2) #0.067
#MJ (slope)
MJ_slope1_R12 <- p_zero(sm1_R12,6) #0.247
#MA (slope)
MA_slope1_R12 <- p_zero(sm1_R12,8) #0.414


##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R12 <- p_difference(sm1_R12,3,1)
FJFA_int1_R12 
#MJ-FJ (intercept)
FJMJ_int1_R12 <- p_difference(sm1_R12,2,1)
FJMJ_int1_R12 
#MJ-FA (intercept)
FAMJ_int1_R12 <- p_difference(sm1_R12,2,3)
FAMJ_int1_R12 
#MA-FJ (intercept)
FJMA_int1_R12 <- p_difference(sm1_R12,4,1)
FJMA_int1_R12
#MA-FA (intercept)
FAMA_int1_R12 <- p_difference(sm1_R12,4,3)
FAMA_int1_R12 
#MA-MJ (intercept)
MJMA_int1_R12 <- p_difference(sm1_R12,4,2)
MJMA_int1_R12 
#FJ-FA (slope)
FJFA_slope1_R12 <- p_difference(sm1_R12,5,7)
FJFA_slope1_R12 
#FJ-MJ (slope)
FJMJ_slope1_R12 <- p_difference(sm1_R12,5,6)
FJMJ_slope1_R12
#FJ-MA (slope)
FJMA_slope1_R12 <- p_difference(sm1_R12,5,8)
FJMA_slope1_R12 
#FA-MJ (slope)
FAMJ_slope1_R12 <- p_difference(sm1_R12,7,6)
FAMJ_slope1_R12 
#FA-MA (slope)
FAMA_slope1_R12 <- p_difference(sm1_R12,7,8)
FAMA_slope1_R12
#MJ-MA (slope)
MJMA_slope1_R12 <- p_difference(sm1_R12,6,8)
MJMA_slope1_R12

###Table
m1_R12_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R12$Pvalue, 2),
                                     round(FJMA_int1_R12$Pvalue, 2),
                                     round(FJMJ_int1_R12$Pvalue, 2), 
                                     round(FAMJ_int1_R12$Pvalue, 2), 
                                     round(FAMA_int1_R12$Pvalue, 2),
                                     round(MJMA_int1_R12$Pvalue, 2),
                                     round(FJFA_slope1_R12$Pvalue, 2),
                                     round(FJMA_slope1_R12$Pvalue, 2),
                                     round(FJMJ_slope1_R12$Pvalue, 2), 
                                     round(FAMJ_slope1_R12$Pvalue, 2), 
                                     round(FAMA_slope1_R12$Pvalue, 2),
                                     round(MJMA_slope1_R12$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R12$PostMode, 2),
                                       round(FJMA_int1_R12$PostMode, 2),
                                       round(FJMJ_int1_R12$PostMode, 2), 
                                       round(FAMJ_int1_R12$PostMode, 2), 
                                       round(FAMA_int1_R12$PostMode, 2),
                                       round(MJMA_int1_R12$PostMode, 2),
                                       round(FJFA_slope1_R12$PostMode, 2),
                                       round(FJMA_slope1_R12$PostMode, 2),
                                       round(FJMJ_slope1_R12$PostMode, 2), 
                                       round(FAMJ_slope1_R12$PostMode, 2), 
                                       round(FAMA_slope1_R12$PostMode, 2),
                                       round(MJMA_slope1_R12$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R12$LowCrI, 2),
                                     round(FJMA_int1_R12$LowCrI, 2),
                                     round(FJMJ_int1_R12$LowCrI, 2), 
                                     round(FAMJ_int1_R12$LowCrI, 2), 
                                     round(FAMA_int1_R12$LowCrI, 2),
                                     round(MJMA_int1_R12$LowCrI, 2),
                                     round(FJFA_slope1_R12$LowCrI, 2),
                                     round(FJMA_slope1_R12$LowCrI, 2),
                                     round(FJMJ_slope1_R12$LowCrI, 2), 
                                     round(FAMJ_slope1_R12$LowCrI, 2), 
                                     round(FAMA_slope1_R12$LowCrI, 2),
                                     round(MJMA_slope1_R12$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R12$HighCrI, 2),
                                      round(FJMA_int1_R12$HighCrI, 2),
                                      round(FJMJ_int1_R12$HighCrI, 2), 
                                      round(FAMJ_int1_R12$HighCrI, 2), 
                                      round(FAMA_int1_R12$HighCrI, 2),
                                      round(MJMA_int1_R12$HighCrI, 2),
                                      round(FJFA_slope1_R12$HighCrI, 2),
                                      round(FJMA_slope1_R12$HighCrI, 2),
                                      round(FJMJ_slope1_R12$HighCrI, 2), 
                                      round(FAMJ_slope1_R12$HighCrI, 2), 
                                      round(FAMA_slope1_R12$HighCrI, 2),
                                      round(MJMA_slope1_R12$HighCrI, 2)), )

###Daily Feeder Visits----
m2_R12 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R12)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R12)
hist(resid(m2_R12))
#DHARMa assumptions test
sim_results_m2_R12 <- simulateResiduals(m2_R12)
plot(sim_results_m2_R12)
test_results_m2_R12 <- testResiduals(sim_results_m2_R12)
print(test_results_m2_R12)

summary(m2_R12)

sm2_R12<-sim(m2_R12, 1000)
mode2_m2_R12<-posterior.mode(as.mcmc(sm2_R12@fixef))
HPD2_m2_R12<-HPDinterval(as.mcmc(sm2_R12@fixef))
mode2_m2_R12 #estimates
HPD2_m2_R12 #CrIs

#between Bird ID variance
var_THC2_R12 <- sm2_R12@ranef$TransponderHexCode
bvar_THC2_R12<-as.vector(apply(var_THC2_R12, 1, var))
bvar_THC2_R12<-as.mcmc(bvar_THC2_R12)
posterior.mode(bvar_THC2_R12) #1.876656     
HPDinterval(bvar_THC2_R12)  #(1.665701, 2.166909)

#between CoreFeeder variance
var_CF2_R12 <- sm2_R12@ranef$CoreFeeder
bvar_CF2_R12<-as.vector(apply(var_CF2_R12, 1, var))
bvar_CF2_R12<-as.mcmc(bvar_CF2_R12)
posterior.mode(bvar_CF2_R12) #0.03855503     
HPDinterval(bvar_CF2_R12)  #(0.01738766, 0.08620087)

#between Residual variance
rvar2_R12<-sm2_R12@sigma^2
rvar2_R12<-as.mcmc(rvar2_R12)
posterior.mode(rvar2_R12) #1.869722     
HPDinterval(rvar2_R12) #(1.802216, 1.947528)

#Repeatability
rep2_R12 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R12, 
                datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R12) # 0.482 (0.406, 0.548)

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R12 <- p_difference(sm2_R12,3,1)
FJFA_int2_R12 
#MJ-FJ (intercept)
FJMJ_int2_R12 <- p_difference(sm2_R12,2,1)
FJMJ_int2_R12 
#MJ-FA (intercept)
FAMJ_int2_R12 <- p_difference(sm2_R12,2,3)
FAMJ_int2_R12 
#MA-FJ (intercept)
FJMA_int2_R12 <- p_difference(sm2_R12,4,1)
FJMA_int2_R12
#MA-FA (intercept)
FAMA_int2_R12 <- p_difference(sm2_R12,4,3)
FAMA_int2_R12 
#MA-MJ (intercept)
MJMA_int2_R12 <- p_difference(sm2_R12,4,2)
MJMA_int2_R12 
#FJ-FA (slope)
FJFA_slope2_R12 <- p_difference(sm2_R12,5,7)
FJFA_slope2_R12 
#FJ-MJ (slope)
FJMJ_slope2_R12 <- p_difference(sm2_R12,5,6)
FJMJ_slope2_R12
#FJ-MA (slope)
FJMA_slope2_R12 <- p_difference(sm2_R12,5,8)
FJMA_slope2_R12 
#FA-MJ (slope)
FAMJ_slope2_R12 <- p_difference(sm2_R12,7,6)
FAMJ_slope2_R12 
#FA-MA (slope)
FAMA_slope2_R12 <- p_difference(sm2_R12,7,8)
FAMA_slope2_R12
#MJ-MA (slope)
MJMA_slope2_R12 <- p_difference(sm2_R12,6,8)
MJMA_slope2_R12

###Table
m2_R12_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R12$Pvalue, 2),
                                     round(FJMA_int2_R12$Pvalue, 2),
                                     round(FJMJ_int2_R12$Pvalue, 2), 
                                     round(FAMJ_int2_R12$Pvalue, 2), 
                                     round(FAMA_int2_R12$Pvalue, 2),
                                     round(MJMA_int2_R12$Pvalue, 2),
                                     round(FJFA_slope2_R12$Pvalue, 2),
                                     round(FJMA_slope2_R12$Pvalue, 2),
                                     round(FJMJ_slope2_R12$Pvalue, 2), 
                                     round(FAMJ_slope2_R12$Pvalue, 2), 
                                     round(FAMA_slope2_R12$Pvalue, 2),
                                     round(MJMA_slope2_R12$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R12$PostMode, 2),
                                       round(FJMA_int2_R12$PostMode, 2),
                                       round(FJMJ_int2_R12$PostMode, 2), 
                                       round(FAMJ_int2_R12$PostMode, 2), 
                                       round(FAMA_int2_R12$PostMode, 2),
                                       round(MJMA_int2_R12$PostMode, 2),
                                       round(FJFA_slope2_R12$PostMode, 2),
                                       round(FJMA_slope2_R12$PostMode, 2),
                                       round(FJMJ_slope2_R12$PostMode, 2), 
                                       round(FAMJ_slope2_R12$PostMode, 2), 
                                       round(FAMA_slope2_R12$PostMode, 2),
                                       round(MJMA_slope2_R12$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R12$LowCrI, 2),
                                     round(FJMA_int2_R12$LowCrI, 2),
                                     round(FJMJ_int2_R12$LowCrI, 2), 
                                     round(FAMJ_int2_R12$LowCrI, 2), 
                                     round(FAMA_int2_R12$LowCrI, 2),
                                     round(MJMA_int2_R12$LowCrI, 2),
                                     round(FJFA_slope2_R12$LowCrI, 2),
                                     round(FJMA_slope2_R12$LowCrI, 2),
                                     round(FJMJ_slope2_R12$LowCrI, 2), 
                                     round(FAMJ_slope2_R12$LowCrI, 2), 
                                     round(FAMA_slope2_R12$LowCrI, 2),
                                     round(MJMA_slope2_R12$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R12$HighCrI, 2),
                                      round(FJMA_int2_R12$HighCrI, 2),
                                      round(FJMJ_int2_R12$HighCrI, 2), 
                                      round(FAMJ_int2_R12$HighCrI, 2), 
                                      round(FAMA_int2_R12$HighCrI, 2),
                                      round(MJMA_int2_R12$HighCrI, 2),
                                      round(FJFA_slope2_R12$HighCrI, 2),
                                      round(FJMA_slope2_R12$HighCrI, 2),
                                      round(FJMJ_slope2_R12$HighCrI, 2), 
                                      round(FAMJ_slope2_R12$HighCrI, 2), 
                                      round(FAMA_slope2_R12$HighCrI, 2),
                                      round(MJMA_slope2_R12$HighCrI, 2)), )

##Remove CoreFeeder=16A----
data_R16 <- data_MS %>% filter(CoreFeeder!="16A")

###Off-Territory Use----
m1_R16 <- glmer(offT ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R16, family=binomial, 
                control=glmerControl(optimizer="bobyqa"))

overdisp_fun(m1_R16) #model is not overdispersed

#DHARMa assumptions test
sim_results_m1_R16 <- simulateResiduals(m1_R16)
plot(sim_results_m1_R16)
test_results_m1_R16 <- testResiduals(sim_results_m1_R16)
print(test_results_m1_R16)

summary(m1_R16)

sm1_R16<-sim(m1_R16, 1000)
mode1_R16<-posterior.mode(as.mcmc(sm1_R16@fixef))
HPD1_R16<-HPDinterval(as.mcmc(sm1_R16@fixef))
mode1_R16 #estimates
HPD1_R16 #CrIs

#between Bird ID variance
var_THC1_R16 <- sm1_R16@ranef$TransponderHexCode
bvar_THC1_R16<-as.vector(apply(var_THC1_R16, 1, var))
bvar_THC1_R16<-as.mcmc(bvar_THC1_R16)
posterior.mode(bvar_THC1_R16) #4.626733        
HPDinterval(bvar_THC1_R16)  #(3.621612, 5.675722)

#between CoreFeeder variance
var_CF1_R16 <- sm1_R16@ranef$CoreFeeder
bvar_CF1_R16<-as.vector(apply(var_CF1_R16, 1, var))
bvar_CF1_R16<-as.mcmc(bvar_CF1_R16)
posterior.mode(bvar_CF1_R16) #6.337645          
HPDinterval(bvar_CF1_R16)  #(2.015135, 13.09185)

#Repeatability
rep1_R16<-bvar_THC1_R16 / (bvar_THC1_R16 + (pi^2)/3)
posterior.mode(rep1_R16) #0.6034938       
HPDinterval(rep1_R16) #(0.5319447, 0.6383637)

##Effect Size Significance
#only calculated for estimates whose CrIs overlap 0
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FJ (intercept)
FJ_int1_R16 <- p_zero(sm1_R16,1) #0.052
#FA (intercept)
FA_int1_R16 <- p_zero(sm1_R16,3) #0.095
#MJ (intercept)
MJ_int1_R16 <- p_zero(sm1_R16,2) #0.064
#MJ (slope)
MJ_slope1_R16 <- p_zero(sm1_R16,6) #0.27
#MA (slope)
MA_slope1_R16 <- p_zero(sm1_R16,8) #0.664

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int1_R16 <- p_difference(sm1_R16,3,1)
FJFA_int1_R16 
#MJ-FJ (intercept)
FJMJ_int1_R16 <- p_difference(sm1_R16,2,1)
FJMJ_int1_R16 
#MJ-FA (intercept)
FAMJ_int1_R16 <- p_difference(sm1_R16,2,3)
FAMJ_int1_R16 
#MA-FJ (intercept)
FJMA_int1_R16 <- p_difference(sm1_R16,4,1)
FJMA_int1_R16
#MA-FA (intercept)
FAMA_int1_R16 <- p_difference(sm1_R16,4,3)
FAMA_int1_R16 
#MA-MJ (intercept)
MJMA_int1_R16 <- p_difference(sm1_R16,4,2)
MJMA_int1_R16 
#FJ-FA (slope)
FJFA_slope1_R16 <- p_difference(sm1_R16,5,7)
FJFA_slope1_R16 
#FJ-MJ (slope)
FJMJ_slope1_R16 <- p_difference(sm1_R16,5,6)
FJMJ_slope1_R16
#FJ-MA (slope)
FJMA_slope1_R16 <- p_difference(sm1_R16,5,8)
FJMA_slope1_R16 
#FA-MJ (slope)
FAMJ_slope1_R16 <- p_difference(sm1_R16,7,6)
FAMJ_slope1_R16 
#FA-MA (slope)
FAMA_slope1_R16 <- p_difference(sm1_R16,7,8)
FAMA_slope1_R16
#MJ-MA (slope)
MJMA_slope1_R16 <- p_difference(sm1_R16,6,8)
MJMA_slope1_R16

###Table
m1_R16_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int1_R16$Pvalue, 2),
                                     round(FJMA_int1_R16$Pvalue, 2),
                                     round(FJMJ_int1_R16$Pvalue, 2), 
                                     round(FAMJ_int1_R16$Pvalue, 2), 
                                     round(FAMA_int1_R16$Pvalue, 2),
                                     round(MJMA_int1_R16$Pvalue, 2),
                                     round(FJFA_slope1_R16$Pvalue, 2),
                                     round(FJMA_slope1_R16$Pvalue, 2),
                                     round(FJMJ_slope1_R16$Pvalue, 2), 
                                     round(FAMJ_slope1_R16$Pvalue, 2), 
                                     round(FAMA_slope1_R16$Pvalue, 2),
                                     round(MJMA_slope1_R16$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int1_R16$PostMode, 2),
                                       round(FJMA_int1_R16$PostMode, 2),
                                       round(FJMJ_int1_R16$PostMode, 2), 
                                       round(FAMJ_int1_R16$PostMode, 2), 
                                       round(FAMA_int1_R16$PostMode, 2),
                                       round(MJMA_int1_R16$PostMode, 2),
                                       round(FJFA_slope1_R16$PostMode, 2),
                                       round(FJMA_slope1_R16$PostMode, 2),
                                       round(FJMJ_slope1_R16$PostMode, 2), 
                                       round(FAMJ_slope1_R16$PostMode, 2), 
                                       round(FAMA_slope1_R16$PostMode, 2),
                                       round(MJMA_slope1_R16$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int1_R16$LowCrI, 2),
                                     round(FJMA_int1_R16$LowCrI, 2),
                                     round(FJMJ_int1_R16$LowCrI, 2), 
                                     round(FAMJ_int1_R16$LowCrI, 2), 
                                     round(FAMA_int1_R16$LowCrI, 2),
                                     round(MJMA_int1_R16$LowCrI, 2),
                                     round(FJFA_slope1_R16$LowCrI, 2),
                                     round(FJMA_slope1_R16$LowCrI, 2),
                                     round(FJMJ_slope1_R16$LowCrI, 2), 
                                     round(FAMJ_slope1_R16$LowCrI, 2), 
                                     round(FAMA_slope1_R16$LowCrI, 2),
                                     round(MJMA_slope1_R16$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int1_R16$HighCrI, 2),
                                      round(FJMA_int1_R16$HighCrI, 2),
                                      round(FJMJ_int1_R16$HighCrI, 2), 
                                      round(FAMJ_int1_R16$HighCrI, 2), 
                                      round(FAMA_int1_R16$HighCrI, 2),
                                      round(MJMA_int1_R16$HighCrI, 2),
                                      round(FJFA_slope1_R16$HighCrI, 2),
                                      round(FJMA_slope1_R16$HighCrI, 2),
                                      round(FJMJ_slope1_R16$HighCrI, 2), 
                                      round(FAMJ_slope1_R16$HighCrI, 2), 
                                      round(FAMA_slope1_R16$HighCrI, 2),
                                      round(MJMA_slope1_R16$HighCrI, 2)), )

###Daily Feeder Visits----
m2_R16 <- lmer(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), data = data_R16)
#boundary (singular) fit: see help('isSingular') error b/c Core Feeder random effect so small

#check model assumptions
plot(m2_R16)
hist(resid(m2_R16))
#DHARMa assumptions test
sim_results_m2_R16 <- simulateResiduals(m2_R16)
plot(sim_results_m2_R16)
test_results_m2_R16 <- testResiduals(sim_results_m2_R16)
print(test_results_m2_R16)

summary(m2_R16)

sm2_R16<-sim(m2_R16, 1000)
mode2_m2_R16<-posterior.mode(as.mcmc(sm2_R16@fixef))
HPD2_m2_R16<-HPDinterval(as.mcmc(sm2_R16@fixef))
mode2_m2_R16 #estimates
HPD2_m2_R16 #CrIs

#between Bird ID variance
var_THC2_R16 <- sm2_R16@ranef$TransponderHexCode
bvar_THC2_R16<-as.vector(apply(var_THC2_R16, 1, var))
bvar_THC2_R16<-as.mcmc(bvar_THC2_R16)
posterior.mode(bvar_THC2_R16) #1.998315    
HPDinterval(bvar_THC2_R16)  #(1.811481, 2.305041)

#between CoreFeeder variance
var_CF2_R16 <- sm2_R16@ranef$CoreFeeder
bvar_CF2_R16<-as.vector(apply(var_CF2_R16, 1, var))
bvar_CF2_R16<-as.mcmc(bvar_CF2_R16)
posterior.mode(bvar_CF2_R16) #0.07742645     
HPDinterval(bvar_CF2_R16)  #(0.04336154, 0.2576291)

#between Residual variance
rvar2_R16<-sm2_R16@sigma^2
rvar2_R16<-as.mcmc(rvar2_R16)
posterior.mode(rvar2_R16) #1.724117     
HPDinterval(rvar2_R16) #(1.663493, 1.811331)

#Repeatability
rep2_R16 <- rpt(sqrt(VisitCount) ~ -1 + Age_Sex + Age_Sex:TempL0 + (1|TransponderHexCode) + (1|CoreFeeder), grname = "TransponderHexCode", data = data_R16, 
                datatype = "Gaussian", nboot = 1000, npermut = 0)
#boundary (singular) fit: see help('isSingular') warning occurs b/c CoreFeeder random effects are small
print(rep2_R16) # 0.51 (0.416, 0.588)

##Pairwise Contrasts
#MJ - Male Juvenile
#MA - Male Adult
#FJ - Female Juvenile
#FA - Female Adult

#FA-FJ (intercept)
FJFA_int2_R16 <- p_difference(sm2_R16,3,1)
FJFA_int2_R16 
#MJ-FJ (intercept)
FJMJ_int2_R16 <- p_difference(sm2_R16,2,1)
FJMJ_int2_R16 
#MJ-FA (intercept)
FAMJ_int2_R16 <- p_difference(sm2_R16,2,3)
FAMJ_int2_R16 
#MA-FJ (intercept)
FJMA_int2_R16 <- p_difference(sm2_R16,4,1)
FJMA_int2_R16
#MA-FA (intercept)
FAMA_int2_R16 <- p_difference(sm2_R16,4,3)
FAMA_int2_R16 
#MA-MJ (intercept)
MJMA_int2_R16 <- p_difference(sm2_R16,4,2)
MJMA_int2_R16 
#FJ-FA (slope)
FJFA_slope2_R16 <- p_difference(sm2_R16,5,7)
FJFA_slope2_R16 
#FJ-MJ (slope)
FJMJ_slope2_R16 <- p_difference(sm2_R16,5,6)
FJMJ_slope2_R16
#FJ-MA (slope)
FJMA_slope2_R16 <- p_difference(sm2_R16,5,8)
FJMA_slope2_R16 
#FA-MJ (slope)
FAMJ_slope2_R16 <- p_difference(sm2_R16,7,6)
FAMJ_slope2_R16 
#FA-MA (slope)
FAMA_slope2_R16 <- p_difference(sm2_R16,7,8)
FAMA_slope2_R16
#MJ-MA (slope)
MJMA_slope2_R16 <- p_difference(sm2_R16,6,8)
MJMA_slope2_R16

###Table
m2_R16_contrasts <- tibble(Contrast = c("FA-FJ (int)",
                                       "MJ-FJ (int)",
                                       "MJ-FA (int)", 
                                       "MA-FJ (int)", 
                                       "MA-FA (int)", 
                                       "MA-MJ (int)", 
                                       "FJ-FA (slope)",
                                       "FJ-MJ (slope)",
                                       "FJ-MA (slope)", 
                                       "FA-MJ (slope)", 
                                       "FA-MA (slope)", 
                                       "MJ-MA (slope)"),
                          Pvalue = c(round(FJFA_int2_R16$Pvalue, 2),
                                     round(FJMA_int2_R16$Pvalue, 2),
                                     round(FJMJ_int2_R16$Pvalue, 2), 
                                     round(FAMJ_int2_R16$Pvalue, 2), 
                                     round(FAMA_int2_R16$Pvalue, 2),
                                     round(MJMA_int2_R16$Pvalue, 2),
                                     round(FJFA_slope2_R16$Pvalue, 2),
                                     round(FJMA_slope2_R16$Pvalue, 2),
                                     round(FJMJ_slope2_R16$Pvalue, 2), 
                                     round(FAMJ_slope2_R16$Pvalue, 2), 
                                     round(FAMA_slope2_R16$Pvalue, 2),
                                     round(MJMA_slope2_R16$Pvalue, 2)), 
                          PostMode = c(round(FJFA_int2_R16$PostMode, 2),
                                       round(FJMA_int2_R16$PostMode, 2),
                                       round(FJMJ_int2_R16$PostMode, 2), 
                                       round(FAMJ_int2_R16$PostMode, 2), 
                                       round(FAMA_int2_R16$PostMode, 2),
                                       round(MJMA_int2_R16$PostMode, 2),
                                       round(FJFA_slope2_R16$PostMode, 2),
                                       round(FJMA_slope2_R16$PostMode, 2),
                                       round(FJMJ_slope2_R16$PostMode, 2), 
                                       round(FAMJ_slope2_R16$PostMode, 2), 
                                       round(FAMA_slope2_R16$PostMode, 2),
                                       round(MJMA_slope2_R16$PostMode, 2)), 
                          LowCrI = c(round(FJFA_int2_R16$LowCrI, 2),
                                     round(FJMA_int2_R16$LowCrI, 2),
                                     round(FJMJ_int2_R16$LowCrI, 2), 
                                     round(FAMJ_int2_R16$LowCrI, 2), 
                                     round(FAMA_int2_R16$LowCrI, 2),
                                     round(MJMA_int2_R16$LowCrI, 2),
                                     round(FJFA_slope2_R16$LowCrI, 2),
                                     round(FJMA_slope2_R16$LowCrI, 2),
                                     round(FJMJ_slope2_R16$LowCrI, 2), 
                                     round(FAMJ_slope2_R16$LowCrI, 2), 
                                     round(FAMA_slope2_R16$LowCrI, 2),
                                     round(MJMA_slope2_R16$LowCrI, 2)), 
                          HighCrI = c(round(FJFA_int2_R16$HighCrI, 2),
                                      round(FJMA_int2_R16$HighCrI, 2),
                                      round(FJMJ_int2_R16$HighCrI, 2), 
                                      round(FAMJ_int2_R16$HighCrI, 2), 
                                      round(FAMA_int2_R16$HighCrI, 2),
                                      round(MJMA_int2_R16$HighCrI, 2),
                                      round(FJFA_slope2_R16$HighCrI, 2),
                                      round(FJMA_slope2_R16$HighCrI, 2),
                                      round(FJMJ_slope2_R16$HighCrI, 2), 
                                      round(FAMJ_slope2_R16$HighCrI, 2), 
                                      round(FAMA_slope2_R16$HighCrI, 2),
                                      round(MJMA_slope2_R16$HighCrI, 2)), )
