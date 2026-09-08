# Data analysis for:
# Sampling is associated with increased survival: A field experiment in black-capped chickadees
# Haave-Audet, E., Martin, J. A., wijmenga, J. J., & Mathot, K. J.

# Libraries----

library(lme4) #v. 1.1.27.1
library(MCMCglmm) #v. 2.32
library(ggpubr) #v. 0.4.0
library(broom.mixed)#v. 0.2.7
library(tidyverse) #v. 1.3.1

# Working directory----
# Set working directory

# Load data----
data<-read.table(file="data_HaaveAudet-et-al_20230529.txt", sep="\t", header = TRUE)

# Analyses----
# * Prep data####
# Separate luxury and necessity sampling by status of adjacent feeder
# full= sampling as luxury (alternative food available)
# empty= sampling as necessity (no alternative food available)

# Sampling as luxury (presence of alternate food)
luxury <- subset(data, Adjacent == "full")

# Rename sampled column to 'Luxury'
luxury <- luxury %>%
  rename(Luxury = Sampled)

# Add column for Necessity (w/out alternate food) that is filled with NAs
luxury <- luxury %>%
  add_column(Necessity = NA)

# Sampling as necessity
necessity <- data %>%
  filter(Adjacent == "empty") %>%
  rename(Necessity = Sampled) %>%
  add_column(Luxury = NA)

# Combine Luxury and Necessity into single dataframe
lux_nec <- bind_rows(luxury, necessity)

# Remove birds with NA/s in DNA sex
lux_nec2 <- subset(lux_nec, !is.na(DNASex))

# Keep a single row for survival per individual
## Keep first observation per ind
surv <- lux_nec2 %>%
  select(TransponderHexCode, Feeder, Round, treatment.sampling, Survived, DNASex) %>%
  group_by(TransponderHexCode) %>%
  slice(1)

## Add single value of survival to full data
lux_nec3 <- left_join(
  lux_nec2, surv,
  by = c("TransponderHexCode", "Feeder", "Round", "treatment.sampling")
)

lux_nec3 <- lux_nec3 %>%
  rename(
    Survival2 = Survived.y,
    DNASex=DNASex.x
  )

# Scale continuous variables
lux_nec3 <- mutate(lux_nec3,
                   bl_rate_sc = scale(baseline_rate),
                   bl_temp_sc = scale(baseline_temp),
                   AvgTemp_sc = scale(AvgTemp)
)

# * Prior####
prior_3var <- list(
  R = list(V = diag(3), nu = 2.002, fix = 2),
  G = list(
    G1 = list(
      V = diag(3), nu = 4,
      alpha.mu = rep(0, 3),
      alpha.V = diag(3)
    )
  )
)

# * MCMC Models####
model.traits <- MCMCglmm(
  cbind(scale(baseline_rate), Luxury, Necessity) ~ trait - 1 +
    at.level(trait, 3):scale(AvgTemp) + 
    at.level(trait, 2):scale(AvgTemp) + 
    at.level(trait, 1):scale(baseline_temp) + 
    trait:DNASex,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ idh(trait):units,
  family = c("gaussian", "threshold", "threshold"),
  data = as.data.frame(lux_nec3),
  prior = prior_3var,
  verbose = TRUE,
  pr = TRUE, #TRUE to calculate blups, FASLE for diagnositcs
  nitt = 53000, thin = 50, burnin = 3000
)
#par(mar = c(1, 1, 1, 1))
#plot(model.traits)
summary(model.traits)

# diagnostics
# heidel.diag(model.traits$Sol) # fixed effects
# heidel.diag(model.traits$VCV) # random effects
# autocorr.diag(model.traits$Sol)

# ** Bayesian p-values####
# Effect of sex on baseline foraging
counts_foraging<-ifelse(model.traits$Sol[,7]>0,1,0)
sum(counts_foraging)
counts_foraging2<-ifelse(model.traits$Sol[,7]<0,1,0)
sum(counts_foraging2)
sum(counts_foraging)/(sum(counts_foraging)+sum(counts_foraging2))

# Effect of sex on luxury sampling
counts_luxury<-ifelse(model.traits$Sol[,8]>0,1,0)
sum(counts_luxury)
counts_luxury2<-ifelse(model.traits$Sol[,8]<0,1,0)
sum(counts_luxury2)
sum(counts_luxury)/(sum(counts_luxury)+sum(counts_luxury2))

# * Repeatability of traits====
# Luxury
lux_rep <- model.traits$VCV[,"traitLuxury:traitLuxury.TransponderHexCode"]/
  (model.traits$VCV[,"traitLuxury:traitLuxury.TransponderHexCode"] + 
     model.traits$VCV[,"traitLuxury.units"])

# Necessity
nec_rep <- model.traits$VCV[,"traitNecessity:traitNecessity.TransponderHexCode"]/
  (model.traits$VCV[,"traitNecessity:traitNecessity.TransponderHexCode"] +
     model.traits$VCV[,"traitNecessity.units"])

# Foraging
forg_rep <- model.traits$VCV[,"traitbaseline_rate:traitbaseline_rate.TransponderHexCode"]/
  (model.traits$VCV[,"traitbaseline_rate:traitbaseline_rate.TransponderHexCode"] +
     model.traits$VCV[,"traitbaseline_rate.units"])

# Combine into a single dataframe
df_trait_reps <- data_frame(Traits = c("Luxury",
                                       "Necessity",
                                       "Foraging"),
                            Estimate = c(mean(lux_rep),
                                         mean(nec_rep),
                                         mean(forg_rep)),
                            Lower = c(HPDinterval(lux_rep)[,"lower"],
                                      HPDinterval(nec_rep)[,"lower"],
                                      HPDinterval(forg_rep)[,"lower"]),
                            Upper = c(HPDinterval(lux_rep)[,"upper"],
                                      HPDinterval(nec_rep)[,"upper"],
                                      HPDinterval(forg_rep)[,"upper"]))
# * Extracting BLUPs====
## lazy function for mode and HPDI on mcmc object
summ_mcmc <- function(object) {
  out <- data.frame(
    mode = posterior.mode(object)
  )
  out <- cbind(out, HPDinterval(object))
}

# ** Luxury####
lux_lm_list <- list()
for (iter in seq_len(nrow(model.traits$Sol))) {
  blups_lux <- select(
    as_tibble(model.traits$Sol),
    contains("traitLuxury.TransponderHexCode.")
  )[iter, ]
  blups_luxury <- tibble(
    TransponderHexCode = str_remove(
      colnames(blups_lux), "traitLuxury.TransponderHexCode."
    ),
    blups_luxury = as.numeric(blups_lux)
  )
  
  data_lux_lm <- merge(blups_luxury, surv, all.x = T)
  lux_lm_list[[iter]] <- glm(
    Survived ~ blups_luxury + DNASex,
    data = data_lux_lm, family = binomial
  )
}

coef_lux <- as.mcmc(
  t(
    sapply(
      lux_lm_list,
      function(x) {
        summary(x)$coefficients[, 1]
      }
    )
  )
)

coef_lux_summ<-summ_mcmc(coef_lux)

# Bayesian p-value
counts_lux<-ifelse(coef_lux[]>0,1,0)
sum(counts_lux)
counts_lux2<-ifelse(coef_lux[]<0,1,0)
sum(counts_lux2)
sum(counts_lux2)/(sum(counts_lux)+sum(counts_lux2))

# ** Necessity####
nec_lm_list <- list()
for (iter in seq_len(nrow(model.traits$Sol))) {
  blups_nec <- select(
    as_tibble(model.traits$Sol),
    contains("traitNecessity.TransponderHexCode.")
  )[iter, ]
  blups_necessity <- tibble(
    TransponderHexCode = str_remove(
      colnames(blups_nec), "traitNecessity.TransponderHexCode."
    ),
    blups_necessity = as.numeric(blups_nec)
  )
  
  data_nec_lm <- merge(blups_necessity, surv, all.x = T)
  nec_lm_list[[iter]] <- glm(
    Survived ~ blups_necessity + DNASex,
    data = data_nec_lm, family = binomial
  )
}

coef_nec <- as.mcmc(
  t(
    sapply(
      nec_lm_list,
      function(x) {
        summary(x)$coefficients[, 1]
      }
    )
  )
)

coeff_nec_summ<-summ_mcmc(coef_nec)

# ** Baseline foraging####
forg_lm_list <- list()
for (iter in seq_len(nrow(model.traits$Sol))) {
  blups_forg <- select(
    as_tibble(model.traits$Sol),
    contains("traitbaseline_rate.TransponderHexCode.")
  )[iter, ]
  blups_foraging <- tibble(
    TransponderHexCode = str_remove(
      colnames(blups_forg), "traitbaseline_rate.TransponderHexCode."
    ),
    blups_foraging = as.numeric(blups_forg)
  )
  
  data_forg_lm <- merge(blups_foraging, surv, all.x = T)
  forg_lm_list[[iter]] <- glm(
    Survived ~ blups_foraging + DNASex,
    data = data_forg_lm, family = binomial
  )
}

coef_forg <- as.mcmc(
  t(
    sapply(
      forg_lm_list,
      function(x) {
        summary(x)$coefficients[, 1]
      }
    )
  )
)

coef_forg_summ<-summ_mcmc(coef_forg)

# ** Supplementary analysis (Table S2)####
# run lm with all three traits and survival
traits_lm_list <- list()
for (iter in seq_len(nrow(model.traits$Sol))) {
  blups_lux <- select(
    as_tibble(model.traits$Sol),
    contains("traitLuxury.TransponderHexCode.")
  )[iter, ]
  blups_nec <- select(
    as_tibble(model.traits$Sol),
    contains("traitNecessity.TransponderHexCode.")
  )[iter, ]
  blups_forg <- select(
    as_tibble(model.traits$Sol),
    contains("traitbaseline_rate.TransponderHexCode.")
  )[iter, ]
  blups_traits <- tibble(
    TransponderHexCode = str_remove(
      colnames(blups_forg), "traitbaseline_rate.TransponderHexCode."
    ),
    blups_luxury = as.numeric(blups_lux),
    blups_necessity = as.numeric(blups_nec),
    blups_foraging = as.numeric(blups_forg)
  )
  
  data_traits_lm <- merge(blups_traits, surv, by = c("TransponderHexCode"))
  
  traits_lm_list[[iter]] <- glm(
    Survived ~ blups_foraging + blups_luxury + blups_necessity + DNASex,
    data = data_traits_lm, family = binomial
  )
}

coef_all <- as.mcmc(
  t(
    sapply(
      traits_lm_list,
      function(x) {
        summary(x)$coefficients[, 1]
      }
    )
  )
)

coef_all_summ<-summ_mcmc(coef_all)

# ** Post-hoc analysis (Table S4)####
# Does structural size affect sampling?
# Tarsus size is measured every time a bird is captured
# We took the average tarsus measurement per individual, 
# and centered and scaled by sex.

model.traits.tar <- MCMCglmm(
  cbind(scale(baseline_rate), Luxury, Necessity) ~ trait - 1 +
    at.level(trait, 3):scale(AvgTemp) + 
    at.level(trait, 2):scale(AvgTemp) + 
    at.level(trait, 1):scale(baseline_temp) + 
    trait:DNASex + trait:ScTar,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ idh(trait):units,
  family = c("gaussian", "threshold", "threshold"),
  data = as.data.frame(lux_nec3),
  prior = prior_3var,
  verbose = TRUE,
  pr = TRUE,
  nitt = 53000, thin = 50, burnin = 3000
)
summary(model.traits.tar)

# ** Post-hoc analysis (Table S3)####
# Does the number of sites visited by a bird predict its sampling behaviour?
# merge with sampling BLUPs & model effect
n_sites<-select(data, TransponderHexCode, NSites)

#Luxury sampling
blups_luxury_sites<-left_join(blups_luxury, n_sites, by="TransponderHexCode") %>% 
  distinct()

m_lux_sites<-lm(blups_luxury~NSites, data=blups_luxury_sites)
summary(m_lux_sites)
hist(resid(m_lux_sites))

#Necessity sapmling
blups_necessity_sites<-left_join(blups_necessity, n_sites, by="TransponderHexCode") %>% 
  distinct()

m_nec_sites<-lm(blups_necessity~NSites, data=blups_necessity_sites)
hist(resid(m_nec_sites))
summary(m_nec_sites)

# Figures----
# * Figure 2: Temp effect====
model.temp<-glmer(Sampled~ + Adjacent:AvgTemp+ (1|TransponderHexCode) + (1|Feeder) + (1|Round), data=data, family = binomial)

model.temp.df<-augment(model.temp, type.predict="response", se_fit=TRUE)
head(model.temp.df)

data$Sampled<-as.numeric(as.character(data$Sampled))

# Get mean fitted value with SE for each temp by status of adjacent feeder

prob.samp<-model.temp.df %>% 
  group_by(Adjacent, AvgTemp) %>% 
  summarize(mean_prob=mean(.fitted), sd=sd(.fitted), n=n(),
            n_yes=sum(Sampled==1), n_no=sum(Sampled=0)) %>%
  mutate(p=(n_yes/n)) %>% 
  mutate(q=1-p) %>% 
  mutate(SE=sqrt((p*q)/n))

temp.samp<-ggplot()+
  stat_smooth(data=model.temp.df, aes(x=AvgTemp,y=.fitted, colour=Adjacent), method="glm", se=TRUE, method.args = list(family=binomial))+
  theme_bw()+
  geom_text(data=prob.samp, aes(x=AvgTemp, y=mean_prob, colour=Adjacent, label=n), vjust=-1, hjust=-0.2, size=3)+
  geom_count(data=data, aes(x=AvgTemp, y=Sampled, colour=Adjacent))+
  geom_pointrange(data=prob.samp, aes(x=AvgTemp, y=mean_prob, ymin=(mean_prob-SE), ymax=(mean_prob+SE), colour=Adjacent), 
                  shape=17)+
  scale_color_manual(values=c("black", "grey50"), labels=c("No", "Yes"))+
  xlab(expression("Temperature ("*~degree*C*", four day average)"))+
  ylab("Sampling\n")+
  ylim(0,1)+
  labs(colour="Alternative Food")+
  theme(axis.title = element_text(size=12), axis.text = element_text(size=11))

temp.samp

# * Figure 3: Trait correlations====
# Correlation between traits
mcmc_lux_nec <- model.traits$VCV[, "traitNecessity:traitLuxury.TransponderHexCode"] /
  (sqrt(model.traits$VCV[, "traitNecessity:traitNecessity.TransponderHexCode"]) *
     sqrt(model.traits$VCV[, "traitLuxury:traitLuxury.TransponderHexCode"]))

mcmc_lux.forg <- model.traits$VCV[, "traitLuxury:traitbaseline_rate.TransponderHexCode"] /
  (sqrt(model.traits$VCV[, "traitLuxury:traitLuxury.TransponderHexCode"]) *
     sqrt(model.traits$VCV[, "traitbaseline_rate:traitbaseline_rate.TransponderHexCode"]))

mcmc_nec.forg <- model.traits$VCV[, "traitNecessity:traitbaseline_rate.TransponderHexCode"] /
  (sqrt(model.traits$VCV[, "traitNecessity:traitNecessity.TransponderHexCode"]) *
     sqrt(model.traits$VCV[, "traitbaseline_rate:traitbaseline_rate.TransponderHexCode"]))

df_mcmc_cors <- data_frame(
  Traits = c(
    "Alt Yes, Alt No",
    "Alt Yes, Foraging",
    "Alt No, Foraging"
  ),
  Estimate = c(
    mean(mcmc_lux_nec),
    mean(mcmc_lux.forg),
    mean(mcmc_nec.forg)
  ),
  Lower = c(
    HPDinterval(mcmc_lux_nec)[, "lower"],
    HPDinterval(mcmc_lux.forg)[, "lower"],
    HPDinterval(mcmc_nec.forg)[, "lower"]
  ),
  Upper = c(
    HPDinterval(mcmc_lux_nec)[, "upper"],
    HPDinterval(mcmc_lux.forg)[, "upper"],
    HPDinterval(mcmc_nec.forg)[, "upper"]
  )
)

traits<-ggplot(df_mcmc_cors, aes(x = Traits, y = Estimate)) +
  geom_pointrange(aes(
    ymin = Lower,
    ymax = Upper
  ), shape = 19, size = 0.7) +
  geom_hline(
    yintercept = 0,
    linetype = "dotted",
    alpha = 0.3
  ) +
  scale_x_discrete(limits = c(
    "Alt Yes, Alt No",
    "Alt Yes, Foraging",
    "Alt No, Foraging"
  )) +
  labs(
    x = NULL,
    y = "Correlation (Estimate +/- 95% CrIs)"
  ) +
  ylim(-1, 1) +
  coord_flip() +
  theme_classic() +
  theme(
    axis.text.y = element_text(size = 12, colour = "black"),
    axis.title.x = element_text(size = 12), axis.text.x = element_text(size = 11)
  )
traits

# * Figure 5: Correlation w/ survival====
# plot intercept and sex for each trait

# ** A) Luxury sampling####
coef_lux_summ<-rownames_to_column(coef_lux_summ, "Traits")

luxury<-ggplot(coef_lux_summ, aes(x= Traits, y = mode))+
  geom_pointrange(aes(
    y = mode,
    ymin = lower,
    ymax = upper)) +
  geom_hline(
    yintercept = 0,
    linetype = "dotted",
    alpha = 0.3
  ) +
  labs(
    x = NULL,
    y = "Log Odds Ratio (Estimate +/- 95% HPDIs)\n"
  ) +
  scale_x_discrete(limits=c("DNASexMale", "blups_luxury","(Intercept)"),
                   labels=c("Sex (Male)", "Alt Yes", "Intercept"))+
  coord_flip()+
  theme_light() +
  theme(
    axis.text.y = element_text(size = 12, colour = "black"),
    axis.title.x = element_text(size = 12), axis.text.x = element_text(size = 11)
  )
luxury

# ** B) Necessity sampling####
coeff_nec_summ<-rownames_to_column(coeff_nec_summ, "Traits")

necessity<-ggplot(coeff_nec_summ, aes(x= Traits, y = mode))+
  geom_pointrange(aes(
    y = mode,
    ymin = lower,
    ymax = upper)) +
  geom_hline(
    yintercept = 0,
    linetype = "dotted",
    alpha = 0.3
  ) +
  labs(
    x = NULL,
    y = "Log Odds Ratio (Estimate +/- 95% HPDIs)\n"
  ) +
  scale_x_discrete(limits=c("DNASexMale", "blups_necessity","(Intercept)"),
                   labels=c("Sex (Male)", "Alt No", "Intercept"))+
  coord_flip()+
  theme_light() +
  theme(
    axis.text.y = element_text(size = 12, colour = "black"),
    axis.title.x = element_text(size = 12), axis.text.x = element_text(size = 11)
  )
necessity

# ** C)Baseline Foraging####
coef_forg_summ<-rownames_to_column(coef_forg_summ, "Traits")

foraging<-ggplot(coef_forg_summ, aes(x= Traits, y = mode))+
  geom_pointrange(aes(
    y = mode,
    ymin = lower,
    ymax = upper)) +
  geom_hline(
    yintercept = 0,
    linetype = "dotted",
    alpha = 0.3
  ) +
  labs(
    x = NULL,
    y = "Log Odds Ratio (Estimate +/- 95% HPDIs)\n"
  ) +
  scale_x_discrete(limits=c("DNASexMale", "blups_foraging","(Intercept)"),
                   labels=c("Sex (Male)", "Foraging", "Intercept"))+
  coord_flip()+
  theme_light() +
  theme(
    axis.text.y = element_text(size = 12, colour = "black"),
    axis.title.x = element_text(size = 12), axis.text.x = element_text(size = 11)
  )
foraging

# ** Figure 4####
fig.4<- ggarrange(luxury, necessity,foraging, labels = "AUTO",
                  ncol = 3, hjust = -5)
fig.4

# ** Figure 5####
# merge survival to BLUP df
# extract survival data
survival<-select(surv, TransponderHexCode, Survived)
blups_cor_traits<-left_join(blups_necessity, blups_luxury, by="TransponderHexCode")
blups_cor_traits<-left_join(blups_cor_traits, survival, by="TransponderHexCode")
blups_cor_traits$Survived<-as.factor(blups_cor_traits$Survived)

fig.5<-ggplot(data=blups_cor_traits, aes(blups_cor_traits$blups_necessity, blups_cor_traits$blups_luxury))+
  geom_point(size=3, aes(shape=Survived))+
  scale_shape_manual(values=c(1, 16))+
  stat_smooth(method="lm", se=FALSE, colour="grey46")+
  theme_bw()+
  xlab(label="Sampling BLUPs (Alt Food: No)")+
  ylab(label="Sampling BLUPs\n (Alt Food: Yes)\n")+
  theme(axis.title = element_text(size=14), axis.text = element_text(size=12))
fig.5

# ** Figure S4####
# Plot the relationship between sampling and temp as function of adjacent feeder with only birds that visited the adjacent feeder
# code copied from fig 2
model.temp2<-glmer(Sampled~ + Adjacent:AvgTemp+ (1|TransponderHexCode) + (1|Feeder) + (1|Round), data=subset(data, Non_Sampled==1), family = binomial)
summary(model.temp2)

model.temp.df2<-augment(model.temp2, type.predict="response", se_fit=TRUE)
head(model.temp.df2)

data$Sampled<-as.numeric(as.character(data$Sampled))

# Get mean fitted value with SE for each temp by status of adjacent feeder

prob.samp2<-model.temp.df2 %>% 
  group_by(Adjacent, AvgTemp) %>% 
  summarize(mean_prob=mean(.fitted), sd=sd(.fitted), n=n(),
            n_yes=sum(Sampled==1), n_no=sum(Sampled=0)) %>%
  mutate(p=(n_yes/n)) %>% 
  mutate(q=1-p) %>% 
  mutate(SE=sqrt((p*q)/n))

Fig.S4<-ggplot()+
  stat_smooth(data=model.temp.df2, aes(x=AvgTemp,y=.fitted, colour=Adjacent), method="glm", se=TRUE, method.args = list(family=binomial))+
  theme_bw()+
  geom_text(data=prob.samp2, aes(x=AvgTemp, y=mean_prob, colour=Adjacent, label=n), vjust=-1.4, hjust=-0.2, size=3)+
  geom_count(data=data, aes(x=AvgTemp, y=Sampled, colour=Adjacent))+
  geom_pointrange(data=prob.samp2, aes(x=AvgTemp, y=mean_prob, ymin=(mean_prob-SE), ymax=(mean_prob+SE), colour=Adjacent), 
                  shape=17)+
  scale_color_manual(values=c("black", "grey50"), labels=c("No", "Yes"))+
  xlab(expression("Temperature ("*~degree*C*", four day average)"))+
  ylab("Sampling\n")+
  ylim(0,1)+
  labs(colour="Alternative Food")+
  theme(axis.title = element_text(size=12), axis.text = element_text(size=11))

Fig.S4
