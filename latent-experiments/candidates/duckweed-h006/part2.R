### Title of accompanying manuscript: Caloric restriction extends lifespan in a clonal plant
### Authors: Suzanne L. Chmilar, Amanda C. Luzardo, Priyanka Dutt, Abbe Pawluk, Victoria C. Thwaites, and Robert A. Laird
### Journal: Ecology Letters
### Contents: Experiment 2 R Scripts for data analysis and figures



##### PART I. LOAD PACKAGES AND SET WORKING DIRECTORY #####



##### 1.   Load packages #####

library(devEMF)



##### 2.   Set working directory #####

# Set working directory 
setwd('c:/RFiles/Lemna_Caloric_Restriction')



##### PART II. DATA ANALYSIS: SURVIVAL AND REPRODUCTION #####



##### 3.   Load daily survival and reproduction data, and perform preliminary processing #####

# Load daily reproduction data
cr2.full <- read.csv('CR2_daily_surv_and_repro.csv', header = T) 

# Exclude appropriate fronds
cr2 <- cr2.full[cr2.full$exclude == "No", ]

# Change light treatment names to be less cryptic 
cr2$light.treatment[cr2$light.treatment == "4"] <- "1/4"
cr2$light.treatment <- factor(cr2$light.treatment, c("1", "1/4"))

# Extract reproduction data 
cr2.repro <- subset(cr2, select = May.31.2022:Aug.12.2022) 

# Double check dates of birth
cr2$date.birth.alt <- apply(cr2.repro, 1, function (x) names(cr2.repro)[min(which(x == 0))])
cr2$date.birth.alt == cr2$date.birth # all entries match
cr2 <- cr2[ , 1:(ncol(cr2) - 1)] # drop unnecessary date.birth.alt column

# Double check dates of last reproduction
cr2$date.last.repro.alt <- apply(cr2.repro, 1, function (x) names(cr2.repro)[max(which(x > 0))])
cr2$date.last.repro.alt == cr2$date.last.repro # all entries match 
cr2 <- cr2[ , 1:(ncol(cr2) - 1)] # drop unnecessary date.last.repro.alt column 

# Calculate dates of first reproduction
cr2$date.first.repro <- apply(cr2.repro, 1, function (x) names(cr2.repro)[min(which(x > 0))])

# Convert date values to R's date format
cr2$date.birth <- as.Date(cr2$date.birth, format = "%b.%d.%Y")
cr2$date.last.repro <- as.Date(cr2$date.last.repro, format = "%b.%d.%Y")
cr2$date.first.repro <- as.Date(cr2$date.first.repro, format = "%b.%d.%Y")

# Calculate lifespan from birth
cr2$lifespan <- as.numeric(cr2$date.last.repro - cr2$date.birth + 1) # first day is Day 1, not Day 0

# Calculate lifespan from first reproduction
cr2$lifespan.ffr <- as.numeric(cr2$date.last.repro - cr2$date.first.repro + 1)

# Calculate lifetime reproduction
cr2$total.offspring <- apply(cr2.repro, 1, function (x) sum(x, na.rm = T))

# Make new data frame with aligned reproduction data relative to dates of birth
cr2.repro.aligned <- matrix(NA, nrow = nrow(cr2.repro), ncol = max(cr2$lifespan))
birth.col2 <- as.numeric(cr2$date.birth - min(cr2$date.birth) + 1) # column index for date of birth       
death.col2 <- as.numeric(cr2$date.last.repro - min(cr2$date.birth) + 1) # column index for date of death
for (i in 1:nrow(cr2.repro)) {
  cr2.repro.aligned[i, 1:cr2$lifespan[i]] <- as.numeric(cr2.repro[i, birth.col2[i]:death.col2[i]])
}

# Calculate intrinsic rate of increase of individuals (r)
for (i in 1:nrow(cr2.repro.aligned)) {
  ind <- cr2.repro.aligned[i, ]                                # extract individual in row i
  L <- max(which(ind > 0))                                     # get lifespan
  lesMat <- matrix(0, nrow = L, ncol = L)                      # create empty lifespan x lifespan Leslie matrix
  lesMat[1, ] <- ind[1:L]                                      # fill first row with reproduction data
  if (L > 1) {
    lesMat[2:L, 1:(L - 1)] <- diag(rep(1, (L - 1)))            # fill sub-diagonal with survival data
  }
  eigenvalues <- eigen(lesMat)$values                          # get list of eigenvalues of Leslie matrix
  lambda <- max(Re(eigenvalues[abs(Im(eigenvalues)) < 1e-6]))  # extract lambda
  cr2$r[i] <- log(lambda)                                      # record intrinsic rate of increase (r)
  if (abs(cr2$r[i]) < 1e-6) {
    cr2$r[i] <- 0                                              # correct for floating point arithmetic rounding errors
  }
} 



##### 4.   Analyze reproductive lifespan (t-test) #####

# Visually inspect boxplot of lifespan
boxplot(lifespan ~ light.treatment, dat = cr2, ylim = c(0, 70),
        las = 1, whisklty = 1, col = "white", xlab = "Light intensity treatment", ylab = "Lifespan (days)")

# Data diagnostics
hist(cr2$lifespan[cr2$light.treatment == "1"]) # right skewed
hist(cr2$lifespan[cr2$light.treatment == "1/4"]) # right skewed
qqnorm(cr2$lifespan[cr2$light.treatment == "1"]) # not linear
qqnorm(cr2$lifespan[cr2$light.treatment == "1/4"]) # not linear

# log10-transformed lifespan data
cr2$log10lifespan <- log10(cr2$lifespan)
hist(cr2$log10lifespan[cr2$light.treatment == "1"]) # less skewed
hist(cr2$log10lifespan[cr2$light.treatment == "1/4"]) # less skewed
qqnorm(cr2$log10lifespan[cr2$light.treatment == "1"]) # straighter
qqnorm(cr2$log10lifespan[cr2$light.treatment == "1/4"]) # straighter

# t-test on log10-transformed lifespan data
t.test(log10lifespan ~ light.treatment, data = cr2, var.equal = T)

# Two Sample t-test
# 
# data:  log10lifespan by light.treatment
# t = -4.6244, df = 204, p-value = 6.662e-06
# alternative hypothesis: true difference in means between group 1 and group 1/4 is not equal to 0
# 95 percent confidence interval:
#   -0.15778351 -0.06345638
# sample estimates:
#   mean in group 1 mean in group 1/4 
#          1.186479          1.297099 



##### 5.   Analyze lifetime reproduction (t-test) #####

# Visually inspect boxplot of lifetime reproduction
boxplot(total.offspring ~ light.treatment, dat = cr2, ylim = c(0, 30), las = 1, whisklty = 1, col = "white", 
        xlab = "Light intensity treatment", ylab = "Total number of offspring")

# Data diagnostics
hist(cr2$total.offspring[cr2$light.treatment == "1"]) # right skewed
hist(cr2$total.offspring[cr2$light.treatment == "1/4"]) # right skewed
qqnorm(cr2$total.offspring[cr2$light.treatment == "1"]) # not linear
qqnorm(cr2$total.offspring[cr2$light.treatment == "1/4"]) # not linear

# log10-transformed lifetime reproduction data
cr2$log10total.offspring <- log10(cr2$total.offspring)
hist(cr2$log10total.offspring[cr2$light.treatment == "1"]) # less skewed
hist(cr2$log10total.offspring[cr2$light.treatment == "1/4"]) # less skewed
qqnorm(cr2$log10total.offspring[cr2$light.treatment == "1"]) # straighter, still some curve
qqnorm(cr2$log10total.offspring[cr2$light.treatment == "1/4"]) # straighter, still some curve

# t-test on log10-transformed lifetime reproduction data
t.test(log10total.offspring ~ light.treatment, data = cr2, var.equal = T)

# Two Sample t-test
# 
# data:  log10total.offspring by light.treatment
# t = -2.9223, df = 204, p-value = 0.003866
# alternative hypothesis: true difference in means between group 1 and group 1/4 is not equal to 0
# 95 percent confidence interval:
#   -0.15179477 -0.02948667
# sample estimates:
#   mean in group 1 mean in group 1/4 
#         0.8666782         0.9573189 



##### 6.   Analyze intrinsic rate of increase of individuals (r) (t-test) #####

# Visually inspect boxplot of intrinsic rate of increase of individuals (r)
boxplot(r ~ light.treatment, dat = cr2, las = 1, ylim = c(0, 0.6), whisklty = 1, col = "white", 
        xlab = "Light intensity treatment", ylab = "Intrinsic rate of increase (r)")

# Data diagnostics
hist(cr2$r[cr2$light.treatment == "1"]) 
hist(cr2$r[cr2$light.treatment == "1/4"]) # right skewed
qqnorm(cr2$r[cr2$light.treatment == "1"]) 
qqnorm(cr2$r[cr2$light.treatment == "1/4"]) # not linear

# log10-transformed r
cr2$log10r <- log10(cr2$r)
hist(cr2$log10r[cr2$light.treatment == "1"]) # slightly left skewed
hist(cr2$log10r[cr2$light.treatment == "1/4"]) # less skewed
qqnorm(cr2$log10r[cr2$light.treatment == "1"]) # some curve
qqnorm(cr2$log10r[cr2$light.treatment == "1/4"]) # straighter

# t-test on log10-transformed r
t.test(log10r ~ light.treatment, data = cr2, var.equal = T)

# Two Sample t-test
# 
# data:  log10r by light.treatment
# t = 2.7342, df = 204, p-value = 0.006803
# alternative hypothesis: true difference in means between group 1 and group 1/4 is not equal to 0
# 95 percent confidence interval:
#   0.01341845 0.08280944
# sample estimates:
#   mean in group 1 mean in group 1/4 
#        -0.5484674        -0.5965814 

# t-test on untransformed r (since log transformation was not as helpful in this instance)
t.test(r ~ light.treatment, data = cr2, var.equal = T)

# Two Sample t-test
#
# data:  r by light.treatment
# t = 2.9396, df = 204, p-value = 0.003665
# alternative hypothesis: true difference in means between group 1 and group 1/4 is not equal to 0
# 95 percent confidence interval:
#   0.01051641 0.05335971
# sample estimates:
#   mean in group 1 mean in group 1/4 
#          0.294912          0.262974 

# Conclusion unchanged



##### 7.   Create aligned reproduction data for each light intensity treatment #####

# Create separate aligned reproduction data for each light intensity treatment
cr2.repro.aligned.01 <- cr2.repro.aligned[cr2$light.treatment == "1", ]
cr2.repro.aligned.04 <- cr2.repro.aligned[cr2$light.treatment == "1/4", ]

# Convert aligned reproduction data into binomial format
cr2.repro.aligned.binom.01 <- apply(cr2.repro.aligned.01, 2, function (x) replace(x, which(x > 1), 1))
cr2.repro.aligned.binom.04 <- apply(cr2.repro.aligned.04, 2, function (x) replace(x, which(x > 1), 1))



##### 8A.  Create life tables for light intensity treatment '1' #####

n.2.01 <- nrow(cr2.repro.aligned.01) # total starting sample size
life.dist.2.01 <- cr2$lifespan[cr2$light.treatment == "1"] # distribution of lifespan
maxAge.2.01 <- max(life.dist.2.01) # max lifespan
meanAge.2.01 <- mean(life.dist.2.01) # mean lifespan
lifeTab.2.01 <- data.frame(matrix(nrow = maxAge.2.01, ncol = 7))
names(lifeTab.2.01) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.2.01$age <- 1:maxAge.2.01 # ages
lifeTab.2.01$age.rel <- lifeTab.2.01$age/meanAge.2.01 # relative ages (in mean lifespans)
lifeTab.2.01$n.last.repro <- tabulate(life.dist.2.01, nbins = maxAge.2.01) # number of deaths at each age
lifeTab.2.01$n.surv.cum <- c(n.2.01, n.2.01 - cumsum(lifeTab.2.01$n.last.repro[1:(maxAge.2.01 - 1)])) # total cumulative survivorship at age
lifeTab.2.01$p.surv.cum <- lifeTab.2.01$n.surv.cum/n.2.01 # proportional cumulative survivorship at age
lifeTab.2.01$n.repro <- colSums(cr2.repro.aligned.binom.01[ , 1:maxAge.2.01], na.rm = TRUE) # number reproducing at each age
lifeTab.2.01$p.repro <- lifeTab.2.01$n.repro/lifeTab.2.01$n.surv.cum # proportion reproducing at age



##### 8B.  Create life tables for light intensity treatment '1/4' #####

n.2.04 <- nrow(cr2.repro.aligned.04) # total starting sample size
life.dist.2.04 <- cr2$lifespan[cr2$light.treatment == "1/4"] # distribution of lifespan
maxAge.2.04 <- max(life.dist.2.04) # max lifespan
meanAge.2.04 <- mean(life.dist.2.04) # mean lifespan
lifeTab.2.04 <- data.frame(matrix(nrow = maxAge.2.04, ncol = 7))
names(lifeTab.2.04) <- c("age", "age.rel", "n.last.repro", "n.surv.cum", "p.surv.cum", "n.repro", "p.repro")    
lifeTab.2.04$age <- 1:maxAge.2.04 # ages
lifeTab.2.04$age.rel <- lifeTab.2.04$age/meanAge.2.04 # relative ages (in mean lifespans)
lifeTab.2.04$n.last.repro <- tabulate(life.dist.2.04, nbins = maxAge.2.04) # number of deaths at each age
lifeTab.2.04$n.surv.cum <- c(n.2.04, n.2.04 - cumsum(lifeTab.2.04$n.last.repro[1:(maxAge.2.04 - 1)])) # total cumulative survivorship at age
lifeTab.2.04$p.surv.cum <- lifeTab.2.04$n.surv.cum/n.2.04 # proportional cumulative survivorship at age
lifeTab.2.04$n.repro <- colSums(cr2.repro.aligned.binom.04[ , 1:maxAge.2.04], na.rm = TRUE) # number reproducing at each age
lifeTab.2.04$p.repro <- lifeTab.2.04$n.repro/lifeTab.2.04$n.surv.cum # proportion reproducing at age



##### 9.   Visually inspect survivorship curves #####

# Visually inspect survivorship curves (age in days)
plot(p.surv.cum ~ age,  dat = lifeTab.2.01, type = "n", las = 1, log = "y",
     xlim = c(0, 65), xlab = "Age (days)", ylab = "Proporting surviving")
lines(p.surv.cum ~ age, dat = lifeTab.2.01, type = "s", col = "#000000") 
lines(p.surv.cum ~ age, dat = lifeTab.2.04, type = "s", col = "#FFA500")
legend("topright", c("1", "1/4"), title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, bty = "n")

# Visually inspect survivorship curves (age in lifespans)
plot(p.surv.cum ~ age.rel,  dat = lifeTab.2.01, type = "n", las = 1, log = "y",
     xlim = c(0, 3.5), xlab = "Age (lifespans)", ylab = "Survivorship")
lines(p.surv.cum ~ age.rel, dat = lifeTab.2.01, type = "s", col = "#000000") 
lines(p.surv.cum ~ age.rel, dat = lifeTab.2.04, type = "s", col = "#FFA500")
legend("topright", c("1", "1/4"), title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, bty = "n")


##### 10.  Kolmogorov-Smirnov test on relative lifespan data #####

# Get relative lifespan distributions
rel.life.dist.2.01 <- life.dist.2.01/mean(life.dist.2.01)
rel.life.dist.2.04 <- life.dist.2.04/mean(life.dist.2.04)

# Perform Kolmogorov-Smirnov test
Kolmog.Smir <- suppressWarnings(ks.test(rel.life.dist.2.01, rel.life.dist.2.04)) # Suppress warnings; we know about ties
Kolmog.Smir

# Asymptotic two-sample Kolmogorov-Smirnov test
# 
# data:  rel.life.dist.2.01 and rel.life.dist.2.04
# D = 0.1233, p-value = 0.414
# alternative hypothesis: two-sided

# Note that D.crit.alt.3 was 0.1339; D < D.crit.alt.3, therefore not significant 
# (rel.life.dist.2.01 and rel.life.dist.2.04 are from same distribution)

# Get the empirical cumulative distribution functions of relative lifespan for L1 and L1/4
ecdf.01 <- ecdf(rel.life.dist.2.01)
ecdf.04 <- ecdf(rel.life.dist.2.04)

# Visually inspect the ECDFs 
plot(ecdf.01, 
     verticals = T, 
     do.points = F, 
     col = "#000000", 
     lwd = 1, 
     xlab = "Relative lifespan", 
     ylab = "Cumulative distribution",
     main = NA)
plot(ecdf.04, 
     verticals = T, 
     do.points = F, 
     col = "#FFA500", 
     lwd = 1, 
     add = T)
legend("right", c("1", "1/4"), title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lwd = 1, bty = "n")

# Note that survivorship is the complementary ECDF of relative lifespan
lines(1 - p.surv.cum ~ age.rel, dat = lifeTab.2.01, type = "S", col = rgb(0, 0, 0, alpha = 0.5), lwd = 4) 
lines(1 - p.surv.cum ~ age.rel, dat = lifeTab.2.04, type = "S", col = rgb(1, 165/255, 0, alpha = 0.5), lwd = 4)

# Double check calculation of Kolmogorov-Smirnov D
# First, combine relative lifespan data; sort in ascending order
rel.life.dist.2.both <- sort(c(rel.life.dist.2.01, rel.life.dist.2.04))

# Find D, the maximum distance between the curves
D <- 0
for (i in 1:(n.2.01 + n.2.04)) {
  x.01 <- sum(rel.life.dist.2.01 <= rel.life.dist.2.both[i])/n.2.01 # height of L1 curve at the ith point 
  x.04 <- sum(rel.life.dist.2.04 <= rel.life.dist.2.both[i])/n.2.04 # height of L1/4 curve at the ith point 
  if (abs(x.01 - x.04) > D) { 
    D <- abs(x.01 - x.04) # update D 
  }
}
D # 0.1233, same as when using built-in ks.test function, above

# Note that D < D.crit = 0.1339 (See Part I code); therefore, do not reject H0 
# i.e., evidence for temporal scaling

# Looking at the residuals of mean log lifespan is an alternate approach to looking at relative lifespan  
# We can double check this
# First get the distributions of log lifespan
log.life.dist.2.01 <- log(life.dist.2.01)
log.life.dist.2.04 <- log(life.dist.2.04)

# Get the residuals of mean log lifespan
resid.log.life.dist.01 <- log.life.dist.2.01 - mean(log.life.dist.2.01)
resid.log.life.dist.04 <- log.life.dist.2.04 - mean(log.life.dist.2.04)

# Perform Kolmogorov-Smirnov test
# Note the results are the same as the first method, above
suppressWarnings(ks.test(resid.log.life.dist.01, resid.log.life.dist.04)) # Suppress warnings; we know about ties
 
# Asymptotic two-sample Kolmogorov-Smirnov test
# 
# data:  resid.log.life.dist.01 and resid.log.life.dist.04
# D = 0.1233, p-value = 0.414
# alternative hypothesis: two-sided

# Get the empirical cumulative distribution functions of residuals of mean log lifespan for L1 and L1/4
ecdf.RMLL.01 <- ecdf(resid.log.life.dist.01)
ecdf.RMLL.04 <- ecdf(resid.log.life.dist.04)

# Visually inspect the ECDFs 
plot(ecdf.RMLL.01, 
     verticals = T, 
     do.points = F, 
     col = "#000000", 
     lwd = 1, 
     xlab = "Residual log lifespan", 
     ylab = "Cumulative distribution",
     main = NA)
plot(ecdf.RMLL.04, 
     verticals = T, 
     do.points = F, 
     col = "#FFA500", 
     lwd = 1, 
     add = T)
legend("right", c("1", "1/4"), title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lwd = 1, bty = "n")



##### 11.  Kolmogorov-Smirnov test on reproduction data #####

# Calculate relative age at birth of every offspring for each focal (parent) plant 
# Relative age is absolute age divided by the age of the focal plant at the birth of an average offspring  
# Group them by light treatment
rel.par.age.2.01 <- numeric(0)
rel.par.age.2.04 <- numeric(0)
for (i in 1:nrow(cr2.repro.aligned)) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr2.repro.aligned[i, 1:cr2$lifespan[i]])
  
  # Calculate age of the focal plant at the birth of an average offspring  
  mean.par.age <- sum(focal.repro*(1:cr2$lifespan[i]))/sum(focal.repro)
  
  # Calculate distribution of relative ages for the focal plant
  # Be sure to include cases where there is more than one offspring born at particular age
  focal.rel.par.age <- numeric(0)
  for (j in 1:max(focal.repro)) { # j is the number born at particular age
    focal.rel.par.age <- c(focal.rel.par.age, which(focal.repro >= j)/mean.par.age)
  }
  focal.rel.par.age <- sort(focal.rel.par.age)
  
  # Group distribution of relative ages for the focal plant with others from the same light treatment
  if (cr2$light.treatment[i] == "1") {
    rel.par.age.2.01 <- c(rel.par.age.2.01, focal.rel.par.age)
  } else if (cr2$light.treatment[i] == "1/4") {
    rel.par.age.2.04 <- c(rel.par.age.2.04, focal.rel.par.age)
  } 
  
}

# Note that all rel.par.age.xx have a mean of 1
mean(rel.par.age.2.01)
mean(rel.par.age.2.04)

# Sort all rel.par.age.xx in ascending order
rel.par.age.2.01 <- sort(rel.par.age.2.01)
rel.par.age.2.04 <- sort(rel.par.age.2.04)

# Perform Kolmogorov-Smirnov test
Kolmog.Smir.repro <- suppressWarnings(ks.test(rel.par.age.2.01, rel.par.age.2.04)) # Suppress warnings; we know about ties
Kolmog.Smir.repro

# Asymptotic two-sample Kolmogorov-Smirnov test
# 
# data:  rel.par.age.2.01 and rel.par.age.2.04
# D = 0.028661, p-value = 0.8329
# alternative hypothesis: two-sided


##### PART III. DATA ANALYSIS: FROND SIZE #####



##### 12.  Load frond size and shape data and perform preliminary processing #####

# Load size and shape data
size2 <- read.csv('CR2_size_and_shape.csv', header = T)

# Change light treatment names to be less cryptic 
size2$treatment[size2$treatment == "L01"] <- "1"
size2$treatment[size2$treatment == "L04"] <- "1/4"
size2$treatment <- factor(size2$treatment, c("1", "1/4"))

# Exclude rows (e.g., due to damaged or dried fronds, or those without photos)
size2 <- size2[size2$exclude == "No", ]



##### 13.  Analyze frond area (t-test) #####

# Visually inspect boxplot of frond area
boxplot(Area.mm ~ treatment, dat = size2, ylim = c(1, 8), las = 1, whisklty = 1, col = "white", 
        xlab = "Light intensity treatment", ylab = "Area (mm^2)")

# Data diagnostics
hist(size2$Area.mm[size2$treatment == "1"]) # slight right skewed
hist(size2$Area.mm[size2$treatment == "1/4"]) # slight left skewed
qqnorm(size2$Area.mm[size2$treatment == "1"]) # some curve
qqnorm(size2$Area.mm[size2$treatment == "1/4"])  

# log10-transformed Area data
size2$log10Area.mm <- log10(size2$Area.mm)
hist(size2$log10Area.mm[size2$treatment == "1"])
hist(size2$log10Area.mm[size2$treatment == "1/4"]) # slight left skewed
qqnorm(size2$log10Area.mm[size2$treatment == "1"]) # some curve
qqnorm(size2$log10Area.mm[size2$treatment == "1/4"]) # quite curved  

# overall, deemed best to not transform data

# t-test on Area data
t.test(Area.mm ~ treatment, data = size2, var.equal = T)

# Two Sample t-test
# 
# data:  Area.mm by treatment
# t = -1.0905, df = 126, p-value = 0.2776
# alternative hypothesis: true difference in means between group 1 and group 1/4 is not equal to 0
# 95 percent confidence interval:
#   -0.5495436  0.1590573
# sample estimates:
#   mean in group 1 mean in group 1/4 
#          4.114557          4.309800 



##### PART IV. FIGURES (.tif versions) #####



##### 14.  Fig. 3.  Boxplots for lifespan and total offspring #####

# Create Fig. 3
tiff(file = "Fig03_boxplots.tiff", width = 5, height = 10, units = "in", res = 600, compression = "lzw")
par(mfrow = c(3, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Panel (a) - boxplot of lifespan versus light treatment
boxplot(lifespan ~ light.treatment, dat = cr2, ylim = c(0, 60), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
lifespan.mean2 <- tapply(cr2$lifespan, INDEX = cr2$light.treatment, FUN = mean)
points(lifespan.mean2, cex = 2, pch = 16, col = "green")
set.seed(123) # so jittered points are always the same
light.treatment.jitter2 <- as.numeric(cr2$light.treatment) + rnorm(length(cr2$light.treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = cr2$lifespan, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(0, 60, 10), labels = seq(0, 60, 10), las = 1, cex.axis = 1.3, tck = -0.03)
axis(3, at = 1:2, line = -0.5, lwd = 0, cex.axis = 1.00, tck = 0, labels = c(expression(paste(italic("n "), "= 102")),
                                                                             expression(paste(italic("n "), "= 104"))))
mtext("Lifespan (days)", side = 2, line = 3.7)
mtext("(a)", side = 2, line = 4.5, at = 60, las = 1, cex = 1.3)
text(2.5, 60, "*", cex = 2)

# Panel (b) - boxplot of total number of offspring versus light treatment
boxplot(total.offspring ~ light.treatment, dat = cr2, ylim = c(0, 30), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
total.offspring.mean2 <- tapply(cr2$total.offspring, INDEX = cr2$light.treatment, FUN = mean)
points(total.offspring.mean2, cex = 2, pch = 16, col = "green")
light.treatment.jitter2 <- as.numeric(cr2$light.treatment) + rnorm(length(cr2$light.treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = cr2$total.offspring, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(0, 30, 5), labels = seq(0, 30, 5), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Total number of offspring", side = 2, line = 3.7)
mtext("(b)", side = 2, line = 4.5, at = 30, las = 1, cex = 1.3)
text(2.5, 30, "*", cex = 2)

# Panel (c) - boxplot of intrinsic rate of increase versus light treatment
boxplot(r ~ light.treatment, dat = cr2, las = 1, ylim = c(0, 0.6), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
r.mean2 <- tapply(cr2$r, INDEX = cr2$light.treatment, FUN = mean)
points(r.mean2, cex = 2, pch = 16, col = "green")
light.treatment.jitter2 <- as.numeric(cr2$light.treatment) + rnorm(length(cr2$light.treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = cr2$r, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(0, 0.6, 0.1), labels = c("0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6"), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Light intensity treatment", side = 1, line = 3.7)
mtext(expression(paste("Intrinsic rate of increase (", italic("r"), ")")), side = 2, line = 3.7)
mtext("(c)", side = 2, line = 4.5, at = 0.6, las = 1, cex = 1.3)
text(2.5, 0.6, "*", cex = 2)

# Close device
dev.off()



##### 15.  Fig. 4.  Survival plots #####

tiff(file = "Fig04_survival.tiff", width = 10, height = 5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 2), mar = c(4.0, 3.0, 0.0, 0.0), oma = c(1.0, 4.0, 1.0, 1.0))

# Panel (a) - Plot of survival versus age in days 
plot(p.surv.cum ~ age, dat = lifeTab.2.01, type = "n", axes = F, 
     xlim = c(0, 65), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 60, 10), labels = seq(0, 60, 10), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Absolute age (days)", side = 1, line = 2.7)
mtext("Proportion surviving", side = 2, line = 3.2)
text(0, 0.04, "(a)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age, dat = lifeTab.2.01, type = "s", col = "#000000", lwd = 2) 
points(p.surv.cum ~ age, dat = lifeTab.2.04, type = "s", col = "#FFA500", lwd = 2)
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, lwd = 2, bty = "n", inset = 0.02)

# Panel (b) - Step plot of survival versus age in lifespans
plot(p.surv.cum ~ age.rel,  dat = lifeTab.2.01, type = "n", axes = F,
     xlim = c(0, 3.75), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 3.5, 0.5), labels = c("0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5"), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Relative age (mean lifespans)", side = 1, line = 2.7)
text(0, 0.04, "(b)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age.rel, dat = lifeTab.2.01, type = "s", col = "#000000", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.2.04, type = "s", col = "#FFA500", lwd = 2)
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, lwd = 2, bty = "n", inset = 0.02)

# Close device
dev.off()



##### 16.  Fig. F2 (Supporting information).  Boxplot for frond area #####

# Create Fig. F2
tiff(file = "FigF2_boxplot.tiff", width = 5, height = 4.5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 1), mar = c(3.0, 3.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Boxplot of area versus light treatment
boxplot(Area.mm ~ treatment, dat = size2, ylim = c(1, 8), axes = F, cex = 1.0, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
Area.mm.mean2 <- tapply(size2$Area.mm, INDEX = size2$treatment, FUN = mean)
points(Area.mm.mean2, cex = 2, pch = 16, col = "green")
light.treatment.jitter2 <- as.numeric(size2$treatment) + rnorm(length(size2$treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = size2$Area.mm, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.0, tck = 0.00, line = 0.25, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                               expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(1, 8, 1), labels = seq(1, 8, 1), las = 1, cex.axis = 1.0, tck = -0.03)
axis(3, at = 1:2, line = -0.5, lwd = 0, cex.axis = 0.7, tck = 0, labels = c(expression(paste(italic("n "), "= 51")),
                                                                            expression(paste(italic("n "), "= 77"))))
mtext("Light intensity treatment", side = 1, line = 2.7)
mtext(expression(paste("Area (mm"^"2"*")")), side = 2, line = 2.7)

# Close device
dev.off()



##### 17.  Fig. I2 (Supporting information).  Proportion of offspring not yet born #####

# Create Fig. I2
tiff(file = "FigI2_reproduction.tiff", width = 10, height = 5, units = "in", res = 600, compression = "lzw")
par(mfrow = c(1, 2), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(3.0, 3.0, 1.0, 1.0))

# Panel (a) number of offspring not yet born versus age (by individual)
plot(0,
     type = "n", 
     las = 1, 
     xlim = c(0, 80),
     ylim = c(0, 30),
     xlab = "Absolute age", 
     ylab = "Number of offspring not yet born")
mtext("(days)", side = 1, line = 4, cex = 0.8)

# Add the lines for each individual (But add them in a random order so it doesn't privilege the last-added treatments as top layers)
lineorder <- sample(1:nrow(cr2.repro.aligned), replace = F)
for (i in lineorder) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr2.repro.aligned[i, 1:cr2$lifespan[i]])
  
  # Determine cumulative number not yet born at each age
  focal.n.not.born.cum <- c(sum(focal.repro), sum(focal.repro) - cumsum(focal.repro[1:(length(focal.repro) - 1)]))
  
  # Determine the line colour, according to light treatment
  if (cr2$light.treatment[i] == "1") {
    linecolour <- "#000000"
  } else if (cr2$light.treatment[i] == "1/4") {
    linecolour <- "#FFA500"
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
  if ((cr2$light.treatment[i] != "1/32") & (cr2$light.treatment[i] != "0")) {
    lines(x = 1:length(focal.repro) + runif(length(focal.repro), min = -jitter.max.x, max = jitter.max.x),
          y = focal.n.not.born.cum.jitter,
          type = "s",
          lwd = 1,
          col = linecolour) 
  }
}

# Add the legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000",
               "#FFA500"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 80, y = 0, "(a)", adj = c(1, 0), cex = 1.25)


# Panel (b) proportion of offspring not yet born versus relative age (by treatment)

# Calculate relative age at birth of every offspring for each focal (parent) plant 
# Relative age is absolute age divided by the age of the focal plant at the birth of an average offspring  
# Group them by light treatment
rel.par.age.2.01 <- numeric(0)
rel.par.age.2.04 <- numeric(0)
for (i in 1:nrow(cr2.repro.aligned)) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr2.repro.aligned[i, 1:cr2$lifespan[i]])
  
  # Calculate age of the focal plant at the birth of an average offspring  
  mean.par.age <- sum(focal.repro*(1:cr2$lifespan[i]))/sum(focal.repro)
  
  # Calculate distribution of relative ages for the focal plant
  # Be sure to include cases where there is more than one offspring born at particular age
  focal.rel.par.age <- numeric(0)
  for (j in 1:max(focal.repro)) { # j is the number born at particular age
    focal.rel.par.age <- c(focal.rel.par.age, which(focal.repro >= j)/mean.par.age)
  }
  focal.rel.par.age <- sort(focal.rel.par.age)
  
  # Group distribution of relative ages for the focal plant with others from the same light treatment
  if (cr2$light.treatment[i] == "1") {
    rel.par.age.2.01 <- c(rel.par.age.2.01, focal.rel.par.age)
  } else if (cr2$light.treatment[i] == "1/4") {
    rel.par.age.2.04 <- c(rel.par.age.2.04, focal.rel.par.age)
  } 
  
}

# Note that all rel.par.age.xx have a mean of 1
mean(rel.par.age.2.01)
mean(rel.par.age.2.04)

# Sort all rel.par.age.xx in ascending order
rel.par.age.2.01 <- sort(rel.par.age.2.01)
rel.par.age.2.04 <- sort(rel.par.age.2.04)

# Calculate cumulative proportion of offspring not yet born, grouped by light treatment
p.not.born.cum.2.01 <- rep(NA, length(rel.par.age.2.01))
p.not.born.cum.2.04 <- rep(NA, length(rel.par.age.2.04))
for (i in 1:length(rel.par.age.2.01)) { p.not.born.cum.2.01[i] <- sum(rel.par.age.2.01 >= rel.par.age.2.01[i])/length(rel.par.age.2.01) }
for (i in 1:length(rel.par.age.2.04)) { p.not.born.cum.2.04[i] <- sum(rel.par.age.2.04 >= rel.par.age.2.04[i])/length(rel.par.age.2.04) }

# Plot grouped data (Proportion of offspring not yet born vs relative age)
plot(x = rel.par.age.2.01,  
     y = p.not.born.cum.2.01, 
     type = "s", 
     las = 1,
     xlim = c(0, 2.5), 
     ylim = c(0, 1),
     xlab = "Relative age",
     ylab = "Proportion of offspring not yet born",
     col = "#000000")
mtext("(scaled to age at birth of average offspring)", side = 1, line = 4, cex = 0.8)
lines(x = rel.par.age.2.04, y = p.not.born.cum.2.04, type = "s", col = "#FFA500")

# Add legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 0, y = 0, "(b)", adj = c(0, 0), cex = 1.25)

dev.off()



##### PART V. FIGURES (.emf versions) #####



##### 18.  Fig. 3.  Boxplots for lifespan and total offspring #####

# Create Fig. 3
emf(file = "Fig03_boxplots.emf", width = 5, height = 10, units = "in", coordDPI = 1200)
par(mfrow = c(3, 1), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Panel (a) - boxplot of lifespan versus light treatment
boxplot(lifespan ~ light.treatment, dat = cr2, ylim = c(0, 60), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
lifespan.mean2 <- tapply(cr2$lifespan, INDEX = cr2$light.treatment, FUN = mean)
points(lifespan.mean2, cex = 2, pch = 16, col = "green")
set.seed(123) # so jittered points are always the same
light.treatment.jitter2 <- as.numeric(cr2$light.treatment) + rnorm(length(cr2$light.treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = cr2$lifespan, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(0, 60, 10), labels = seq(0, 60, 10), las = 1, cex.axis = 1.3, tck = -0.03)
axis(3, at = 1:2, line = -0.5, lwd = 0, cex.axis = 1.00, tck = 0, labels = c(expression(paste(italic("n "), "= 102")),
                                                                             expression(paste(italic("n "), "= 104"))))
mtext("Lifespan (days)", side = 2, line = 3.7)
mtext("(a)", side = 2, line = 4.5, at = 60, las = 1, cex = 1.3)
text(2.5, 60, "*", cex = 2)

# Panel (b) - boxplot of total number of offspring versus light treatment
boxplot(total.offspring ~ light.treatment, dat = cr2, ylim = c(0, 30), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
total.offspring.mean2 <- tapply(cr2$total.offspring, INDEX = cr2$light.treatment, FUN = mean)
points(total.offspring.mean2, cex = 2, pch = 16, col = "green")
light.treatment.jitter2 <- as.numeric(cr2$light.treatment) + rnorm(length(cr2$light.treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = cr2$total.offspring, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(0, 30, 5), labels = seq(0, 30, 5), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Total number of offspring", side = 2, line = 3.7)
mtext("(b)", side = 2, line = 4.5, at = 30, las = 1, cex = 1.3)
text(2.5, 30, "*", cex = 2)

# Panel (c) - boxplot of intrinsic rate of increase versus light treatment
boxplot(r ~ light.treatment, dat = cr2, las = 1, ylim = c(0, 0.6), axes = F, cex = 1.8, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
r.mean2 <- tapply(cr2$r, INDEX = cr2$light.treatment, FUN = mean)
points(r.mean2, cex = 2, pch = 16, col = "green")
light.treatment.jitter2 <- as.numeric(cr2$light.treatment) + rnorm(length(cr2$light.treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = cr2$r, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.3, tck = 0.00, line = 0.7, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                              expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(0, 0.6, 0.1), labels = c("0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6"), las = 1, cex.axis = 1.3, tck = -0.03)
mtext("Light intensity treatment", side = 1, line = 3.7)
mtext(expression(paste("Intrinsic rate of increase (", italic("r"), ")")), side = 2, line = 3.7)
mtext("(c)", side = 2, line = 4.5, at = 0.6, las = 1, cex = 1.3)
text(2.5, 0.6, "*", cex = 2)

# Close device
dev.off()



##### 19.  Fig. 4.  Survival plots #####

emf(file = "Fig04_survival.emf", width = 10, height = 5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 2), mar = c(4.0, 3.0, 0.0, 0.0), oma = c(1.0, 4.0, 1.0, 1.0))

# Panel (a) - Plot of survival versus age in days 
plot(p.surv.cum ~ age, dat = lifeTab.2.01, type = "n", axes = F, 
     xlim = c(0, 65), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 60, 10), labels = seq(0, 60, 10), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Absolute age (days)", side = 1, line = 2.7)
mtext("Proportion surviving", side = 2, line = 3.2)
text(0, 0.04, "(a)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age, dat = lifeTab.2.01, type = "s", col = "#000000", lwd = 2) 
points(p.surv.cum ~ age, dat = lifeTab.2.04, type = "s", col = "#FFA500", lwd = 2)
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, lwd = 2, bty = "n", inset = 0.02)

# Panel (b) - Step plot of survival versus age in lifespans
plot(p.surv.cum ~ age.rel,  dat = lifeTab.2.01, type = "n", axes = F,
     xlim = c(0, 3.75), xlab = NA, ylab = NA)
box()
axis(1, at = seq(0, 3.5, 0.5), labels = c("0.0", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5"), cex.axis = 1, tck = -0.03)
axis(2, at = seq(0, 1, 0.2), labels = c("0.0", "0.2", "0.4", "0.6", "0.8", "1.0"), las = 1, cex.axis = 1, tck = -0.03)
mtext("Relative age (mean lifespans)", side = 1, line = 2.7)
text(0, 0.04, "(b)", cex = 1.3, adj = c(0, 0))
points(p.surv.cum ~ age.rel, dat = lifeTab.2.01, type = "s", col = "#000000", lwd = 2)
points(p.surv.cum ~ age.rel, dat = lifeTab.2.04, type = "s", col = "#FFA500", lwd = 2)
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, lwd = 2, bty = "n", inset = 0.02)

# Close device
dev.off()



##### 20.  Fig. F2 (Supporting information).  Boxplot for frond area #####

# Create Fig. F2
emf(file = "FigF2_boxplot.emf", width = 5, height = 4.5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 1), mar = c(3.0, 3.0, 0.0, 0.0), oma = c(1.0, 2.0, 2.0, 1.0))

# Boxplot of area versus light treatment
boxplot(Area.mm ~ treatment, dat = size2, ylim = c(1, 8), axes = F, cex = 1.0, whisklty = 1, 
        col = "white", xlab = NA, ylab = NA, outline = F)
Area.mm.mean2 <- tapply(size2$Area.mm, INDEX = size2$treatment, FUN = mean)
points(Area.mm.mean2, cex = 2, pch = 16, col = "green")
light.treatment.jitter2 <- as.numeric(size2$treatment) + rnorm(length(size2$treatment), 0, 0.05)
points(x = light.treatment.jitter2, y = size2$Area.mm, pch = 21, col = NA, bg = rgb(125, 125, 125, max = 255, alpha = 95))
box()
axis(1, at = 1:2, cex.axis = 1.3, tck = -0.03, label = rep("", 2)) 
axis(1, at = 1:2, cex.axis = 1.0, tck = 0.00, line = 0.25, lwd = 0, labels = c(expression(paste(italic("L")["1"])),
                                                                               expression(paste(italic("L")["1/4"]))))
axis(2, at = seq(1, 8, 1), labels = seq(1, 8, 1), las = 1, cex.axis = 1.0, tck = -0.03)
axis(3, at = 1:2, line = -0.5, lwd = 0, cex.axis = 0.7, tck = 0, labels = c(expression(paste(italic("n "), "= 51")),
                                                                            expression(paste(italic("n "), "= 77"))))
mtext("Light intensity treatment", side = 1, line = 2.7)
mtext(expression(paste("Area (mm"^"2"*")")), side = 2, line = 2.7)

# Close device
dev.off()



##### 21.  Fig. I2 (Supporting information).  Proportion of offspring not yet born #####

# Create Fig. I2
emf(file = "FigI2_reproduction.emf", width = 10, height = 5, units = "in", coordDPI = 1200)
par(mfrow = c(1, 2), mar = c(4.0, 5.0, 0.0, 0.0), oma = c(3.0, 3.0, 1.0, 1.0))

# Panel (a) number of offspring not yet born versus age (by individual)
plot(0,
     type = "n", 
     las = 1, 
     xlim = c(0, 80),
     ylim = c(0, 30),
     xlab = "Absolute age", 
     ylab = "Number of offspring not yet born")
mtext("(days)", side = 1, line = 4, cex = 0.8)

# Add the lines for each individual (But add them in a random order so it doesn't privilege the last-added treatments as top layers)
lineorder <- sample(1:nrow(cr2.repro.aligned), replace = F)
for (i in lineorder) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr2.repro.aligned[i, 1:cr2$lifespan[i]])
  
  # Determine cumulative number not yet born at each age
  focal.n.not.born.cum <- c(sum(focal.repro), sum(focal.repro) - cumsum(focal.repro[1:(length(focal.repro) - 1)]))
  
  # Determine the line colour, according to light treatment
  if (cr2$light.treatment[i] == "1") {
    linecolour <- "#000000"
  } else if (cr2$light.treatment[i] == "1/4") {
    linecolour <- "#FFA500"
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
  if ((cr2$light.treatment[i] != "1/32") & (cr2$light.treatment[i] != "0")) {
    lines(x = 1:length(focal.repro) + runif(length(focal.repro), min = -jitter.max.x, max = jitter.max.x),
          y = focal.n.not.born.cum.jitter,
          type = "s",
          lwd = 1,
          col = linecolour) 
  }
}

# Add the legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000",
               "#FFA500"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 80, y = 0, "(a)", adj = c(1, 0), cex = 1.25)


# Panel (b) proportion of offspring not yet born versus relative age (by treatment)

# Calculate relative age at birth of every offspring for each focal (parent) plant 
# Relative age is absolute age divided by the age of the focal plant at the birth of an average offspring  
# Group them by light treatment
rel.par.age.2.01 <- numeric(0)
rel.par.age.2.04 <- numeric(0)
for (i in 1:nrow(cr2.repro.aligned)) {
  
  # Select focal individual's reproduction-by-age data
  focal.repro <- as.numeric(cr2.repro.aligned[i, 1:cr2$lifespan[i]])
  
  # Calculate age of the focal plant at the birth of an average offspring  
  mean.par.age <- sum(focal.repro*(1:cr2$lifespan[i]))/sum(focal.repro)
  
  # Calculate distribution of relative ages for the focal plant
  # Be sure to include cases where there is more than one offspring born at particular age
  focal.rel.par.age <- numeric(0)
  for (j in 1:max(focal.repro)) { # j is the number born at particular age
    focal.rel.par.age <- c(focal.rel.par.age, which(focal.repro >= j)/mean.par.age)
  }
  focal.rel.par.age <- sort(focal.rel.par.age)
  
  # Group distribution of relative ages for the focal plant with others from the same light treatment
  if (cr2$light.treatment[i] == "1") {
    rel.par.age.2.01 <- c(rel.par.age.2.01, focal.rel.par.age)
  } else if (cr2$light.treatment[i] == "1/4") {
    rel.par.age.2.04 <- c(rel.par.age.2.04, focal.rel.par.age)
  } 
  
}

# Note that all rel.par.age.xx have a mean of 1
mean(rel.par.age.2.01)
mean(rel.par.age.2.04)

# Sort all rel.par.age.xx in ascending order
rel.par.age.2.01 <- sort(rel.par.age.2.01)
rel.par.age.2.04 <- sort(rel.par.age.2.04)

# Calculate cumulative proportion of offspring not yet born, grouped by light treatment
p.not.born.cum.2.01 <- rep(NA, length(rel.par.age.2.01))
p.not.born.cum.2.04 <- rep(NA, length(rel.par.age.2.04))
for (i in 1:length(rel.par.age.2.01)) { p.not.born.cum.2.01[i] <- sum(rel.par.age.2.01 >= rel.par.age.2.01[i])/length(rel.par.age.2.01) }
for (i in 1:length(rel.par.age.2.04)) { p.not.born.cum.2.04[i] <- sum(rel.par.age.2.04 >= rel.par.age.2.04[i])/length(rel.par.age.2.04) }

# Plot grouped data (Proportion of offspring not yet born vs relative age)
plot(x = rel.par.age.2.01,  
     y = p.not.born.cum.2.01, 
     type = "s", 
     las = 1,
     xlim = c(0, 2.5), 
     ylim = c(0, 1),
     xlab = "Relative age",
     ylab = "Proportion of offspring not yet born",
     col = "#000000")
mtext("(scaled to age at birth of average offspring)", side = 1, line = 4, cex = 0.8)
lines(x = rel.par.age.2.04, y = p.not.born.cum.2.04, type = "s", col = "#FFA500")

# Add legend
leg.titles <- c(expression(paste(italic("L")["1"])),
                expression(paste(italic("L")["1/4"])))
legend("topright", legend = leg.titles, title = "Light intensity treatment",
       col = c("#000000", "#FFA500"), 
       lty = 1, lwd = 1, bty = "n", inset = 0.04)

text(x = 0, y = 0, "(b)", adj = c(0, 0), cex = 1.25)

dev.off()
