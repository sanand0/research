####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########
#### COMPLETE ANALYSIS OF RESULTS PRESENTED IN:
#### Extracting reproductive parameters from GPS tracking data for a nesting raptor in Europe
#### Oppel, Steffen; Beeli, Ursin; Grüebler, Martin; van Bergen, Valentijn; Kolbe, Martin; Pfeiffer, Thomas; Scherler, Patrick
#### Journal of Avian Biology. DOI:  10.1111/jav.03246
####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

## prepared by Steffen Oppel steffen.oppel@vogelwarte.ch
## FINALISED on 29 August 2024 after acceptance of manuscript


################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# LOAD PACKAGES AND DATA -----------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

library(data.table)
library(tidyverse)
library(devtools)
library(dplyr, warn.conflicts = FALSE)
library(NestTool)
library(janitor)
library(readxl)
library(tictoc)
library(nestR)
library(sf)
library(pROC)
library(kableExtra)

## set root folder for project
try(setwd("C:/Users/sop/OneDrive - Vogelwarte/General/MANUSCRIPTS/NestTool"),silent=T)
try(setwd("C:/STEFFEN/OneDrive - Vogelwarte/General/MANUSCRIPTS/NestTool"),silent=T)





####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

# #### SECTION 1: ANALYSIS OF SWISS DATA ################ -----------------

####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

### LOAD THE TRACKING DATA AND INDIVIDUAL SEASON SUMMARIES

trackingdata<-fread("./Zenodo_archive/SUI_trackingdata.csv")
indseasondata<-fread("./Zenodo_archive/SUI_indseasondata.csv")


tic()
#### STEP 1: prepare data - this takes approximately 15 minutes------------------
nest_data_input<-data_prep(trackingdata=trackingdata,
                           indseasondata=indseasondata,
                           latboundary=45,
                           longboundary=4,
                           crs_epsg=3035,
                           broodstart= yday(ymd("2023-05-01")),
                           broodend<- yday(ymd("2023-06-01")),
                           minlocs=800,
                           nestradius=50,
                           homeradius=2000,
                           startseason=70,
                           endseason=175,
                           settleEnd = 97,  # end of the settlement period in yday
                           Incu1End = 113,   # end of the first incubation phase in yday
                           Incu2End = 129,  # end of the second incubation phase in yday
                           Chick1End = 152, # end of the first chick phase in yday
                           age =10)         # age of individuals for which no age is provided with data



#### STEP 2: train home range model and predict home range-------------------
trackingsummary<-nest_data_input$summary
hr_model<-train_home_range_detection(trackingsummary=trackingsummary,plot=T)
pred_hr<-predict_ranging(model=hr_model$model,trackingsummary=trackingsummary) # if a model has been trained


#### STEP 3: train nest model and predict nesting----------------------------
trackingsummary<-nest_data_input$summary
nest_model<-train_nest_detection(trackingsummary=trackingsummary[!is.na(trackingsummary$nest),],plot=T)
pred_nest<-predict_nesting(model=nest_model$model,trackingsummary=pred_hr) # if a model has been trained
NestTool_data_prep_time<-toc()


################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# QUANTIFY UNCERTAIN CLASSIFICATIONS AND PREDICTIONS-----------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

nest_test_cert <- pred_nest %>%
  filter(nest_prob>=0.75 | nest_prob <=(1-0.75)) %>%
  dplyr::mutate(nest_predicted = as.factor(dplyr::case_when(nest_prob > no_nest_prob ~ "nest",
                                                            nest_prob < no_nest_prob ~ "no nest"))) %>% dplyr::select(year_id, bird_id, nest_id, nest_predicted, nest_observed)
nest_test_cert$nest_observed <- factor(ifelse(nest_test_cert$nest_observed=="nest","nest", "no nest"), levels = c("nest", "no nest"))
nest_cert_eval<-caret::confusionMatrix(data = nest_test_cert$nest_observed, reference = nest_test_cert$nest_predicted)
(dim(pred_nest)[1]-dim(nest_test_cert)[1])/dim(pred_nest)[1]

################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# COMPARISON WITH nestR for nest detection ---------------------------------------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

tic()
nestR_input <- trackingdata %>%
  mutate(burst = year_id,
         date = timestamp,
         long = long_wgs,
         lat = lat_wgs) %>%
  select(burst, date, year, long, lat)
FINAL_NEST <-
  find_nests(gps_data = nestR_input,
             buffer = 50,  # changed from 15 as radius needs to be larger
             min_pts = 150, # changed to 150 as RF indicated 187
             min_d_fix = 8,
             nest_cycle = 80, # changed to 80, as argument nest_cycle is the duration (in days) of a complete nesting attempt of 37d incubation + 50d feeding
             min_consec = 16, # changed from 3 to 16, as RF indicated 16
             min_top_att = 32, # changed from 10 to 32 as CART indicated 32 and RF 38: birds should spend 30% of their time at the nest on the day with the highest attendance
             min_days_att = 45, # changed from 10 to 45 as RF indicated 47%, and birds should visit the nest basically every day!
             sea_start = "03-15", sea_end = "06-30")
NestR_data_prep_time<-toc()


######  EVALUATION of nestR: CALCULATE PROPORTION OF TRUE NESTS THAT WERE ACTUALLY DETECTED---------------------------------
pred_nestR_nests<-FINAL_NEST$nests %>%
  filter(loc_id != "2211") %>% # this is a duplicate nest
  rename(year_id=burst)

nestR_VAL_DAT_nests<- left_join(indseasondata,pred_nestR_nests[,1:4], by="year_id") %>%
  dplyr::filter(nest %in% c("nest","no nest")) %>%
  dplyr::filter(year_id %in% unique(trackingsummary$year_id)) %>%
  mutate(Observed = ifelse(nest=="no nest",0,1), Predicted=ifelse(is.na(loc_id),0,1))

nestR_validation_nests<-caret::confusionMatrix(as.factor(nestR_VAL_DAT_nests$Observed),as.factor(nestR_VAL_DAT_nests$Predicted))



################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# QUANTIFYING NEST SUCCESS ---------------------------------------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

#### STEP 4: train outcome model and predict nesting success------------------
tic()
succ_model<-train_nest_success(nestingsummary=pred_nest[pred_nest$success %in% c("yes","no"),],plot=T)
pred_succ<-predict_success(model=succ_model$model,nestingsummary=pred_nest,nest_cutoff =succ_model$nest_cutoff) # if a model has been trained
NestTool_nest_succ_time<-toc()

### evaluate predictions and quantify proportion of certain predictions
prop_cert<-pred_succ %>% dplyr::filter(success_observed %in% c("yes","no"))  %>%     ### filter out all data that are not useful for training purposes
  mutate(certain=ifelse(succ_prob>=0.75 | succ_prob <=(1-0.75),1,0)) %>%
  ungroup() %>%
  summarise(prop_certain=sum(certain)/length(certain))

succ_test_cert <- pred_succ %>% dplyr::filter(success_observed %in% c("yes","no")) %>%     ### filter out all data that are not useful for training purposes
  filter(succ_prob>=0.75 | succ_prob <=(1-0.75)) %>%
  dplyr::mutate(success_predicted = as.factor(dplyr::case_when(succ_prob > no_succ_prob ~ "yes",
                                                               succ_prob < no_succ_prob ~ "no")))
succ_test_cert$success <- factor(ifelse(succ_test_cert$success_observed=="yes","yes", "no"), levels = c("yes", "no"))
succ_cert_eval<-caret::confusionMatrix(data = succ_test_cert$success, reference = succ_test_cert$success_predicted)
(dim(pred_nest)[1]-dim(nest_test_cert)[1])/dim(pred_nest)[1]



############ ASSEMBLE VALIDATION METRICS IN A TABLE --------------------------
val.out.train<-data.frame(method="NestTool",data="SUI",subset="training",
                          n=sum(hr_model$eval_train$table),
                          HR_accur=hr_model$eval_train$overall[1],
                          nest_accur=nest_model$eval_train$overall[1],
                          succ_accur=succ_model$eval_train$overall[1],
                          nest_cert_accur=0,
                          succ_cert_accur=0)

val.out.test<-data.frame(method="NestTool",data="SUI",subset="internal validation",
                         n= sum(hr_model$eval_test$table),
                         HR_accur=hr_model$eval_test$overall[1],
                         nest_accur=nest_model$eval_test$overall[1],
                         succ_accur=succ_model$eval_test$overall[1],
                         nest_cert_accur=0,
                         succ_cert_accur=succ_cert_eval$overall[1])




################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# COMPARISON WITH nestR for nest success ---------------------------------------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

### THIS FITS A BAYESIAN SURVIVAL MODEL WHICH RUNS FOR 3 HRS

tic()
nest_attempts<-format_attempts(nest_info=FINAL_NEST,nest_cycle=80)
outcome_prediction<-estimate_outcomes(fixes=nest_attempts$fixes,visits=nest_attempts$visits, model="phi_time_p_time")
NestR_nest_succ_time<-toc()

### calculate accuracy for nestR output -------------------------------------
nestR_SUCC_PRED<-data.frame(burst=outcome_prediction$names, surv_prob=apply(outcome_prediction$z,c(1,2),FUN=mean)[,80]) %>%
  separate(burst, into=c("year","bird_id","loc_id"), sep="_") %>%
  mutate(year_id = paste0(year, "_", bird_id))

nestR_VAL_DAT_succ<- left_join(indseasondata,nestR_SUCC_PRED[,3:5], by="year_id") %>%
  dplyr::filter(success %in% c("yes","no")) %>%
  dplyr::filter(year_id %in% unique(trackingsummary$year_id)) %>%
  mutate(Observed = ifelse(success=="no",0,1), Predicted=ifelse(surv_prob>0.5,1,0))

nestR_validation_succ<-caret::confusionMatrix(as.factor(nestR_VAL_DAT_succ$Observed),as.factor(nestR_VAL_DAT_succ$Predicted))


############ ASSEMBLE nestR VALIDATION METRICS IN A TABLE --------------------
val.out.nestR<-data.frame(method="nestR",data="SUI",subset="training",
                          n= sum(nestR_validation_nests$table),
                          HR_accur=NA,
                          nest_accur=nestR_validation_nests$overall[1],
                          succ_accur=nestR_validation_succ$overall[1],
                          nest_cert_accur=NA,
                          succ_cert_accur=NA)

Table2_SUI<-bind_rows(val.out.train, val.out.test,val.out.nestR)



################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# SUMMARISE BREEDING PROPENSITY AND SUCCESS ---------------------------------------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

ALL<-pred_succ %>% select(year_id,nest_observed,success_observed,hr_observed,hr_prob,nest_prob,succ_prob) %>%
  mutate(HR=ifelse(hr_prob>0.5,1,0),Nest=ifelse(nest_prob>0.5,1,0),Success=ifelse(succ_prob>0.5,1,0))

## breeding propensity - what proportion of birds with a homerange have a nesting attempt?
ALL %>% filter(HR==1) %>% ungroup() %>%
  summarise(Propensity=mean(Nest))

ALL %>% filter(hr_observed=="yes") %>% ungroup() %>% 
  mutate(Nest=ifelse(nest_observed=="nest",1,0)) %>%
  summarise(Propensity=mean(Nest))

## breeding success - what proportion of birds with a nesting attempt are successful?
ALL %>% filter(Nest==1) %>% ungroup() %>%
  summarise(Success=mean(Success))

indseasondata %>% filter(nest== "nest") %>%
  filter(success %in% c("yes","no")) %>%
  filter(year_id %in% ALL$year_id) %>% 
  mutate(Success=ifelse(success=="yes",1,0)) %>%
  summarise(Success=mean(Success))

## HR settlement of 2 and 3 year old birds
ALL<-ALL %>% left_join(indseasondata[,3:5], by="year_id")

yr2old<-ALL$year_id[ALL$age_cy==2]
yr3old<-ALL$year_id[ALL$age_cy==3]

ageHR<-ALL %>% filter(year_id %in% yr2old) %>% ungroup() %>%
  summarise(N=sum(HR)) %>%
  mutate(prop=N/length(yr2old), age_cy=2) 

ageHR<-ALL %>% filter(year_id %in% yr3old) %>% ungroup() %>%
  summarise(N=sum(HR)) %>%
  mutate(prop=N/length(yr3old), age_cy=3) %>%
  bind_rows(ageHR)

ageHR<-indseasondata %>% 
  filter(year_id %in% ALL$year_id) %>% 
  group_by(age_cy,HR) %>%
  summarise(N=length(unique(year_id))) %>%
  filter(age_cy %in% c(2,3)) %>%
  filter(HR %in% c("yes","no")) %>%
  spread(key=HR, value=N) %>%
  mutate(prop_obs=(yes)/(no+yes)) %>%
  left_join(ageHR, by="age_cy")



## breeding propensity of 2 and 3 year old birds
ageBR<-ALL %>% filter(year_id %in% yr2old) %>% ungroup() %>%
  summarise(N=sum(Nest)) %>%
  mutate(prop=N/length(yr2old), age_cy=2)

ageBR<-ALL %>% filter(year_id %in% yr3old) %>% ungroup() %>%
  summarise(N=sum(Nest)) %>%
  mutate(prop=N/length(yr3old), age_cy=3) %>%
  bind_rows(ageBR)

ageBR<-indseasondata %>% 
  filter(year_id %in% ALL$year_id) %>% 
  group_by(age_cy,nest) %>%
  summarise(N=length(unique(year_id))) %>%
  filter(age_cy %in% c(2,3)) %>%
  filter(nest %in% c("nest","no nest")) %>%
  spread(key=nest, value=N) %>%
  rename(none=`no nest`) %>%
  mutate(prop_obs=(nest)/(none+nest))%>%
  left_join(ageBR, by="age_cy")





####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

# #### SECTION 2: ANALYSIS OF GERMAN DATA ################ -----------------

####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

# LOAD VALIDATION TRACKING DATA

GERtrackingdata<-fread("./Zenodo_archive/GER_trackingdata.csv")
GERseasondata<-fread("./Zenodo_archive/GER_indseasondata.csv")


#### STEP 1: prepare validation data -----------------------------
tic()
GER_data_input<-data_prep(trackingdata=GERtrackingdata,
                          indseasondata=GERseasondata,
                          latboundary=50,
                          longboundary=9,
                          crs_epsg=3035,
                          broodstart= yday(ymd("2023-05-15")),
                          broodend<- yday(ymd("2023-06-15")),
                          minlocs=800,
                          nestradius=150,
                          homeradius=5000,
                          startseason=yday(ymd("2023-03-15")),
                          endseason=yday(ymd("2023-07-10")),
                          settleEnd = yday(ymd("2023-04-05")),  # end of the settlement period in yday
                          Incu1End = yday(ymd("2023-04-25")),   # end of the first incubation phase in yday
                          Incu2End = yday(ymd("2023-05-15")),  # end of the second incubation phase in yday
                          Chick1End = yday(ymd("2023-06-15")), # end of the first chick phase in yday
                          age =10)         # age of individuals for which no age is provided with data 

summary(GER_data_input$summary %>% ungroup())
summary(nest_data_input$summary %>% ungroup())

#### STEP 2: identify home ranges-------------------
GER_hr_model<-hr_model
GER_pred_hr<-predict_ranging(model=GER_hr_model$model,trackingsummary=GER_data_input$summary) # uses the model trained with our data (automatically loaded in the function)

#### STEP 3: identify nests------------------------
GER_nest_model<-nest_model
GER_pred_nest<-predict_nesting(model=GER_nest_model$model,trackingsummary=GER_pred_hr) # uses the model trained with our data (automatically loaded in the function)
NestTool_GER_data_prep_time<-toc()

#### STEP 4: determine outcome---------------------
tic()
GER_succ_model<-succ_model
GER_pred_succ<-predict_success(model=GER_succ_model$model,nestingsummary=GER_pred_nest, nest_cutoff=GER_succ_model$nest_cutoff) # uses the model trained with our data (automatically loaded in the function)
NestTool_GER_nest_succ_time<-toc()

##### COMBINE PREDICTIONS FOR NEST SUCCESS--------
GER_ALL<-GER_pred_succ %>% select(year_id,hr_prob,nest_prob,succ_prob) %>%
  mutate(HR=ifelse(hr_prob>0.5,1,0),Nest=ifelse(nest_prob>0.5,1,0),Success=ifelse(succ_prob>0.5,1,0))

VALIDAT<-GERseasondata %>% rename(HR_true=HR, Nest_true=nest) %>%
  mutate(Success_true=ifelse(success==0,0,1)) %>%
  select(year_id,HR_true,Nest_true,Success_true) %>%
  right_join(GER_ALL, by="year_id")

# ### 8.1. evaluate home range identification-------
VX <- VALIDAT %>%
  dplyr::mutate(HR_true = as.factor(dplyr::case_when(HR_true==1 ~ "YES",
                                                     HR_true==0 ~ "NO"))) %>%
  dplyr::mutate(HR = as.factor(dplyr::case_when(HR==1 ~ "YES",
                                                HR==0 ~ "NO")))
GER_hrval<-caret::confusionMatrix(data = VX$HR_true, reference = VX$HR, positive="YES")
GER_hrval_cert<-caret::confusionMatrix(data = VX$HR_true[VALIDAT$hr_prob>0.75 | VX$hr_prob<0.25], reference = VX$HR[VX$hr_prob>0.75 | VX$hr_prob<0.25], positive="YES")



### 8.2. evaluate nesting identification-----------
VX <- VX %>%
  dplyr::mutate(Nest_true = as.factor(dplyr::case_when(Nest_true==1 ~ "YES",
                                                       Nest_true==0 ~ "NO"))) %>%
  dplyr::mutate(Nest = as.factor(dplyr::case_when(Nest==1 ~ "YES",
                                                  Nest==0 ~ "NO")))
GER_nestval<-caret::confusionMatrix(data = VX$Nest_true, reference = VX$Nest, positive="YES")
GER_nestval_cert<-caret::confusionMatrix(data = VX$Nest_true[VX$nest_prob>0.75 | VX$nest_prob<0.25], reference = VX$Nest[VX$nest_prob>0.75 | VX$nest_prob<0.25], positive="YES")
length(VX$Nest_true[VX$nest_prob>0.75 | VX$nest_prob<0.25])/length(VX$Nest_true)

# ### 8.3. evaluate nest success prediction----------
VX <- VX %>%
  dplyr::mutate(Success_true = as.factor(dplyr::case_when(Success_true==1 ~ "YES",
                                                          Success_true==0 ~ "NO"))) %>%
  dplyr::mutate(Success = as.factor(dplyr::case_when(Success==1 ~ "YES",
                                                     Success==0 ~ "NO")))
GER_succval<-caret::confusionMatrix(data = VX$Success_true, reference = VX$Success, positive="YES")

GER_succval_cert<-caret::confusionMatrix(data = VX$Success_true[VX$succ_prob>0.75 | VX$succ_prob<0.25], reference = VX$Success[VX$succ_prob>0.75 | VX$succ_prob<0.25], positive="YES")
length(VX$Success_true[VX$succ_prob>0.75 | VX$succ_prob<0.25])/dim(VX[VX$Nest_true=='YES',])[1]

#### COLLATE ACCURACY INFORMATION--------------------)
val.out<-data.frame(method="NestTool",data="GER",subset="external validation",
                    n= sum(GER_hrval$table),
                    HR_accur=GER_hrval$overall[1],
                    nest_accur=GER_nestval$overall[1],
                    succ_accur=GER_succval$overall[1],
                    HR_cert_accur=GER_hrval_cert$overall[1],
                    nest_cert_accur=GER_nestval_cert$overall[1],
                    succ_cert_accur=GER_succval_cert$overall[1])




################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# COMPARISON OF GERMAN DATA WITH nestR ---------------------------------------------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

tic()
nestR_input_GER <- GERtrackingdata %>%
  filter(lat_wgs>0) %>%
  filter(long_wgs<100) %>%
  mutate(burst = year_id,
         year=year(timestamp),
         date = timestamp,
         long = long_wgs,
         lat = lat_wgs) %>%
  select(burst, date, year, long, lat)
FINAL_NEST_GER <-
  find_nests(gps_data = nestR_input_GER,
             buffer = 150,  # changed from 15 as radius needs to be larger
             min_pts = 150, # changed to 150 as RF indicated 187
             min_d_fix = 8,
             nest_cycle = 80, # changed to 80, as argument nest_cycle is the duration (in days) of a complete nesting attempt of 37d incubation + 50d feeding
             min_consec = 16, # changed from 3 to 16, as RF indicated 16
             min_top_att = 32, # changed from 10 to 32 as CART indicated 32 and RF 38: birds should spend 30% of their time at the nest on the day with the highest attendance
             min_days_att = 45, # changed from 10 to 45 as RF indicated 47%, and birds should visit the nest basically every day!
             sea_start = "03-15", sea_end = "07-10")
FINAL_NEST_GER
NestR_GER_data_prep_time<-toc()


### nestR nest survival model ------------------------------
tic()
nest_attempts_GER<-format_attempts(nest_info=FINAL_NEST_GER,nest_cycle=80)
outcome_prediction_GER<-estimate_outcomes(fixes=nest_attempts_GER$fixes,visits=nest_attempts_GER$visits, model="phi_time_p_time")
NestR_GER_nest_succ_time<-toc()


######  EVALUATION of nestR: CALCULATE PROPORTION OF TRUE NESTS THAT WERE ACTUALLY DETECTED---------------------------------
duplicate_nests<-FINAL_NEST_GER$nests %>% group_by(burst) %>% summarise(N=length(unique(loc_id))) %>% filter(N>1)
FINAL_NEST_GER$nests %>% filter(burst %in% duplicate_nests$burst)
pred_nestR_nests_GER<-FINAL_NEST_GER$nests %>% 
  filter(!(loc_id %in% c(1212,1214))) %>%  ### these are duplicate nests of the same year_id
  rename(year_id=burst)

nestR_VAL_DAT_nests_GER<- left_join(GERseasondata,pred_nestR_nests_GER[,1:4], by="year_id") %>%
  dplyr::filter(year_id %in% unique(GER_data_input$summary$year_id)) %>%
  mutate(Predicted=ifelse(is.na(loc_id),0,1))

nestR_validation_nests_GER<-caret::confusionMatrix(as.factor(nestR_VAL_DAT_nests_GER$nest),as.factor(nestR_VAL_DAT_nests_GER$Predicted))



######  EVALUATION of nestR: CALCULATE PROPORTION OF SUCCESSFUL NESTS THAT WERE ESTIMATED AS SURVIVING---------------------------------
nestR_SUCC_PRED_GER<-data.frame(burst=outcome_prediction_GER$names, surv_prob=apply(outcome_prediction_GER$z,c(1,2),FUN=mean)[,80]) %>%
  separate(burst, into=c("year","bird_id","loc_id"), sep="_") %>%
  mutate(year_id = paste0(year, "_", bird_id))

nestR_VAL_DAT_succ_GER<- left_join(GERseasondata,nestR_SUCC_PRED_GER[,3:5], by="year_id") %>%
  dplyr::filter(!is.na(surv_prob)) %>%
  mutate(Predicted=ifelse(surv_prob>0.5,1,0))

nestR_validation_succ_GER<-caret::confusionMatrix(as.factor(nestR_VAL_DAT_succ_GER$success),as.factor(nestR_VAL_DAT_succ_GER$Predicted))


############ ASSEMBLE nestR VALIDATION METRICS IN A TABLE ---------------------
val.out.nestR.GER<-data.frame(method="nestR",data="GER",subset="external validation",
                              n= sum(nestR_validation_nests_GER$table),
                              HR_accur=NA,
                              nest_accur=nestR_validation_nests_GER$overall[1],
                              succ_accur=nestR_validation_succ_GER$overall[1],
                              nest_cert_accur=NA,
                              succ_cert_accur=NA)

Table2_GER<-bind_rows(val.out, val.out.nestR.GER)



####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

# #### SECTION 3: COMPILE OUTPUT TABLES AND FIGURES ################ -----------------

####~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###########

Table2<-bind_rows(Table2_SUI,Table2_GER) %>%
  arrange(desc(data),desc(subset),method) %>%
  select(data,subset,method,n,HR_accur,nest_accur,succ_accur)




################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# #### COMPILE SAMPLE SIZES FOR TABLE S2 ########## -----------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################

## quantify sex and age ratio for SUI
sampsize<-indseasondata %>% 
  filter(year_id %in% unique(nest_data_input$summary$year_id)) %>%
  mutate(age_cy=ifelse(age_cy>9,10,age_cy)) %>%
  group_by(sex,age_cy) %>%
  summarise(n=length(unique(year_id))) %>%
  spread(key=sex, value=n) %>%
  ungroup() %>%
  adorn_totals()

## quantify sex and age ratio for GER
length(unique(GERseasondata$bird_id))
sampsizeGER<-GERseasondata %>% 
  filter(year_id %in% unique(GER_data_input$summary$year_id)) %>%
  mutate(age_cy=ifelse(age_cy>9,10,age_cy)) %>%
  group_by(sex,age_cy) %>%
  summarise(n=length(unique(year_id))) %>%
  spread(key=sex, value=n) %>%
  ungroup() %>%
  adorn_totals()

TableS2<-
  left_join(sampsize,sampsizeGER, by="age_cy") %>%
  replace_na(list(f.x=0,m.y=0,f.y=0))



#### create new Table S3 after reviewer requested age at tagging









################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
# #### COMPILE CONFUSION MATRICES FOR TABLE S3 ########## -----------------
################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##########################
TableS3<-
  as_tibble(rbind(
    hr_model$eval_train$table,
    hr_model$eval_test$table,
    GER_hrval$table,
    
    nest_model$eval_train$table,
    nest_model$eval_test$table,
    GER_nestval$table,
    nestR_validation_succ$table,
    nestR_validation_nests_GER$table,
    
    succ_model$eval_train$table[2:1, 2:1],
    succ_model$eval_test$table,
    GER_succval$table,
    nestR_validation_succ$table,
    nestR_validation_succ_GER$table)) %>%
  mutate(Breeding_parameter=c(rep("home range",each=6),rep(c("breeding initiation","breeding success"), each=10))) %>%
  mutate(Origin=c(rep(c("Switzerland","Switzerland","Germany"), each=2),rep(rep(c("Switzerland","Switzerland","Germany","Switzerland","Germany"), each=2),2))) %>%
  mutate(Subset=c(rep(c("training","internal validation","external validation"), each=2),rep(rep(c("training","internal validation","external validation","training","external validation"), each=2),2))) %>%
  mutate(predicted=rep(c("no","yes"), 13)) %>%
  mutate(Method=c(rep("NestTool",12),rep("nestR",4), rep("NestTool",6),rep("nestR",4))) %>%
  select(Breeding_parameter,Origin,Subset,Method,predicted,no,yes)

TableS3_kn<-knitr::kable(TableS3, format= "simple", caption="Table S3. Confusion matrices showing the observed and automatically classified (predicted) outcomes of red kite breeding seasons in either Switzerland or Germany based on our training, testing, and external validation data.",col.names=  c("Breeding parameter","Data","Subset","Method", "predicted","no","yes"), digits=0)

collapse_rows(
  kable_input=TableS3_kn,
  columns = c(1,2,3,4),
  valign = "middle",
  latex_hline = "full",
  row_group_label_position = "identity"
)
