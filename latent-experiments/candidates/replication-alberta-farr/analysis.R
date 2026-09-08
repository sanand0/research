##  No effect of PIT tagging method on survival or body condition in a northern population of Black-capped Chickadees (Poecile atricapilus) ##

# Jonathan J Farr, Elene Haave-Audet, Peter R Thompson, Kimberley J Mathot

# corresponding author: Jonathan J Farr, jfarr@ualberta.ca

# loading packages
library(ggplot2)
library(survival)
library(survminer)
library(dplyr)
library(tidyverse)
library(coxed)
library(here)



dir<-setwd(here())
DATA = read.csv("NORFID.csv") # loading data frame
head(DATA)

####structuring the data properly
DATA$ID<-as.factor(DATA$ID)
DATA$Sex = as.factor(DATA$Sex)
DATA$PIT = as.factor(DATA$PIT)
DATA$FC_Mass<-as.numeric(as.character(DATA$FC_Mass))
DATA$Recap_Mass <- as.numeric(as.character(DATA$Recap_Mass))
DATA$FC_Time <- as.numeric(as.character(DATA$FC_Time))
DATA$FC_Temp <- as.numeric(as.character(DATA$FC_Temp))
DATA$Catching_Season = as.factor(DATA$Catching_Season)

str(DATA)

# removing three birds that were not PIT tagged because of high stress: 
DATA = DATA[!(DATA$ID=="68" | DATA$ID =="107" | DATA$ID =="249"),]

################## Checking for biases in PIT tag assignment #####################
      
# assessing biases in sex distributions with Chi-square test across PIT Treatments
DATASEX = subset(DATA, Sex!="U")
      Sextbl=table(DATASEX$Sex, DATASEX$PIT) #making a contingency table 
      head(Sextbl)
      SEXCHISQ = chisq.test(Sextbl[1:2,1:3]) # chi square test
      SEXCHISQ

      prop.table(table(DATASEX$Sex, DATASEX$PIT),2) # compare sex ratios, proportion of males in each PIT treatment 
    
### assessing biases in body mass with anova to compare the within-sex centered body mass across PIT treatments
DATAMASS=subset(DATASEX, FC_Mass!="NA")
      CenteredMale=subset(DATAMASS, Sex=="M")
      CenteredMale$FC_Mass=scale(CenteredMale$FC_Mass, center=TRUE, scale=FALSE)
      CenteredFemale=subset(DATAMASS, Sex=="F")
      CenteredFemale$FC_Mass=scale(CenteredFemale$FC_Mass, center=TRUE, scale=FALSE)
      CenteredDATA=rbind(CenteredFemale, CenteredMale)
      MASS_ANOVA=aov(formula=FC_Mass~PIT, data=CenteredDATA)  # run the anova 
      summary(MASS_ANOVA)
    
      CenteredDATA %>% # calculate mean within-sex centered mass for each PIT treatment - for summary stats
        group_by(PIT) %>% 
        summarise(mean = mean(FC_Mass),sum = sum(FC_Mass))
      
      ### look for treatment related differences in time of day or mean daily temperature (for supplementary table 1)
      hist(DATA$FC_Time) # normal, no issues with using lm
      m_Time = lm(FC_Time~ PIT, data=DATA)
      summary(m_Time) #time of capture doesn't change across PIT treatments
      
      hist(DATA$FC_Temp) # normal, no issues with using lm
      m_Temp=lm(FC_Temp~PIT, data=DATA)
      summary(m_Temp) ##temperature doesn't change across PIT treatments


################## Survival effects #####################
        
# cox proportional hazards model to compare survival across PIT treatments
        
    mistnet_surv=Surv(time=DATA$Event, event=DATA$Censored) # creating a survival object
    mistnet_cox=coxph(mistnet_surv~PIT, data=DATA) # cox proportional hazard model 
    summary(mistnet_cox)
        
    total_test.ph <- cox.zph(mistnet_cox) # tests the proportional hazards assumption
    total_test.ph ### does not violate the proportional hazards assumption
    
# calculating point estimate needed for the CI to exclude 1 - for the discussion re: sample sizes & detection power
       # leg band PIT
        legcoef = 1.96*0.1627
        legcoef
        exp(legcoef) # hazard ratio required for lower CI to be greater than 1
      # implant PIT
        impcoef = 1.96*0.1640
        impcoef
        exp(impcoef) #  hazard ratio required for lower CI to be greater than 1
   
# generating a data frame with model outputs to plot        
        Model.output <- as.data.frame(exp(cbind("hazard ratio"=coef(mistnet_cox), confint.default(mistnet_cox, level=0.95))))
        Model.output<-rownames_to_column(Model.output, var="variate")
        names(Model.output)[names(Model.output)=="2.5 %"]="lower2.5"
        names(Model.output)[names(Model.output)=="97.5 %"]="upper97.5"
        names(Model.output)[names(Model.output)=="hazard ratio"]="hazard"
        Row <- data.frame(variate='PITA', hazard=1, lower2.5=1, upper97.5=1) # adding in a hazard ratio = 1 for reference category
        coxDATA=rbind(Row, Model.output)
        coxDATA$variate <- factor(coxDATA$variate, levels = c("PITA", "PITB", "PITC"), # changing labels to PIT treatments
                                  labels = c("Control", "Leg Band PIT", "Implant PIT"))
        
# generate graph with hazard ratios
        totalcox = ggplot(data=coxDATA,
                        aes(x=variate, y=hazard, ymin=lower2.5, ymax=upper97.5))+
         geom_pointrange(size=1, stroke=2, position=position_dodge(width=0.6), shape=15)+
          geom_hline(yintercept =1, linetype=2)+
          geom_hline(yintercept =c(0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6), linetype=1, color="grey80")+
          geom_linerange(size=1, position=position_dodge(width=0.1)) + 
          xlab(NULL)+ ylab("Hazard ratio (95% C.I.)\n")+
          geom_errorbar(aes(ymin=lower2.5, ymax=upper97.5), position=position_dodge(width=0.1), width=0.2,size=1.5)+ 
          theme_classic()+
          theme(
                axis.text.y=element_text(size=20, family="Helvetica", color="black", angle=90, hjust=0.5),
                axis.ticks.y=element_blank(),
                axis.text.x=element_text(size=16, family="Helvetica", color="black"),
                axis.title=element_text(size=20, family="Helvetica"))+
          coord_flip()
        totalcox
        
 # kaplan meier curves to look at survival probabilities across time - used later for survival adjustment with RFID data
        mistnet_km = survfit(mistnet_surv~PIT, data=DATA)
        summary(mistnet_km) # generates survival probs at each time step
        
 ########### Compare survival of RFID to mistnet in leg banded birds ##############
        RFID = read.csv("RFID.csv") 
        str(RFID)

        sexRFID = subset(RFID, Sex!="U")
        
 # cox proportional hazards model to compare survival between male and female leg band chickadees from RFID recaptures
        sexRFID = subset(sexRFID, PIT=="D") # only for birds detected at feeders (no mistnet recap data)
        sexRFID_surv=Surv(time=sexRFID$Event, event=sexRFID$Censored) # generates survival object
        sexRFID_cox=coxph(sexRFID_surv~Sex, data=sexRFID) # cox test
        summary(sexRFID_cox) # no significant effect of sex on survival 

        sex_test.ph <- cox.zph(sexRFID_cox) # tests the proportional hazards assumption
        sex_test.ph ### does not violate the proportional hazards assumption
       

#### compare survival of leg band mistnet to leg band RFID
        
        RFID_surv=Surv(time=RFID$Event, event=RFID$Censored) # survival object 

    # kaplan meier curves to look at survival probabilities across time for different PIT treatments 
        
        RFID_km = survfit(Surv(time=RFID$Event, event=RFID$Censored)~PIT, data=RFID)
        summary(RFID_km) # survival probabilities for mistnet vs RFID
        
        RFID_survdiff = survdiff(Surv(time=RFID$Event, event=RFID$Censored) ~ PIT, data=RFID)
        RFID_survdiff ### log rank test to compare survival - substantial difference between mist net and RFID 
      
      # calculating the difference in mortality estimates with mistnet compared to RFID (for leg bands at t=2)
        t2 = (1-0.0506)/(1-0.3038) # 0.0506 = mistnet survival at t2, 0.3038 = RFID survival at t2
        t2 # the mortality overestimation factor = 1.364
RStudio.Version()
        summary(mistnet_km) # provides survival estimates for control and implant birds based on mist net survival 
        control2 = (1-0.1053)/1.363689 # 0.1013 = control bird survival at t=2
        control2 # projected mortality probability at t=2 for control birds
        1-control2 # generates survival probability
        legband2 = (1-0.0506)/1.363689
        legband2 # projected mortality probability at t=2 for control birds
        1-legband2 # generates survival prob
        implant2 = (1-0.0909)/1.363689
        implant2 # projected mortality probability at t=2 for implants
        1-implant2 # survival prob
        
################## Body Condition (sublethal) Effects #####################

        sublethal = subset(DATA, Recap_Mass!="NA") # subset the data to only birds recaptured and weighed 0.5yrs after fall PIT tagging
        
        # compare sex ratios, proportion of males in each PIT treatment 
        prop.table(table(sublethal$Sex, sublethal$PIT),2) # uneven male/female distribution - analyses need to be done separately 
        sublethal %>% # mean mass of males is 0.8 higher than females - run models separately
          group_by(Sex) %>% summarise(mean = mean(FC_Mass), se = sd(FC_Mass)/sqrt(n()), count = n())
        
        #### subset data frame, analysis for males 
        M_sublethal = subset(sublethal, Sex=="M") # subset for males only
        hist(M_sublethal$Recap_Mass) # response (mass) is pretty normal 
        M_sub_model = lm(Recap_Mass~PIT+FC_Mass+Catching_Season, data = M_sublethal) # linear regression model 
        summary(M_sub_model)  ## model output
      
        #### subset data frame, analysis for females
        F_sublethal = subset(sublethal, Sex=="F") # subset for females only 
        hist(F_sublethal$Recap_Mass) # response (mass) is pretty normal 
        F_sub_model = lm(Recap_Mass~PIT+FC_Mass+Catching_Season, data = F_sublethal) # linear regression model 
        summary(F_sub_model) ## model output
        
        ## summary statistics
         M_sublethal %>% ## males summary statistics
          group_by(PIT) %>%  summarise(mean = mean(Recap_Mass), sd = sd(Recap_Mass),count = n())
        F_sublethal %>%  ## females summary statistics
          group_by(PIT) %>% summarise(mean = mean(Recap_Mass),sd = sd(Recap_Mass),count=n())
      
