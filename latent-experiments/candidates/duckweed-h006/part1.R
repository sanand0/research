### Title of accompanying manuscript: Caloric restriction extends lifespan in a clonal plant
### Authors: Suzanne L. Chmilar, Amanda C. Luzardo, Priyanka Dutt, Abbe Pawluk, Victoria C. Thwaites, and Robert A. Laird
### Journal: Ecology Letters
### Contents: Experiment 1 and ancillary experiment (supporting information) R Scripts for data analysis and figures



##### PART I. LOAD PACKAGES AND SET WORKING DIRECTORY #####



##### 1.   Load packages #####

library(emmeans)
library(multcomp)
library(multcompView)
library(devEMF)



##### 2.   Set working directory #####

# Set working directory 
setwd('c:/RFiles/Lemna_Caloric_Restriction')



##### PART II. DATA ANALYSIS: TEMPERATURE #####



##### 3.   Load temperature data and perform preliminary processing #####

# Load temperature data
temp <- read.csv('CR_temperature.csv', header = T)

# Change light treatment names to be less cryptic 
temp$treatment[temp$treatment == "L1"] <- "1"
temp$treatment[temp$treatment == "L2"] <- "1/2"
temp$treatment[temp$treatment == "L4"] <- "1/4"
temp$treatment[temp$treatment == "L8"] <- "1/8"
temp$treatment[temp$treatment == "L16"] <- "1/16"
temp$treatment[temp$treatment == "L32"] <- "1/32"
temp$treatment[temp$treatment == "L0"] <- "0"
temp$treatment <- factor(temp$treatment, c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0"))



##### 4.   Analyze temperature #####

# Get max and min temperature
max.temp <- max(temp$temperature) # 29.6
min.temp <- min(temp$temperature) # 22.5

# Get temperature data for each treatment-by-shelf combination
temp.L00.S2 <- temp[temp$treatment == "0"    & temp$shelf == "S2", ]$temperature
temp.L32.S2 <- temp[temp$treatment == "1/32" & temp$shelf == "S2", ]$temperature
temp.L16.S2 <- temp[temp$treatment == "1/16" & temp$shelf == "S2", ]$temperature
temp.L08.S2 <- temp[temp$treatment == "1/8"  & temp$shelf == "S2", ]$temperature
temp.L04.S2 <- temp[temp$treatment == "1/4"  & temp$shelf == "S2", ]$temperature
temp.L02.S2 <- temp[temp$treatment == "1/2"  & temp$shelf == "S2", ]$temperature
temp.L01.S2 <- temp[temp$treatment == "1"    & temp$shelf == "S2", ]$temperature
temp.L00.S4 <- temp[temp$treatment == "0"    & temp$shelf == "S4", ]$temperature
temp.L32.S4 <- temp[temp$treatment == "1/32" & temp$shelf == "S4", ]$temperature
temp.L16.S4 <- temp[temp$treatment == "1/16" & temp$shelf == "S4", ]$temperature
temp.L08.S4 <- temp[temp$treatment == "1/8"  & temp$shelf == "S4", ]$temperature
temp.L04.S4 <- temp[temp$treatment == "1/4"  & temp$shelf == "S4", ]$temperature
temp.L02.S4 <- temp[temp$treatment == "1/2"  & temp$shelf == "S4", ]$temperature
temp.L01.S4 <- temp[temp$treatment == "1"    & temp$shelf == "S4", ]$temperature

# Get mean temperatures
temp.mean <- c(mean(temp.L01.S2),
               mean(temp.L02.S2),
               mean(temp.L04.S2),
               mean(temp.L08.S2),
               mean(temp.L16.S2),
               mean(temp.L32.S2),
               mean(temp.L00.S2),
               mean(temp.L01.S4),
               mean(temp.L02.S4),
               mean(temp.L04.S4),
               mean(temp.L08.S4),
               mean(temp.L16.S4),
               mean(temp.L32.S4),
               mean(temp.L00.S4))

# Get SEM of temperatures
temp.sem  <- c(sd(temp.L01.S2)/sqrt(length(temp.L01.S2)),
               sd(temp.L02.S2)/sqrt(length(temp.L02.S2)),
               sd(temp.L04.S2)/sqrt(length(temp.L04.S2)),
               sd(temp.L08.S2)/sqrt(length(temp.L08.S2)),
               sd(temp.L16.S2)/sqrt(length(temp.L16.S2)),
               sd(temp.L32.S2)/sqrt(length(temp.L32.S2)),
               sd(temp.L00.S2)/sqrt(length(temp.L00.S2)),
               sd(temp.L01.S4)/sqrt(length(temp.L01.S4)),
               sd(temp.L02.S4)/sqrt(length(temp.L02.S4)),
               sd(temp.L04.S4)/sqrt(length(temp.L04.S4)),
               sd(temp.L08.S4)/sqrt(length(temp.L08.S4)),
               sd(temp.L16.S4)/sqrt(length(temp.L16.S4)),
               sd(temp.L32.S4)/sqrt(length(temp.L32.S4)),
               sd(temp.L00.S4)/sqrt(length(temp.L00.S4)))

# Visually inspect interaction plot of temperature means
plot(temp.mean[1:7], 
     xaxt = "n", 
     xlab = "Light intensity treatment", 
     ylab = "Mean temperature ± SEM (\u00B0C)",
     ylim = c(23, 29), 
     las = 1,
     cex = 1.25,
     pch = 16)
lines(temp.mean[1:7])
a.size <- 0.05
arrows(1, temp.mean[1]  + temp.sem[1],  1, temp.mean[1]  - temp.sem[1],  angle = 90, length = a.size, code = 3)
arrows(2, temp.mean[2]  + temp.sem[2],  2, temp.mean[2]  - temp.sem[2],  angle = 90, length = a.size, code = 3)
arrows(3, temp.mean[3]  + temp.sem[3],  3, temp.mean[3]  - temp.sem[3],  angle = 90, length = a.size, code = 3)
arrows(4, temp.mean[4]  + temp.sem[4],  4, temp.mean[4]  - temp.sem[4],  angle = 90, length = a.size, code = 3)
arrows(5, temp.mean[5]  + temp.sem[5],  5, temp.mean[5]  - temp.sem[5],  angle = 90, length = a.size, code = 3)
arrows(6, temp.mean[6]  + temp.sem[6],  6, temp.mean[6]  - temp.sem[6],  angle = 90, length = a.size, code = 3)
arrows(7, temp.mean[7]  + temp.sem[7],  7, temp.mean[7]  - temp.sem[7],  angle = 90, length = a.size, code = 3)
arrows(1, temp.mean[8]  + temp.sem[8],  1, temp.mean[8]  - temp.sem[8],  angle = 90, length = a.size, code = 3)
arrows(2, temp.mean[9]  + temp.sem[9],  2, temp.mean[9]  - temp.sem[9],  angle = 90, length = a.size, code = 3)
arrows(3, temp.mean[10] + temp.sem[10], 3, temp.mean[10] - temp.sem[10], angle = 90, length = a.size, code = 3)
arrows(4, temp.mean[11] + temp.sem[11], 4, temp.mean[11] - temp.sem[11], angle = 90, length = a.size, code = 3)
arrows(5, temp.mean[12] + temp.sem[12], 5, temp.mean[12] - temp.sem[12], angle = 90, length = a.size, code = 3)
arrows(6, temp.mean[13] + temp.sem[13], 6, temp.mean[13] - temp.sem[13], angle = 90, length = a.size, code = 3)
arrows(7, temp.mean[14] + temp.sem[14], 7, temp.mean[14] - temp.sem[14], angle = 90, length = a.size, code = 3)
lines(temp.mean[8:14])
points(temp.mean[8:14], cex = 1.25, pch = 21, bg = "white")
treat <- c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0")
axis(1, at = 1:7, labels = treat)
legend("topleft", c("top", "bottom"), title = "Shelf", bty = 'n',  
       pch = c(16, 21), pt.cex = 1.25, lty = FALSE, inset = 0.05)

# Two-way ANOVA on temperature data
temp.aov <- aov(temperature ~ treatment*shelf, dat = temp)
anova(temp.aov)

# Analysis of Variance Table
#
# Response: temperature
#                 Df  Sum Sq Mean Sq F value    Pr(>F)    
# treatment        6  42.165   7.027  3.1774  0.009384 ** 
# shelf            1  59.248  59.248 26.7883 3.181e-06 ***
# treatment:shelf  6  10.114   1.686  0.7622  0.602685    
# Residuals       56 123.856   2.212   
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = temp.aov$fitted.values, y = temp.aov$residuals)
hist(temp.aov$residuals)
qqnorm(temp.aov$residuals)

# Tukey HSD test
TukeyHSD(temp.aov, "treatment")

# Tukey multiple comparisons of means
# 95% family-wise confidence level
#
# Fit: aov(formula = temperature ~ treatment * shelf, data = temp)
#
# $treatment
#            diff        lwr        upr     p adj
# 1/2-1     -0.05 -2.0838462  1.9838462 1.0000000
# 1/4-1      0.55 -1.4838462  2.5838462 0.9810839
# 1/8-1      0.11 -1.9238462  2.1438462 0.9999981
# 1/16-1     0.99 -1.0438462  3.0238462 0.7503007
# 1/32-1     1.24 -0.7938462  3.2738462 0.5117803
# 0-1       -1.31 -3.3438462  0.7238462 0.4449181
# 1/4-1/2    0.60 -1.4338462  2.6338462 0.9707416
# 1/8-1/2    0.16 -1.8738462  2.1938462 0.9999824
# 1/16-1/2   1.04 -0.9938462  3.0738462 0.7053456
# 1/32-1/2   1.29 -0.7438462  3.3238462 0.4637449
# 0-1/2     -1.26 -3.2938462  0.7738462 0.4924245
# 1/8-1/4   -0.44 -2.4738462  1.5938462 0.9941473
# 1/16-1/4   0.44 -1.5938462  2.4738462 0.9941473
# 1/32-1/4   0.69 -1.3438462  2.7238462 0.9429135
# 0-1/4     -1.86 -3.8938462  0.1738462 0.0942309
# 1/16-1/8   0.88 -1.1538462  2.9138462 0.8382316
# 1/32-1/8   1.13 -0.9038462  3.1638462 0.6195298
# 0-1/8     -1.42 -3.4538462  0.6138462 0.3471450
# 1/32-1/16  0.25 -1.7838462  2.2838462 0.9997583
# 0-1/16    -2.30 -4.3338462 -0.2661538 0.0170491
# 0-1/32    -2.55 -4.5838462 -0.5161538 0.0056264

# Note that both contrasts for which p < 0.05 involve the '0' treatment

# Omit '0' treatment and repeat
temp2 <- temp[temp$treatment != '0', ]

# Two-way ANOVA on temperature data ('0' treatment omitted)
temp2.aov <- aov(temperature ~ treatment*shelf, dat = temp2)
anova(temp2.aov)

# Analysis of Variance Table
#
# Response: temperature
#                 Df  Sum Sq Mean Sq F value    Pr(>F)    
# treatment        5  14.905   2.981  1.1990    0.3239    
# shelf            1  62.424  62.424 25.1077 7.772e-06 ***
# treatment:shelf  5   5.914   1.183  0.4757    0.7925    
# Residuals       48 119.340   2.486                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = temp2.aov$fitted.values, y = temp2.aov$residuals)
hist(temp2.aov$residuals)
qqnorm(temp2.aov$residuals)



##### PART III. DATA ANALYSIS: LIGHT INTENSITY #####



##### 5.   Load light intensity data, and perform preliminary processing #####

# Load temperature data
light <- read.csv('CR_PAR.csv', header = T)

# Change light treatment names to be less cryptic 
light$treatment[light$treatment == "L01"] <- "1"
light$treatment[light$treatment == "L02"] <- "1/2"
light$treatment[light$treatment == "L04"] <- "1/4"
light$treatment[light$treatment == "L08"] <- "1/8"
light$treatment[light$treatment == "L16"] <- "1/16"
light$treatment[light$treatment == "L32"] <- "1/32"
light$treatment[light$treatment == "L00"] <- "0"
light$treatment <- factor(light$treatment, c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0"))



##### 6.   Analyze light intensity #####

# Get max and min PAR
max.PAR <- max(light$PAR) # 362.5
min.PAR <- min(light$PAR) # 2

# Get mean PARs (by treatment alone)
mean(light$PAR[light$treatment == "1"])    # 339.83 umol/m2/s
mean(light$PAR[light$treatment == "1/2"])  # 174.96 umol/m2/s
mean(light$PAR[light$treatment == "1/4"])  #  81.6  umol/m2/s
mean(light$PAR[light$treatment == "1/8"])  #  39.23 umol/m2/s
mean(light$PAR[light$treatment == "1/16"]) #  24.7  umol/m2/s
mean(light$PAR[light$treatment == "1/32"]) #  12.36 umol/m2/s
mean(light$PAR[light$treatment == "0"])    #   4.02 umol/m2/s

# Get PAR data for each treatment-by-shelf combination
PAR.L00.S2 <- light[light$treatment == "0"    & light$shelf == "S2", ]$PAR
PAR.L32.S2 <- light[light$treatment == "1/32" & light$shelf == "S2", ]$PAR
PAR.L16.S2 <- light[light$treatment == "1/16" & light$shelf == "S2", ]$PAR
PAR.L08.S2 <- light[light$treatment == "1/8"  & light$shelf == "S2", ]$PAR
PAR.L04.S2 <- light[light$treatment == "1/4"  & light$shelf == "S2", ]$PAR
PAR.L02.S2 <- light[light$treatment == "1/2"  & light$shelf == "S2", ]$PAR
PAR.L01.S2 <- light[light$treatment == "1"    & light$shelf == "S2", ]$PAR
PAR.L00.S4 <- light[light$treatment == "0"    & light$shelf == "S4", ]$PAR
PAR.L32.S4 <- light[light$treatment == "1/32" & light$shelf == "S4", ]$PAR
PAR.L16.S4 <- light[light$treatment == "1/16" & light$shelf == "S4", ]$PAR
PAR.L08.S4 <- light[light$treatment == "1/8"  & light$shelf == "S4", ]$PAR
PAR.L04.S4 <- light[light$treatment == "1/4"  & light$shelf == "S4", ]$PAR
PAR.L02.S4 <- light[light$treatment == "1/2"  & light$shelf == "S4", ]$PAR
PAR.L01.S4 <- light[light$treatment == "1"    & light$shelf == "S4", ]$PAR

# Get mean PARs (by treatment and shelf)
PAR.mean <- c(mean(PAR.L01.S2),
              mean(PAR.L02.S2),
              mean(PAR.L04.S2),
              mean(PAR.L08.S2),
              mean(PAR.L16.S2),
              mean(PAR.L32.S2),
              mean(PAR.L00.S2),
              mean(PAR.L01.S4),
              mean(PAR.L02.S4),
              mean(PAR.L04.S4),
              mean(PAR.L08.S4),
              mean(PAR.L16.S4),
              mean(PAR.L32.S4),
              mean(PAR.L00.S4))

# Get SEM of PARs (by treatment and shelf)
PAR.sem  <- c(sd(PAR.L01.S2)/sqrt(length(PAR.L01.S2)),
              sd(PAR.L02.S2)/sqrt(length(PAR.L02.S2)),
              sd(PAR.L04.S2)/sqrt(length(PAR.L04.S2)),
              sd(PAR.L08.S2)/sqrt(length(PAR.L08.S2)),
              sd(PAR.L16.S2)/sqrt(length(PAR.L16.S2)),
              sd(PAR.L32.S2)/sqrt(length(PAR.L32.S2)),
              sd(PAR.L00.S2)/sqrt(length(PAR.L00.S2)),
              sd(PAR.L01.S4)/sqrt(length(PAR.L01.S4)),
              sd(PAR.L02.S4)/sqrt(length(PAR.L02.S4)),
              sd(PAR.L04.S4)/sqrt(length(PAR.L04.S4)),
              sd(PAR.L08.S4)/sqrt(length(PAR.L08.S4)),
              sd(PAR.L16.S4)/sqrt(length(PAR.L16.S4)),
              sd(PAR.L32.S4)/sqrt(length(PAR.L32.S4)),
              sd(PAR.L00.S4)/sqrt(length(PAR.L00.S4)))

# Visually inspect interaction plot of PAR means
plot(PAR.mean[1:7],
     xaxt = "n", 
     xlab = "Light intensity treatment", 
     ylab = expression(paste("Mean PAR (", mu, "mol m"^"-2", " s"^"-1",")")),
     ylim = c(0, 350), 
     las = 1,
     cex = 1.25,
     pch = 16)
lines(PAR.mean[1:7])
a.size <- 0.05
arrows(1, PAR.mean[1]  + PAR.sem[1],  1, PAR.mean[1]  - PAR.sem[1],  angle = 90, length = a.size, code = 3)
arrows(2, PAR.mean[2]  + PAR.sem[2],  2, PAR.mean[2]  - PAR.sem[2],  angle = 90, length = a.size, code = 3)
arrows(3, PAR.mean[3]  + PAR.sem[3],  3, PAR.mean[3]  - PAR.sem[3],  angle = 90, length = a.size, code = 3)
arrows(4, PAR.mean[4]  + PAR.sem[4],  4, PAR.mean[4]  - PAR.sem[4],  angle = 90, length = a.size, code = 3)
arrows(5, PAR.mean[5]  + PAR.sem[5],  5, PAR.mean[5]  - PAR.sem[5],  angle = 90, length = a.size, code = 3)
arrows(6, PAR.mean[6]  + PAR.sem[6],  6, PAR.mean[6]  - PAR.sem[6],  angle = 90, length = a.size, code = 3)
arrows(7, PAR.mean[7]  + PAR.sem[7],  7, PAR.mean[7]  - PAR.sem[7],  angle = 90, length = a.size, code = 3)
arrows(1, PAR.mean[8]  + PAR.sem[8],  1, PAR.mean[8]  - PAR.sem[8],  angle = 90, length = a.size, code = 3)
arrows(2, PAR.mean[9]  + PAR.sem[9],  2, PAR.mean[9]  - PAR.sem[9],  angle = 90, length = a.size, code = 3)
arrows(3, PAR.mean[10] + PAR.sem[10], 3, PAR.mean[10] - PAR.sem[10], angle = 90, length = a.size, code = 3)
arrows(4, PAR.mean[11] + PAR.sem[11], 4, PAR.mean[11] - PAR.sem[11], angle = 90, length = a.size, code = 3)
arrows(5, PAR.mean[12] + PAR.sem[12], 5, PAR.mean[12] - PAR.sem[12], angle = 90, length = a.size, code = 3)
arrows(6, PAR.mean[13] + PAR.sem[13], 6, PAR.mean[13] - PAR.sem[13], angle = 90, length = a.size, code = 3)
arrows(7, PAR.mean[14] + PAR.sem[14], 7, PAR.mean[14] - PAR.sem[14], angle = 90, length = a.size, code = 3)
lines(PAR.mean[8:14])
points(PAR.mean[8:14], cex = 1.25, pch = 21, bg = "white")
treat <- c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0")
axis(1, at = 1:7, labels = treat)
legend("topright", c("top", "bottom"), title = "Shelf", bty = 'n',  
       pch = c(16, 21), pt.cex = 1.25, lty = FALSE, inset = 0.05)

# Two-way ANOVA on PAR data
PAR.aov <- aov(PAR ~ treatment*shelf, dat = light)
anova(PAR.aov)

# Analysis of Variance Table
#
# Response: PAR
#                 Df Sum Sq Mean Sq   F value  Pr(>F)    
# treatment        6 896520  149420 2834.4479 < 2e-16 ***
# shelf            1    283     283    5.3678 0.02419 *  
# treatment:shelf  6    624     104    1.9718 0.08516 .  
# Residuals       56   2952      53                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = PAR.aov$fitted.values, y = PAR.aov$residuals) # heteroscedastic
hist(PAR.aov$residuals)
qqnorm(PAR.aov$residuals)

# Two-way ANOVA on log10-transformed PAR data
light$log10PAR <- log10(light$PAR)
PAR.log10.aov <- aov(log10PAR ~ treatment*shelf, dat = light)
anova(PAR.log10.aov)

# Analysis of Variance Table
#
# Response: log10PAR
#                 Df  Sum Sq Mean Sq   F value    Pr(>F)    
# treatment        6 27.2484  4.5414 1387.6697 < 2.2e-16 ***
# shelf            1  0.0065  0.0065    1.9986     0.163    
# treatment:shelf  6  0.1525  0.0254    7.7680 4.218e-06 ***
# Residuals       56  0.1833  0.0033                        
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = PAR.log10.aov$fitted.values, y = PAR.log10.aov$residuals) # much less (but still somewhat) heteroscedastic 
hist(PAR.log10.aov$residuals)
qqnorm(PAR.log10.aov$residuals) # much better qqnorm plot

# Tukey HSD test
TukeyHSD(PAR.log10.aov, "treatment")

# Tukey multiple comparisons of means
# 95% family-wise confidence level
#
#Fit: aov(formula = log10PAR ~ treatment * shelf, data = light)
#
# $treatment
#                 diff        lwr        upr p adj
# 1/2-1     -0.2881057 -0.3663415 -0.2098699     0
# 1/4-1     -0.6207300 -0.6989658 -0.5424942     0
# 1/8-1     -0.9394818 -1.0177176 -0.8612460     0
# 1/16-1    -1.1406384 -1.2188742 -1.0624026     0
# 1/32-1    -1.4437077 -1.5219435 -1.3654719     0
# 0-1       -1.9528032 -2.0310390 -1.8745674     0
# 1/4-1/2   -0.3326242 -0.4108600 -0.2543884     0
# 1/8-1/2   -0.6513760 -0.7296118 -0.5731402     0
# 1/16-1/2  -0.8525327 -0.9307684 -0.7742969     0
# 1/32-1/2  -1.1556020 -1.2338378 -1.0773662     0
# 0-1/2     -1.6646975 -1.7429333 -1.5864617     0
# 1/8-1/4   -0.3187518 -0.3969876 -0.2405160     0
# 1/16-1/4  -0.5199084 -0.5981442 -0.4416726     0
# 1/32-1/4  -0.8229777 -0.9012135 -0.7447419     0
# 0-1/4     -1.3320733 -1.4103091 -1.2538375     0
# 1/16-1/8  -0.2011566 -0.2793924 -0.1229208     0
# 1/32-1/8  -0.5042259 -0.5824617 -0.4259901     0
# 0-1/8     -1.0133215 -1.0915573 -0.9350857     0
# 1/32-1/16 -0.3030693 -0.3813051 -0.2248335     0
# 0-1/16    -0.8121649 -0.8904007 -0.7339291     0
# 0-1/32    -0.5090955 -0.5873313 -0.4308597     0

# Omit '0' treatment and repeat
light2 <- light[light$treatment != '0', ]

# Two-way ANOVA on light data ('0' treatment omitted)
PAR2.aov <- aov(PAR ~ treatment*shelf, dat = light2)
anova(PAR2.aov)

# Analysis of Variance Table
#
# Response: PAR
#                 Df Sum Sq Mean Sq   F value  Pr(>F)    
# treatment        5 796372  159274 2597.5150 < 2e-16 ***
# shelf            1    369     369    6.0171 0.01785 *  
# treatment:shelf  5    528     106    1.7214 0.14774    
# Residuals       48   2943      61                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = PAR2.aov$fitted.values, y = PAR2.aov$residuals) # heteroscedastic 
hist(PAR2.aov$residuals)
qqnorm(PAR2.aov$residuals)

# Two-way ANOVA on log10-transformed PAR data  ('0' treatment omitted)
light2$log10PAR <- log10(light2$PAR)
PAR2.log10.aov <- aov(log10PAR ~ treatment*shelf, dat = light2)
anova(PAR2.log10.aov)

# Analysis of Variance Table
#
# Response: log10PAR
#                 Df  Sum Sq Mean Sq   F value Pr(>F)    
# treatment        5 14.6153 2.92307 1487.1143 <2e-16 ***
# shelf            1  0.0035 0.00353    1.7983 0.1862    
# treatment:shelf  5  0.0093 0.00186    0.9488 0.4584    
# Residuals       48  0.0943 0.00197                     
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = PAR2.log10.aov$fitted.values, y = PAR2.log10.aov$residuals) # less heteroscedastic 
hist(PAR2.log10.aov$residuals)
qqnorm(PAR2.log10.aov$residuals) # much straighter

# Tukey HSD test
TukeyHSD(PAR2.log10.aov, "treatment")

# Tukey multiple comparisons of means
# 95% family-wise confidence level
# 
# Fit: aov(formula = log10PAR ~ treatment * shelf, data = light2)
# 
# $treatment
# diff        lwr        upr p adj
# 1/2-1     -0.2881057 -0.3469509 -0.2292606     0
# 1/4-1     -0.6207300 -0.6795751 -0.5618848     0
# 1/8-1     -0.9394818 -0.9983269 -0.8806366     0
# 1/16-1    -1.1406384 -1.1994835 -1.0817932     0
# 1/32-1    -1.4437077 -1.5025529 -1.3848626     0
# 1/4-1/2   -0.3326242 -0.3914694 -0.2737791     0
# 1/8-1/2   -0.6513760 -0.7102212 -0.5925309     0
# 1/16-1/2  -0.8525327 -0.9113778 -0.7936875     0
# 1/32-1/2  -1.1556020 -1.2144471 -1.0967568     0
# 1/8-1/4   -0.3187518 -0.3775970 -0.2599067     0
# 1/16-1/4  -0.5199084 -0.5787536 -0.4610633     0
# 1/32-1/4  -0.8229777 -0.8818229 -0.7641326     0
# 1/16-1/8  -0.2011566 -0.2600018 -0.1423115     0
# 1/32-1/8  -0.5042259 -0.5630711 -0.4453808     0
# 1/32-1/16 -0.3030693 -0.3619145 -0.2442242     0



##### PART IV. DATA ANALYSIS: SURVIVAL AND REPRODUCTION #####



##### 7.   Load daily survival and reproduction data, and perform preliminary processing #####

# Load daily reproduction data
cr <- read.csv('CR_daily_surv_and_repro.csv', header = T) 

# Change light treatment names to be less cryptic 
cr$light.treatment[cr$light.treatment == "L01"] <- "1"
cr$light.treatment[cr$light.treatment == "L02"] <- "1/2"
cr$light.treatment[cr$light.treatment == "L04"] <- "1/4"
cr$light.treatment[cr$light.treatment == "L08"] <- "1/8"
cr$light.treatment[cr$light.treatment == "L16"] <- "1/16"
cr$light.treatment[cr$light.treatment == "L32"] <- "1/32"
cr$light.treatment[cr$light.treatment == "L00"] <- "0"
cr$light.treatment <- factor(cr$light.treatment, c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0"))

# Extract reproduction data 
cr.repro <- subset(cr, select = Aug.12.2021:Jan.03.2022) 

# Double check dates of birth
cr$date.birth.alt <- apply(cr.repro, 1, function (x) names(cr.repro)[min(which(x == 0))])
cr$date.birth.alt == cr$date.birth # all entries match
cr <- cr[ , 1:(ncol(cr) - 1)] # drop unnecessary date.birth.alt column

# Double check dates of last reproduction
# Note: The column called 'date.last.repro' represents the date of last 
# reproduction for the 199 fronds that were already dead by Jan. 3, 2022. For 
# the 19 fronds that were still alive on Jan. 3, 2022, when the experiment was
# truncated, date.last.repro was set to Jan.03.2022.
cr$date.last.repro.alt <- apply(cr.repro, 1, function (x) names(cr.repro)[max(which(x > 0))])
cr$date.last.repro.alt == cr$date.last.repro # not all entries match 
sum(cr$date.last.repro.alt != cr$date.last.repro) # entries don't match for 17 fronds
cr$id[which(cr$date.last.repro.alt != cr$date.last.repro)] # IDs of the 17 mismatches
cr$Status.on.Jan.03.2022[which(cr$date.last.repro.alt != cr$date.last.repro)] # mismatches are 17 fronds alive Jan. 3
# the other two alive-on-Jan. 3 fronds produced a daughter on Jan. 3 and were therefore not mismatches:
Alive.not.mismatch <- setdiff(cr$id[which(cr$Status.on.Jan.03.2022 == "Alive")], 
                              cr$id[which(cr$date.last.repro.alt != cr$date.last.repro)])
cr$Jan.03.2022[cr$id == Alive.not.mismatch[1]] # produced daughter on Jan. 3
cr$Jan.03.2022[cr$id == Alive.not.mismatch[2]] # produced daughter on Jan. 3
# moreover, those were the only two fronds that produced a daughter on Jan. 3:
cr$id[which(cr$Jan.03.2022 > 0)] # same as Alive.not.mismatch
cr <- cr[ , 1:(ncol(cr) - 1)] # everything checks out; drop unnecessary date.last.repro.alt column 

# Calculate dates of first reproduction
cr$date.first.repro <- apply(cr.repro, 1, function (x) names(cr.repro)[min(which(x > 0))])

# Convert date values to R's date format
cr$date.birth <- as.Date(cr$date.birth, format = "%b.%d.%Y")
cr$date.last.repro <- as.Date(cr$date.last.repro, format = "%b.%d.%Y")
cr$date.first.repro <- as.Date(cr$date.first.repro, format = "%b.%d.%Y")

# Calculate lifespan from birth
cr$lifespan <- as.numeric(cr$date.last.repro - cr$date.birth + 1) # first day is Day 1, not Day 0

# Calculate lifespan from first reproduction
cr$lifespan.ffr <- as.numeric(cr$date.last.repro - cr$date.first.repro + 1)

# Calculate lifetime reproduction
cr$total.offspring <- apply(cr.repro, 1, function (x) sum(x, na.rm = T))

# Make new data frame with aligned reproduction data relative to dates of birth
cr.repro.aligned <- matrix(NA, nrow = nrow(cr.repro), ncol = max(cr$lifespan))
birth.col <- as.numeric(cr$date.birth - min(cr$date.birth) + 1) # column index for date of birth       
death.col <- as.numeric(cr$date.last.repro - min(cr$date.birth) + 1) # column index for date of death
for (i in 1:nrow(cr.repro)) {
  cr.repro.aligned[i, 1:cr$lifespan[i]] <- as.numeric(cr.repro[i, birth.col[i]:death.col[i]])
}

# Calculate intrinsic rate of increase of individuals (r)
for (i in 1:nrow(cr.repro.aligned)) {
  ind <- cr.repro.aligned[i, ]                                # extract individual in row i
  L <- max(which(ind > 0))                                    # get lifespan
  lesMat <- matrix(0, nrow = L, ncol = L)                     # create empty lifespan x lifespan Leslie matrix
  lesMat[1, ] <- ind[1:L]                                     # fill first row with reproduction data
  if (L > 1) {
    lesMat[2:L, 1:(L - 1)] <- diag(rep(1, (L - 1)))           # fill sub-diagonal with survival data
  }
  eigenvalues <- eigen(lesMat)$values                         # get list of eigenvalues of Leslie matrix
  lambda <- max(Re(eigenvalues[abs(Im(eigenvalues)) < 1e-6])) # extract lambda
  cr$r[i] <- log(lambda)                                      # record intrinsic rate of increase (r)
  if (abs(cr$r[i]) < 1e-6) {
    cr$r[i] <- 0                                              # correct for floating point arithmetic rounding errors
  }
} 



##### 8a.  Analyze reproductive lifespan (ANOVA) ##### 

# Visually inspect boxplot of lifespan
boxplot(lifespan ~ light.treatment, dat = cr, ylim = c(0, 150),
        las = 1, whisklty = 1, col = "white", xlab = "Light intensity treatment", ylab = "Lifespan (days)")

# One-way ANOVA on lifespan (omitting 1/32 and 0 light intensity treatments)
use.rows <- cr$light.treatment == "1" | cr$light.treatment == "1/2" | cr$light.treatment == "1/4" | 
  cr$light.treatment == "1/8" | cr$light.treatment == "1/16"
lifespan.aov <- aov(lifespan ~ light.treatment, dat = cr[use.rows, ])
anova(lifespan.aov)

# Analysis of Variance Table
#
# Response: lifespan
#                  Df Sum Sq Mean Sq F value    Pr(>F)    
# light.treatment   4  44928   11232  46.042 < 2.2e-16 ***
# Residuals       154  37569     244                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = lifespan.aov$fitted.values, y = lifespan.aov$residuals) # somewhat heteroscedastic
hist(lifespan.aov$residuals) # somewhat skewed
qqnorm(lifespan.aov$residuals)

# One-way ANOVA on log10-transformed lifespan data (omitting 1/32 and 0 light intensity treatments)
cr$log10lifespan <- log10(cr$lifespan)
lifespan.log10.aov <- aov(log10lifespan ~ light.treatment, dat = cr[use.rows, ])
anova(lifespan.log10.aov)

# Analysis of Variance Table
# 
# Response: log10lifespan
#                  Df Sum Sq Mean Sq F value    Pr(>F)    
# light.treatment   4 4.7237  1.1809  61.514 < 2.2e-16 ***
# Residuals       154 2.9564  0.0192                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = lifespan.log10.aov$fitted.values, y = lifespan.log10.aov$residuals) # considerably improved
hist(lifespan.log10.aov$residuals) # still a small bit skewed
qqnorm(lifespan.log10.aov$residuals) # much straighter

# Tukey HSD test
TukeyHSD(lifespan.log10.aov)

# Tukey multiple comparisons of means
# 95% family-wise confidence level
# 
# Fit: aov(formula = log10lifespan ~ light.treatment, data = cr[use.rows, ])
# 
# $light.treatment
#                diff         lwr       upr     p adj
# 1/2-1    0.10579736  0.00941351 0.2021812 0.0236504
# 1/4-1    0.16551202  0.06989618 0.2611279 0.0000399
# 1/8-1    0.34599260  0.25037676 0.4416084 0.0000000
# 1/16-1   0.48026582  0.38464999 0.5758817 0.0000000
# 1/4-1/2  0.05971466 -0.03666919 0.1560985 0.4307601
# 1/8-1/2  0.24019524  0.14381140 0.3365791 0.0000000
# 1/16-1/2 0.37446847  0.27808462 0.4708523 0.0000000
# 1/8-1/4  0.18048058  0.08486475 0.2760964 0.0000059
# 1/16-1/4 0.31475381  0.21913797 0.4103696 0.0000000
# 1/16-1/8 0.13427322  0.03865739 0.2298891 0.0014550

# Letters for post-hoc comparisons
# 1    A
# 1/2  B
# 1/4  B
# 1/8  C
# 1/16 D

# Double check letters for post-hoc comparisons
lifespan.log10.means <- emmeans(object = lifespan.log10.aov, specs = "light.treatment")
tapply(X = cr$log10lifespan, INDEX = cr$light.treatment, FUN = mean) # gives same means
lifespan.log10.means.cld <- cld(object = lifespan.log10.means, Letters = letters, alpha = 0.05)
lifespan.log10.means.cld # same letters

# light.treatment emmean     SE  df lower.CL upper.CL .group
# 1                 1.33 0.0245 154     1.29     1.38  a    
# 1/2               1.44 0.0249 154     1.39     1.49   b   
# 1/4               1.50 0.0245 154     1.45     1.55   b   
# 1/8               1.68 0.0245 154     1.63     1.73    c  
# 1/16              1.81 0.0245 154     1.77     1.86     d 



##### 8b.  Analyze reproductive lifespan (Michaelis-Menten kinetics) ##### 

# Convert light treatment to a numerical variable
cr$light.treatment.num[cr$light.treatment == "1"]    <- 1
cr$light.treatment.num[cr$light.treatment == "1/2"]  <- 1/2
cr$light.treatment.num[cr$light.treatment == "1/4"]  <- 1/4
cr$light.treatment.num[cr$light.treatment == "1/8"]  <- 1/8
cr$light.treatment.num[cr$light.treatment == "1/16"] <- 1/16
cr$light.treatment.num[cr$light.treatment == "1/32"] <- 1/32
cr$light.treatment.num[cr$light.treatment == "0"]    <- 0

# Fit Michaelis-Menten-power-law model (light intensity treatments 1 to 1/16)
MMpow.1to16.nls <- nls(log(lifespan) ~ c - v*log(light.treatment.num/(b + light.treatment.num)),
                       data = cr[cr$light.treatment != '0' & cr$light.treatment != '1/32', ],
                       start = list(c = log(min(cr$lifespan)), b = 0.3, v = 1))

# Extract parameter values (light intensity treatments 1 to 1/16)
MMpow.1to16.nls.c <- summary(MMpow.1to16.nls)$parameters[1, 1]
MMpow.1to16.nls.b <- summary(MMpow.1to16.nls)$parameters[2, 1]
MMpow.1to16.nls.v <- summary(MMpow.1to16.nls)$parameters[3, 1]

# Visually inspect fit (light intensity treatments 1 to 1/16)
plot(lifespan ~ light.treatment.num, log = "y", data = cr[cr$light.treatment != '0' & cr$light.treatment != '1/32', ])
MMpow.1to16.nls.x <- seq(1/16, 1, 1/1600)
MMpow.1to16.nls.y <- exp(MMpow.1to16.nls.c - MMpow.1to16.nls.v*log(MMpow.1to16.nls.x/(MMpow.1to16.nls.b + MMpow.1to16.nls.x)))
lines(MMpow.1to16.nls.x, MMpow.1to16.nls.y)

# Model diagnostics (light intensity treatments 1 to 1/16)
hist(summary(MMpow.1to16.nls)$residuals)
plot(summary(MMpow.1to16.nls)$residuals ~ cr$light.treatment.num[cr$light.treatment != '0' & cr$light.treatment != '1/32']) # possible outlier in treatment 1/2

# Fit Michaelis-Menten-power-law model (light intensity treatments 1 to 1/32)
MMpow.1to32.nls <- nls(log(lifespan) ~ c - v*log(light.treatment.num/(b + light.treatment.num)),
                       data = cr[cr$light.treatment != '0', ],
                       start = list(c = log(min(cr$lifespan)), b = 0.3, v = 1))

# Extract parameter values (light intensity treatments 1 to 1/32)
MMpow.1to32.nls.c <- summary(MMpow.1to32.nls)$parameters[1, 1]
MMpow.1to32.nls.b <- summary(MMpow.1to32.nls)$parameters[2, 1]
MMpow.1to32.nls.v <- summary(MMpow.1to32.nls)$parameters[3, 1]

# Visually inspect fit (light intensity treatments 1 to 1/32)
plot(lifespan ~ light.treatment.num, log = "y", data = cr[cr$light.treatment != '0', ])
MMpow.1to32.nls.x <- seq(1/32, 1, 1/1600)
MMpow.1to32.nls.y <- exp(MMpow.1to32.nls.c - MMpow.1to32.nls.v*log(MMpow.1to32.nls.x/(MMpow.1to32.nls.b + MMpow.1to32.nls.x)))
lines(MMpow.1to32.nls.x, MMpow.1to32.nls.y)

# Model diagnostics (light intensity treatments 1 to 1/32)
hist(summary(MMpow.1to32.nls)$residuals)
plot(summary(MMpow.1to32.nls)$residuals ~ cr$light.treatment.num[cr$light.treatment != '0']) # possible outlier in treatment 1/2



##### 9.   Analyze lifetime reproduction (ANOVA) #####

# Visually inspect boxplot of lifetime reproduction
boxplot(total.offspring ~ light.treatment, dat = cr, ylim = c(0, 20), las = 1, whisklty = 1, col = "white", 
        xlab = "Light intensity treatment", ylab = "Total number of offspring")

# One-way ANOVA on total.offspring (omitting 1/32 and 0 light intensity treatments)
use.rows <- cr$light.treatment == "1" | cr$light.treatment == "1/2" | cr$light.treatment == "1/4" | 
  cr$light.treatment == "1/8" | cr$light.treatment == "1/16"
total.offspring.aov <- aov(total.offspring ~ light.treatment, dat = cr[use.rows, ])
anova(total.offspring.aov)

# Analysis of Variance Table
#
# Response: total.offspring
#                  Df  Sum Sq Mean Sq F value    Pr(>F)    
# light.treatment   4  193.74  48.434  6.5146 7.188e-05 ***
# Residuals       154 1144.95   7.435                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = total.offspring.aov$fitted.values, y = total.offspring.aov$residuals)
hist(total.offspring.aov$residuals) # somewhat skewed
qqnorm(total.offspring.aov$residuals)

# One-way ANOVA on log10-transformed total.offspring data (omitting 1/32 and 0 light intensity treatments)
cr$log10total.offspring <- log10(cr$total.offspring)
total.offspring.log10.aov <- aov(log10total.offspring ~ light.treatment, dat = cr[use.rows, ])
anova(total.offspring.log10.aov)

# Analysis of Variance Table
#
# Response: log10total.offspring
#                  Df  Sum Sq  Mean Sq F value   Pr(>F)    
# light.treatment   4 0.43901 0.109754  7.5777 1.34e-05 ***
# Residuals       154 2.23050 0.014484                     
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = total.offspring.log10.aov$fitted.values, y = total.offspring.log10.aov$residuals)
hist(total.offspring.log10.aov$residuals) # much less skewed
qqnorm(total.offspring.log10.aov$residuals) # much straighter

# Tukey HSD test
TukeyHSD(total.offspring.log10.aov)

# Tukey multiple comparisons of means
# 95% family-wise confidence level
#
# Fit: aov(formula = log10total.offspring ~ light.treatment, data = cr[use.rows, ])
#
# $light.treatment
#                 diff          lwr        upr     p adj
# 1/2-1    0.059552277 -0.024166349 0.14327090 0.2888479
# 1/4-1    0.105560942  0.022509406 0.18861248 0.0052788
# 1/8-1    0.133253735  0.050202200 0.21630527 0.0001722
# 1/16-1   0.141244653  0.058193117 0.22429619 0.0000571
# 1/4-1/2  0.046008664 -0.037709962 0.12972729 0.5530652
# 1/8-1/2  0.073701458 -0.010017169 0.15742008 0.1128557
# 1/16-1/2 0.081692376 -0.002026251 0.16541100 0.0595074
# 1/8-1/4  0.027692794 -0.055358742 0.11074433 0.8886590
# 1/16-1/4 0.035683711 -0.047367824 0.11873525 0.7593945
# 1/16-1/8 0.007990918 -0.075060618 0.09104245 0.9988959

# Letters for post-hoc comparisons
# 1    A
# 1/2  AB
# 1/4  B
# 1/8  B
# 1/16 B

# Double check letters for post-hoc comparisons
total.offspring.log10.means <- emmeans(object = total.offspring.log10.aov, specs = "light.treatment")
tapply(X = cr$log10total.offspring, INDEX = cr$light.treatment, FUN = mean) # gives same means
total.offspring.log10.means.cld <- cld(object = total.offspring.log10.means, Letters = letters, alpha = 0.05)
total.offspring.log10.means.cld # same letters

# light.treatment emmean     SE  df lower.CL upper.CL .group
# 1                0.860 0.0213 154    0.818    0.902  a    
# 1/2              0.920 0.0216 154    0.877    0.962  ab   
# 1/4              0.966 0.0213 154    0.924    1.008   b   
# 1/8              0.993 0.0213 154    0.951    1.036   b   
# 1/16             1.001 0.0213 154    0.959    1.044   b   



##### 10.  Analyze intrinsic rate of increase of individuals (r) (ANOVA) #####

# Visually inspect boxplot of intrinsic rate of increase of individuals (r)
boxplot(r ~ light.treatment, dat = cr, las = 1, ylim = c(0, 0.4), whisklty = 1, col = "white", 
        xlab = "Light intensity treatment", ylab = "Intrinsic rate of increase (r)")

# One-way ANOVA on r (omitting 1/32 and 0 light intensity treatments)
use.rows <- cr$light.treatment == "1" | cr$light.treatment == "1/2" | cr$light.treatment == "1/4" | 
  cr$light.treatment == "1/8" | cr$light.treatment == "1/16"
r.aov <- aov(r ~ light.treatment, dat = cr[use.rows, ])
anova(r.aov)

# Analysis of Variance Table
# 
# Response: r
#                  Df  Sum Sq  Mean Sq F value    Pr(>F)    
# light.treatment   4 0.21990 0.054976  35.604 < 2.2e-16 ***
# Residuals       154 0.23779 0.001544                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = r.aov$fitted.values, y = r.aov$residuals)
hist(r.aov$residuals) # somewhat skewed
qqnorm(r.aov$residuals)

# One-way ANOVA on log10-transformed r data (omitting 1/32 and 0 light intensity treatments)
cr$log10r <- log10(cr$r) # note: one r value of 0 cannot be transformed, but it is in the '0' treatment (already excluded)
r.log10.aov <- aov(log10r ~ light.treatment, dat = cr[use.rows, ])
anova(r.log10.aov)

# Analysis of Variance Table
# 
# Response: log10r
#                  Df Sum Sq Mean Sq F value    Pr(>F)    
# light.treatment   4 1.2952 0.32380  39.413 < 2.2e-16 ***
# Residuals       154 1.2652 0.00822                      
# ---
# Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

# Model diagnostics
plot(x = r.log10.aov$fitted.values, y = r.log10.aov$residuals)
hist(r.log10.aov$residuals) # much less skewed
qqnorm(r.log10.aov$residuals) # straighter

# Tukey HSD test
TukeyHSD(r.log10.aov)

# Tukey multiple comparisons of means
# 95% family-wise confidence level
# 
# Fit: aov(formula = log10r ~ light.treatment, data = cr[use.rows, ])
# 
# $light.treatment
#                 diff        lwr          upr     p adj
# 1/2-1    -0.04823097 -0.1112833  0.014821411 0.2204753
# 1/4-1    -0.09830137 -0.1608513 -0.035751409 0.0002483
# 1/8-1    -0.18162056 -0.2441705 -0.119070595 0.0000000
# 1/16-1   -0.24998159 -0.3125316 -0.187431632 0.0000000
# 1/4-1/2  -0.05007040 -0.1131228  0.012981976 0.1882341
# 1/8-1/2  -0.13338959 -0.1964420 -0.070337210 0.0000003
# 1/16-1/2 -0.20175063 -0.2648030 -0.138698246 0.0000000
# 1/8-1/4  -0.08331919 -0.1458691 -0.020769224 0.0029672
# 1/16-1/4 -0.15168022 -0.2142302 -0.089130261 0.0000000
# 1/16-1/8 -0.06836104 -0.1309110 -0.005811075 0.0245711

# Letters for post-hoc comparisons
# 1    D
# 1/2  CD 
# 1/4  C
# 1/8  B
# 1/16 A

# Double check letters for post-hoc comparisons
r.log10.means <- emmeans(object = r.log10.aov, specs = "light.treatment")
tapply(X = cr$log10r, INDEX = cr$light.treatment, FUN = mean) # gives same means
r.log10.means.cld <- cld(object = r.log10.means, Letters = letters, alpha = 0.05)
r.log10.means.cld # same letters (note inverted order below)

# light.treatment emmean     SE  df lower.CL upper.CL .group
# 1/16            -0.862 0.0160 154   -0.894   -0.831  a    
# 1/8             -0.794 0.0160 154   -0.826   -0.762   b   
# 1/4             -0.711 0.0160 154   -0.742   -0.679    c  
# 1/2             -0.660 0.0163 154   -0.693   -0.628    cd 
# 1               -0.612 0.0160 154   -0.644   -0.581     d 



##### 11.  Create aligned reproduction data for each light intensity treatment #####

# Create separate aligned reproduction data for each light intensity treatment
cr.repro.aligned.01 <- cr.repro.aligned[cr$light.treatment == "1", ]
cr.repro.aligned.02 <- cr.repro.aligned[cr$light.treatment == "1/2", ]
cr.repro.aligned.04 <- cr.repro.aligned[cr$light.treatment == "1/4", ]
cr.repro.aligned.08 <- cr.repro.aligned[cr$light.treatment == "1/8", ]
cr.repro.aligned.16 <- cr.repro.aligned[cr$light.treatment == "1/16", ]
cr.repro.aligned.32 <- cr.repro.aligned[cr$light.treatment == "1/32", ]
cr.repro.aligned.00 <- cr.repro.aligned[cr$light.treatment == "0", ]

# Convert aligned reproduction data into binomial format
cr.repro.aligned.binom.01 <- apply(cr.repro.aligned.01, 2, function (x) replace(x, which(x > 1), 1))
cr.repro.aligned.binom.02 <- apply(cr.repro.aligned.02, 2, function (x) replace(x, which(x > 1), 1))
cr.repro.aligned.binom.04 <- apply(cr.repro.aligned.04, 2, function (x) replace(x, which(x > 1), 1))
cr.repro.aligned.binom.08 <- apply(cr.repro.aligned.08, 2, function (x) replace(x, which(x > 1), 1))
cr.repro.aligned.binom.16 <- apply(cr.repro.aligned.16, 2, function (x) replace(x, which(x > 1), 1))
cr.repro.aligned.binom.32 <- apply(cr.repro.aligned.32, 2, function (x) replace(x, which(x > 1), 1))
cr.repro.aligned.binom.00 <- apply(cr.repro.aligned.00, 2, function (x) replace(x, which(x > 1), 1))



##### 12A. Create life tables for light intensity treatment '1' #####

n.01 <- nrow(cr.repro.aligned.01) # total starting sample size
life.dist.01 <- cr$lifespan[cr$light.treatment == "1"] # distribution of lifespan
maxAge.01 <- max(life.dist.01) # max lifespan
meanAge.01 <- mean(life.dist.01) # mean lifespan
lifeTab.01 <- data.frame(matrix(nrow = maxAge.01, ncol = 7))
names(lifeTab.01) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.01$age <- 1:maxAge.01 # ages
lifeTab.01$age.rel <- lifeTab.01$age/meanAge.01 # relative ages (in mean lifespans)
lifeTab.01$n.last.repro <- tabulate(life.dist.01, nbins = maxAge.01) # number of deaths at each age
lifeTab.01$n.surv.cum <- c(n.01, n.01 - cumsum(lifeTab.01$n.last.repro[1:(maxAge.01 - 1)])) # total cumulative survivorship at age
lifeTab.01$p.surv.cum <- lifeTab.01$n.surv.cum/n.01 # proportional cumulative survivorship at age
lifeTab.01$n.repro <- colSums(cr.repro.aligned.binom.01[ , 1:maxAge.01], na.rm = TRUE) # number reproducing at each age
lifeTab.01$p.repro <- lifeTab.01$n.repro/lifeTab.01$n.surv.cum # proportion reproducing at age



##### 12B. Create life tables for light intensity treatment '1/2' #####

n.02 <- nrow(cr.repro.aligned.02) # total starting sample size
life.dist.02 <- cr$lifespan[cr$light.treatment == "1/2"] # distribution of lifespan
maxAge.02 <- max(life.dist.02) # max lifespan
meanAge.02 <- mean(life.dist.02) # mean lifespan
lifeTab.02 <- data.frame(matrix(nrow = maxAge.02, ncol = 7))
names(lifeTab.02) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.02$age <- 1:maxAge.02 # ages
lifeTab.02$age.rel <- lifeTab.02$age/meanAge.02 # relative ages (in mean lifespans)
lifeTab.02$n.last.repro <- tabulate(life.dist.02, nbins = maxAge.02) # number of deaths at each age
lifeTab.02$n.surv.cum <- c(n.02, n.02 - cumsum(lifeTab.02$n.last.repro[1:(maxAge.02 - 1)])) # total cumulative survivorship at age
lifeTab.02$p.surv.cum <- lifeTab.02$n.surv.cum/n.02 # proportional cumulative survivorship at age
lifeTab.02$n.repro <- colSums(cr.repro.aligned.binom.02[ , 1:maxAge.02], na.rm = TRUE) # number reproducing at each age
lifeTab.02$p.repro <- lifeTab.02$n.repro/lifeTab.02$n.surv.cum # proportion reproducing at age



##### 12C. Create life tables for light intensity treatment '1/4' #####

n.04 <- nrow(cr.repro.aligned.04) # total starting sample size
life.dist.04 <- cr$lifespan[cr$light.treatment == "1/4"] # distribution of lifespan
maxAge.04 <- max(life.dist.04) # max lifespan
meanAge.04 <- mean(life.dist.04) # mean lifespan
lifeTab.04 <- data.frame(matrix(nrow = maxAge.04, ncol = 7))
names(lifeTab.04) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.04$age <- 1:maxAge.04 # ages
lifeTab.04$age.rel <- lifeTab.04$age/meanAge.04 # relative ages (in mean lifespans)
lifeTab.04$n.last.repro <- tabulate(life.dist.04, nbins = maxAge.04) # number of deaths at each age
lifeTab.04$n.surv.cum <- c(n.04, n.04 - cumsum(lifeTab.04$n.last.repro[1:(maxAge.04 - 1)])) # total cumulative survivorship at age
lifeTab.04$p.surv.cum <- lifeTab.04$n.surv.cum/n.04 # proportional cumulative survivorship at age
lifeTab.04$n.repro <- colSums(cr.repro.aligned.binom.04[ , 1:maxAge.04], na.rm = TRUE) # number reproducing at each age
lifeTab.04$p.repro <- lifeTab.04$n.repro/lifeTab.04$n.surv.cum # proportion reproducing at age



##### 12D. Create life tables for light intensity treatment '1/8' #####

n.08 <- nrow(cr.repro.aligned.08) # total starting sample size
life.dist.08 <- cr$lifespan[cr$light.treatment == "1/8"] # distribution of lifespan
maxAge.08 <- max(life.dist.08) # max lifespan
meanAge.08 <- mean(life.dist.08) # mean lifespan
lifeTab.08 <- data.frame(matrix(nrow = maxAge.08, ncol = 7))
names(lifeTab.08) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.08$age <- 1:maxAge.08 # ages
lifeTab.08$age.rel <- lifeTab.08$age/meanAge.08 # relative ages (in mean lifespans)
lifeTab.08$n.last.repro <- tabulate(life.dist.08, nbins = maxAge.08) # number of deaths at each age
lifeTab.08$n.surv.cum <- c(n.08, n.08 - cumsum(lifeTab.08$n.last.repro[1:(maxAge.08 - 1)])) # total cumulative survivorship at age
lifeTab.08$p.surv.cum <- lifeTab.08$n.surv.cum/n.08 # proportional cumulative survivorship at age
lifeTab.08$n.repro <- colSums(cr.repro.aligned.binom.08[ , 1:maxAge.08], na.rm = TRUE) # number reproducing at each age
lifeTab.08$p.repro <- lifeTab.08$n.repro/lifeTab.08$n.surv.cum # proportion reproducing at age



##### 12E. Create life tables for light intensity treatment '1/16' #####

n.16 <- nrow(cr.repro.aligned.16) # total starting sample size
life.dist.16 <- cr$lifespan[cr$light.treatment == "1/16"] # distribution of lifespan
maxAge.16 <- max(life.dist.16) # max lifespan
meanAge.16 <- mean(life.dist.16) # mean lifespan
lifeTab.16 <- data.frame(matrix(nrow = maxAge.16, ncol = 7))
names(lifeTab.16) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.16$age <- 1:maxAge.16 # ages
lifeTab.16$age.rel <- lifeTab.16$age/meanAge.16 # relative ages (in mean lifespans)
lifeTab.16$n.last.repro <- tabulate(life.dist.16, nbins = maxAge.16) # number of deaths at each age
lifeTab.16$n.surv.cum <- c(n.16, n.16 - cumsum(lifeTab.16$n.last.repro[1:(maxAge.16 - 1)])) # total cumulative survivorship at age
lifeTab.16$p.surv.cum <- lifeTab.16$n.surv.cum/n.16 # proportional cumulative survivorship at age
lifeTab.16$n.repro <- colSums(cr.repro.aligned.binom.16[ , 1:maxAge.16], na.rm = TRUE) # number reproducing at each age
lifeTab.16$p.repro <- lifeTab.16$n.repro/lifeTab.16$n.surv.cum # proportion reproducing at age



##### 12F. Create life tables for light intensity treatment '1/32' #####

n.32 <- nrow(cr.repro.aligned.32) # total starting sample size
life.dist.32 <- cr$lifespan[cr$light.treatment == "1/32"] # distribution of lifespan
maxAge.32 <- max(life.dist.32) # max lifespan
meanAge.32 <- mean(life.dist.32) # mean lifespan
lifeTab.32 <- data.frame(matrix(nrow = maxAge.32, ncol = 7))
names(lifeTab.32) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.32$age <- 1:maxAge.32 # ages
lifeTab.32$age.rel <- lifeTab.32$age/meanAge.32 # relative ages (in mean lifespans)
lifeTab.32$n.last.repro <- tabulate(life.dist.32, nbins = maxAge.32) # number of deaths at each age
lifeTab.32$n.surv.cum <- c(n.32, n.32 - cumsum(lifeTab.32$n.last.repro[1:(maxAge.32 - 1)])) # total cumulative survivorship at age
lifeTab.32$p.surv.cum <- lifeTab.32$n.surv.cum/n.32 # proportional cumulative survivorship at age
lifeTab.32$n.repro <- colSums(cr.repro.aligned.binom.32[ , 1:maxAge.32], na.rm = TRUE) # number reproducing at each age
lifeTab.32$p.repro <- lifeTab.32$n.repro/lifeTab.32$n.surv.cum # proportion reproducing at age



##### 12G. Create life tables for light intensity treatment '0' #####

n.00 <- nrow(cr.repro.aligned.00) # total starting sample size
life.dist.00 <- cr$lifespan[cr$light.treatment == "0"] # distribution of lifespan
maxAge.00 <- max(life.dist.00) # max lifespan
meanAge.00 <- mean(life.dist.00) # mean lifespan
lifeTab.00 <- data.frame(matrix(nrow = maxAge.00, ncol = 7))
names(lifeTab.00) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.00$age <- 1:maxAge.00 # ages
lifeTab.00$age.rel <- lifeTab.00$age/meanAge.00 # relative ages (in mean lifespans)
lifeTab.00$n.last.repro <- tabulate(life.dist.00, nbins = maxAge.00) # number of deaths at each age
lifeTab.00$n.surv.cum <- c(n.00, n.00 - cumsum(lifeTab.00$n.last.repro[1:(maxAge.00 - 1)])) # total cumulative survivorship at age
lifeTab.00$p.surv.cum <- lifeTab.00$n.surv.cum/n.00 # proportional cumulative survivorship at age
lifeTab.00$n.repro <- colSums(cr.repro.aligned.binom.00[ , 1:maxAge.00], na.rm = TRUE) # number reproducing at each age
lifeTab.00$p.repro <- lifeTab.00$n.repro/lifeTab.00$n.surv.cum # proportion reproducing at age



##### 13.  Visually inspect survivorship curves #####

# Visually inspect survivorship curves (age in days)
plot(p.surv.cum ~ age,  dat = lifeTab.01, type = "n", las = 1, log = "y",
     xlim = c(0, 145), xlab = "Age (days)", ylab = "Proporting surviving")
lines(p.surv.cum ~ age, dat = lifeTab.01, type = "s", col = "#000000") 
lines(p.surv.cum ~ age, dat = lifeTab.02, type = "s", col = "#FF0000")
lines(p.surv.cum ~ age, dat = lifeTab.04, type = "s", col = "#FFA500")
lines(p.surv.cum ~ age, dat = lifeTab.08, type = "s", col = "#00FF00")
lines(p.surv.cum ~ age, dat = lifeTab.16, type = "s", col = "#00FFFF")
lines(p.surv.cum ~ age, dat = lifeTab.32, type = "s", col = "#0000FF")
lines(p.surv.cum ~ age, dat = lifeTab.00, type = "s", col = "#FF00FF")
legend("topright", c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0"), title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF", "#0000FF", "#FF00FF"), 
       lty = 1, bty = "n")

# Visually inspect survivorship curves (age in lifespans)
plot(p.surv.cum ~ age.rel,  dat = lifeTab.01, type = "n", las = 1, log = "y",
     xlim = c(0, 2.2), xlab = "Age (lifespans)", ylab = "Survivorship")
lines(p.surv.cum ~ age.rel, dat = lifeTab.01, type = "s", col = "#000000") 
lines(p.surv.cum ~ age.rel, dat = lifeTab.02, type = "s", col = "#FF0000")
lines(p.surv.cum ~ age.rel, dat = lifeTab.04, type = "s", col = "#FFA500")
lines(p.surv.cum ~ age.rel, dat = lifeTab.08, type = "s", col = "#00FF00")
lines(p.surv.cum ~ age.rel, dat = lifeTab.16, type = "s", col = "#00FFFF")
# lines for 1/32 and 0 treatments omitted because mean lifespan (and therefore relative age) cannot be calculated 
legend("topright", c("1", "1/2", "1/4", "1/8", "1/16"), title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF"), 
       lty = 1, bty = "n")



##### 14.  Determine modified critical Kolmogorov-Smirnov value, D.crit, for use in Experiment 2 #####

# Set random seed
set.seed(321) # arbitrary seed for code repeatability

# Set sample size and number of bootstrap replicates
n.target <- 112 # Set equal to initial sample size (per treatment) in Experiment 2
n.reps <- 10000 # number of bootstrap replicates (recommend 10000; takes a few seconds to compute)

# Initialize KS, which will house the test statistic (D) of the Kolmogorov-Smirnov tests on the bootstrap replicates 
KS <- rep(NA, n.reps)

# Bootstrap process
for (i in 1:n.reps) {
  
  # Sample (with replacement) the lifespan distributions for the L1 and L1/4 treatments
  # Use the distributions of Expt 1, but with the initial sample sizes of Expt 2
  sample.01 <- sample(life.dist.01, size = n.target, replace = T)
  sample.04 <- sample(life.dist.04, size = n.target, replace = T)
  
  # Convert the sample lifespan distributions into relative lifespan distributions
  rel.sample.01 <- sample.01/mean(sample.01)
  rel.sample.04 <- sample.04/mean(sample.04)
  
  # Perform a Kolmogorov-Smirnov test on the relative lifespan distributions for the current replicate; extract D
  KS[i] <- suppressWarnings(ks.test(rel.sample.01, rel.sample.04)$statistic) # warning suppressed; we know about ties
  
}

# Set target beta
targ.beta <- 0.2 # e.g., for 'high' power of 1 - beta = 0.8, set targ.beta to 0.2

# Calculate D.crit
# D.crit is the value that the proportion 1 - targ.beta of KS D's
# (on the bootstrap replicates) would be GREATER than
D.crit <- sort(KS, decreasing = T)[n.reps*(1 - targ.beta)] # 0.1429 
D.crit.alt <- sort(KS, decreasing = F)[n.reps*(targ.beta)] # 0.1429; exactly the same

# Double check using a previous similar method; from before alpha.prime = 0.2031888
D.crit.alt.2 <- sqrt(-log(0.2031888/2)*0.5)*sqrt((112 + 112)/(112*112)) # 0.1429; same to four decimals

# Compare D.crit with what it would be for alpha = 0.05
D.crit.alpha.0.05 <- sqrt(-log(0.05/2)*0.5)*sqrt((112 + 112)/(112*112)) # 0.1814839
# Thus, D.crit has become *lower* than D.crit.alpha.0.05, which makes sense because a 
# *non*-significant KS test implies temporal scaling; i.e., this makes the 
# test more conservative, which is important when drawing inference from a 
# non-sig result

# Check if there are ties
sum(KS == D.crit) > 1 # TRUE; therefore, there are ties

# Re-calculate D.crit, accounting for ties (more conservative approach)
# Correct for rounding errors associated with floating point arithmetic 
D.crit.alt.3 <- max(KS[D.crit - KS > 1e-6]) # 0.1339 (lower than original estimate) 

# Double check that D.crit.alt.3 is the next step down from D.crit
u <- max(which(sort(KS) < D.crit))
sort(KS)[(u - 3):(u + 3)]
# 0.1339286 0.1339286 0.1339286 0.1339286 0.1428571 0.1428571 0.1428571 # confirmed

# Generate the empirical cumulative distribution function for KS D's
KS.ecdf <- matrix(rep(NA, n.reps*2), ncol = 2)
KS.ecdf[ , 1] <- sort(KS) # column 1:  D-values in ascending order
for (i in 1:n.reps) {     # column 2:  proportion of D-values less or equal to the current one
  KS.ecdf[i, 2] <- sum(KS.ecdf[ , 1] <= KS.ecdf[i, 1])/n.reps
}

# Visually inspect empirical cumulative frequency distribution of KS D's  
plot(x = KS.ecdf[, 1],
     y = KS.ecdf[, 2],
     xlim = c(0.05, 0.35),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.35, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.alt.3, D.crit.alt.3), c(0, 1), lty = 2)
text(x = D.crit.alt.3 + 0.005, y = 0, expression(paste(italic("D")[crit], " = 0.1339")), adj = c(0, 0))

# Repeat with realized final sample sizes from Expt 2 (even more conservative)

# Set sample sizes
n.target.01 <- 102 # treatment L1
n.target.04 <- 104 # treatment L1/4

# Initialize KS.2, which will house the test statistic (D) of the Kolmogorov-Smirnov tests on the bootstrap replicates 
KS.2 <- rep(NA, n.reps)

# Bootstrap process
for (i in 1:n.reps) {
  
  # Sample (with replacement) the lifespan distributions for the L1 and L1/4 treatments
  # Use the distributions of Expt 1, but with the realized sample sizes of Expt 2
  sample.01 <- sample(life.dist.01, size = n.target.01, replace = T)
  sample.04 <- sample(life.dist.04, size = n.target.04, replace = T)
  
  # Convert the sample lifespan distributions into relative lifespan distributions
  rel.sample.01 <- sample.01/mean(sample.01)
  rel.sample.04 <- sample.04/mean(sample.04)
  
  # Perform a Kolmogorov-Smirnov test on the relative lifespan distributions for the current replicate; extract D
  KS.2[i] <- suppressWarnings(ks.test(rel.sample.01, rel.sample.04)$statistic) # warning suppressed; we know about ties
  
}

# Calculate D.crit.2
# D.crit.2 is the value that the proportion 1 - targ.beta of KS.2 D's
# (on the bootstrap replicates) would be GREATER than
D.crit.2 <- sort(KS.2, decreasing = T)[n.reps*(1 - targ.beta)] # 0.1422 
D.crit.2.alt <- sort(KS.2, decreasing = F)[n.reps*(targ.beta)] # 0.1422; exactly the same

# Double check using a previous similar method; from before alpha.prime = 0.2490544
D.crit.2.alt.2 <- sqrt(-log(0.2490544/2)*0.5)*sqrt((102 + 104)/(102*104)) # 0.1422; same to four decimals

# Compare D.crit with what it would be for alpha = 0.05
D.crit.2.alpha.0.05 <- sqrt(-log(0.05/2)*0.5)*sqrt((102 + 104)/(102*104)) # 0.1892558
# Thus, D.crit has become *lower* than D.crit.2.alpha.0.05, which makes sense because a 
# *non*-significant KS test implies temporal scaling; # i.e., this makes the 
# test more conservative, which is important when drawing inference from a 
# non-sig result

# Check if there are ties
sum(KS.2 == D.crit.2) > 1 # TRUE; therefore, there are ties

# Recalculate D.crit, accounting for ties (more conservative approach)
# Correct for rounding errors associated with floating point arithmetic
D.crit.2.alt.3 <- max(KS.2[D.crit.2 - KS.2 > 1e-6]) # 0.1420 (a small amount lower)

# Double check that D.crit.2.alt.3 is the next step down from D.crit.2
u.2 <- max(which(sort(KS.2) < D.crit.2))
sort(KS.2)[(u.2 - 3):(u.2 + 3)]
# 0.1419683 0.1419683 0.1419683 0.1421569 0.1421569 0.1421569 0.1421569 # confirmed
# However, step-down was one position earlier than anticipated; this is due to rounding error
# associated with floating point arithmetic:
sort(KS.2)[u.2 + 1] - sort(KS.2)[u.2] # very small amount apart (2.775558e-17)
sort(KS.2)[u.2] - sort(KS.2)[u.2 - 1] # there's the real step (0.000188537)
D.crit.2 - D.crit.2.alt.3             # same (0.000188537)

# Generate the empirical cumulative distribution function for KS.2 D's 
KS.2.ecdf <- matrix(rep(NA, n.reps*2), ncol = 2)
KS.2.ecdf[ , 1] <- sort(KS.2) # column 1:  D-values in ascending order
for (i in 1:n.reps) {         # column 2:  proportion of D-values less or equal to the current one
  KS.2.ecdf[i, 2] <- sum(KS.2.ecdf[ , 1] <= KS.2.ecdf[i, 1])/n.reps
}

# Visually inspect empirical cumulative frequency distribution of KS.2 D's 
plot(x = KS.2.ecdf[, 1],
     y = KS.2.ecdf[, 2],
     xlim = c(0.05, 0.35),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.35, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.2.alt.3, D.crit.2.alt.3), c(0, 1), lty = 2)
text(x = D.crit.2.alt.3 + 0.005, y = 0, expression(paste(italic("D")[crit], " = 0.1420")), adj = c(0, 0))



##### 15.  Determine modified critical Kolmogorov-Smirnov value, D.crit, for potential use in Appendix I #####

# Calculate relative age at birth of every offspring for each focal (parent) plant 
# Relative age is absolute age divided by the age of the focal plant at the birth of an average offspring  
# Group them by light treatment
rel.par.age.01 <- numeric(0)
rel.par.age.04 <- numeric(0)
for (i in 1:nrow(cr.repro.aligned)) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr.repro.aligned[i, 1:cr$lifespan[i]])
  
  # Calculate age of the focal plant at the birth of an average offspring  
  mean.par.age <- sum(focal.repro*(1:cr$lifespan[i]))/sum(focal.repro)
  
  # Calculate distribution of relative ages for the focal plant
  # Be sure to include cases where there is more than one offspring born at particular age
  focal.rel.par.age <- numeric(0)
  for (j in 1:max(focal.repro)) { # j is the number born at particular age
    focal.rel.par.age <- c(focal.rel.par.age, which(focal.repro >= j)/mean.par.age)
  }
  focal.rel.par.age <- sort(focal.rel.par.age)
  
  # Group distribution of relative ages for the focal plant with others from the same light treatment
  # (only for L1 to L04)
  if (cr$light.treatment[i] == "1") {
    rel.par.age.01 <- c(rel.par.age.01, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/4") {
    rel.par.age.04 <- c(rel.par.age.04, focal.rel.par.age)
  } 
  
}

# Note that rel.par.age.01 and rel.par.age.04 both have a mean of 1
mean(rel.par.age.01)
mean(rel.par.age.04)

# Sort all rel.par.age.xx in ascending order
rel.par.age.01 <- sort(rel.par.age.01)
rel.par.age.04 <- sort(rel.par.age.04)

# Set sample sizes (based on total number of offspring in Experiment 2)
n.target.repro.01 <- 849 # treatment L1
n.target.repro.04 <- 1063 # treatment L1/4

# Initialize KS.2, which will house the test statistic (D) of the Kolmogorov-Smirnov tests on the bootstrap replicates 
# use the same number of reps as set in the previous section
KS.repro <- rep(NA, n.reps)

# Bootstrap process
for (i in 1:n.reps) {
  
  # Sample (with replacement) the rel age at reproduction distributions for the L1 and L1/4 treatments
  # Use the distributions of Expt 1, but with the realized sample sizes of Expt 2
  sample.repro.01 <- sample(rel.par.age.01, size = n.target.repro.01, replace = T)
  sample.repro.04 <- sample(rel.par.age.04, size = n.target.repro.04, replace = T)
  
  # Re-standardize the sample distributions so they have a mean of 1
  rel.sample.repro.01 <- sample.repro.01/mean(sample.repro.01)
  rel.sample.repro.04 <- sample.repro.04/mean(sample.repro.04)
  
  # Perform a Kolmogorov-Smirnov test on the relative lifespan distributions for the current replicate; extract D
  KS.repro[i] <- suppressWarnings(ks.test(rel.sample.repro.01, rel.sample.repro.04)$statistic) # warning suppressed; we know about ties
  
}

# Calculate D.crit.repro
# D.crit.repro is the value that the proportion 1 - targ.beta of KS.repro D's
# (on the bootstrap replicates) would be GREATER than
D.crit.repro <- sort(KS.repro, decreasing = T)[n.reps*(1 - targ.beta)] # 0.0697251 
D.crit.repro.alt <- sort(KS.repro, decreasing = F)[n.reps*(targ.beta)] # 0.0697251; exactly the same

# Compare D.crit.repro with what it would be for alpha = 0.05
D.crit.repro.alpha.0.05 <- sqrt(-log(0.05/2)*0.5)*sqrt((849 + 1063)/(849*1063)) # 0.06251089
# D.crit.repro is *greater* than this; so it is actually more conservative to *not* use a modified Dcrit
# but rather just to use a straight KS test (i.e., since a non-significant test implies temporal scaling)

# Check if there are ties
sum(KS.repro == D.crit.repro) > 1 # TRUE; therefore, there are ties

# Recalculate D.crit.repro, accounting for ties (more conservative approach)
# Correct for rounding errors associated with floating point arithmetic
D.crit.repro.alt.2 <- max(KS.repro[D.crit.repro - KS.repro > 1e-6]) 
# 0.06971735 (a small amount lower; still greater than D.crit.repro.alpha.0.05)

# Double check that D.crit.repro.alt.2 is the next step down from D.crit.repro
u.repro <- max(which(sort(KS.repro) < D.crit.repro))
sort(KS.repro)[(u.repro - 3):(u.repro + 3)]
# 0.06971402 0.06971402 0.06971735 0.06971735 0.06972510 0.06972510 0.06973286 # confirmed

# Generate the empirical cumulative distribution function for KS.2 D's 
KS.repro.ecdf <- matrix(rep(NA, n.reps*2), ncol = 2)
KS.repro.ecdf[ , 1] <- sort(KS.repro) # column 1:  D-values in ascending order
for (i in 1:n.reps) {                 # column 2:  proportion of D-values less or equal to the current one
  KS.repro.ecdf[i, 2] <- sum(KS.repro.ecdf[ , 1] <= KS.repro.ecdf[i, 1])/n.reps
}

# Visually inspect empirical cumulative frequency distribution of KS.2 D's 
plot(x = KS.repro.ecdf[, 1],
     y = KS.repro.ecdf[, 2],
     xlim = c(0.04, 0.14),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.14, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.repro.alt.2, D.crit.repro.alt.2), c(0, 1), lty = 2)
text(x = D.crit.repro.alt.2 + 0.003, y = 0, expression(paste(italic("D")[crit], " = 0.06972 (provisional)")), adj = c(0, 0))



##### PART V. DATA ANALYSIS: FROND SIZE #####



##### 16.  Load frond size and shape data and perform preliminary processing #####

# Load size and shape data
size <- read.csv('CR_size_and_shape.csv', header = T)

# Change light treatment names to be less cryptic 
size$treatment[size$treatment == "L01"] <- "1"
size$treatment[size$treatment == "L02"] <- "1/2"
size$treatment[size$treatment == "L04"] <- "1/4"
size$treatment[size$treatment == "L08"] <- "1/8"
size$treatment[size$treatment == "L16"] <- "1/16"
size$treatment[size$treatment == "L32"] <- "1/32"
size$treatment[size$treatment == "L00"] <- "0"
size$treatment <- factor(size$treatment, c("1", "1/2", "1/4", "1/8", "1/16", "1/32", "0"))

# Exclude rows (e.g., due to damaged or dried fronds, or those without photos)
size <- size[size$exclude == "No", ]



##### 17.  Analyze frond area (ANOVA) #####

# Visually inspect boxplot of frond area
boxplot(Area.mm ~ treatment, dat = size, ylim = c(2, 7), las = 1, whisklty = 1, col = "white", 
        xlab = "Light intensity treatment", ylab = "Area (mm^2)")

# One-way ANOVA on Area.mm (omitting 1/32 and 0 light intensity treatments)
Area.mm.aov <- aov(Area.mm ~ treatment, dat = size)
anova(Area.mm.aov)

# Analysis of Variance Table
#
# Response: Area.mm
#            Df Sum Sq Mean Sq F value Pr(>F)
# treatment   6  2.951 0.49187  1.0161 0.4168
# Residuals 158 76.481 0.48406

# Model diagnostics
plot(x = Area.mm.aov$fitted.values, y = Area.mm.aov$residuals)
hist(Area.mm.aov$residuals)
qqnorm(Area.mm.aov$residuals)



##### PART VI. FIGURES (.tif versions) #####



##### 18.  Fig. 1.  Boxplots for lifespan, total offspring, and intrinsic rate of natural increase #####

# Create Fig. 1
tiff(file = "Fig01_boxplots.tiff", width = 5, height = 10, units = "in", res = 600, compression = "lzw")
par(mfrow = c(3, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Panel (a) - boxplot of lifespan versus light treatment
boxplot(lifespan ~ light.treatment, dat = cr, ylim = c(0, 150), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
lifespan.mean <- tapply(cr$lifespan, INDEX = cr$light.treatment, FUN = mean)
points(lifespan.mean, cex = 2, pch = 16, col = "green")
lines(1 - log2(MMpow.1to32.nls.x), MMpow.1to32.nls.y, col = "blue", lwd = 2) # Michaelis-Menten-power-law, treatments 1 to 1/32
lines(1 - log2(MMpow.1to16.nls.x), MMpow.1to16.nls.y, col = "red", lwd = 2)  # Michaelis-Menten-power-law, treatments 1 to 1/16
set.seed(123) # so jittered points are always the same
light.treatment.jitter <- as.numeric(cr$light.treatment) + rnorm(length(cr$light.treatment), 0, 0.05)
points(x = light.treatment.jitter, y = cr$lifespan, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
abline(v = 5.5, lty = 2)
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/2"])),
                                                                              expression(paste(italic("L")["1/4"])),
                                                                              expression(paste(italic("L")["1/8"])),
                                                                              expression(paste(italic("L")["1/16"])),
                                                                              expression(paste(italic("L")["1/32"])),
                                                                              expression(paste(italic("L")["0"]))))
axis(2, at = seq(0, 150, 25), labels = seq(0, 150, 25), las = 1, cex.axis = 1.3, tck = -0.03)
axis(3, at = 1:7, line = -0.5, lwd = 0, cex.axis = 1.00, tck = 0, labels = c(expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 31")),
                                                                             expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 31")),
                                                                             expression(paste(italic("n "), "= 28"))))
mtext("Lifespan (days)", side = 2, line = 3.7)
mtext("(a)", side = 2, line = 4.5, at = 150, las = 1, cex = 1.3)
text(1, 150, "A")  # 1
text(2, 150, "B")  # 1/2
text(3, 150, "B")  # 1/4
text(4, 150, "C")  # 1/8
text(5, 150, "D")  # 1/16

legend("topleft", legend = c(expression(paste(italic("L")["1"], " to ", italic("L")["1/16"])), 
                             expression(paste(italic("L")["1"], " to ", italic("L")["1/32"]))),
       title = "Michaelis-Menten / power law fits",
       col = c("red", "blue"), lty = 1, lwd = 2, bty = "n", inset = c(0.02, 0.12))


# Panel (b) - boxplot of total number of offspring versus light treatment
boxplot(total.offspring ~ light.treatment, dat = cr, ylim = c(0, 25), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
total.offspring.mean <- tapply(cr$total.offspring, INDEX = cr$light.treatment, FUN = mean)
points(total.offspring.mean, cex = 2, pch = 16, col = "green")
light.treatment.jitter <- as.numeric(cr$light.treatment) + rnorm(length(cr$light.treatment), 0, 0.05)
points(x = light.treatment.jitter, y = cr$total.offspring, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
abline(v = 5.5, lty = 2)
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/2"])),
                                                                              expression(paste(italic("L")["1/4"])),
                                                                              expression(paste(italic("L")["1/8"])),
                                                                              expression(paste(italic("L")["1/16"])),
                                                                              expression(paste(italic("L")["1/32"])),
                                                                              expression(paste(italic("L")["0"]))))
axis(2, at = seq(0, 25, 5), labels = seq(0, 25, 5), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Total number of offspring", side = 2, line = 3.7)
mtext("(b)", side = 2, line = 4.5, at = 25, las = 1, cex = 1.3)
text(1, 25, "A")  # 1
text(2, 25, "AB") # 1/2
text(3, 25, "B")  # 1/4
text(4, 25, "B")  # 1/8
text(5, 25, "B")  # 1/16


# Panel (c) - boxplot of intrinsic rate of increase versus light treatment
boxplot(r ~ light.treatment, dat = cr, las = 1, ylim = c(0, 0.4), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
r.mean <- tapply(cr$r, INDEX = cr$light.treatment, FUN = mean)
points(r.mean, cex = 2, pch = 16, col = "green")
light.treatment.jitter <- as.numeric(cr$light.treatment) + rnorm(length(cr$light.treatment), 0, 0.05)
points(x = light.treatment.jitter, y = cr$r, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
abline(v = 5.5, lty = 2)
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/2"])),
                                                                              expression(paste(italic("L")["1/4"])),
                                                                              expression(paste(italic("L")["1/8"])),
                                                                              expression(paste(italic("L")["1/16"])),
                                                                              expression(paste(italic("L")["1/32"])),
                                                                              expression(paste(italic("L")["0"]))))
axis(2, at = seq(0, 0.4, 0.1), labels = c("0.0", "0.1", "0.2", "0.3", "0.4"), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Light intensity treatment", side = 1, line = 3.7)
mtext(expression(paste("Intrinsic rate of increase (", italic("r"), ")")), side = 2, line = 3.7)
mtext("(c)", side = 2, line = 4.5, at = 0.4, las = 1, cex = 1.3)
text(1, 0.4, "D")  # 1
text(2, 0.4, "DC") # 1/2
text(3, 0.4, "C")  # 1/4
text(4, 0.4, "B")  # 1/8
text(5, 0.4, "A")  # 1/16

# Close device
dev.off()



##### 19.  Fig. 2.  Survival plots #####

# Create Fig. 2
tiff(file = "Fig02_survival.tiff", width = 10, height = 5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 2), mar = c(4.0, 3.0, 0.0, 0.0), oma = c(1.0, 4.0, 1.0, 1.0))

# Panel (a) - Plot of survival versus age in days 
plot(p.surv.cum ~ age, dat = lifeTab.01, type = "n", axes = F, 
     xlim = c(0, 160), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 150, 25), labels = seq(0, 150, 25), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Absolute age (days)", side = 1, line = 2.7)
mtext("Proportion surviving", side = 2, line = 3.2)
text(0, 0.04, "(a)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age, dat = lifeTab.01, type = "s", col = "#000000", lwd = 2) 
points(p.surv.cum ~ age, dat = lifeTab.02, type = "s", col = "#FF0000", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.04, type = "s", col = "#FFA500", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.08, type = "s", col = "#00FF00", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.16, type = "s", col = "#00FFFF", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.32, type = "s", col = "#0000FF", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.00, type = "s", col = "#FF00FF", lwd = 2)
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])),
                expression(paste(italic("L")["1/32"])),
                expression(paste(italic("L")["0"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF", "#0000FF", "#FF00FF"), 
       lty = 1, lwd = 2, bty = "n", cex = 0.7, inset = 0.02)


# Panel (b) - Plot of survival versus age in lifespans 
plot(p.surv.cum ~ age.rel,  dat = lifeTab.01, type = "n", axes = F,
     xlim = c(0, 2.2), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 2, 0.5), labels = c("0.0", "0.5", "1.0", "1.5", "2.0"), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Relative age (mean lifespans)", side = 1, line = 2.7)
text(0, 0.04, "(b)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age.rel, dat = lifeTab.01, type = "s", col = "#000000", lwd = 2) 
points(p.surv.cum ~ age.rel, dat = lifeTab.02, type = "s", col = "#FF0000", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.04, type = "s", col = "#FFA500", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.08, type = "s", col = "#00FF00", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.16, type = "s", col = "#00FFFF", lwd = 2)
# points and lines for 1/32 and 0 treatments omitted because mean lifespan (and therefore relative age) cannot be calculated 
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF"), 
       lty = 1, lwd = 2, bty = "n", cex = 0.7, inset = 0.02)

# Close device
dev.off()



##### 20.  Fig. D1 (Supporting information).  Interaction plot for light intensity #####

# Fit intercept for line with slope of log10(1/2)
a1 <- mean(log10(light$PAR[light$treatment != '0']) - log10(1/2)*rep(0:5, times = 1, each = 10))

# Fit line and get intercept and slope 
x <- rep(1:6, times = 1, each = 10)
PAR.lm <- lm(log10(light$PAR[light$treatment != '0']) ~ x)
a2 <- PAR.lm$coefficients[1]
b2 <- PAR.lm$coefficients[2]

# Create Fig. D1
tiff(file = "FigD1_PAR.tiff", width = 5, height = 4.5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 1), mar = c(4.0, 5.0, 1.0, 1.0))

# Make interaction plot
plot(PAR.mean[1:7], log = 'y',
     type = 'n',
     xaxt = "n", 
     xlab = "Light intensity treatment", 
     ylab = expression(paste("Mean PAR ± SEM (", mu, "mol m"^"-2", " s"^"-1",")")),
     xlim = c(0.5, 7.5),
     ylim = c(0.9, 600), 
     las = 1)
lines(x = c(1, 6), y = c(10^a1, 10^a1/32), col = 'grey', lty = 1, lwd = 6)
lines(x = c(1, 6), y = c(10^(a2 + b2*1), 10^(a2 + b2*6)), lty = 2)
points(PAR.mean[1:7], cex = 1.25, pch = 16)
lines(PAR.mean[1:7])
a.size <- 0.05
arrows(1, PAR.mean[1]  + PAR.sem[1],  1, PAR.mean[1]  - PAR.sem[1],  angle = 90, length = a.size, code = 3)
arrows(2, PAR.mean[2]  + PAR.sem[2],  2, PAR.mean[2]  - PAR.sem[2],  angle = 90, length = a.size, code = 3)
arrows(3, PAR.mean[3]  + PAR.sem[3],  3, PAR.mean[3]  - PAR.sem[3],  angle = 90, length = a.size, code = 3)
arrows(4, PAR.mean[4]  + PAR.sem[4],  4, PAR.mean[4]  - PAR.sem[4],  angle = 90, length = a.size, code = 3)
arrows(5, PAR.mean[5]  + PAR.sem[5],  5, PAR.mean[5]  - PAR.sem[5],  angle = 90, length = a.size, code = 3)
arrows(6, PAR.mean[6]  + PAR.sem[6],  6, PAR.mean[6]  - PAR.sem[6],  angle = 90, length = a.size, code = 3)
arrows(7, PAR.mean[7]  + PAR.sem[7],  7, PAR.mean[7]  - PAR.sem[7],  angle = 90, length = a.size, code = 3)
arrows(1, PAR.mean[8]  + PAR.sem[8],  1, PAR.mean[8]  - PAR.sem[8],  angle = 90, length = a.size, code = 3)
arrows(2, PAR.mean[9]  + PAR.sem[9],  2, PAR.mean[9]  - PAR.sem[9],  angle = 90, length = a.size, code = 3)
arrows(3, PAR.mean[10] + PAR.sem[10], 3, PAR.mean[10] - PAR.sem[10], angle = 90, length = a.size, code = 3)
arrows(4, PAR.mean[11] + PAR.sem[11], 4, PAR.mean[11] - PAR.sem[11], angle = 90, length = a.size, code = 3)
arrows(5, PAR.mean[12] + PAR.sem[12], 5, PAR.mean[12] - PAR.sem[12], angle = 90, length = a.size, code = 3)
arrows(6, PAR.mean[13] + PAR.sem[13], 6, PAR.mean[13] - PAR.sem[13], angle = 90, length = a.size, code = 3)
arrows(7, PAR.mean[14] + PAR.sem[14], 7, PAR.mean[14] - PAR.sem[14], angle = 90, length = a.size, code = 3)
lines(PAR.mean[8:14])
points(PAR.mean[8:14], cex = 1.25, pch = 21, bg = "white")
axis(1, at = 1:7, labels = c(expression(paste(italic("L")["1"])),
                             expression(paste(italic("L")["1/2"])),
                             expression(paste(italic("L")["1/4"])),
                             expression(paste(italic("L")["1/8"])),
                             expression(paste(italic("L")["1/16"])),
                             expression(paste(italic("L")["1/32"])),
                             expression(paste(italic("L")["0"]))))
legend("topright", c("top", "bottom"), title = "Shelf", bty = 'n',  
       pch = c(16, 21), pt.cex = 1.25, lty = FALSE, inset = c(0.05, 0.18))
legend("bottomleft", c("best-fit line with anticipated slope", "best-fit line"), bty = 'n', lwd = c(6, 1), 
       lty = c(1, 2), col = c("grey", "black"), inset = 0.03)
text(1, 600, "G") # 1
text(2, 600, "F") # 1/2
text(3, 600, "E") # 1/4
text(4, 600, "D") # 1/8
text(5, 600, "C") # 1/16
text(6, 600, "B") # 1/32
text(7, 600, "A") # 0

# Close device
dev.off()



##### 21.  Fig. E1 (Supporting information).  Interaction plot for temperature #####

# Create Fig. E1
tiff(file = "FigE1_temperature.tiff", width = 5, height = 4.5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 1), mar = c(4.0, 5.0, 1.0, 1.0))

# Make interaction plot
plot(temp.mean[1:7], 
     xaxt = "n", 
     xlab = "Light intensity treatment", 
     ylab = "Mean temperature ± SEM (\u00B0C)",
     xlim = c(0.5, 7.5),
     ylim = c(23, 30), 
     las = 1,
     cex = 1.25,
     pch = 16)
lines(temp.mean[1:7])
a.size <- 0.05
arrows(1, temp.mean[1]  + temp.sem[1],  1, temp.mean[1]  - temp.sem[1],  angle = 90, length = a.size, code = 3)
arrows(2, temp.mean[2]  + temp.sem[2],  2, temp.mean[2]  - temp.sem[2],  angle = 90, length = a.size, code = 3)
arrows(3, temp.mean[3]  + temp.sem[3],  3, temp.mean[3]  - temp.sem[3],  angle = 90, length = a.size, code = 3)
arrows(4, temp.mean[4]  + temp.sem[4],  4, temp.mean[4]  - temp.sem[4],  angle = 90, length = a.size, code = 3)
arrows(5, temp.mean[5]  + temp.sem[5],  5, temp.mean[5]  - temp.sem[5],  angle = 90, length = a.size, code = 3)
arrows(6, temp.mean[6]  + temp.sem[6],  6, temp.mean[6]  - temp.sem[6],  angle = 90, length = a.size, code = 3)
arrows(7, temp.mean[7]  + temp.sem[7],  7, temp.mean[7]  - temp.sem[7],  angle = 90, length = a.size, code = 3)
arrows(1, temp.mean[8]  + temp.sem[8],  1, temp.mean[8]  - temp.sem[8],  angle = 90, length = a.size, code = 3)
arrows(2, temp.mean[9]  + temp.sem[9],  2, temp.mean[9]  - temp.sem[9],  angle = 90, length = a.size, code = 3)
arrows(3, temp.mean[10] + temp.sem[10], 3, temp.mean[10] - temp.sem[10], angle = 90, length = a.size, code = 3)
arrows(4, temp.mean[11] + temp.sem[11], 4, temp.mean[11] - temp.sem[11], angle = 90, length = a.size, code = 3)
arrows(5, temp.mean[12] + temp.sem[12], 5, temp.mean[12] - temp.sem[12], angle = 90, length = a.size, code = 3)
arrows(6, temp.mean[13] + temp.sem[13], 6, temp.mean[13] - temp.sem[13], angle = 90, length = a.size, code = 3)
arrows(7, temp.mean[14] + temp.sem[14], 7, temp.mean[14] - temp.sem[14], angle = 90, length = a.size, code = 3)
lines(temp.mean[8:14])
points(temp.mean[8:14], cex = 1.25, pch = 21, bg = "white")
axis(1, at = 1:7, labels = c(expression(paste(italic("L")["1"])),
                             expression(paste(italic("L")["1/2"])),
                             expression(paste(italic("L")["1/4"])),
                             expression(paste(italic("L")["1/8"])),
                             expression(paste(italic("L")["1/16"])),
                             expression(paste(italic("L")["1/32"])),
                             expression(paste(italic("L")["0"]))))
legend("topleft", c("top", "bottom"), title = "Shelf", bty = 'n',  
       pch = c(16, 21), pt.cex = 1.25, lty = FALSE, inset = c(0.05, 0.13))
text(1, 30, "BA") # 1
text(2, 30, "BA") # 1/2
text(3, 30, "BA") # 1/4
text(4, 30, "BA") # 1/8
text(5, 30, "B")  # 1/16
text(6, 30, "B")  # 1/32
text(7, 30, "A")  # 0

# Close device
dev.off()



##### 22.  Fig. F1 (Supporting information).  Boxplot for frond area #####

# Create Fig. F1
tiff(file = "FigF1_boxplot.tiff", width = 5, height = 4.5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 1), mar = c(3.0, 3.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Boxplot of area versus light treatment
boxplot(Area.mm ~ treatment, dat = size, ylim = c(2, 7), axes = F, cex = 1.0, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
Area.mm.mean <- tapply(size$Area.mm, INDEX = size$treatment, FUN = mean)
points(Area.mm.mean, cex = 2, pch = 16, col = "green")
light.treatment.jitter <- as.numeric(size$treatment) + rnorm(length(size$treatment), 0, 0.05)
points(x = light.treatment.jitter, y = size$Area.mm, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.0, tck = 0.00, line = 0.25, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                               expression(paste(italic("L")["1/2"])),
                                                                               expression(paste(italic("L")["1/4"])),
                                                                               expression(paste(italic("L")["1/8"])),
                                                                               expression(paste(italic("L")["1/16"])),
                                                                               expression(paste(italic("L")["1/32"])),
                                                                               expression(paste(italic("L")["0"]))))
axis(2, at = seq(2, 7, 1), labels = seq(2, 7, 1), las = 1, cex.axis = 1.0, tck = -0.03)
axis(3, at = 1:7, line = -0.5, lwd = 0, cex.axis = 0.7, tck = 0, labels = c(expression(paste(italic("n "), "= 16")),
                                                                            expression(paste(italic("n "), "= 23")),
                                                                            expression(paste(italic("n "), "= 28")),
                                                                            expression(paste(italic("n "), "= 26")),
                                                                            expression(paste(italic("n "), "= 25")),
                                                                            expression(paste(italic("n "), "= 21")),
                                                                            expression(paste(italic("n "), "= 26"))))
mtext("Light intensity treatment", side = 1, line = 2.7)
mtext(expression(paste("Area (mm"^"2"*")")), side = 2, line = 2.7)

# Close device
dev.off()



##### 23.  Fig. H1 (Supporting information).  ECDFs for Kolmogorov-Smirnov's D #####

# Create Fig. H1
tiff(file = "FigH1_ECDF.tiff", width = 5, height = 7, units = "in", res = 600, compression = "lzw")
par(mfrow = c(2, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Panel (a) - using initial sample sizes  
plot(x = KS.ecdf[, 1],
     y = KS.ecdf[, 2],
     xlim = c(0.05, 0.35),
     ylim = c(0, 1),
     xlab = NA,
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)
text(0.05, 1, "(a)", cex = 1.3, adj = c(0, 1))

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.35, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.alt.3, D.crit.alt.3), c(0, 1), lty = 2)
text(x = D.crit.alt.3 + 0.005, y = 0, expression(paste(italic("D")[crit], " = 0.1339")), adj = c(0, 0))

# Panel (b) - using realized final sample sizes
plot(x = KS.2.ecdf[, 1],
     y = KS.2.ecdf[, 2],
     xlim = c(0.05, 0.35),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)
text(0.05, 1, "(b)", cex = 1.3, adj = c(0, 1))

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.35, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.2.alt.3, D.crit.2.alt.3), c(0, 1), lty = 2)
text(x = D.crit.2.alt.3 + 0.005, y = 0, expression(paste(italic("D")[crit], " = 0.1420")), adj = c(0, 0))

dev.off()



##### 24.  Fig. I1 (Supporting information).  Proportion of offspring not yet born #####

# Create Fig. I1
tiff(file = "FigI1_reproduction.tiff", width = 10, height = 5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 2), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(3.0, 3.0, 1.0, 1.0))

# Panel (a) number of offspring not yet born versus age (by individual)
plot(0,
     type = "n", 
     las = 1, 
     xlim = c(0, 140),
     ylim = c(0, 20),
     xlab = "Absolute age", 
     ylab = "Number of offspring not yet born")
mtext("(days)", side = 1, line = 4, cex = 0.8)

# Add the lines for each individual (But add them in a random order so it doesn't privilege the last-added treatments as top layers)
lineorder <- sample(1:nrow(cr.repro.aligned), replace = F)
for (i in lineorder) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr.repro.aligned[i, 1:cr$lifespan[i]])

  # Determine cumulative number not yet born at each age
  focal.n.not.born.cum <- c(sum(focal.repro), sum(focal.repro) - cumsum(focal.repro[1:(length(focal.repro) - 1)]))
  
  # Determine the line colour, according to light treatment
  if (cr$light.treatment[i] == "1") {
    linecolour <- "#000000"
  } else if (cr$light.treatment[i] == "1/2") {
    linecolour <- "#FF0000"
  } else if (cr$light.treatment[i] == "1/4") {
    linecolour <- "#FFA500"
  } else if (cr$light.treatment[i] == "1/8") {
    linecolour <- "#00FF00"
  } else if (cr$light.treatment[i] == "1/16") {
    linecolour <- "#00FFFF"
  }  
  
  # Jitter points to make step plots easier to distinguish
  jitter.max.y <- 0.2 # recommend less than 0.5 so jittering cannot change the order of points
  focal.n.not.born.cum.jitter <- focal.n.not.born.cum 
  focal.n.not.born.cum.jitter[1] <- focal.n.not.born.cum.jitter[1] + runif(1, min = -jitter.max.y, max = jitter.max.y) 
  for (j in 2:length(focal.repro)) {
    if (focal.n.not.born.cum[j] == focal.n.not.born.cum[j - 1]) {
      focal.n.not.born.cum.jitter[j] <- focal.n.not.born.cum.jitter[j - 1] 
    } else {
      focal.n.not.born.cum.jitter[j] <- focal.n.not.born.cum.jitter[j] + runif(1, min = -jitter.max.y, max = jitter.max.y) 
    }   
  }
  
  # Add the line to the plot
  jitter.max.x <- 0.4 # recommend less than 0.5 so jittering cannot change the order of points
  if ((cr$light.treatment[i] != "1/32") & (cr$light.treatment[i] != "0")) {
    lines(x = 1:length(focal.repro) + runif(length(focal.repro), min = -jitter.max.x, max = jitter.max.x),
          y = focal.n.not.born.cum.jitter,
          type = "s",
          lwd = 1,
          col = linecolour) 
  }
}

# Add the legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000",
               "#FF0000",
               "#FFA500",
               "#00FF00",
               "#00FFFF"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 140, y = 0, "(a)", adj = c(1, 0), cex = 1.25)


# Panel (b) proportion of offspring not yet born versus relative age (by treatment)

# Calculate relative age at birth of every offspring for each focal (parent) plant 
# Relative age is absolute age divided by the age of the focal plant at the birth of an average offspring  
# Group them by light treatment
rel.par.age.01 <- numeric(0)
rel.par.age.02 <- numeric(0)
rel.par.age.04 <- numeric(0)
rel.par.age.08 <- numeric(0)
rel.par.age.16 <- numeric(0)
for (i in 1:nrow(cr.repro.aligned)) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr.repro.aligned[i, 1:cr$lifespan[i]])
  
  # Calculate age of the focal plant at the birth of an average offspring  
  mean.par.age <- sum(focal.repro*(1:cr$lifespan[i]))/sum(focal.repro)

  # Calculate distribution of relative ages for the focal plant
  # Be sure to include cases where there is more than one offspring born at particular age
  focal.rel.par.age <- numeric(0)
  for (j in 1:max(focal.repro)) { # j is the number born at particular age
    focal.rel.par.age <- c(focal.rel.par.age, which(focal.repro >= j)/mean.par.age)
  }
  focal.rel.par.age <- sort(focal.rel.par.age)
  
  # Group distribution of relative ages for the focal plant with others from the same light treatment
  # (only for L1 to L16, i.e., for which total reproduction is known for every individual)
  if (cr$light.treatment[i] == "1") {
    rel.par.age.01 <- c(rel.par.age.01, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/2") {
    rel.par.age.02 <- c(rel.par.age.02, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/4") {
    rel.par.age.04 <- c(rel.par.age.04, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/8") {
    rel.par.age.08 <- c(rel.par.age.08, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/16") {
    rel.par.age.16 <- c(rel.par.age.16, focal.rel.par.age)
  } 
  
}

# Note that all rel.par.age.xx have a mean of 1
mean(rel.par.age.01)
mean(rel.par.age.02)
mean(rel.par.age.04)
mean(rel.par.age.08)
mean(rel.par.age.16)

# Sort all rel.par.age.xx in ascending order
rel.par.age.01 <- sort(rel.par.age.01)
rel.par.age.02 <- sort(rel.par.age.02)
rel.par.age.04 <- sort(rel.par.age.04)
rel.par.age.08 <- sort(rel.par.age.08)
rel.par.age.16 <- sort(rel.par.age.16)

# Calculate cumulative proportion of offspring not yet born, grouped by light treatment
p.not.born.cum.01 <- rep(NA, length(rel.par.age.01))
p.not.born.cum.02 <- rep(NA, length(rel.par.age.02))
p.not.born.cum.04 <- rep(NA, length(rel.par.age.04))
p.not.born.cum.08 <- rep(NA, length(rel.par.age.08))
p.not.born.cum.16 <- rep(NA, length(rel.par.age.16))
for (i in 1:length(rel.par.age.01)) { p.not.born.cum.01[i] <- sum(rel.par.age.01 >= rel.par.age.01[i])/length(rel.par.age.01) }
for (i in 1:length(rel.par.age.02)) { p.not.born.cum.02[i] <- sum(rel.par.age.02 >= rel.par.age.02[i])/length(rel.par.age.02) }
for (i in 1:length(rel.par.age.04)) { p.not.born.cum.04[i] <- sum(rel.par.age.04 >= rel.par.age.04[i])/length(rel.par.age.04) }
for (i in 1:length(rel.par.age.08)) { p.not.born.cum.08[i] <- sum(rel.par.age.08 >= rel.par.age.08[i])/length(rel.par.age.08) }
for (i in 1:length(rel.par.age.16)) { p.not.born.cum.16[i] <- sum(rel.par.age.16 >= rel.par.age.16[i])/length(rel.par.age.16) }

# Plot grouped data (Proportion of offspring not yet born vs relative age)
plot(x = rel.par.age.01,  
     y = p.not.born.cum.01, 
     type = "s", 
     las = 1,
     xlim = c(0, 2.5), 
     ylim = c(0, 1),
     xlab = "Relative age",
     ylab = "Proportion of offspring not yet born",
     col = "#000000")
mtext("(scaled to age at birth of average offspring)", side = 1, line = 4, cex = 0.8)
lines(x = rel.par.age.02, y = p.not.born.cum.02, type = "s", col = "#FF0000")
lines(x = rel.par.age.04, y = p.not.born.cum.04, type = "s", col = "#FFA500")
lines(x = rel.par.age.08, y = p.not.born.cum.08, type = "s", col = "#00FF00")
lines(x = rel.par.age.16, y = p.not.born.cum.16, type = "s", col = "#00FFFF")

# Add legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 0, y = 0, "(b)", adj = c(0, 0), cex = 1.25)

dev.off()



##### 25.  Fig. I3 (Supporting information).  ECDF for Kolmogorov-Smirnov's D (for reproduction) #####

# Create Fig. I3
tiff(file = "FigI3_ECDF.tiff", width = 5, height = 4, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

plot(x = KS.repro.ecdf[, 1],
     y = KS.repro.ecdf[, 2],
     xlim = c(0.04, 0.14),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.14, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.repro.alt.2, D.crit.repro.alt.2), c(0, 1), lty = 2)
text(x = D.crit.repro.alt.2 + 0.003, y = 0, expression(paste(italic("D")[crit], " = 0.06972 (provisional)")), adj = c(0, 0))

dev.off()



##### PART VII. FIGURES (.emf versions) #####



##### 26.  Fig. 1.  Boxplots for lifespan, total offspring, and intrinsic rate of natural increase #####

# Create Fig. 1
emf(file = "Fig01_boxplots.emf", width = 5, height = 10, units = "in", coordDPI = 1200)
par(mfrow = c(3, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Panel (a) - boxplot of lifespan versus light treatment
boxplot(lifespan ~ light.treatment, dat = cr, ylim = c(0, 150), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
lifespan.mean <- tapply(cr$lifespan, INDEX = cr$light.treatment, FUN = mean)
points(lifespan.mean, cex = 2, pch = 16, col = "green")
lines(1 - log2(MMpow.1to32.nls.x), MMpow.1to32.nls.y, col = "blue", lwd = 2) # Michaelis-Menten-power-law, treatments 1 to 1/32
lines(1 - log2(MMpow.1to16.nls.x), MMpow.1to16.nls.y, col = "red", lwd = 2)  # Michaelis-Menten-power-law, treatments 1 to 1/16
set.seed(123) # so jittered points are always the same
light.treatment.jitter <- as.numeric(cr$light.treatment) + rnorm(length(cr$light.treatment), 0, 0.05)
points(x = light.treatment.jitter, y = cr$lifespan, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
abline(v = 5.5, lty = 2)
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/2"])),
                                                                              expression(paste(italic("L")["1/4"])),
                                                                              expression(paste(italic("L")["1/8"])),
                                                                              expression(paste(italic("L")["1/16"])),
                                                                              expression(paste(italic("L")["1/32"])),
                                                                              expression(paste(italic("L")["0"]))))
axis(2, at = seq(0, 150, 25), labels = seq(0, 150, 25), las = 1, cex.axis = 1.3, tck = -0.03)
axis(3, at = 1:7, line = -0.5, lwd = 0, cex.axis = 1.00, tck = 0, labels = c(expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 31")),
                                                                             expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 32")),
                                                                             expression(paste(italic("n "), "= 31")),
                                                                             expression(paste(italic("n "), "= 28"))))
mtext("Lifespan (days)", side = 2, line = 3.7)
mtext("(a)", side = 2, line = 4.5, at = 150, las = 1, cex = 1.3)
text(1, 150, "A")  # 1
text(2, 150, "B")  # 1/2
text(3, 150, "B")  # 1/4
text(4, 150, "C")  # 1/8
text(5, 150, "D")  # 1/16

legend("topleft", legend = c(expression(paste(italic("L")["1"], " to ", italic("L")["1/16"])), 
                             expression(paste(italic("L")["1"], " to ", italic("L")["1/32"]))),
       title = "Michaelis-Menten / power law fits",
       col = c("red", "blue"), lty = 1, lwd = 2, bty = "n", inset = c(0.02, 0.12))


# Panel (b) - boxplot of total number of offspring versus light treatment
boxplot(total.offspring ~ light.treatment, dat = cr, ylim = c(0, 25), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
total.offspring.mean <- tapply(cr$total.offspring, INDEX = cr$light.treatment, FUN = mean)
points(total.offspring.mean, cex = 2, pch = 16, col = "green")
light.treatment.jitter <- as.numeric(cr$light.treatment) + rnorm(length(cr$light.treatment), 0, 0.05)
points(x = light.treatment.jitter, y = cr$total.offspring, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
abline(v = 5.5, lty = 2)
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/2"])),
                                                                              expression(paste(italic("L")["1/4"])),
                                                                              expression(paste(italic("L")["1/8"])),
                                                                              expression(paste(italic("L")["1/16"])),
                                                                              expression(paste(italic("L")["1/32"])),
                                                                              expression(paste(italic("L")["0"]))))
axis(2, at = seq(0, 25, 5), labels = seq(0, 25, 5), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Total number of offspring", side = 2, line = 3.7)
mtext("(b)", side = 2, line = 4.5, at = 25, las = 1, cex = 1.3)
text(1, 25, "A")  # 1
text(2, 25, "AB") # 1/2
text(3, 25, "B")  # 1/4
text(4, 25, "B")  # 1/8
text(5, 25, "B")  # 1/16


# Panel (c) - boxplot of intrinsic rate of increase versus light treatment
boxplot(r ~ light.treatment, dat = cr, las = 1, ylim = c(0, 0.4), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
r.mean <- tapply(cr$r, INDEX = cr$light.treatment, FUN = mean)
points(r.mean, cex = 2, pch = 16, col = "green")
light.treatment.jitter <- as.numeric(cr$light.treatment) + rnorm(length(cr$light.treatment), 0, 0.05)
points(x = light.treatment.jitter, y = cr$r, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
abline(v = 5.5, lty = 2)
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/2"])),
                                                                              expression(paste(italic("L")["1/4"])),
                                                                              expression(paste(italic("L")["1/8"])),
                                                                              expression(paste(italic("L")["1/16"])),
                                                                              expression(paste(italic("L")["1/32"])),
                                                                              expression(paste(italic("L")["0"]))))
axis(2, at = seq(0, 0.4, 0.1), labels = c("0.0", "0.1", "0.2", "0.3", "0.4"), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Light intensity treatment", side = 1, line = 3.7)
mtext(expression(paste("Intrinsic rate of increase (", italic("r"), ")")), side = 2, line = 3.7)
mtext("(c)", side = 2, line = 4.5, at = 0.4, las = 1, cex = 1.3)
text(1, 0.4, "D")  # 1
text(2, 0.4, "DC") # 1/2
text(3, 0.4, "C")  # 1/4
text(4, 0.4, "B")  # 1/8
text(5, 0.4, "A")  # 1/16

# Close device
dev.off()



##### 27.  Fig. 2.  Survival plots #####

# Create Fig. 2
emf(file = "Fig02_survival.emf", width = 10, height = 5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 2), mar = c(4.0, 3.0, 0.0, 0.0), oma = c(1.0, 4.0, 1.0, 1.0))

# Panel (a) - Plot of survival versus age in days 
plot(p.surv.cum ~ age, dat = lifeTab.01, type = "n", axes = F, 
     xlim = c(0, 160), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 150, 25), labels = seq(0, 150, 25), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Absolute age (days)", side = 1, line = 2.7)
mtext("Proportion surviving", side = 2, line = 3.2)
text(0, 0.04, "(a)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age, dat = lifeTab.01, type = "s", col = "#000000", lwd = 2) 
points(p.surv.cum ~ age, dat = lifeTab.02, type = "s", col = "#FF0000", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.04, type = "s", col = "#FFA500", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.08, type = "s", col = "#00FF00", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.16, type = "s", col = "#00FFFF", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.32, type = "s", col = "#0000FF", lwd = 2)
points(p.surv.cum ~ age, dat = lifeTab.00, type = "s", col = "#FF00FF", lwd = 2)
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])),
                expression(paste(italic("L")["1/32"])),
                expression(paste(italic("L")["0"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF", "#0000FF", "#FF00FF"), 
       lty = 1, lwd = 2, bty = "n", cex = 0.7, inset = 0.02)


# Panel (b) - Plot of survival versus age in lifespans 
plot(p.surv.cum ~ age.rel,  dat = lifeTab.01, type = "n", axes = F,
     xlim = c(0, 2.2), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 2, 0.5), labels = c("0.0", "0.5", "1.0", "1.5", "2.0"), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Relative age (mean lifespans)", side = 1, line = 2.7)
text(0, 0.04, "(b)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age.rel, dat = lifeTab.01, type = "s", col = "#000000", lwd = 2) 
points(p.surv.cum ~ age.rel, dat = lifeTab.02, type = "s", col = "#FF0000", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.04, type = "s", col = "#FFA500", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.08, type = "s", col = "#00FF00", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.16, type = "s", col = "#00FFFF", lwd = 2)
# points and lines for 1/32 and 0 treatments omitted because mean lifespan (and therefore relative age) cannot be calculated 
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF"), 
       lty = 1, lwd = 2, bty = "n", cex = 0.7, inset = 0.02)

# Close device
dev.off()



##### 28.  Fig. D1 (Supporting information).  Interaction plot for light intensity #####

# Fit intercept for line with slope of log10(1/2)
a1 <- mean(log10(light$PAR[light$treatment != '0']) - log10(1/2)*rep(0:5, times = 1, each = 10))

# Fit line and get intercept and slope 
x <- rep(1:6, times = 1, each = 10)
PAR.lm <- lm(log10(light$PAR[light$treatment != '0']) ~ x)
a2 <- PAR.lm$coefficients[1]
b2 <- PAR.lm$coefficients[2]

# Create Fig. D1
emf(file = "FigD1_PAR.emf", width = 5, height = 4.5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 1), mar = c(4.0, 5.0, 1.0, 1.0))

# Make interaction plot
plot(PAR.mean[1:7], log = 'y',
     type = 'n',
     xaxt = "n", 
     xlab = "Light intensity treatment", 
     ylab = expression(paste("Mean PAR ± SEM (", mu, "mol m"^"-2", " s"^"-1",")")),
     xlim = c(0.5, 7.5),
     ylim = c(0.9, 600), 
     las = 1)
lines(x = c(1, 6), y = c(10^a1, 10^a1/32), col = 'grey', lty = 1, lwd = 6)
lines(x = c(1, 6), y = c(10^(a2 + b2*1), 10^(a2 + b2*6)), lty = 2)
points(PAR.mean[1:7], cex = 1.25, pch = 16)
lines(PAR.mean[1:7])
a.size <- 0.05
arrows(1, PAR.mean[1]  + PAR.sem[1],  1, PAR.mean[1]  - PAR.sem[1],  angle = 90, length = a.size, code = 3)
arrows(2, PAR.mean[2]  + PAR.sem[2],  2, PAR.mean[2]  - PAR.sem[2],  angle = 90, length = a.size, code = 3)
arrows(3, PAR.mean[3]  + PAR.sem[3],  3, PAR.mean[3]  - PAR.sem[3],  angle = 90, length = a.size, code = 3)
arrows(4, PAR.mean[4]  + PAR.sem[4],  4, PAR.mean[4]  - PAR.sem[4],  angle = 90, length = a.size, code = 3)
arrows(5, PAR.mean[5]  + PAR.sem[5],  5, PAR.mean[5]  - PAR.sem[5],  angle = 90, length = a.size, code = 3)
arrows(6, PAR.mean[6]  + PAR.sem[6],  6, PAR.mean[6]  - PAR.sem[6],  angle = 90, length = a.size, code = 3)
arrows(7, PAR.mean[7]  + PAR.sem[7],  7, PAR.mean[7]  - PAR.sem[7],  angle = 90, length = a.size, code = 3)
arrows(1, PAR.mean[8]  + PAR.sem[8],  1, PAR.mean[8]  - PAR.sem[8],  angle = 90, length = a.size, code = 3)
arrows(2, PAR.mean[9]  + PAR.sem[9],  2, PAR.mean[9]  - PAR.sem[9],  angle = 90, length = a.size, code = 3)
arrows(3, PAR.mean[10] + PAR.sem[10], 3, PAR.mean[10] - PAR.sem[10], angle = 90, length = a.size, code = 3)
arrows(4, PAR.mean[11] + PAR.sem[11], 4, PAR.mean[11] - PAR.sem[11], angle = 90, length = a.size, code = 3)
arrows(5, PAR.mean[12] + PAR.sem[12], 5, PAR.mean[12] - PAR.sem[12], angle = 90, length = a.size, code = 3)
arrows(6, PAR.mean[13] + PAR.sem[13], 6, PAR.mean[13] - PAR.sem[13], angle = 90, length = a.size, code = 3)
arrows(7, PAR.mean[14] + PAR.sem[14], 7, PAR.mean[14] - PAR.sem[14], angle = 90, length = a.size, code = 3)
lines(PAR.mean[8:14])
points(PAR.mean[8:14], cex = 1.25, pch = 21, bg = "white")
axis(1, at = 1:7, labels = c(expression(paste(italic("L")["1"])),
                             expression(paste(italic("L")["1/2"])),
                             expression(paste(italic("L")["1/4"])),
                             expression(paste(italic("L")["1/8"])),
                             expression(paste(italic("L")["1/16"])),
                             expression(paste(italic("L")["1/32"])),
                             expression(paste(italic("L")["0"]))))
legend("topright", c("top", "bottom"), title = "Shelf", bty = 'n',  
       pch = c(16, 21), pt.cex = 1.25, lty = FALSE, inset = c(0.05, 0.18))
legend("bottomleft", c("best-fit line with anticipated slope", "best-fit line"), bty = 'n', lwd = c(6, 1), 
       lty = c(1, 2), col = c("grey", "black"), inset = 0.03)
text(1, 600, "G") # 1
text(2, 600, "F") # 1/2
text(3, 600, "E") # 1/4
text(4, 600, "D") # 1/8
text(5, 600, "C") # 1/16
text(6, 600, "B") # 1/32
text(7, 600, "A") # 0

# Close device
dev.off()



##### 29.  Fig. E1 (Supporting information).  Interaction plot for temperature #####

# Create Fig. E1
emf(file = "FigE1_temperature.emf", width = 5, height = 4.5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 1), mar = c(4.0, 5.0, 1.0, 1.0))

# Make interaction plot
plot(temp.mean[1:7], 
     xaxt = "n", 
     xlab = "Light intensity treatment", 
     ylab = "Mean temperature ± SEM (\u00B0C)",
     xlim = c(0.5, 7.5),
     ylim = c(23, 30), 
     las = 1,
     cex = 1.25,
     pch = 16)
lines(temp.mean[1:7])
a.size <- 0.05
arrows(1, temp.mean[1]  + temp.sem[1],  1, temp.mean[1]  - temp.sem[1],  angle = 90, length = a.size, code = 3)
arrows(2, temp.mean[2]  + temp.sem[2],  2, temp.mean[2]  - temp.sem[2],  angle = 90, length = a.size, code = 3)
arrows(3, temp.mean[3]  + temp.sem[3],  3, temp.mean[3]  - temp.sem[3],  angle = 90, length = a.size, code = 3)
arrows(4, temp.mean[4]  + temp.sem[4],  4, temp.mean[4]  - temp.sem[4],  angle = 90, length = a.size, code = 3)
arrows(5, temp.mean[5]  + temp.sem[5],  5, temp.mean[5]  - temp.sem[5],  angle = 90, length = a.size, code = 3)
arrows(6, temp.mean[6]  + temp.sem[6],  6, temp.mean[6]  - temp.sem[6],  angle = 90, length = a.size, code = 3)
arrows(7, temp.mean[7]  + temp.sem[7],  7, temp.mean[7]  - temp.sem[7],  angle = 90, length = a.size, code = 3)
arrows(1, temp.mean[8]  + temp.sem[8],  1, temp.mean[8]  - temp.sem[8],  angle = 90, length = a.size, code = 3)
arrows(2, temp.mean[9]  + temp.sem[9],  2, temp.mean[9]  - temp.sem[9],  angle = 90, length = a.size, code = 3)
arrows(3, temp.mean[10] + temp.sem[10], 3, temp.mean[10] - temp.sem[10], angle = 90, length = a.size, code = 3)
arrows(4, temp.mean[11] + temp.sem[11], 4, temp.mean[11] - temp.sem[11], angle = 90, length = a.size, code = 3)
arrows(5, temp.mean[12] + temp.sem[12], 5, temp.mean[12] - temp.sem[12], angle = 90, length = a.size, code = 3)
arrows(6, temp.mean[13] + temp.sem[13], 6, temp.mean[13] - temp.sem[13], angle = 90, length = a.size, code = 3)
arrows(7, temp.mean[14] + temp.sem[14], 7, temp.mean[14] - temp.sem[14], angle = 90, length = a.size, code = 3)
lines(temp.mean[8:14])
points(temp.mean[8:14], cex = 1.25, pch = 21, bg = "white")
axis(1, at = 1:7, labels = c(expression(paste(italic("L")["1"])),
                             expression(paste(italic("L")["1/2"])),
                             expression(paste(italic("L")["1/4"])),
                             expression(paste(italic("L")["1/8"])),
                             expression(paste(italic("L")["1/16"])),
                             expression(paste(italic("L")["1/32"])),
                             expression(paste(italic("L")["0"]))))
legend("topleft", c("top", "bottom"), title = "Shelf", bty = 'n',  
       pch = c(16, 21), pt.cex = 1.25, lty = FALSE, inset = c(0.05, 0.13))
text(1, 30, "BA") # 1
text(2, 30, "BA") # 1/2
text(3, 30, "BA") # 1/4
text(4, 30, "BA") # 1/8
text(5, 30, "B")  # 1/16
text(6, 30, "B")  # 1/32
text(7, 30, "A")  # 0

# Close device
dev.off()



##### 30.  Fig. F1 (Supporting information).  Boxplot for frond area #####

# Create Fig. F1
emf(file = "FigF1_boxplot.emf", width = 5, height = 4.5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 1), mar = c(3.0, 3.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Boxplot of area versus light treatment
boxplot(Area.mm ~ treatment, dat = size, ylim = c(2, 7), axes = F, cex = 1.0, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
Area.mm.mean <- tapply(size$Area.mm, INDEX = size$treatment, FUN = mean)
points(Area.mm.mean, cex = 2, pch = 16, col = "green")
light.treatment.jitter <- as.numeric(size$treatment) + rnorm(length(size$treatment), 0, 0.05)
points(x = light.treatment.jitter, y = size$Area.mm, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:7, cex.axis = 1.3, tck = -0.03, label = rep("", 7)) 
axis(1, at = 1:7, cex.axis = 1.0, tck = 0.00, line = 0.25, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                               expression(paste(italic("L")["1/2"])),
                                                                               expression(paste(italic("L")["1/4"])),
                                                                               expression(paste(italic("L")["1/8"])),
                                                                               expression(paste(italic("L")["1/16"])),
                                                                               expression(paste(italic("L")["1/32"])),
                                                                               expression(paste(italic("L")["0"]))))
axis(2, at = seq(2, 7, 1), labels = seq(2, 7, 1), las = 1, cex.axis = 1.0, tck = -0.03)
axis(3, at = 1:7, line = -0.5, lwd = 0, cex.axis = 0.7, tck = 0, labels = c(expression(paste(italic("n "), "= 16")),
                                                                            expression(paste(italic("n "), "= 23")),
                                                                            expression(paste(italic("n "), "= 28")),
                                                                            expression(paste(italic("n "), "= 26")),
                                                                            expression(paste(italic("n "), "= 25")),
                                                                            expression(paste(italic("n "), "= 21")),
                                                                            expression(paste(italic("n "), "= 26"))))
mtext("Light intensity treatment", side = 1, line = 2.7)
mtext(expression(paste("Area (mm"^"2"*")")), side = 2, line = 2.7)

# Close device
dev.off()



##### 31.  Fig. H1 (Supporting information).  ECDFs for Kolmogorov-Smirnov's D #####

# Create Fig. H1
emf(file = "FigH1_ECDF.emf", width = 5, height = 7, units = "in", coordDPI = 1200)
par(mfrow = c(2, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Panel (a) - using initial sample sizes  
plot(x = KS.ecdf[, 1],
     y = KS.ecdf[, 2],
     xlim = c(0.05, 0.35),
     ylim = c(0, 1),
     xlab = NA,
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)
text(0.05, 1, "(a)", cex = 1.3, adj = c(0, 1))

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.35, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.alt.3, D.crit.alt.3), c(0, 1), lty = 2)
text(x = D.crit.alt.3 + 0.005, y = 0, expression(paste(italic("D")[crit], " = 0.1339")), adj = c(0, 0))

# Panel (b) - using realized final sample sizes
plot(x = KS.2.ecdf[, 1],
     y = KS.2.ecdf[, 2],
     xlim = c(0.05, 0.35),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)
text(0.05, 1, "(b)", cex = 1.3, adj = c(0, 1))

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.35, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.2.alt.3, D.crit.2.alt.3), c(0, 1), lty = 2)
text(x = D.crit.2.alt.3 + 0.005, y = 0, expression(paste(italic("D")[crit], " = 0.1420")), adj = c(0, 0))

dev.off()



##### 32.  Fig. I1 (Supporting information).  Proportion of offspring not yet born #####

# Create Fig. I1
emf(file = "FigI1_reproduction.emf", width = 10, height = 5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 2), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(3.0, 3.0, 1.0, 1.0))

# Panel (a) number of offspring not yet born versus age (by individual)
plot(0,
     type = "n", 
     las = 1, 
     xlim = c(0, 140),
     ylim = c(0, 20),
     xlab = "Absolute age", 
     ylab = "Number of offspring not yet born")
mtext("(days)", side = 1, line = 4, cex = 0.8)

# Add the lines for each individual (But add them in a random order so it doesn't privilege the last-added treatments as top layers)
lineorder <- sample(1:nrow(cr.repro.aligned), replace = F)
for (i in lineorder) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr.repro.aligned[i, 1:cr$lifespan[i]])
  
  # Determine cumulative number not yet born at each age
  focal.n.not.born.cum <- c(sum(focal.repro), sum(focal.repro) - cumsum(focal.repro[1:(length(focal.repro) - 1)]))
  
  # Determine the line colour, according to light treatment
  if (cr$light.treatment[i] == "1") {
    linecolour <- "#000000"
  } else if (cr$light.treatment[i] == "1/2") {
    linecolour <- "#FF0000"
  } else if (cr$light.treatment[i] == "1/4") {
    linecolour <- "#FFA500"
  } else if (cr$light.treatment[i] == "1/8") {
    linecolour <- "#00FF00"
  } else if (cr$light.treatment[i] == "1/16") {
    linecolour <- "#00FFFF"
  }  
  
  # Jitter points to make step plots easier to distinguish
  jitter.max.y <- 0.2 # recommend less than 0.5 so jittering cannot change the order of points
  focal.n.not.born.cum.jitter <- focal.n.not.born.cum 
  focal.n.not.born.cum.jitter[1] <- focal.n.not.born.cum.jitter[1] + runif(1, min = -jitter.max.y, max = jitter.max.y) 
  for (j in 2:length(focal.repro)) {
    if (focal.n.not.born.cum[j] == focal.n.not.born.cum[j - 1]) {
      focal.n.not.born.cum.jitter[j] <- focal.n.not.born.cum.jitter[j - 1] 
    } else {
      focal.n.not.born.cum.jitter[j] <- focal.n.not.born.cum.jitter[j] + runif(1, min = -jitter.max.y, max = jitter.max.y) 
    }   
  }
  
  # Add the line to the plot
  jitter.max.x <- 0.4 # recommend less than 0.5 so jittering cannot change the order of points
  if ((cr$light.treatment[i] != "1/32") & (cr$light.treatment[i] != "0")) {
    lines(x = 1:length(focal.repro) + runif(length(focal.repro), min = -jitter.max.x, max = jitter.max.x),
          y = focal.n.not.born.cum.jitter,
          type = "s",
          lwd = 1,
          col = linecolour) 
  }
}

# Add the legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000",
               "#FF0000",
               "#FFA500",
               "#00FF00",
               "#00FFFF"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 140, y = 0, "(a)", adj = c(1, 0), cex = 1.25)


# Panel (b) proportion of offspring not yet born versus relative age (by treatment)

# Calculate relative age at birth of every offspring for each focal (parent) plant 
# Relative age is absolute age divided by the age of the focal plant at the birth of an average offspring  
# Group them by light treatment
rel.par.age.01 <- numeric(0)
rel.par.age.02 <- numeric(0)
rel.par.age.04 <- numeric(0)
rel.par.age.08 <- numeric(0)
rel.par.age.16 <- numeric(0)
for (i in 1:nrow(cr.repro.aligned)) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr.repro.aligned[i, 1:cr$lifespan[i]])
  
  # Calculate age of the focal plant at the birth of an average offspring  
  mean.par.age <- sum(focal.repro*(1:cr$lifespan[i]))/sum(focal.repro)
  
  # Calculate distribution of relative ages for the focal plant
  # Be sure to include cases where there is more than one offspring born at particular age
  focal.rel.par.age <- numeric(0)
  for (j in 1:max(focal.repro)) { # j is the number born at particular age
    focal.rel.par.age <- c(focal.rel.par.age, which(focal.repro >= j)/mean.par.age)
  }
  focal.rel.par.age <- sort(focal.rel.par.age)
  
  # Group distribution of relative ages for the focal plant with others from the same light treatment
  # (only for L1 to L16, i.e., for which total reproduction is known for every individual)
  if (cr$light.treatment[i] == "1") {
    rel.par.age.01 <- c(rel.par.age.01, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/2") {
    rel.par.age.02 <- c(rel.par.age.02, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/4") {
    rel.par.age.04 <- c(rel.par.age.04, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/8") {
    rel.par.age.08 <- c(rel.par.age.08, focal.rel.par.age)
  } else if (cr$light.treatment[i] == "1/16") {
    rel.par.age.16 <- c(rel.par.age.16, focal.rel.par.age)
  } 
  
}

# Note that all rel.par.age.xx have a mean of 1
mean(rel.par.age.01)
mean(rel.par.age.02)
mean(rel.par.age.04)
mean(rel.par.age.08)
mean(rel.par.age.16)

# Sort all rel.par.age.xx in ascending order
rel.par.age.01 <- sort(rel.par.age.01)
rel.par.age.02 <- sort(rel.par.age.02)
rel.par.age.04 <- sort(rel.par.age.04)
rel.par.age.08 <- sort(rel.par.age.08)
rel.par.age.16 <- sort(rel.par.age.16)

# Calculate cumulative proportion of offspring not yet born, grouped by light treatment
p.not.born.cum.01 <- rep(NA, length(rel.par.age.01))
p.not.born.cum.02 <- rep(NA, length(rel.par.age.02))
p.not.born.cum.04 <- rep(NA, length(rel.par.age.04))
p.not.born.cum.08 <- rep(NA, length(rel.par.age.08))
p.not.born.cum.16 <- rep(NA, length(rel.par.age.16))
for (i in 1:length(rel.par.age.01)) { p.not.born.cum.01[i] <- sum(rel.par.age.01 >= rel.par.age.01[i])/length(rel.par.age.01) }
for (i in 1:length(rel.par.age.02)) { p.not.born.cum.02[i] <- sum(rel.par.age.02 >= rel.par.age.02[i])/length(rel.par.age.02) }
for (i in 1:length(rel.par.age.04)) { p.not.born.cum.04[i] <- sum(rel.par.age.04 >= rel.par.age.04[i])/length(rel.par.age.04) }
for (i in 1:length(rel.par.age.08)) { p.not.born.cum.08[i] <- sum(rel.par.age.08 >= rel.par.age.08[i])/length(rel.par.age.08) }
for (i in 1:length(rel.par.age.16)) { p.not.born.cum.16[i] <- sum(rel.par.age.16 >= rel.par.age.16[i])/length(rel.par.age.16) }

# Plot grouped data (Proportion of offspring not yet born vs relative age)
plot(x = rel.par.age.01,  
     y = p.not.born.cum.01, 
     type = "s", 
     las = 1,
     xlim = c(0, 2.5), 
     ylim = c(0, 1),
     xlab = "Relative age",
     ylab = "Proportion of offspring not yet born",
     col = "#000000")
mtext("(scaled to age at birth of average offspring)", side = 1, line = 4, cex = 0.8)
lines(x = rel.par.age.02, y = p.not.born.cum.02, type = "s", col = "#FF0000")
lines(x = rel.par.age.04, y = p.not.born.cum.04, type = "s", col = "#FFA500")
lines(x = rel.par.age.08, y = p.not.born.cum.08, type = "s", col = "#00FF00")
lines(x = rel.par.age.16, y = p.not.born.cum.16, type = "s", col = "#00FFFF")

# Add legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/2"])),
                expression(paste(italic("L")["1/4"])),
                expression(paste(italic("L")["1/8"])),
                expression(paste(italic("L")["1/16"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FF0000", "#FFA500", "#00FF00", "#00FFFF"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 0, y = 0, "(b)", adj = c(0, 0), cex = 1.25)

dev.off()



##### 33.  Fig. I3 (Supporting information).  ECDF for Kolmogorov-Smirnov's D (for reproduction) #####

# Create Fig. I3
emf(file = "FigI3_ECDF.emf", width = 5, height = 4, units = "in", coordDPI = 1200)
par(mfrow = c(1, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

plot(x = KS.repro.ecdf[, 1],
     y = KS.repro.ecdf[, 2],
     xlim = c(0.04, 0.14),
     ylim = c(0, 1),
     xlab = expression(paste("Kolmogorov-Smirnov ", italic("D"), " statistic")),
     ylab = "Cumulative frequency",
     las = 1,
     type = "s",
     col = "purple",
     lwd = 2)

# Add lines for visual assessment of D.crit
lines(c(0, 1), c(targ.beta, targ.beta), lty = 2)
text(x = 0.14, y = 0.22,
     expression(paste("Target maximum ", beta)), adj = c(1, 0))
lines(c(D.crit.repro.alt.2, D.crit.repro.alt.2), c(0, 1), lty = 2)
text(x = D.crit.repro.alt.2 + 0.003, y = 0, expression(paste(italic("D")[crit], " = 0.06972 (provisional)")), adj = c(0, 0))

dev.off()

