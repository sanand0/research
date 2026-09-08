#=========================================#
#Set working directory, load libraries----
#=========================================#

setwd("C:/Users/kimbe/Desktop/analyses")

recap<-read.csv("recap_data.csv")
names(recap)

recap2019<-subset(recap, recap$Year==2019)
recap2020<-subset(recap, recap$Year==2020)
recap$YearID<-paste(recap$TransponderHexCode,sep="", recap$Year)

update.packages(checkBuilt=TRUE)

require(Matrix)
require(MASS)
library(lme4)
require(MCMCglmm)
library(arm)
library(MuMIn)
library(r2glmm)
library(rptR)
library(tidyverse)
library(ggplot2)

#====================================#
#a) Sex bias in recapture probability----
#====================================#

sexbias<-na.omit(recap) ##remove birds with unknown sex (sex data missing due to lack of DNA sample)
sexbias$Year2<-as.factor(sexbias$Year)


m1<-glmer(Recap~sex+Year2+(1|TransponderHexCode), data=sexbias, family="binomial")
summary(m1)

smod<-sim(m1,1000)
sex_mode<-posterior.mode(as.mcmc(smod@fixef))
sex_HPD<-HPDinterval(as.mcmc(smod@fixef))

mean(as.mcmc(smod@fixef))
sex_mode
sex_HPD

sex_pos<-ifelse(smod@fixef>0,1,0)
sex_neg<-ifelse(smod@fixef<0,1,0)
sex_bayesianp<-sum(sex_pos)/(sum(sex_pos)+sum(sex_neg))
sex_bayesianp


#=======================#
###b) Feeding rate----
#=======================#

feeding<-read.csv("feeding_recap.csv")
names(feeding)

feeding$Year2<-as.factor(feeding$Year)
feeding$logFR<-log(feeding$DailyVisits+1)
feeding$YearID<-paste(feeding$TransponderHexCode,sep="", feeding$Year2)

#sample sizes
feeding_count<-feeding %>% group_by(TransponderHexCode) %>% summarize(count=n())
feeding_count
summary(feeding_count$count)

##calculate repeatability of feeding rate
rpt(logFR~Year2+(1|TransponderHexCode), grname=c("TransponderHexCode"), datatype="Gaussian", data=feeding, nboot=100, npermut=0)

##model for extracting posterior distribution of BLUPS of FR
## need to add pr = TRUE to model argument to save posterior distribution of BLUPS
prior <- list(
  R = list(V = diag(1), nu = 0.002),
  G = list(
    G1 = list(
      V = diag(1), nu = 0.002,
      alpha.mu = rep(0),
      alpha.V = diag(1)
    )
  )
)

m_feeding<-MCMCglmm(logFR ~ Year2,
                    random =~TransponderHexCode,
                    family = "gaussian",
                    prior=prior,    
                    nitt=1010000,
                    burnin=10000,
                    thin=1000,
                    verbose = TRUE,
                    pr = TRUE,
                    data = feeding)

summary(m_feeding)
plot(m_feeding)


###ask whether FR predicts recapture probability----
F2_lm_list <- list()
for (iter in seq_len(nrow(m_feeding$Sol))) {
  blups_F2 <- select(
    as_tibble(m_feeding$Sol),
    contains("TransponderHexCode")
  )[iter, ] 
  blups_F <- tibble(
    TransponderHexCode = str_remove(colnames(blups_F2), "TransponderHexCode."), 
    blups_F = as.numeric(blups_F2))
  
  data_F2_lm <- merge(blups_F, recap, by = "TransponderHexCode")
  F2_lm_list[[iter]] <- glmer(Recap ~ blups_F+(1|TransponderHexCode), data = data_F2_lm, family = binomial)
}

coef_F2 <- as.mcmc(
  sapply(
    F2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)

posterior.mode(coef_F2)
mean(coef_F2)
HPDinterval(coef_F2)

feeding_pos<-ifelse(coef_F2>0,1,0)
feeding_neg<-ifelse(coef_F2<0,1,0)
feeding_bayesianp<-sum(feeding_neg)/(sum(feeding_pos)+sum(feeding_neg))
feeding_bayesianp

#===================#
#c) Latency data----
#===================#
josue<-read.csv("latency_data.csv")
names(josue)

#transform latency data
josue$logLatency<-log(josue$Sec)
hist(josue$logLatency)

#center and scale Temperature data
josue$cTemp<-scale(josue$TempDay)

#make treatment a factor
josue$FTreatment<-as.factor(josue$Treatment)

###recapture and latency
josue$logLatency<-as.numeric(josue$logLatency)
josue$cTemp<-as.numeric(josue$cTemp)
names(josue)

##sample sizes
josue_count<-josue %>% group_by(TransponderHexCode) %>% summarize(count=n())
josue_count
summary(josue_count$count)

#repeatability
rpt(logLatency~cTemp*FTreatment+(1|TransponderHexCode), grname=c("TransponderHexCode"), datatype="Gaussian", data=josue, nboot=100, npermut=0)

###Josue run with fixed effects
m_latency <- MCMCglmm(logLatency ~
                        cTemp*FTreatment,
                      random =~ TransponderHexCode,
                      family = "gaussian",
                      prior=prior,    
                      nitt=1010000,
                      burnin=10000,
                      thin=1000,
                      verbose = TRUE,
                      pr = TRUE,
                      data = josue)

summary(m_latency)
plot(m_latency)


#recapture analyses----

L2_lm_list <- list()
for (iter in seq_len(nrow(m_latency$Sol))) {
  blups_L2 <- select(
    as_tibble(m_latency$Sol),
    contains("TransponderHexCode")
  )[iter, ] 
  blups_L <- tibble(
    TransponderHexCode = str_remove(colnames(blups_L2), "TransponderHexCode."), 
    blups_L = as.numeric(blups_L2))
  
  data_L2_lm <- merge(blups_L, recap2019, by = "TransponderHexCode")
  L2_lm_list[[iter]] <- glm(Recap ~ blups_L, data = data_L2_lm, family = binomial)
}

coef_L2 <- as.mcmc(
  sapply(
    L2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)


posterior.mode(coef_L2)
mean(coef_L2)
HPDinterval(coef_L2)


pos<-ifelse(coef_L2>0,1,0)
neg<-ifelse(coef_L2<0,1,0)
bayesianp<-sum(pos)/(sum(pos)+sum(neg))
bayesianp


#======================#
###d) Cage test data----
#======================#

cage<-read.csv("cage_test.csv") 
names(cage)

##samplesizes
cage_count<-cage %>% group_by(CatchRingNumber) %>% summarize(count=n())
cage_count
summary(cage_count$count)

##repeatability
rpt(CageTestScore~1+(1|CatchRingNumber), grname=c("CatchRingNumber"), datatype="Gaussian", data=cage, nboot=100, npermut=0)


m_cage <- MCMCglmm(CageTestScore ~ 1,
                   random =~ CatchRingNumber,
                   family = "gaussian",
                   prior = prior,
                   nitt=1010000,
                   burnin=10000,
                   thin=1000,
                   verbose = TRUE,
                   pr = TRUE,
                   data = cage)

summary(m_cage)
plot(m_cage)


#survival analyses----
###note- some of the 1000 iterations have singular fit. Re-running analyses while escluding TransponderHexCode as a random effect does not affect results
###analyses presented in main text include random effect for individual ID(i.e., TransponderHexCode)
C2_lm_list <- list()
for (iter in seq_len(nrow(m_cage$Sol))) {
  blups_C2 <- select(
    as_tibble(m_cage$Sol),
    contains("CatchRingNumber")
  )[iter, ] 
  blups_C <- tibble(
    CatchRingNumber = str_remove(colnames(blups_C2), "CatchRingNumber."), 
    blups_C = as.numeric(blups_C2))
  
  data_C2_lm <- merge(blups_C, recap, by = "CatchRingNumber")
  C2_lm_list[[iter]] <- glmer(Recap ~ blups_C +(1|CatchRingNumber), data = data_C2_lm, family = binomial)
}

coef_C2 <- as.mcmc(
  sapply(
    C2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)

posterior.mode(coef_C2)
mean(coef_C2)
HPDinterval(coef_C2)

#========================#
###d) Aggression data---- 
#========================#

aggression<-read.csv("aggression_test.csv")
names(aggression)

aggression_count<-aggression %>% group_by(CatchRingNumber) %>% summarize(count=n())
summary(aggression_count$count)

rpt(AggressivenessScore~1+(1|CatchRingNumber), grname=c("CatchRingNumber"), datatype="Gaussian", data=aggression, nboot=100, npermut=0)

m_aggression <- MCMCglmm(AggressivenessScore ~ 1,
                         random =~ CatchRingNumber,
                         family = "gaussian",
                         prior = prior,
                         nitt=1010000,
                         burnin=10000,
                         thin=1000,
                         verbose = TRUE,
                         pr = TRUE,
                         data = aggression)

summary(m_aggression)
plot(m_aggression)

#recapture analyses----
A2_lm_list <- list()
for (iter in seq_len(nrow(m_aggression$Sol))) {
  blups_A2 <- select(
    as_tibble(m_aggression$Sol),
    contains("CatchRingNumber")
  )[iter, ] 
  blups_A <- tibble(
    CatchRingNumber = str_remove(colnames(blups_A2), "CatchRingNumber."), 
    blups_A = as.numeric(blups_A2))
  
  data_A2_lm <- merge(blups_A, recap, by = "CatchRingNumber")
  A2_lm_list[[iter]] <- glmer(Recap ~ blups_A + (1|CatchRingNumber), data = data_A2_lm, family = binomial)
}

coef_A2 <- as.mcmc(
  sapply(
    A2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)


posterior.mode(coef_A2)
mean(coef_A2)
HPDinterval(coef_A2)


#======================#
###e) Sampling data ----
#======================#

sampling<-read.csv("sampling.csv")
names(sampling)
sampling$cTemp<-scale(sampling$AvgTemp)

#sample size summaries
sample_count<-sampling %>% group_by(TransponderHexCode) %>% summarize(count=n())
sample_count
summary(sample_count$count)


#repeatability
rptBinary(Sampled~Adjacent+cTemp+Adjacent:cTemp+(1|TransponderHexCode), grname=c("TransponderHexCode"), data=sampling, nboot=100, npermut=0)


## need to add pr = TRUE to model argument to save posterior distribution of BLUPS
prior_sampling <- list(
  R = list(V = diag(1), nu = 0.002),
  G = list(
    G1 = list(
      V = diag(1), nu = 0.002,
      alpha.mu = rep(0),
      alpha.V = diag(1)
    )
  )
)

m_sampling<-MCMCglmm(Sampled ~ -1+
                       Adjacent +
                       cTemp +
                       Adjacent:cTemp,
                     random =~TransponderHexCode,
                     family = "threshold",
                     prior=prior_sampling,    
                     nitt=1010000,
                     burnin=10000,
                     thin=1000,
                     verbose = TRUE,
                     pr = TRUE,
                     data = sampling)

summary(m_sampling)
plot(m_sampling)


#recapture analyses----

S2_lm_list <- list()
for (iter in seq_len(nrow(m_sampling$Sol))) {
  blups_S2 <- select(
    as_tibble(m_sampling$Sol),
    contains("TransponderHexCode")
  )[iter, ] 
  blups_S <- tibble(
    TransponderHexCode = str_remove(colnames(blups_S2), "TransponderHexCode."), 
    blups_S = as.numeric(blups_S2))
  
  data_S2_lm <- merge(blups_S, recap2020, by = "TransponderHexCode")
  S2_lm_list[[iter]] <- glm(Recap ~ blups_S, data = data_S2_lm, family = binomial)
}

coef_S2 <- as.mcmc(
  sapply(
    S2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)


posterior.mode(coef_S2)
mean(coef_S2)
HPDinterval(coef_S2)



##Post hoc test for sex-related differences in feeding rate----

data_FR_sex <- merge(feeding, sexbias, by = "TransponderHexCode")
datax<-na.omit(data_FR_sex)
mx<-lmer(logFR~sex+as.factor(Year.x)+(1|TransponderHexCode), data=datax)   
summary(mx)

smod<-sim(mx,1000)
sf_mode<-posterior.mode(as.mcmc(smod@fixef))
sf_HPD<-HPDinterval(as.mcmc(smod@fixef))

mean(as.mcmc(smod@fixef))
sf_mode
sf_HPD

bID<-smod@ranef$TransponderHexCode
bvar<-as.vector(apply(bID, 1, var)) ##between individual variance posterior distribution
bvar<-as.mcmc(bvar)
posterior.mode(bvar )## mode of the distribution
HPDinterval(bvar)


rvar<-smod@sigma^2
rvar<-as.mcmc(rvar)
posterior.mode(rvar)
HPDinterval(rvar)




###Producing figure with estimated effects of traits on recapture----
###Figure 2----
OddsRatioPlots<-data.frame(Traits=c("Sex",
                                    "Feeding Rate",
                                    "Latency",
                                    "Cage Test",
                                    "Handling Aggression",
                                    "Sampling"),
                           Estimate = c(mean(as.mcmc(smod@fixef[,2])),
                                        mean(coef_F2),
                                        mean(coef_L2),
                                        mean(coef_C2),
                                        mean(coef_A2),
                                        mean(coef_S2)),
                           Lower=c(HPDinterval(as.mcmc(smod@fixef[,2]))[,"lower"],
                                   HPDinterval(coef_F2)[,"lower"],
                                   HPDinterval(coef_L2)[,"lower"],
                                   HPDinterval(coef_C2)[,"lower"],
                                   HPDinterval(coef_A2)[,"lower"],
                                   HPDinterval(coef_S2)[,"lower"]),
                           Upper=c(HPDinterval(as.mcmc(smod@fixef[,2]))[,"upper"],
                                   HPDinterval(coef_F2)[,"upper"],
                                   HPDinterval(coef_L2)[,"upper"],
                                   HPDinterval(coef_C2)[,"upper"],
                                   HPDinterval(coef_A2)[,"upper"],
                                   HPDinterval(coef_S2)[,"upper"]))

dev.off()

ggplot(OddsRatioPlots, aes(x=Traits, y = Estimate))+
  geom_pointrange(aes(ymin=Lower,
                      ymax=Upper))+
  geom_hline(yintercept = 0,
             linetype="dotted",
             alpha=0.3)+
  scale_x_discrete(limits = c("Sex",
                              "Feeding Rate",
                              "Latency",
                              "Cage Test",
                              "Handling Aggression",
                              "Sampling")) +
  labs(x = "Trait",
       y = "Log odds ratio of recapture probability (+/- 95% CrI)") +
  ylim(-1.2,0.6) +
  coord_flip() +
  theme_classic()


##flip order
OddsRatioPlots<-data.frame(Traits=c("Sampling",
                                    "Handling Aggression",
                                    "Cage Exploration Test",
                                    "Latency to Resume Feeding",
                                    "Feeding Rate",
                                    "Sex"),
                           Estimate = c(posterior.mode(coef_S2),
                                        posterior.mode(coef_A2),
                                        posterior.mode(coef_C2),
                                        posterior.mode(coef_L2),
                                        posterior.mode(coef_F2),
                                        posterior.mode(as.mcmc(smod@fixef[,2]))),
                           
                           Lower=c(HPDinterval(coef_S2)[,"lower"],
                                   HPDinterval(coef_A2)[,"lower"],
                                   HPDinterval(coef_C2)[,"lower"],
                                   HPDinterval(coef_L2)[,"lower"],
                                   HPDinterval(coef_F2)[,"lower"],
                                   HPDinterval(as.mcmc(smod@fixef[,2]))[,"lower"]),
                           
                           Upper=c(HPDinterval(coef_S2)[,"upper"],
                                   HPDinterval(coef_A2)[,"upper"],
                                   HPDinterval(coef_C2)[,"upper"],
                                   HPDinterval(coef_L2)[,"upper"],
                                   HPDinterval(coef_F2)[,"upper"],
                                   HPDinterval(as.mcmc(smod@fixef[,2]))[,"upper"]))

dev.off()

ggplot(OddsRatioPlots, aes(x=Traits, y = Estimate))+
  geom_pointrange(aes(ymin=Lower,
                      ymax=Upper))+
  geom_hline(yintercept = 0,
             linetype="dotted",
             alpha=0.3)+
  scale_x_discrete(limits = c("Sampling",
                              "Handling Aggression",
                              "Cage Exploration Test",
                              "Latency to Resume Feeding",
                              "Feeding Rate",
                               "Sex")) +
  labs(x = "Trait\n",
       y = "Log odds ratio of recapture probability (+/- 95% CrI)") +
  ylim(-1.2,0.6) +
  coord_flip() +
  theme_classic()+
  theme(text=element_text(size=20))





##Figure 3----
##First generate dataframe with mean BLUP value for each behavioural trait and link to survival data----
##mean feeding blups
posterior.mode.feeding<-data.frame(apply(m_feeding$Sol, 2, mean))
names(posterior.mode.feeding)

blups_feeding2 <- select(
  as_tibble(m_feeding$Sol),
  contains("TransponderHexCode")
) 

f3<-blups_feeding2 %>%
  summarise_if(is.numeric, mean)

f4<-data.frame(t(f3))
f5<-mutate(f4, TransponderHexCode=rownames(f4))
f5$TransponderHexCode<-str_remove(f5$TransponderHexCode, "TransponderHexCode.")
names(f5)[names(f5)=='t.f3.']<-'feed_blup'

data_fig3_feed <- merge(f5, recap, by = "TransponderHexCode")


##mean latency blups
posterior.mode.latency<-data.frame(apply(m_latency$Sol, 2, mean))
names(posterior.mode.latency)

blups_latency2 <- select(
  as_tibble(m_latency$Sol),
  contains("TransponderHexCode")
) 

l3<-blups_latency2 %>%
  summarise_if(is.numeric, mean)

l4<-data.frame(t(l3))
l5<-mutate(l4, TransponderHexCode=rownames(l4))
l5$TransponderHexCode<-str_remove(l5$TransponderHexCode, "TransponderHexCode.")
names(l5)[names(l5)=='t.l3.']<-'latency_blup'

data_fig3_latency <- merge(l5, recap2019, by = "TransponderHexCode")


##mean cage test blups
apply(m_cage$Sol, 2, mean)
posterior.mode.cage<-data.frame(apply(m_cage$Sol, 2, mean))
names(posterior.mode.cage)

blups_cage2 <- select(
  as_tibble(m_cage$Sol),
  contains("CatchRingNumber")
) 

c3<-blups_cage2 %>%
  summarise_if(is.numeric, mean)

c4<-data.frame(t(c3))
c5<-mutate(c4, CatchRingNumber=rownames(c4))
c5$CatchRingNumber<-str_remove(c5$CatchRingNumber, "CatchRingNumber.")
names(c5)[names(c5)=='t.c3.']<-'cage_blup'


data_fig3_cage <- merge(c5, recap, by = "CatchRingNumber")

##mean aggression blups

posterior.mode.aggression<-data.frame(apply(m_aggression$Sol, 2, mean))
names(posterior.mode.aggression)

blups_aggression2 <- select(
  as_tibble(m_aggression$Sol),
  contains("CatchRingNumber")
) 

a3<-blups_cage2 %>%
  summarise_if(is.numeric, mean)

a4<-data.frame(t(a3))
a5<-mutate(a4, CatchRingNumber=rownames(a4))
a5$CatchRingNumber<-str_remove(a5$CatchRingNumber, "CatchRingNumber.")
names(a5)[names(a5)=='t.a3.']<-'aggression_blup'

data_fig3_aggression <- merge(a5, recap, by = "CatchRingNumber")


##mean sampling blups
posterior.mode.sampling<-data.frame(apply(m_sampling$Sol, 2, mean))
names(posterior.mode.sampling)

blups_sampling2 <- select(
  as_tibble(m_sampling$Sol),
  contains("TransponderHexCode")
) 

s3<-blups_sampling2 %>%
  summarise_if(is.numeric, mean)

s4<-data.frame(t(s3))
s5<-mutate(s4, TransponderHexCode=rownames(s4))
s5$TransponderHexCode<-str_remove(s5$TransponderHexCode, "TransponderHexCode.")
names(s5)[names(s5)=='t.s3.']<-'sampling_blup'

data_fig3_sampling <- merge(s5, recap2020, by = "TransponderHexCode")


###generate figure 3----
library(ggbeeswarm) #helps visualise the raw data distribution within the boxplot
library(patchwork) #helps stack the plots as a panel


foraging_plot <- ggplot(data_fig3_feed,
                        aes(y = feed_blup,
                            x = as.factor(Recap)))+
  geom_violin()+
  geom_boxplot(width=0.2)+
  geom_beeswarm(cex = 0.5,
                alpha = 0.15)+
  ggtitle("(a)")+
  coord_flip()+
  theme_bw()+
  theme(panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.line = element_line(colour = "black"))+
  xlab("")+
  ylab("BLUP of foraging rate (visits/hour)")

latency_plot <- ggplot(data_fig3_latency,
                       aes(y = latency_blup,
                           x = as.factor(Recap)))+
  geom_violin()+
  geom_boxplot(width=0.2)+
  geom_beeswarm(cex = 0.5,
                alpha = 0.15)+
  ggtitle("(b)")+
  coord_flip()+
  theme_bw()+
  theme(panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.line = element_line(colour = "black"))+
  xlab("")+
  ylab("BLUP of latency to resume feeding (seconds)")

cage_plot <- ggplot(data_fig3_cage,
                       aes(y = cage_blup,
                           x = as.factor(Recap)))+
  geom_violin()+
  geom_boxplot(width=0.2)+
  geom_beeswarm(cex = 0.5,
                alpha = 0.15)+
  ggtitle("(c)")+
  coord_flip()+
  theme_bw()+
  theme(panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.line = element_line(colour = "black"))+
  xlab("Recapture")+
  ylab("BLUP of cage test score")


aggression_plot <- ggplot(data_fig3_aggression,
                       aes(y = aggression_blup,
                           x = as.factor(Recap)))+
  geom_violin()+
  geom_boxplot(width=0.2)+
  geom_beeswarm(cex = 0.5,
                alpha = 0.15)+
  ggtitle("(d)")+
  coord_flip()+
  theme_bw()+
  theme(panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.line = element_line(colour = "black"))+
  xlab("")+
  ylab("BLUP of aggression score")

sampling_plot <- ggplot(data_fig3_sampling,
                       aes(y = sampling_blup,
                           x = as.factor(Recap)))+
  geom_violin()+
  geom_boxplot(width=0.2)+
  geom_beeswarm(cex = 0.5,
                alpha = 0.15)+
  ggtitle("(e)")+
  coord_flip()+
  theme_bw()+
  theme(panel.border = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.line = element_line(colour = "black"))+
  xlab("")+
  ylab("BLUP sampling behaviour")


patch <- foraging_plot/latency_plot/cage_plot/aggression_plot/sampling_plot
patch



