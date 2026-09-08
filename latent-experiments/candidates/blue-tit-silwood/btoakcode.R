rm(list=ls())

#Load packages
library(dplyr)
library(MCMCglmm)
library(lme4)
library(ggplot2)
library(stringr)
library(ggpubr)

#Read files
btoak<-read.csv("btoak.csv",header=TRUE)
oakbd<-read.csv("oakbd.csv", header=TRUE)


#===================LDBD relationship==================#
#Mean-centred LD and BD relationship
m.mcld.mcbd<-lmer(mc.LD~mc.BD+(1|year)+(1|female), data=btoak,na.action=na.omit)
summary(m.mcld.mcbd)

#Within individual LD-BD plasticity
btoak.ldbd.wi<-btoak%>%filter(BD!="NA"&LD!="NA")
tally1<-table(btoak.ldbd.wi$female) #Count number of records for each ID
btoak.ldbd.wi<-btoak.ldbd.wi[btoak.ldbd.wi$female %in% names(tally1)[tally1>1],] #Exclude one-time breeders
btoak.ldbd.wi<-btoak.ldbd.wi%>%group_by(female)%>%mutate(wi.BD=scale(mc.BD, scale=FALSE),idm.BD=mean(mc.BD)) #Calculate within-individual deviations
plot(btoak.ldbd.wi$wi.BD,btoak.ldbd.wi$mc.LD, xlab="Within-individual centred BD", ylab="Mean-centred LD")
m.mcld.wibd<-lmer(mc.LD~wi.BD+(1|female),data=btoak.ldbd.wi)
summary(m.mcld.wibd)

#Export model results
sink("LDBD.lmm.txt")
print(summary(m.mcld.mcbd))
print(summary(m.mcld.wibd))
sink()

#LD-BD bivariate random regression
#Generate Lifetime Breeding Success (LBS) stack data
LDBD.LBS<-btoak%>%group_by(female)%>%summarize(LBS=sum(no.hatchlings)) #Generate LBS for each female.
last.year<-btoak%>%group_by(female)%>%summarize(last.year=max(year)) #Year when female bred for the last time.
LDBD.LBS<-full_join(LDBD.LBS,last.year,by="female")
LDBD.LBS<-filter(LDBD.LBS,last.year!=2019) #Exclude birds still breeding in the latest year
LDBD.LBS$year<-rep(1) #year column necessary for OBS but irrelevant to LBS so set to 1
LDBD.LBS$age<-as.factor(rep(1)) #year column necessary for OBS but irrelevant to LBS so set to 1
LDBD.LBS$BD<-rep(0) #LD column necessary for OBS but irrelevant to LBS so set to 0
LDBD.LBS$obs<-1:length(LDBD.LBS$female) #Obs ID necessary for OBS but irrelevant to LBS so labelled consecutively.
LDBD.LBS<-LDBD.LBS[,c(7,1,4,5,6,2)]
colnames(LDBD.LBS)<-c("obs","ID","year","age","BD","LBS.LD")
LDBD.LBS$trait<-rep("LBS")
LDBD.LBS$variable<-rep("LBS")
LDBD.LBS$family<-rep("poisson")

#Generate Observations (OBS) stack data
LDBD.OBS<-btoak%>%filter(year<2019&mc.BD!="NA")%>%select(year,female,f.age,mc.BD,mc.LD)
LDBD.OBS$obs<-seq(from=nrow(LDBD.LBS)+1,to=nrow(LDBD.OBS)+nrow(LDBD.LBS)) #Add observation IDs. Continue from end of LBS table.
LDBD.OBS<-LDBD.OBS[,c(6,2,1,3,4,5)]
colnames(LDBD.OBS)<-c("obs","ID","year","age","BD","LBS.LD")
LDBD.OBS$trait<-rep("LD")
LDBD.OBS$variable<-rep("LD")
LDBD.OBS$family<-rep("gaussian")

#Combine stacks
LDBD.stack<-bind_rows(LDBD.LBS,LDBD.OBS)
LDBD.stack$age<-as.factor(LDBD.stack$age)
LDBD.stack$trait<-as.factor(LDBD.stack$trait)
LDBD.stack$variable<-as.factor(LDBD.stack$variable)
LDBD.stack$year<-as.factor(LDBD.stack$year)

#Set prior
LDBD.prior<-list(G=list(G1=list(V=diag(1),nu=1)),
                 R=list(R1=list(V=diag(3),nu=3,covu=TRUE),
                        R2=list(V=diag(1),nu=1)))

#MCMCglmm
LDBD.mcmc<-MCMCglmm(LBS.LD ~ variable-1 + #variable -1 indicates no single overall effect to be estimated
                    at.level(variable,"LD"):BD,
                    random=~us(at.level(variable,"LD")):year + #year as random effect
                            us(at.level(variable,"LD") + at.level(variable,"LD"):BD) :ID,
                            #|^-----Intercept------^| & |^---------Slope---------^|  grouped by ID
                    rcov=~us(at.level(variable,"LBS")):ID + #Correlate indivdual LBS
                          us(at.level(variable,"LD")):obs, #residuals
                    data=LDBD.stack,
                    prior=LDBD.prior,
                    family=NULL,
                    nitt=15000000, thin=1000, burnin=1500000, verbose=TRUE)
save(LDBD.mcmc, file="LDBD.mcmc.RData")
load("LDBD.mcmc.RData")
autocorr(LDBD.mcmc$VCV)
plot(LDBD.mcmc$VCV)
heidel.diag(LDBD.mcmc$VCV)
summary(LDBD.mcmc)

#Extract 3x3 VCV matrix
LDBD.mcmc.P<- LDBD.mcmc$VCV[,2:10] #VCV stored in columns 2 to 10 in model
LDBD.mcmc.Pmode <- matrix(1:9, nrow = 3) #Generate empty 3x3 matrix for VCV posterior modes.
for (k in 1:9) LDBD.mcmc.Pmode[k] <- posterior.mode(LDBD.mcmc.P[,k]) #Fill in Pmode matrix.
LDBD.mcmc.Pmode
posterior.mode(mcmc(LDBD.mcmc.P))
HPDinterval(mcmc(LDBD.mcmc.P))

#Estimate selection gradients for intercept and slope (beta = S / P)
LDBD.mcmc.n <- length(LDBD.mcmc$VCV[,2])   # sample size
LDBD.mcmc.beta <- matrix(NA, LDBD.mcmc.n ,2)
for (i in 1:LDBD.mcmc.n) {
  LDBD.mcmc.P3 <- matrix(rep(NA, 9), nrow = 3)  # 3x3 matrix of var-cov for individual int, slope and LBS
  for (k in 1:9) {LDBD.mcmc.P3[k] <- LDBD.mcmc.P[i, k] }  
  LDBD.mcmc.P2 <- LDBD.mcmc.P3[1:2, 1:2]   # 2x2 matrix of just trait intercept & slope var-cov
  LDBD.mcmc.S <- LDBD.mcmc.P3[1:2, 3]   # selection differentials on traits (last column of P3)
  LDBD.mcmc.beta[i,] <- solve(LDBD.mcmc.P2) %*% LDBD.mcmc.S   # selection gradients beta = P^-1 * S
}
colnames(LDBD.mcmc.beta) <- c("beta.intercepts", "beta.slopes")
posterior.mode(mcmc(LDBD.mcmc.beta))
HPDinterval(mcmc(LDBD.mcmc.beta))

#Save post.mode and HPDinterval of matrix values to a .txt file
sink("LDBD.mcmc.txt")
print(summary(LDBD.mcmc))
print(posterior.mode(mcmc(LDBD.mcmc.P)))
print(HPDinterval(mcmc(LDBD.mcmc.P)))
print(posterior.mode(mcmc(LDBD.mcmc.beta)))
print(HPDinterval(mcmc(LDBD.mcmc.beta)))
sink()

#Plot graphs
LDBD.overall<-ggplot(LDBD.OBS,aes(x=BD, y=LBS.LD))+
              geom_point()+
              labs(x="Mean-centered budburst date", y="Mean-centered laying date", size=10)+
              theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                    panel.background = element_blank(), axis.line = element_line(colour = "black"),
                    axis.title=element_text(size=10))+
              stat_smooth(method="lm",color="black", fill="gray")
LDBD.overall
ggsave(LDBD.overall, filename = "LDBD.overall.png", height=6, width=8) #Export to png

LDBD.wi<-ggplot(btoak.ldbd.wi,aes(x=wi.BD, y=mc.LD))+
         geom_point()+
         labs(x="Within-individual mean-centered budburst date", y="Mean-centered laying date", size=10)+
         theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
               panel.background = element_blank(), axis.line = element_line(colour = "black"),
               axis.title=element_text(size=10))+
         stat_smooth(method="lm",color="black", fill="gray")
LDBD.wi
ggsave(LDBD.wi, filename = "LDBD.wi.png", height=6, width=8) #Export to png


#=================================CS-LD relationship============================#
#Mean-centred CS and LD relationship
m.mccs.mcld<-lmer(mc.CS~mc.LD+(1|year)+(1|female), data=btoak,na.action=na.omit)
summary(m.mccs.mcld)

#CS-LD plasticity
btoak.csld.wi<-btoak%>%filter(LD!="NA"&CS!="NA")
tally2<-table(btoak.csld.wi$female) #Count no. of observations per ID
btoak.csld.wi<-btoak.csld.wi[btoak.csld.wi$female %in% names(tally2)[tally2>1],] #Exclude one-time breeders
btoak.csld.wi<-btoak.csld.wi%>%group_by(female)%>%mutate(wi.LD=scale(mc.LD, scale=FALSE)) #Caluclate within-individual deviations
plot(btoak.csld.wi$wi.LD,btoak.csld.wi$mc.CS, xlab="Within-individual mean-centred BD", ylab="Mean-centred LD")
m.mccs.wild<-lmer(mc.CS~wi.LD+(1|female),data=btoak.csld.wi)
summary(m.mccs.wild)

sink("CSLD.lmm.txt")
print(summary(m.mccs.mcld))
print(summary(m.mccs.wild))
sink()

#poisson?
m.pocs.mcld<-glmer(CS~mc.LD+(1|year)+(1|female), data=btoak,na.action=na.omit, family = "poisson")
summary(m.pocs.mcld)

#CS-LD plasticity
btoak.csld.wi<-btoak%>%filter(LD!="NA"&CS!="NA")
tally2<-table(btoak.csld.wi$female) #Count no. of observations per ID
btoak.csld.wi<-btoak.csld.wi[btoak.csld.wi$female %in% names(tally2)[tally2>1],] #Exclude one-time breeders
btoak.csld.wi<-btoak.csld.wi%>%group_by(female)%>%mutate(wi.LD=scale(mc.LD, scale=FALSE)) #Caluclate within-individual deviations
plot(btoak.csld.wi$wi.LD,btoak.csld.wi$mc.CS, xlab="Within-individual mean-centred BD", ylab="Mean-centred LD")
m.pocs.wild<-glmer(CS~wi.LD+(1|female),data=btoak.csld.wi, family = "poisson")
summary(m.pocs.wild)

sink("CSLD.lmm.txt")
print(summary(m.mccs.mcld))
print(summary(m.mccs.wild))
sink()

#CS-LD bivariate random regression
#Generate Lifetime Breeding Success (LBS) stack data
CSLD.LBS<-LDBD.LBS
colnames(CSLD.LBS)[5:6]<-c("LD","LBS.CS")

#Generate Observations (OBS) stack data
CSLD.OBS<-btoak%>%filter(year<2019)%>%select(year,female,f.age,mc.LD,mc.CS)
CSLD.OBS$obs<-seq(from=nrow(CSLD.LBS)+1,to=nrow(CSLD.OBS)+nrow(CSLD.LBS)) #Add observation IDs. Continue from end of LBS table.
CSLD.OBS<-CSLD.OBS[,c(6,2,1,3,4,5)]
colnames(CSLD.OBS)<-c("obs","ID","year","age","LD","LBS.CS")
CSLD.OBS$trait<-rep("CS")
CSLD.OBS$variable<-rep("CS")
CSLD.OBS$family<-rep("gaussian")

#Combine stacks
CSLD.stack<-bind_rows(CSLD.LBS,CSLD.OBS)
CSLD.stack$age<-as.factor(CSLD.stack$age)
CSLD.stack$trait<-as.factor(CSLD.stack$trait)
CSLD.stack$variable<-as.factor(CSLD.stack$variable)
CSLD.stack$year<-as.factor(CSLD.stack$year)

#Set prior
CSLD.prior<-list(G=list(G1=list(V=diag(1),nu=1)), #For random effect of year
                 R=list(R1=list(V=diag(3),nu=3,covu=TRUE), #For 3-level VCV 
                        R2=list(V=diag(1),nu=1))) #For residuals

#MCMCglmm
CSLD.mcmc<-MCMCglmm(LBS.CS ~ variable-1 + 
                    at.level(variable,"CS"):LD, 
                    random=~us(at.level(variable,"CS")):year +
                            us(at.level(variable,"CS") + at.level(variable,"CS"):LD) :ID,
                    #|^-----Intercept------^| & |^---------Slope---------^|  grouped by ID
                    rcov=~us(at.level(variable,"LBS")):ID +   
                          us(at.level(variable,"CS")):obs,
                    data=CSLD.stack,
                    prior=CSLD.prior, 
                    family=NULL,
                    nitt=15000000, thin=1000, burnin=1500000, verbose=TRUE)
save(CSLD.mcmc, file="CSLD.mcmc.RData")
autocorr(CSLD.mcmc$VCV)
plot(CSLD.mcmc$VCV)
summary(CSLD.mcmc)

#Extract 3x3 VCV matrix
CSLD.mcmc.P<- CSLD.mcmc$VCV[,2:10]         
CSLD.mcmc.Pmode <- matrix(1:9, nrow = 3)
for (k in 1:9) CSLD.mcmc.Pmode[k] <- posterior.mode(CSLD.mcmc.P[,k])
CSLD.mcmc.Pmode
posterior.mode(mcmc(CSLD.mcmc.P))
HPDinterval(mcmc(CSLD.mcmc.P))

#Estimate selection gradients for intercept and slope (beta = S / P)
CSLD.mcmc.n <- length(CSLD.mcmc$VCV[,2])   # sample size
CSLD.mcmc.beta <- matrix(NA, CSLD.mcmc.n ,2)
for (i in 1:CSLD.mcmc.n) {
  CSLD.mcmc.P3 <- matrix(rep(NA, 9), nrow = 3)  # 3x3 matrix of var-cov for individual int, slope and LBS
  for (k in 1:9) {CSLD.mcmc.P3[k] <- CSLD.mcmc.P[i, k] }  
  CSLD.mcmc.P2 <- CSLD.mcmc.P3[1:2, 1:2]   # 2x2 matrix of just trait intercept & slope var-cov
  CSLD.mcmc.S <- CSLD.mcmc.P3[1:2, 3]   # selection differentials on traits (last column of P3)
  CSLD.mcmc.beta[i,] <- solve(CSLD.mcmc.P2) %*% CSLD.mcmc.S   # selection gradients beta = P^-1 * S
}
colnames(CSLD.mcmc.beta) <- c("beta.intercepts", "beta.slopes")
posterior.mode(mcmc(CSLD.mcmc.beta))
HPDinterval(mcmc(CSLD.mcmc.beta))

#Save post.mode and HPDinterval of matrix values to a .txt file
sink("CSLD.mcmc.txt")
print(summary(CSLD.mcmc))
print(posterior.mode(mcmc(CSLD.mcmc.P)))
print(HPDinterval(mcmc(CSLD.mcmc.P)))
print(posterior.mode(mcmc(CSLD.mcmc.beta)))
print(HPDinterval(mcmc(CSLD.mcmc.beta)))
sink()

#Plot graphs
CSLD.overall<-ggplot(btoak,aes(x=mc.LD, y=mc.CS))+
              geom_jitter(height=0.5, width=0)+
              labs(x="Mean-centered laying date", y="Mean-centered clutch size", size=10)+
              theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
                    panel.background = element_blank(), axis.line = element_line(colour = "black"),
                    axis.title=element_text(size=10))+
              stat_smooth(method="lm",color="black", fill="gray")
CSLD.overall
ggsave(CSLD.overall, filename = "CSLD.overall.png", height=6, width=8) #Export to png

CSLD.wi<-ggplot(btoak.csld.wi,aes(x=wi.LD, y=mc.CS))+
         geom_jitter(height=0.5, width=0)+
         labs(x="Within-individual mean-centered laying date", y="Mean-centered clutch size", size=10)+
         theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
               panel.background = element_blank(), axis.line = element_line(colour = "black"),
               axis.title=element_text(size=10))+
         stat_smooth(method="lm",color="black", fill="gray")
CSLD.wi
ggsave(CSLD.wi, filename = "CSLD.wi.png", height=6, width=8) #Export to png

plot<-ggarrange(LDBD.overall,LDBD.wi,CSLD.overall,CSLD.wi,
                labels=c("A","B","C","D"),
                ncol=2, nrow=2)
plot
ggsave(plot, filename = "plot.pdf", height=6, width=8)
#=================================Other wrangling============================#
#Female descriptives
table(table(btoak$female))
mean(CSLD.LBS$LBS.CS)
range(CSLD.LBS$LBS.CS)
var(CSLD.LBS$LBS.CS)

#Breeding summary
breed.sum<-btoak%>%group_by(year)%>%summarize(nests=table(year),
                                              mean.ld=mean(LD), min.ld=min(LD),max.ld=max(LD),var.ld=var(LD),
                                              mean.cs=mean(CS), min.cs=min(CS),max.cs=max(CS),var.cs=var(CS),
                                              tol.no.hatch=sum(no.hatchlings),mean.no.hatch=sum(no.hatchlings)/nests)

#Oak summary
oakphen<-read.csv("oakphen.csv",header = TRUE)
oak.count<-oakphen%>%group_by(year)%>%summarise(oak=length(unique(treeID)),nest=length(unique(nest.box)),mean.oak=oak/nest) 
oak.sum<-oakbd%>%group_by(year)%>%summarize(mean.bd=mean(date), min.bd=min(date), max.bd=max(date), var.bd=var(date))%>%ungroup()%>%group_by(year,nest.box)%>%summarize(var.bd.within.nb=var(date))