#load data and libraries ----
setwd("C:\\Users\\kimbe\\Desktop\\feeders")
data<-read.csv("data_20210608.csv")
names(data)


library(lme4)
require(MCMCglmm)
library(arm)
library(ggplot2)
library(here)
library(rptR)
library(MCMCglmm)
library(ggpubr)
library(tidyverse) # better if last package loaded usually



#data processing----

#create sex variable that is categorical
summary(data$Sex)
data$sex<-ifelse(data$Sex==-0.5, "Male", "Female")

#transform latency data
data$logLatency<-scale(log(data$Sec))
hist(data$logLatency)

#center and scale Temperature data
data$cTemp<-scale(data$TempDay)

#transform and center foraging data
data$logFR<-scale(log(data$HFRBef))


##annual survival
data$survival2<-ifelse(data$survival>0,1,0)

##Treatment as factor
data$FTreatment<-as.factor(data$Treatment)


###create separate file for survival
surv <- data %>%
  select(ID, survival2, Sex) %>%
  group_by(ID) %>%
  slice(1)


#### Run a bivariate model for latency + FR----
prior_2var <- list(
  R = list(V = diag(2), nu = 0.002),
  G = list(
    G1 = list(
      V = diag(2), nu = 2,
      alpha.mu = rep(0, 2),
      alpha.V = diag(2^2,2,2)
    )
  )
)

## need to add pr = TRUE to model argument to save posterior distribution of BLUPS
model.traits <- MCMCglmm(
  cbind(logFR, logLatency) ~trait-1+
    at.level(trait,1):sex+
    at.level(trait,1):cTemp+
    at.level(trait,2):sex+
    at.level(trait,2):FTreatment+
    at.level(trait, 2):FTreatment:cTemp,
  random = ~ us(trait):ID,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian"),
  data = data,
  prior = prior_2var,
  verbose = TRUE,
  singular.ok=TRUE,
  pr = TRUE,
  nitt=103000,
  burnin=3000,
  thin=100
)
par(mar = c(1, 1, 1, 1))
plot(model.traits)
summary(model.traits)


# among-individual correlations between FR and latency
mcmc_FR_latency <- model.traits$VCV[, "traitlogFR:traitlogLatency.ID"] /
  (sqrt(model.traits$VCV[, "traitlogFR:traitlogFR.ID"]) *
     sqrt(model.traits$VCV[, "traitlogLatency:traitlogLatency.ID"]))

mean(mcmc_FR_latency)
HPDinterval(mcmc_FR_latency)

# within-individual correlations between FR and latency
within<-model.traits$VCV[, "traitlogFR:traitlogLatency.units"] /
  (sqrt(model.traits$VCV[, "traitlogFR:traitlogFR.units"]) *
     sqrt(model.traits$VCV[, "traitlogLatency:traitlogLatency.units"]))

mean(within)
HPDinterval(within)


###adjusted repeatability
summary(model.traits)

##repeatability of feeding rate
repeatabilityFR<-model.traits$VCV[, "traitlogFR:traitlogFR.ID"] /
  (model.traits$VCV[,"traitlogFR:traitlogFR.units"]+model.traits$VCV[, "traitlogFR:traitlogFR.ID"])
mean(repeatabilityFR)
HPDinterval(repeatabilityFR)

#repeatability of latency to resume feeding
repeatabilityrisk<-model.traits$VCV[, "traitlogLatency:traitlogLatency.ID"] /
  (model.traits$VCV[,"traitlogLatency:traitlogLatency.units"]+model.traits$VCV[, "traitlogLatency:traitlogLatency.ID"])
mean(repeatabilityrisk)
HPDinterval(repeatabilityrisk)


#survival analyses----
# multivariate models with survival fitted as third trait showed poor mixing/convergence
#instead, use distribution of blups for behavioural traits drawn from multivariate model above
# do among-individual differences in feeding rate predict survival?
# script runs 1000 simulations, each with a separate BLUP value drawn from a distribution of BLUPs
FR2_lm_list <- list()
for (iter in seq_len(nrow(model.traits$Sol))) {
  blups_FR2 <- select(
    as_tibble(model.traits$Sol),
    contains("traitlogFR.ID")
  )[iter, ] 
  blups_FR <- tibble(
    ID = str_remove(colnames(blups_FR2), "traitlogFR.ID."),
    blups_FR = as.numeric(blups_FR2))
  
  data_FR2_lm <- merge(blups_FR, surv, by = "ID")
  FR2_lm_list[[iter]] <- glm(survival2 ~ blups_FR, data = data_FR2_lm, family = binomial)
}

coef_FR2 <- as.mcmc(
  sapply(
    FR2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)
coef_FR2 <- as.mcmc(
  sapply(
    FR2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)

posterior.mode(coef_FR2)
mean(coef_FR2)
HPDinterval(coef_FR2)

#calculate bayesian p-value
pos<-ifelse(coef_FR2>0,1,0)
sum(pos)
neg<-ifelse(coef_FR2<0,1,0)
sum(neg)
bayesian_p<-sum(pos)/(sum(pos)+sum(neg))
bayesian_p

# Risk
# do among-individual differences in latency to resume feeding predict survival?
# script runs 1000 simulations, each with a separate BLUP value drawn from a distribution of BLUPs
risk2_lm_list <- list()
for (iter in seq_len(nrow(model.traits$Sol))) {
  blups_risk2 <- select(
    as_tibble(model.traits$Sol),
    contains("traitlogLatency.ID")
  )[iter, ] 
  blups_risk <- tibble(
    ID = str_remove(colnames(blups_risk2), "traitlogLatency.ID."),
    blups_risk = as.numeric(blups_risk2))
  
  data_risk2_lm <- merge(blups_risk, surv, by = "ID")
  risk2_lm_list[[iter]] <- glm(survival2 ~ blups_risk, data = data_risk2_lm, family = binomial)
}


coef_risk2 <- as.mcmc(
  sapply(
    risk2_lm_list,
    function(x) {
      summary(x)$coefficients[2, 1]
    }
  )
)

posterior.mode(coef_risk2)
mean(coef_risk2)
HPDinterval(coef_risk2)

#calculate bayesian p-value
pos<-ifelse(coef_risk2>0,1,0)
sum(pos)
neg<-ifelse(coef_risk2<0,1,0)
sum(neg)
bayesian_p<-sum(pos)/(sum(pos)+sum(neg))
bayesian_p


###glm sex survival
##does sex predict differences in survival
names(surv)
surv$sex<-ifelse(surv$Sex==-0.5, "Male", "Female")

m<-glm(survival2~sex, data=surv, family=binomial)
summary(m)
confint(m)



###generate plotplot----

###first, FR
###each column is an ID, 1000 rows per ID
library(data.table)
FR <- select(
  as_tibble(model.traits$Sol),
  contains("traitlogFR.ID")
)

#converts from wide to long format
FR_long<-
  FR %>%
  pivot_longer(
    everything(),
    names_to=c("traitlogFR.ID.")
  )
FR_long<-tibble(FR_long)

FR_long$ID<-str_remove(FR_long$traitlogFR.ID., "traitlogFR.ID.")
FR_long$FRblup<-FR_long$value

#calculate means and 95% CrI
df <- FR_long %>% 
  group_by(ID) %>% 
  summarise(
    FR_l = quantile(FRblup, 0.05),
    FR_mean = mean(FRblup),
    FR_u = quantile(FRblup, 0.95))




###second, latency
###each column is an ID, 1000 rows per ID
latency <- select(
  as_tibble(model.traits$Sol),
  contains("traitlogLatency.ID")
)

#converts from wide to long format
Latency_long<-
  latency %>%
  pivot_longer(
    everything(),
    names_to=c("traitlogLatency.ID.")
  )
Latency_long<-tibble(Latency_long)

Latency_long$ID<-str_remove(Latency_long$traitlogLatency.ID., "traitlogLatency.ID.")
Latency_long$Latencyblup<-Latency_long$value

#calculate means and 95% CrI
df2 <- Latency_long %>% 
  group_by(ID) %>% 
  summarise(
    Latency_l = quantile(Latencyblup, 0.05),
    Latency_mean = mean(Latencyblup),
    Latency_u = quantile(Latencyblup, 0.95))



plotdf<- merge(df, df2, by = "ID")
plotdf2<-merge(plotdf, surv, by = "ID")

plotdf2$survive<-as.factor(plotdf2$survival2)
names(plotdf2)



ggplot(plotdf2, aes(x=FR_mean, y=Latency_mean, shape=survive, colour=survive))+
  geom_point(size=3)+
  scale_shape_manual(values=c(1,2))+
  scale_colour_manual(values=c(1,2))+
  theme_bw()+
  theme(panel.border = element_blank(), panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(), axis.line = element_line(colour = "black"))+
  geom_errorbar(aes(ymin=Latency_l, ymax=Latency_u))+
  geom_errorbar(aes(xmin=FR_l, xmax=FR_u))+
  xlab("Feeding rate (BLUP +/- 95% CrI)")+
  ylab("Latency to resume feeding (BLUP +/- 95% CrI)")
