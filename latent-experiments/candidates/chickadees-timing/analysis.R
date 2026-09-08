### Code for reproducible analyses for "Exploring sources of (co-)variation in the timing and intensity rate of foraging in a wild population of Black-capped chickadees (Poecile atricapillus)"

# Nathan Hobbs, Deborah M. Hawkshaw, Jan J. Wijmenga and Kimberley J. Mathot

# R version ----
# Version 4.3.1

# Package download ----
library(data.table) # V1.14.4
library(lme4) # V1.1-27.1
library(ggplot2) # V3.3.5
library(rptR) # V0.9.22
library(dplyr) # V1.0.7
library(MCMCglmm) # V2.35
library(tidyverse) # V2.0.0
library(broom) # V1.3-28.1
library(nadiv) # V2.17.2
library(ggpubr) # V0.6.0
setwd("C:/Users/kimbe/Desktop/Nathan/data&code")###modify as needed
# Load the data file----
data2023 <- read.csv(file = "2022-2023data.csv", header = TRUE)


# Data selection----
# Remove transponder readings that were the observer transponder during visits to feeders for battery changes and feeder refills
data2023_V2 <- subset(data2023, type == "bird")

# Feeders were full continuously for 2022-2023 season, therefore, all days without technical issues can be used for feeding data
# But, want to restrict data range to December 1st through February 28th 
# This means start date for feeders observations is at least 1 week after catching attempt at feeder
# Last day is final day when feeders were maintained full and with antennas

# Make a date column
data2023_V2$date <- as.Date(data2023_V2$Date_Time, format = "%Y-%m-%d")
feederdays_V1 <- subset(data2023_V2, date >= "2022-12-01" & date <= "2023-02-28")

# We now have constrained data to December-February dates, lets do a quick proof
as.numeric(length(unique(feederdays_V1$date)))
levels(as.factor(feederdays_V1$date))


## Now we want to remove all birds that were known to use feeder 14
# Feeder 14 could not be used during main study period because it was operating on a different RFID frequency
# All birds known to use feeder 14 to be removed from analyses
# We were able to monitor birds at feeder 14 prior to December 5th, so we use these dates to remove them
feederdays_V2 <- subset(data2023_V2, date >= "2022-10-29" & date <= "2022-12-05")
write.csv(feederdays_V2, file = "feederdays_V2.csv", row.names = FALSE)
feederdays_V2 <- data.table(feederdays_V2)
# Testing how many times in total a bird visited a specific feeder prior to the 5th
feeder14birds <- subset(feederdays_V2, feederdays_V2$Feeder == "14A")
feeder14birds_2 <- (count(feeder14birds, Feeder, TransponderHexCode))


# Data filtering: feeder 14 hex codes (includes all 51 birds from feeder14birds_2 + 1 bird caught at feeder 14 but which didn't feed at feeder 14 "3B00193DBF")
feederdays_c <- subset(feederdays_V1, TransponderHexCode != "011016FC45" & TransponderHexCode != "01101710EB" &
  TransponderHexCode != "01103F48AB" & TransponderHexCode != "01103F55EE" &
  TransponderHexCode != "01103F60E2" & TransponderHexCode != "01103F67FF" &
  TransponderHexCode != "01103F74E6" & TransponderHexCode != "01103F7854" &
  TransponderHexCode != "01103FB6D8" & TransponderHexCode != "01103FCC73" &
  TransponderHexCode != "01103FD993" & TransponderHexCode != "01103FE5E9" &
  TransponderHexCode != "3B00181ADD" & TransponderHexCode != "3B0018B5BE" &
  TransponderHexCode != "3B0018E766" & TransponderHexCode != "3B0048FDA5" &
  TransponderHexCode != "3B004A03A4" & TransponderHexCode != "0110172140" &
  TransponderHexCode != "01103F3F6A" & TransponderHexCode != "01103F53ED" &
  TransponderHexCode != "01103F7371" & TransponderHexCode != "01103FDC0D" &
  TransponderHexCode != "01103FE3C8" & TransponderHexCode != "01103FE63C" &
  TransponderHexCode != "3B00187F30" & TransponderHexCode != "3B00493A82" &
  TransponderHexCode != "01103F8C29" & TransponderHexCode != "01103FB2CA" &
  TransponderHexCode != "3B00185EDE" & TransponderHexCode != "3B00191DE6" &
  TransponderHexCode != "3B004B37AA" & TransponderHexCode != "011016DD7C" &
  TransponderHexCode != "01103F3BB4" & TransponderHexCode != "01103F6D79" &
  TransponderHexCode != "01103F70F7" & TransponderHexCode != "01103F80C6" &
  TransponderHexCode != "01103F8F8F" & TransponderHexCode != "01103FA7E1" &
  TransponderHexCode != "01103FCA1E" & TransponderHexCode != "01103FDBDA" &
  TransponderHexCode != "01103FDBE3" & TransponderHexCode != "01103FDC3F" &
  TransponderHexCode != "01103FDF6D" & TransponderHexCode != "01103FE025" &
  TransponderHexCode != "01103FE0D6" & TransponderHexCode != "01103FE3C3" &
  TransponderHexCode != "3B0018830D" & TransponderHexCode != "3B00192733" &
  TransponderHexCode != "3B0019388F" & TransponderHexCode != "3B00193C82" &
  TransponderHexCode != "3B00194777" & TransponderHexCode != "3B00193DBF")


## "feederdays_c.csv" is raw data restricted to relevant dates (December 1st, 2022, to February 28th, 2023, inclusive) and relevant birds (feeder 14 birds excluded)
write.csv(feederdays_c, file = "feederdays_c.csv", row.names = FALSE)

# Key data needed for analysis is first, last, and total feeding events per day, per bird
feederdays_c <- data.table(feederdays_c)
feederdays_c$Time.continuous <- as.numeric(as.POSIXct(strptime(feederdays_c$Time, format = "%H:%M:%OS"))) - as.numeric(as.POSIXct(strptime("0", format = "%S"))) # Setting time as a continuous variable

feederdays_c <- setorder(feederdays_c, TransponderHexCode, date, Time.continuous) # Set order of visits for each bird for each day. 


feederdays_c <- feederdays_c[, .(first.feeding.event = data.table::first(Time), last.feeding.event = data.table::last(Time), total.feeding.events = .N), by = c("TransponderHexCode", "date")]

# Turn time of first and last feeder visit into a continuous variable.
feederdays_c$first.feed.continuous <- as.numeric(as.POSIXct(strptime(feederdays_c$first.feeding.event, format = "%H:%M:%OS"))) - as.numeric(as.POSIXct(strptime("0", format = "%S")))
feederdays_c$last.feed.continuous <- as.numeric(as.POSIXct(strptime(feederdays_c$last.feeding.event, format = "%H:%M:%OS"))) - as.numeric(as.POSIXct(strptime("0", format = "%S")))

# Introduction of weather data----
weather23 <- read.csv(file = "TempDay2023.csv", header = TRUE)
# In order to merge weather and foraging data, there needs to be a column with a shared name

weather23$date <- as.Date(weather23$date, format = "%Y-%m-%d") # may need to add ?.. to run
master_foraging <- merge(feederdays_c, weather23, by = c("date")) 

# Timing of sunrise and sunset is provided on the 24 hour clock from our data sheet
# So it needs to be converted to a continuous value, to make interpreting data easier and to calculate the time of first feeder and last feed, relative to sunrise and sunset respectively.
master_foraging$sunrise.continuous <- as.numeric(as.POSIXct(strptime(master_foraging$Sunrise, format = "%H:%M"))) - as.numeric(as.POSIXct(strptime("0", format = "%S")))
master_foraging$sunset.continuous <- as.numeric(as.POSIXct(strptime(master_foraging$Sunset, format = "%H:%M"))) - as.numeric(as.POSIXct(strptime("0", format = "%S")))

# Since longer days may be associated with warmer temperatures, it is necessary to
# check if temperature and daylength values are correlated in our dataset
cor.test(weather23$Temperature, weather23$Daylength, method = "pearson")
# r = 0.235, so fairly weak correlation. It is significantly non-zero, however
# 0.66 cut off before you worry about colinearity

# Adding in sex and age data----
sex_age <- read.csv(file = "Age_Sex_V2.csv", header = TRUE)
# Firstly, we have to merge the datasheets by using a column with a similar name
sex_age$TransponderHexCode <- as.character(sex_age$TransponderHexCode) # may need to add ?.. to run
master_foraging_V2 <- merge(master_foraging, sex_age, by = c("TransponderHexCode"))

# By subtracting max hatch year from 2023, we can find the minimum age of each bird
master_foraging_V2$Min_age <- as.numeric(2023 - master_foraging_V2$MaxHatchYear)
# In order to avoid a large skew in the data, we create juvenile (J) and adult (A) age classes
master_foraging_V2$age_category <- ifelse(master_foraging_V2$Min_age == 1, "J", "A")

# Five individuals from our dataset were unable to be sexed
# Because this only represents 3.4% of our previous 148 individuals, we simply removed the five from the dataset
master_foraging_V3 <- subset(master_foraging_V2, TransponderHexCode != "01103F4581" & TransponderHexCode != "01103F79A2" &
  TransponderHexCode != "01103F82A5" & TransponderHexCode != "01103FB625" & TransponderHexCode != "0110174F9C")

# Lastly, we removed the foraging data for any bird that fed less than ten times on a given day, for that day
# This is because it is difficult to draw any meaningful conclusions about foraging behavior from such a small number of feeder visits
master_foraging_V4 <- subset(master_foraging_V3, total.feeding.events >= 10)

# As daylength varied substantially over our study period, we also scaled
# our first and last feed values to sunrise and sunset, respectively.
master_foraging_V4$first.feed.centered <- as.numeric(master_foraging_V4$first.feed.continuous - master_foraging_V4$sunrise.continuous)
master_foraging_V4$last.feed.centered <- as.numeric(master_foraging_V4$last.feed.continuous - master_foraging_V4$sunset.continuous)

# Adding a column to master_foraging_V4 where the units of first and last feed
# centered are converted from seconds to minutes to aid in interpretability of results
master_foraging_V4$first.feed.centered.m <- master_foraging_V4$first.feed.centered / 60
master_foraging_V4$last.feed.centered.m <- master_foraging_V4$last.feed.centered / 60

# Create composite age/sex category (age-sex class). Has four values --> Adult males,
# Juvenile males, Adult females, Juvenile females
master_foraging_V4$AgeSex <- paste(master_foraging_V4$age_category, master_foraging_V4$SexConclusion)

# master_foraging_V4 represents an individuals first feed, last feed, and total
# feeds for a given day, whilst also providing information on their sex and age category
# master_foraging_V4 also has removed any individuals that visited feeder 14 or could not be assigned sex, and any very low daily feeder visits

# Finding information for the methods----
# Number of unique individuals 
length(unique(master_foraging_V4$TransponderHexCode))

# Mean and standard deviation of observation days of our 143 individuals
observation_days <- master_foraging_V4 %>%
  group_by(TransponderHexCode) %>%
  summarize(total_observation_days = n_distinct(date))
mean(observation_days$total_observation_days)
sd(observation_days$total_observation_days)

# Mean and standard deviation of total feeding events of our 143 individuals
observation_feeds <- master_foraging_V4 %>%
  group_by(TransponderHexCode) %>%
  summarize(total.feeding.events = sum(total.feeding.events))
mean(master_foraging_V4$total.feeding.events)
sd(master_foraging_V4$total.feeding.events)

# Mean and sd of weather and daylength 
mean(master_foraging_V4$Temperature)
sd(master_foraging_V4$Temperature)

mean(master_foraging_V4$Daylength)
sd(master_foraging_V4$Daylength)

# As a first step, run a series of univariate models----
# Purpose is quality checking for when we run our MCMCglmm
# Namely, we want to confirm normal distributions of residuals (And thus that Gaussian is correct for MCMCGLMM)

# As a note, exponents were included in the models in order to create AgeSex*Temperature and AgeSex*Daylength interactions
m1 <- lmer(first.feed.centered.m ~ (AgeSex + scale(Temperature) + scale(Daylength))^2 - scale(Temperature):scale(Daylength) + (1 | TransponderHexCode), data = master_foraging_V4)
summary(m1)
anova(m1)
plot(m1)
qqnorm(resid(m1))

m2 <- lmer(last.feed.continuous ~ (AgeSex + scale(Temperature) + scale(Daylength))^2 - scale(Temperature):scale(Daylength) + (1 | TransponderHexCode), data = master_foraging_V4)
summary(m2)
anova(m2)
plot(m2)
qqnorm(resid(m2))

m3 <- lmer(total.feeding.events ~ (AgeSex + scale(Temperature) + scale(Daylength))^2 - scale(Temperature):scale(Daylength) + (1 | TransponderHexCode), data = master_foraging_V4)
summary(m3)
anova(m3)
plot(m3)
qqnorm(resid(m3))

# Residual check to confirm that using a Gaussian distribution for the MCMCglmm is viable
hist(resid(m1))
hist(resid(m2))
hist(resid(m3))
# Models 1 and 3 are fairly normally distributed. Model 2 is not as good, but a Gaussian may still be possible will confirm with model checking for Bayesian models. 


# MCMCglmm model creation----

# Develop a prior for the model
# Our model has three variables, and the prior is developed to reflect that
prior_feeds_V1 <- list(
  R = list(V = diag(3), nu = 0.003),
  G = list(G1 = list(
    V = diag(3), nu = 10,
    alpha.mu = rep(0, 3),
    alpha.V = diag(25^2, 3, 3, 3)
  ))
)

# As an aside, we also tested each model with the following prior, in order to 
# confirm the robustness of our model 

prior_feeds_V2 = list(R = list(V = diag(2), nu = 0.002),
                                          G = list(G1 = list(V = diag(2), nu = 2,
                                                            alpha.mu = rep(0, 2),
                                                           alpha.V = diag(25^2, 2, 2))))

# Create the model
# Model assuming interactions between age:sex, temperature and daylength.
mcmc_feeds_V1 <- MCMCglmm(
  cbind(first.feed.centered.m, last.feed.centered.m, total.feeding.events) ~
    trait:AgeSex +
    trait:scale(Temperature):AgeSex +
    trait:scale(Daylength):AgeSex - 1,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = FALSE, # Set pr = FALSE for model checking.
  data = as.data.frame(master_foraging_V4)
)

# Now that our model is created, we begin to analyze the results----
# Plotting the model shows a brief overview of the data, and it also allows us
# to know if we included enough iterations, as each plot should
# resemble a "fuzzy caterpillar"
plot(mcmc_feeds_V1)

# Summarize to discern the fixed effect sizes for each trait and interaction
# and random effects and repeatability for main model
MCMCran <- mcmc_feeds_V1$VCV
posterior.mode(as.mcmc(MCMCran))
HPDinterval(as.mcmc(MCMCran))

MCMCfix <- mcmc_feeds_V1$Sol
posterior.mode((MCMCfix))
HPDinterval(MCMCfix)

# Repeatability
# First feed
Rep1 <- mcmc_feeds_V1$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.TransponderHexCode"] /
  (mcmc_feeds_V1$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.units"] + mcmc_feeds_V1$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.TransponderHexCode"])
mean(Rep1)
HPDinterval(Rep1)

# Last feed
Rep2 <- mcmc_feeds_V1$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"] /
  (mcmc_feeds_V1$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.units"] + mcmc_feeds_V1$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"])
mean(Rep2)
HPDinterval(Rep2)

# Total feed
Rep3 <- mcmc_feeds_V1$VCV[, "traittotal.feeding.events:traittotal.feeding.events.TransponderHexCode"] /
  (mcmc_feeds_V1$VCV[, "traittotal.feeding.events:traittotal.feeding.events.units"] + mcmc_feeds_V1$VCV[, "traittotal.feeding.events:traittotal.feeding.events.TransponderHexCode"])
mean(Rep3)
HPDinterval(Rep3)

# Interested in seeing if including interactions changes interpretations ----
# Model without interactions
mcmc_feeds_V2 <- MCMCglmm(cbind(first.feed.centered.m, last.feed.centered.m, total.feeding.events) ~
    trait:AgeSex +
    trait:scale(Temperature) +
    trait:scale(Daylength) - 1,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set PR = FALSE for model checking
  data = as.data.frame(master_foraging_V4)
)

# Model checking
plot(mcmc_feeds_V2) 

# First, random and fixed effects
MCMCran <- mcmc_feeds_V2$VCV
posterior.mode(as.mcmc(MCMCran))
HPDinterval(as.mcmc(MCMCran))

MCMCfix <- mcmc_feeds_V2$Sol
posterior.mode((MCMCfix))
HPDinterval(MCMCfix)
# Both yield similar results to the model without interactions

# Second, repeatability
# First feed
Rep1.2 <- mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.TransponderHexCode"] /
  (mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.units"] + mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.TransponderHexCode"])
mean(Rep1.2)
HPDinterval(Rep1.2)

# Last feed
Rep2.2 <- mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"] /
  (mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.units"] + mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"])
mean(Rep2.2)
HPDinterval(Rep2.2)

# Total feed
Rep3.2 <- mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.TransponderHexCode"] /
  (mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.units"] + mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.TransponderHexCode"])
mean(Rep3.2)
HPDinterval(Rep3.2)
# Repeatability also similar to model lacking interactions
# Thus, we will stick with the model that doesn't use interactions for simplicity (mcmc_feeds_V2)

# Extracting covariance values----
# Within-individual covariance
cw1 <- posterior.cor(mcmc_feeds_V2$VCV[, 10:18])
round(apply(cw1, 2, mean), 2)
round(apply(cw1, 2, quantile, c(0.025, 0.975)), 2)
# Var2 represents the relationship between timing of first and last feeder visit
# Var3 represents the relationship between timing of first feeder visit and total daily feeder visits
# Var6 represents the relationship between timing of last feeder visit and total daily feeder visits

# Among-individual covariance
c1 <- posterior.cor(mcmc_feeds_V2$VCV[, 1:9])
round(apply(c1, 2, mean), 2)
round(apply(c1, 2, quantile, c(0.025, 0.975)), 2)
# Var2 represents the relationship between timing of first and last feeder visit
# Var3 represents the relationship between timing of first feeder visit and total daily feeder visits
# Var6 represents the relationship between timing of last feeder visit and total daily feeder visits

# Figure 2 ----
# Multipanel figures showing effect of temperature, daylength as well as age:sex differences in each trait.

# Generating predicted values from a new dataframe were Daylength is held constant (at the average) for temperature predictions and Temperature is held constant for daylength predictions. 

# First rerunning the model but scaling the variables before running the model.
master_foraging_plot <- master_foraging_V4
master_foraging_plot$scaled.Temperature <- scale(master_foraging_plot$Temperature)
master_foraging_plot$scaled.Daylength <- scale(master_foraging_plot$Daylength)

mcmc_feeds_plot <- MCMCglmm(cbind(first.feed.centered.m, last.feed.centered.m, total.feeding.events) ~
    trait:AgeSex +
    trait:scaled.Temperature +
    trait:scaled.Daylength - 1,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set PR = FALSE for model checking
  data = as.data.frame(master_foraging_plot)
)


summary(mcmc_feeds_plot)

### Temperature effects
# Generating data frame to make predictions for.
temp_pred_data<- master_foraging_plot  # same as dataframe to make model. 
temp_pred_data2 <- master_foraging_plot[1,] # second dataframe to merge with so that predict with run (not throw an error) but will remove after. Predict will through an error if there is no variation in a given variable.

temp_pred_data$scaled.Daylength <- mean(master_foraging_plot$scaled.Daylength) # set daylength to mean.
temp_pred_data$first.feed.centered.m <- 0 # set response varaibles to 0
temp_pred_data$last.feed.centered.m <- 0
temp_pred_data$total.feeding.events <- 0

temp_pred_data2$first.feed.centered.m <- 0
temp_pred_data2$last.feed.centered.m <- 0
temp_pred_data2$total.feeding.events <- 0

temp_pred_data <- rbind(temp_pred_data, temp_pred_data2) # merge together

temp_prediction <- predict(mcmc_feeds_plot, newdata = temp_pred_data, interval = "confidence") # this is marginalized over all TransponderHexCodes 
temp_prediction_df <- cbind(first.feed.fit = temp_prediction[1:11762], first.feed.lwr = temp_prediction[1:11762, 2], first.feed.upr = temp_prediction[1:11762, 3], last.feed.fit = temp_prediction[11763:23524, 1], last.feed.lwr = temp_prediction[11763:23524, 2], last.feed.upr = temp_prediction[11763:23524, 3], total.feed.fit = temp_prediction[23525:35286, 1], total.feed.lwr = temp_prediction[23525:35286, 2], total.feed.upr = temp_prediction[23525:35286, 3])

temp_prediction_df <- temp_prediction_df[1:11761,] # remove predictions where daylength wasn't held constant
temp_prediction_df <- cbind(master_foraging_plot, temp_prediction_df) # merge with initial data frame so can plot

# First Feed vs. Temperature (Panel A)
Panel_2A <- ggplot(temp_prediction_df, aes(y = first.feed.centered.m , x = Temperature))+geom_point(col = "darkgrey")+theme_classic()+  stat_smooth(aes(y = first.feed.fit), method = "lm", se = FALSE, col = "red") +
  stat_smooth(aes(y = first.feed.upr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") +
  stat_smooth(aes(y = first.feed.lwr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red")+ labs(x = "Temperature (°C)", y = "First feeder visit") + labs(tag = "A") + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2A

# Last Feed vs. Temperature (Panel B)
Panel_2B <- ggplot(temp_prediction_df, aes(y = last.feed.centered.m , x = Temperature))+geom_point(col = "darkgrey")+theme_classic()+  stat_smooth(aes(y = last.feed.fit), method = "lm", se = FALSE, col = "red") +
  stat_smooth(aes(y = last.feed.upr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") +
  stat_smooth(aes(y = last.feed.lwr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") + labs(x = "Temperature (°C)", y = "Last feeder visit") + labs(tag = "B") + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2B

# Total Feeds vs Temperature (Panel C)
Panel_2C <- ggplot(temp_prediction_df, aes(y = total.feeding.events , x = Temperature))+geom_point(col = "darkgrey")+theme_classic()+  stat_smooth(aes(y = total.feed.fit), method = "lm", se = FALSE, col = "red") +
  stat_smooth(aes(y = total.feed.upr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") +
  stat_smooth(aes(y = total.feed.lwr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") + labs(x = "Temperature (°C)", y = "Total daily feeder visits") + labs(tag = "C") + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2C

# Daylength effects 
daylength_pred_data <- master_foraging_plot  # same as dataframe to make model.
daylength_pred_data2 <- master_foraging_plot[1,] # second dataframe to merge with so that predict with run (not throw an error) but will remove after. Predict will through an error if there is no variation in a given variable.

daylength_pred_data$scaled.Temperature <- mean(master_foraging_plot$scaled.Temperature) # set to mean temperature
daylength_pred_data$first.feed.centered.m <- 0 # set response varaible to 0
daylength_pred_data$last.feed.centered.m <- 0
daylength_pred_data$total.feeding.events <- 0

daylength_pred_data2$first.feed.centered.m <- 0
daylength_pred_data2$last.feed.centered.m <- 0
daylength_pred_data2$total.feeding.events <- 0

daylength_pred_data <- rbind(daylength_pred_data, daylength_pred_data2)

daylength_prediction <- predict(mcmc_feeds_plot, newdata = daylength_pred_data, interval = "confidence") # this is marginalized over all TransponderHexCodes 
daylength_prediction_df <- cbind(first.feed.fit = daylength_prediction[1:11762], first.feed.lwr = daylength_prediction[1:11762, 2], first.feed.upr = daylength_prediction[1:11762, 3], last.feed.fit = daylength_prediction[11763:23524, 1], last.feed.lwr = daylength_prediction[11763:23524, 2], last.feed.upr = daylength_prediction[11763:23524, 3], total.feed.fit = daylength_prediction[23525:35286, 1], total.feed.lwr = daylength_prediction[23525:35286, 2], total.feed.upr = daylength_prediction[23525:35286, 3])

daylength_prediction_df <- daylength_prediction_df[1:11761,] # remove predictions where daylength wasn't held constant
daylength_prediction_df <- cbind(master_foraging_plot, daylength_prediction_df)

# First feed vs Daylength (Panel D)
Panel_2D <- ggplot(daylength_prediction_df, aes(y = first.feed.centered.m , x = Daylength))+geom_point(col = "darkgrey")+theme_classic()+  stat_smooth(aes(y =first.feed.fit), method = "lm", se = FALSE, col = "red") +
  stat_smooth(aes(y = first.feed.upr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") +
  stat_smooth(aes(y = first.feed.lwr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") + labs(x = "Daylength (hr)", y = "First feeder visit") + labs(tag = "D") +theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2D

# Last feed vs Daylength (Panel E)
Panel_2E <- ggplot(daylength_prediction_df, aes(y = last.feed.centered.m , x = Daylength))+geom_point(col = "darkgrey")+theme_classic()+  stat_smooth(aes(y = last.feed.fit), method = "lm", se = FALSE, col = "red") +
  stat_smooth(aes(y = last.feed.upr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") +
  stat_smooth(aes(y = last.feed.lwr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") + labs(x = "Daylength (hr)", y = "Last feeder visit") + labs(tag = "E") +theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2E

# Totol feeds vs Daylength (Panel F)
Panel_2F <- ggplot(daylength_prediction_df, aes(y = total.feeding.events , x = Daylength))+geom_point(col = "darkgrey")+theme_classic()+  stat_smooth(aes(y = total.feed.fit), method = "lm", se = FALSE, col = "red") +
  stat_smooth(aes(y = total.feed.upr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") +
  stat_smooth(aes(y = total.feed.lwr), method = "lm", linetype = 2, se = FALSE, linewidth = 0.75, col = "red") + labs(x = "Daylength (hr)", y = "Total daily feeder visits") + labs(tag = "F") + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2F

### Age:Sex differences in each trait 
##### First feeder visit (Panel G)
AgeSexEffects1 <- data.frame(
  Traits = c(
    "JF",
    "AF",
    "JM",
    "AM"
  ),
  Estimate = c(
    mean(mcmc_feeds_V2$Sol[, 7]),
    mean(mcmc_feeds_V2$Sol[, 1]),
    mean(mcmc_feeds_V2$Sol[, 10]),
    mean(mcmc_feeds_V2$Sol[, 4])
  ),
  Lower = c(
    HPDinterval(mcmc_feeds_V2$Sol[, 7])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 1])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 10])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 4])[, "lower"]
  ),
  Upper = c(
    HPDinterval(mcmc_feeds_V2$Sol[, 7])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 1])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 10])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 4])[, "upper"]
  )
)

Panel_2G <- ggplot(AgeSexEffects1, aes(x = Traits, y = Estimate)) +
  geom_pointrange(aes(
    ymin = Lower,
    ymax = Upper
  )) +
  scale_x_discrete(limits = c(
    "JF",
    "AF",
    "JM",
    "AM"
  )) +
  labs(
    x = "Age-Sex Category",
    y = "First feeder visit\n(+/- 95% CrIs)"
  ) +
  labs(tag = "G") + theme_classic() + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
Panel_2G


# Last feeder visit (Panel H)
AgeSexEffects2 <- data.frame(
  Traits = c(
    "JF",
    "AF",
    "JM",
    "AM"
  ),
  Estimate = c(
    mean(mcmc_feeds_V2$Sol[, 8]),
    mean(mcmc_feeds_V2$Sol[, 2]),
    mean(mcmc_feeds_V2$Sol[, 11]),
    mean(mcmc_feeds_V2$Sol[, 5])
  ),
  Lower = c(
    HPDinterval(mcmc_feeds_V2$Sol[, 8])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 2])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 11])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 5])[, "lower"]
  ),
  Upper = c(
    HPDinterval(mcmc_feeds_V2$Sol[, 8])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 2])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 11])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 5])[, "upper"]
  )
)


Panel_2H <- ggplot(AgeSexEffects2, aes(x = Traits, y = Estimate)) +
  geom_pointrange(aes(
    ymin = Lower,
    ymax = Upper
  )) +
  scale_x_discrete(limits = c(
    "JF",
    "AF",
    "JM",
    "AM"
  )) +
  labs(
    x = "Age-Sex Category",
    y = "Last feeder visit\n(+/- 95% CrIs)"
  ) +
  labs(tag = "H") + theme_classic() + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))

# Total daily feeder visits (Panel I)
AgeSexEffects3 <- data.frame(
  Traits = c(
    "JF",
    "AF",
    "JM",
    "AM"
  ),
  Estimate = c(
    mean(mcmc_feeds_V2$Sol[, 9]),
    mean(mcmc_feeds_V2$Sol[, 3]),
    mean(mcmc_feeds_V2$Sol[, 12]),
    mean(mcmc_feeds_V2$Sol[, 6])
  ),
  Lower = c(
    HPDinterval(mcmc_feeds_V2$Sol[, 9])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 3])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 12])[, "lower"],
    HPDinterval(mcmc_feeds_V2$Sol[, 6])[, "lower"]
  ),
  Upper = c(
    HPDinterval(mcmc_feeds_V2$Sol[, 9])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 3])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 12])[, "upper"],
    HPDinterval(mcmc_feeds_V2$Sol[, 6])[, "upper"]
  )
)


Panel_2I <- ggplot(AgeSexEffects3, aes(x = Traits, y = Estimate)) +
  geom_pointrange(aes(
    ymin = Lower,
    ymax = Upper
  )) +
  scale_x_discrete(limits = c(
    "JF",
    "AF",
    "JM",
    "AM"
  )) +
  labs(
    x = "Age-Sex Category",
    y = "Total daily feeder visits\n(+/- 95% CrIs)"
  ) +
  labs(tag = "I") + theme_classic() + theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))


# Merging the panels together to create Figure 2
Fig2 <- ggarrange(Panel_2A, Panel_2B, Panel_2C, Panel_2D, Panel_2E, Panel_2F, Panel_2G, Panel_2H, Panel_2I, nrow = 3, ncol = 3)
Fig2
ggsave(file = "Fig2.jpeg", plot = Fig2, width = 20, height = 15, units = "in", dpi = 300)


### Figure 3 ----
# Within- and among-individual correlation between each trait (first feeder visits, last feeder visits and total daily feeder visits)

# Within-individual correlations (Panel A)
first_last_within_cor <- mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitlast.feed.centered.m.units"] /
  (sqrt(mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.units"]) *
      sqrt(mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.units"]))

first_total_within_cor <- mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traittotal.feeding.events.units"] /
  (sqrt(mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.units"]) *
      sqrt(mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.units"]))

last_total_within_cor <- mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traittotal.feeding.events.units"] /
  (sqrt(mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.units"]) *
      sqrt(mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.units"]))

df_mcmc_within_cors <- data_frame(
  Traits = c(
    "First feeder visit, Last feeder visit",
    "First feeder visit, Total daily feeder visits",
    "Last feeder visit, Total daily feeder visits"
  ),
  Estimate = c(
    mean(first_last_within_cor),
    mean(first_total_within_cor),
    mean(last_total_within_cor)
  ),
  Lower = c(
    HPDinterval(first_last_within_cor)[, "lower"],
    HPDinterval(first_total_within_cor)[, "lower"],
    HPDinterval(last_total_within_cor)[, "lower"]
  ),
  Upper = c(
    HPDinterval(first_last_within_cor)[, "upper"],
    HPDinterval(first_total_within_cor)[, "upper"],
    HPDinterval(last_total_within_cor)[, "upper"]
  )
)

Figure3A <-ggplot(df_mcmc_within_cors, aes(x = Traits, y = Estimate)) +
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
    "Last feeder visit, Total daily feeder visits",
    "First feeder visit, Total daily feeder visits",
    "First feeder visit, Last feeder visit"
  ), labels = c(
    "Last feeder visit,\n Total daily feeder visits",
    "First feeder visit,\n Total daily feeder visits",
    "First feeder visit,\n Last feeder visit")) +
  labs(
    x = NULL,
    y = "Correlation (Estimate +/- 95% CrIs)"
  ) +
  ylim(-0.4, 0.4) +
  coord_flip() +
  theme_classic() +
  theme(
    axis.text.y = element_text(size = 20, colour = "black"),
    axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), text = element_text(size = 20)
  ) +
  labs(tag = "A")

Figure3A

# Among-individual correlations (Panel B)
first_last_among_cor <- mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"] /
  (sqrt(mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.TransponderHexCode"]) *
      sqrt(mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"]))

first_total_among_cor <- mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traittotal.feeding.events.TransponderHexCode"] /
  (sqrt(mcmc_feeds_V2$VCV[, "traitfirst.feed.centered.m:traitfirst.feed.centered.m.TransponderHexCode"]) *
      sqrt(mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.TransponderHexCode"]))

last_total_among_cor <- mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traittotal.feeding.events.TransponderHexCode"] /
  (sqrt(mcmc_feeds_V2$VCV[, "traitlast.feed.centered.m:traitlast.feed.centered.m.TransponderHexCode"]) *
      sqrt(mcmc_feeds_V2$VCV[, "traittotal.feeding.events:traittotal.feeding.events.TransponderHexCode"]))

df_mcmc_among_cors <- data_frame(
  Traits = c(
    "First feeder visit, Last feeder visit",
    "First feeder visit, Total daily feeder visits",
    "Last feeder visit, Total daily feeder visits"
  ),
  Estimate = c(
    mean(first_last_among_cor),
    mean(first_total_among_cor),
    mean(last_total_among_cor)
  ),
  Lower = c(
    HPDinterval(first_last_among_cor)[, "lower"],
    HPDinterval(first_total_among_cor)[, "lower"],
    HPDinterval(last_total_among_cor)[, "lower"]
  ),
  Upper = c(
    HPDinterval(first_last_among_cor)[, "upper"],
    HPDinterval(first_total_among_cor)[, "upper"],
    HPDinterval(last_total_among_cor)[, "upper"]
  )
)

Figure3B <-ggplot(df_mcmc_among_cors, aes(x = Traits, y = Estimate)) +
  geom_pointrange(aes(
    ymin = Lower,
    ymax = Upper
  ), shape = 19, size = 0.7) +
  geom_hline(
    yintercept = 0,
    linetype = "dotted",
    alpha = 0.3
  ) + scale_x_discrete(limits = c(
    "Last feeder visit, Total daily feeder visits",
    "First feeder visit, Total daily feeder visits",
    "First feeder visit, Last feeder visit"), 
    labels = c(
      "Last feeder visit,\n Total daily feeder visits",
      "First feeder visit,\n Total daily feeder visits",
      "First feeder visit,\n Last feeder visit")) +
  labs(
    x = NULL,
    y = "Correlation (Estimate +/- 95% CrIs)"
  ) +
  ylim(-0.7, 0.7) +
  coord_flip() +
  theme_classic() +
  theme(
    axis.text.y = element_text(size = 20, colour = "black"),
    axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), text = element_text(size = 20)
  ) +
  labs(tag = "B")
Figure3B

# Creation of Figure 3
Fig3 <- ggarrange(Figure3A, Figure3B, nrow = 1, ncol = 2)
Fig3
ggsave(file = "Fig3.jpeg", plot = Fig3, width = 20, height = 10, units = "in", dpi = 300)

# Figure S2 ----
# Within- and among- individual correlations using raw centered data and BLUPS

# Within-individual correlation panels for Figure S2 (Panels ABC)
# Firstly, we have to extract averages and standard deviation values for the timing of first feeder visit, last feeder visit, and total daily feeder visits
master_foraging_V4 <- master_foraging_V4 %>%
  group_by(TransponderHexCode) %>%
  mutate(
    mean_first = mean(first.feed.centered),
    mean_last = mean(last.feed.centered),
    mean_total = mean(total.feeding.events),
    sd_first = sd(first.feed.centered),
    sd_last = sd(last.feed.centered),
    sd_total = sd(total.feeding.events)
  )

# Next, we calculate columns with within-individual centered variables by
# subtracting the mean from each observation and then dividing by two standard deviations
master_foraging_V4$c_first <- (master_foraging_V4$first.feed.centered - master_foraging_V4$mean_first) / (2 * master_foraging_V4$sd_first)
master_foraging_V4$c_last <- (master_foraging_V4$last.feed.centered - master_foraging_V4$mean_last) / (2 * master_foraging_V4$sd_last)
master_foraging_V4$c_total <- (master_foraging_V4$total.feeding.events - master_foraging_V4$mean_total) / (2 * master_foraging_V4$sd_total)

# This results in a lot of data at the within-indivdiual level. To remedy
# this, we plot only a subset of the data so the graphs aren't over saturated with points
subset_data <- master_foraging_V4[seq(1, nrow(master_foraging_V4), by = 50), ]
# For each panel we also limited values on the x and y axis to be between 1 and
# -1, which was done to further reduce the noise of the figure and aid interpretability 

# Creation of panel A (First feeder visit vs Last feeder visit)
panel_S2A <- ggplot(subset_data, aes(x = c_first, y = c_last)) +
  geom_point() +
  geom_smooth(method = "lm", col = "blue") +
  theme_classic() +
  xlab("Within-individual\nfirst feeder visit") +
  ylab("Within-individual\nlast feeder visit") +
  xlim(-1, 1) +
  ylim(-1, 1) +
  labs(tag = "A") +
  theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
panel_S2A

# Creation of panel B (First feeder visit vs Total daily feeder visits)
panel_S2B <- ggplot(subset_data, aes(x = c_first, y = c_total)) +
  geom_point() +
  geom_smooth(method = "lm", col = "blue") +
  theme_classic() +
  xlab("Within-individual\nfirst feeder visit") +
  ylab("Within-individual\ntotal daily feeder visits") +
  xlim(-1, 1) +
  ylim(-1, 1) +
  labs(tag = "B") +
  theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
panel_S2B

# Creation of panel C (Last feeder visit vs Total daily feeder visits)
panel_S2C <- ggplot(subset_data, aes(x = c_last, y = c_total)) +
  geom_point() +
  geom_smooth(method = "lm", col = "blue") +
  theme_classic() +
  xlab("Within-individual\nlast feeder visit") +
  ylab("Within-individual\ntotal daily feeder visits") +
  xlim(-1, 1) +
  ylim(-1, 1) +
  labs(tag = "C") +
  theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
panel_S2C

# Among-individual BLUP panels for Figure S2 (Panels DEF)

# Part 1: First feeder visit
First <- select(
  as_tibble(mcmc_feeds_V2$Sol),
  contains("traitfirst.feed.centered.m.TransponderHexCode")
)

First_long <-
  First %>%
  pivot_longer(
    everything(),
    names_to = c("traitfirst.feed.centered.m.TransponderHexCode.")
  )
First_long <- tibble(First_long)

First_long$TransponderHexCode <- str_remove(First_long$traitfirst.feed.centered.m.TransponderHexCode., "traitfirst.feed.centered.m.TransponderHexCode.")
First_long$Firstblup <- First_long$value

df1 <- First_long %>%
  group_by(TransponderHexCode) %>%
  summarise(
    First_l = quantile(Firstblup, 0.05),
    First_mean = mean(Firstblup),
    First_u = quantile(Firstblup, 0.95)
  )

# Part 2: Last feeder visit

Last <- select(
  as_tibble(mcmc_feeds_V2$Sol),
  contains("traitlast.feed.centered.m.TransponderHexCode")
)

Last_long <-
  Last %>%
  pivot_longer(
    everything(),
    names_to = c("traitlast.feed.centered.m.TransponderHexCode.")
  )
Last_long <- tibble(Last_long)

Last_long$TransponderHexCode <- str_remove(Last_long$traitlast.feed.centered.m.TransponderHexCode., "traitlast.feed.centered.m.TransponderHexCode.")
Last_long$Lastblup <- Last_long$value

df2 <- Last_long %>%
  group_by(TransponderHexCode) %>%
  summarise(
    Last_l = quantile(Lastblup, 0.05),
    Last_mean = mean(Lastblup),
    Last_u = quantile(Lastblup, 0.95)
  )

# Part 3: Total daily feeder visits

Total <- select(
  as_tibble(mcmc_feeds_V2$Sol),
  contains("traittotal.feeding.events.TransponderHexCode")
)

Total_long <-
  Total %>%
  pivot_longer(
    everything(),
    names_to = c("traittotal.feeding.events.TransponderHexCode.")
  )
Total_long <- tibble(Total_long)

Total_long$TransponderHexCode <- str_remove(Total_long$traittotal.feeding.events.TransponderHexCode., "traittotal.feeding.events.TransponderHexCode.")
Total_long$Totalblup <- Total_long$value

df3 <- Total_long %>%
  group_by(TransponderHexCode) %>%
  summarise(
    Total_l = quantile(Totalblup, 0.05),
    Total_mean = mean(Totalblup),
    Total_u = quantile(Totalblup, 0.95)
  )

# Step 4: Group together first feeder visit, last feeder visit, and total daily feeder visits for graphing

plotdf1 <- merge(df1, df2, by = "TransponderHexCode")
plotdf1_AS <- merge(plotdf1, master_foraging_V4, by = "TransponderHexCode")

plotdf2 <- merge(df2, df3, by = "TransponderHexCode")
plotdf2_AS <- merge(plotdf2, master_foraging_V4, by = "TransponderHexCode")

plotdf3 <- merge(df1, df3, by = "TransponderHexCode")
plotdf3_AS <- merge(plotdf3, master_foraging_V4, by = "TransponderHexCode")

# Average total daily feeder visits
average_feeds_ID <- master_foraging_V4 %>%
  group_by(TransponderHexCode) %>%
  summarize(total_feeds = sum(total.feeding.events))
average_feeds_ID <- average_feeds_ID %>%
  mutate(average_feeds_per_observation = total_feeds / n())

# First feeder visit averages
average_first_ID <- master_foraging_V4 %>%
  group_by(TransponderHexCode) %>%
  summarize(total_first = sum(first.feed.centered.m))
average_first_ID <- average_first_ID %>%
  mutate(average_first_feed = total_first / n())

# Last feeder visit averages
average_last_ID <- master_foraging_V4 %>%
  group_by(TransponderHexCode) %>%
  summarize(total_last = sum(last.feed.centered.m))
average_last_ID <- average_last_ID %>%
  mutate(average_last_feed = total_last / n())

# Step 5 - making the panels
# Creation of panel D (First feeder visit  vs Last daily feeder visit)
panel_S2D <- ggplot(plotdf1_AS, aes(x = First_mean, y = Last_mean)) +
  geom_point() +
  theme_classic() +
  geom_errorbar(aes(ymin = Last_l, ymax = Last_u)) +
  geom_errorbar(aes(xmin = First_l, xmax = First_u)) +
  xlab("First feeder visit\n(BLUP +/- 95% CrI)") +
  ylab("Total feeder visits\n(BLUP +/- 95% CrI)") +
  labs(tag = "D") +
  theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
panel_S2D

# Creation of panel E (First feeder visit vs Total daily feeder visits)
panel_S2E <- ggplot(plotdf3_AS, aes(x = First_mean, y = Total_mean)) +
  geom_point() +
  theme_classic() +
  geom_errorbar(aes(ymin = Total_l, ymax = Total_u)) +
  geom_errorbar(aes(xmin = First_l, xmax = First_u)) +
  xlab("First feeder visit\n(BLUP +/- 95% CrI)") +
  ylab("Total daily feeder visits\n(BLUP +/- 95% CrI)") +
  labs(tag = "E") +
  theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
panel_S2E

# Creation of panel F (Last feeder visit vs Total daily feeder visits)
panel_S2F <- ggplot(plotdf2_AS, aes(x = Last_mean, y = Total_mean)) +
  geom_point() +
  theme_classic() +
  geom_errorbar(aes(ymin = Total_l, ymax = Total_u)) +
  geom_errorbar(aes(xmin = Last_l, xmax = Last_u)) +
  xlab("Last feeder visit\n(BLUP +/- 95% CrI)") +
  ylab("Total daily feeder visits\n(BLUP +/- 95% CrI)") +
  labs(tag = "F") +
  theme(axis.title.x = element_text(size = 20), axis.text.x = element_text(size = 20), axis.text.y = element_text(size = 20), axis.title.y = element_text(size = 20), text = element_text(size = 20))
panel_S2F
# ggsave(file = "Panel_S2F.jpeg", plot = panel_S2F, width = 15, height = 15, units = "in", dpi = 300)

# Creation of Figure S2
FigS2 <- ggarrange(panel_S2A, panel_S2D, panel_S2B, panel_S2E, panel_S2C, panel_S2F, ncol = 2, nrow = 3)
ggsave(file = "FigS2.jpeg", plot = FigS2, width = 15, height = 15, units = "in", dpi = 300)
FigS2

# Post-hoc. Partitioning MCMCglmm outputs by age-sex class ----
# Results of the MCMCglmm and covariances were separated by age-sex class to see
# if there were any major differences from the global estimates

# Pt1. Adult males 
# First, we subset master_foraging_V4 so that it only consists of adult males:
master_foraging_V6 <- master_foraging_V4 %>%
  filter(AgeSex %in% c("A Male"))
# Checking the N value for methodological data:
n_distinct(master_foraging_V6$TransponderHexCode)

# Secondly, we conduct a new MCMCglmm model with the subset data
mcmc_feeds_V3 <- MCMCglmm(
  cbind(first.feed.centered, last.feed.centered, total.feeding.events) ~ trait - 1 +
    trait:scale(Temperature) +
    trait:scale(Daylength),
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set pr = FALSE when model checking
  data = as.data.frame(master_foraging_V6)
)

# Model checking 
plot(mcmc_feeds_V3)

# Now we check covariances using the new model
# Within-individuals:
cw2 <- posterior.cor(mcmc_feeds_V3$VCV[, 10:18])
round(apply(cw2, 2, mean), 2)
round(apply(cw2, 2, quantile, c(0.025, 0.975)), 2)

# Among-individuals:
c2 <- posterior.cor(mcmc_feeds_V3$VCV[, 1:9])
round(apply(c2, 2, mean), 2)
round(apply(c2, 2, quantile, c(0.025, 0.975)), 2)

# This same process is used for each age-sex class
# Pt2: Juvenile males
# Subset
master_foraging_V7 <- master_foraging_V4 %>%
  filter(AgeSex %in% c("J Male"))
# Check N value
n_distinct(master_foraging_V7$TransponderHexCode)

# Redo MCMCglmm with subset data
mcmc_feeds_V4 <- MCMCglmm(
  cbind(first.feed.centered, last.feed.centered, total.feeding.events) ~ trait - 1 +
    trait:scale(Temperature) +
    trait:scale(Daylength),
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set pr = FALSE when model checking
  data = as.data.frame(master_foraging_V7)
)

# Model checking 
plot(mcmc_feeds_V4)

# Within-individuals
cw3 <- posterior.cor(mcmc_feeds_V4$VCV[, 10:18])
round(apply(cw3, 2, mean), 2)
round(apply(cw3, 2, quantile, c(0.025, 0.975)), 2)

# Among-individuals
c3 <- posterior.cor(mcmc_feeds_V4$VCV[, 1:9])
round(apply(c3, 2, mean), 2)
round(apply(c3, 2, quantile, c(0.025, 0.975)), 2)

# Pt3: Adult females
# Subset
master_foraging_V8 <- master_foraging_V4 %>%
  filter(AgeSex %in% c("A Female"))
# Check N value
n_distinct(master_foraging_V8$TransponderHexCode)

# Run subset model
mcmc_feeds_V5 <- MCMCglmm(
  cbind(first.feed.centered, last.feed.centered, total.feeding.events) ~ trait - 1 +
    trait:scale(Temperature) +
    trait:scale(Daylength),
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set pr = FALSE when model checking
  data = as.data.frame(master_foraging_V8)
)

# Model checking 
plot(mcmc_feeds_V5)

# Within-individuals
cw4 <- posterior.cor(mcmc_feeds_V5$VCV[, 10:18])
round(apply(cw4, 2, mean), 2)
round(apply(cw4, 2, quantile, c(0.025, 0.975)), 2)

# Among-individuals
c4 <- posterior.cor(mcmc_feeds_V5$VCV[, 1:9])
round(apply(c4, 2, mean), 2)
round(apply(c4, 2, quantile, c(0.025, 0.975)), 2)

# Pt4: Juvenile females
# Subset
master_foraging_V9 <- master_foraging_V4 %>%
  filter(AgeSex %in% c("J Female"))
# Check N value
n_distinct(master_foraging_V9$TransponderHexCode)

# Run subset model
mcmc_feeds_V6 <- MCMCglmm(
  cbind(first.feed.centered, last.feed.centered, total.feeding.events) ~ trait - 1 +
    trait:scale(Temperature) +
    trait:scale(Daylength),
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set pr = FALSE when model checking
  data = as.data.frame(master_foraging_V9)
)

# Model checking 
plot(mcmc_feeds_V6)

# Within-individuals
cw5 <- posterior.cor(mcmc_feeds_V6$VCV[, 10:18])
round(apply(cw5, 2, mean), 2)
round(apply(cw5, 2, quantile, c(0.025, 0.975)), 2)

# Among-individuals
c5 <- posterior.cor(mcmc_feeds_V6$VCV[, 1:9])
round(apply(c5, 2, mean), 2)
round(apply(c5, 2, quantile, c(0.025, 0.975)), 2)


# Checking outlier removal----
# Posthoc decided to remove an outlier to see if it changed global results
# Step 1. Subset out outlier
master_foraging_V5 <- subset(master_foraging_V4, TransponderHexCode != "01103F692D")

# Step 2. Run subset model
mcmc_feeds_V7 <- MCMCglmm(
  cbind(first.feed.centered.m, last.feed.centered.m, total.feeding.events) ~
    trait:AgeSex +
    trait:scale(Temperature) +
    trait:scale(Daylength) - 1,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian", "gaussian"),
  prior = prior_feeds_V1,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set pr = FALSE for model checking
  data = as.data.frame(master_foraging_V5)
)

# Model checking 
plot(mcmc_feeds_V7)

# Check results
MCMCran_Out <- mcmc_feeds_V7$VCV
posterior.mode(as.mcmc(MCMCran_Out))
HPDinterval(as.mcmc(MCMCran_Out))

MCMCfix_Out <- mcmc_feeds_V7$Sol
posterior.mode((MCMCfix_Out))
HPDinterval(MCMCfix_Out)
# Within-individuals
cw6 <- posterior.cor(mcmc_feeds_V7$VCV[, 10:18])
round(apply(cw6, 2, mean), 2)
round(apply(cw6, 2, quantile, c(0.025, 0.975)), 2)

# Among-individuals
c6 <- posterior.cor(mcmc_feeds_V7$VCV[, 1:9])
round(apply(c6, 2, mean), 2)
round(apply(c6, 2, quantile, c(0.025, 0.975)), 2)



##post-hoc analysis based on referee comments----
##longer foraging window (both within- and among-individuals) is associated with higher total daily feeder visits. Is there a change in foraging rate?

master_foraging_V4$window<-(master_foraging_V4$last.feed.continuous-master_foraging_V4$first.feed.continuous)/3600  #calculates total feeder use window in hours
master_foraging_V4$rate<-master_foraging_V4$total.feeding.events/master_foraging_V4$window  #calculates feeds/hour
hist(master_foraging_V4$window)
hist(master_foraging_V4$rate)

##prior for 2 trait model
prior_2trait <- list(
  R = list(V = diag(2), nu = 0.002),
  G = list(G1 = list(
    V = diag(2), nu = 10,
    alpha.mu = rep(0, 2),
    alpha.V = diag(25^2, 2, 2)
  ))
)

##post-hoc test for relationship between feeding rate (feeds/unit time) and feeding window (total time using feeder per day)
mcmc_posthoc_test <- MCMCglmm(
  cbind(window, rate) ~
    trait:AgeSex +
    trait:scale(Temperature) +
    trait:scale(Daylength) - 1,
  random = ~ us(trait):TransponderHexCode,
  rcov = ~ us(trait):units,
  family = c("gaussian", "gaussian"),
  prior = prior_2trait,
  nitt = 300000,
  burnin = 20000,
  thin = 70,
  verbose = TRUE, pr = TRUE, # Set pr = FALSE for model checking
  data = as.data.frame(master_foraging_V4)
)

summary(mcmc_posthoc_test)
plot(mcmc_posthoc_test)


# Within-individuals
c_a <- posterior.cor(mcmc_posthoc_test$VCV[, 1:4])
round(apply(c_a, 2, mean), 2)
round(apply(c_a, 2, quantile, c(0.025, 0.975)), 2)

# Among-individuals
c_w <- posterior.cor(mcmc_posthoc_test$VCV[, 5:8])
round(apply(c_w, 2, mean), 2)
round(apply(c_w, 2, quantile, c(0.025, 0.975)), 2)


repeatability_window<-mcmc_posthoc_test$VCV[,1]/(mcmc_posthoc_test$VCV[,1]+mcmc_posthoc_test$VCV[,5])
posterior.mode(repeatability_window)
HPDinterval(repeatability_window)

repeatability_rate<-mcmc_posthoc_test$VCV[,4]/(mcmc_posthoc_test$VCV[,4]+mcmc_posthoc_test$VCV[,8])
posterior.mode(repeatability_rate)
HPDinterval(repeatability_rate)
