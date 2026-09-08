# Visual vs Acoustic BCCH -------------------------------------------------
# Paper title "Visual cues of predation risk outweigh acoustic cues: 
#                 a field experiment in black-capped chickadees"
rm(list = ls()) ## Clean memory

# Packages ----------------------------------------------------------------
library(lme4)
library(ggplot2); theme_set(theme_classic())
library(plyr)
library(arm)
library(tidyverse)
require(MCMCglmm)   #Simulation Markov Chain
library(stargazer) ### For tables results presentations
library(MASS) #To run Quasi-poisson
library(glmmTMB)

#map
library(maps) 
library(sp)   
library(raster) 
library(rgdal) 
library(osmdata)
library(tmap)
library(sf)
library(grid)
library(dplyr)

# Table upload and cleaning -----------------------------------------------
setwd("C:/Users/josue/Desktop/IME_BCCH")
FR<-read.csv("FR_Filtered.csv") #Filtered records analysis
#FR<-read.csv("FR_All_records.csv") #All records analysis

#Make Return a factor ### WARNING: ONLY USE WITH FILTERED RECORDS
FR$Return <- factor(FR$Return, levels = c("0", "1")) #Yes-No Data 


# Coding Variables as factors ---------------------------------------------
#Year, Month, Day, Rep, Feeder, Mount, Speaker, and Track as factors
for (i in 1:8){
  FR[,i] <- as.factor(FR[,i])
}

#Make Treatment a factor
FR$Treatment <- factor(FR$Treatment, levels= c("1","2","3","4"),
                       labels = c("Control", "Acoustic", "Visual", "Both"))  

# Exploring Data and Transforming -----------------------------------------

#rescaling temperature
FR$TempAve=scale(FR$TempDay)
hist(as.numeric(FR$TempAve))

#Latency to resume feeding (LRF in Seconds)
hist(FR$Sec)
FR$LogSec=log(FR$Sec)
hist(FR$LogSec)

#Hourly Feeding Rate calculated (HFRcal)
hist(FR$HFRcal)

#Splitting tables
LRF <- FR
FR_Day <- subset (FR, Return==1) # ONLY USE WITH FILTERED DATA SET
#FR_Day <- FR #ONLY US WITH ALL RECORDS DATA SET
LRF_Day <- FR_Day

N=count(LRF_Day,LRF_Day$Treatment)

# Models ------------------------------------------------------------------

# Filtered Real Latency (LMM Log transformed) ----------------------------------------------------------

mLRF<- MCMCglmm(LogSec~ -1+Sex+
                  Treatment+
                  TempAve:Treatment,
                random = ~ID+Feeder+Rep, data=LRF_Day, family = "gaussian")

summary(mLRF)

FixEf <- mLRF$Sol
RanEf <- mLRF$VCV
posterior.mode((FixEf))
posterior.mode(as.mcmc(RanEf))
HPDinterval(FixEf)
HPDinterval(as.mcmc(RanEf))

#repeatability
ID <- RanEf[,1]
Resid <- RanEf[,4]
rvar <- ID/(ID + Resid) 
posterior.mode(rvar)
HPDinterval(rvar)

#Bayesian p-values 
#p value Temperature:Visual
counts=if_else(FixEf [,8]<0, 1,0)
p=sum(counts)/length(FixEf [,8])

# Filtered Max Latency (LMM Log transformed) ----------------------------------------------------------

m2LRF<- MCMCglmm(LogSec~ -1+Sex+
                  Treatment+
                  TempAve:Treatment,
                random = ~ID+Feeder+Rep, data=LRF, family = "gaussian")

summary(m2LRF)

FixEf2 <- m2LRF$Sol
RanEf2 <- m2LRF$VCV
posterior.mode((FixEf2))
posterior.mode(as.mcmc(RanEf2))
HPDinterval(FixEf2)
HPDinterval(as.mcmc(RanEf2))

#repeatability
ID2 <- RanEf2[,1]
Resid2 <- RanEf2[,4]
rvar2 <- ID2/(ID2 + Resid2) 
posterior.mode(rvar2)
HPDinterval(rvar2)

#Bayesian p-values 
#p value Temperature:Visual
counts2=if_else(FixEf2 [,8]<0, 1,0)
p=sum(counts2)/length(FixEf2 [,8])

# Not filtered Latency (LMM Log transformed) ----------------------------------------------------------

#ONLY USE WITH All RECORDS DATA SET
# m3LRF<- MCMCglmm(LogSec~ -1+Sex+
#                    Treatment+
#                    TempAve:Treatment,
#                  random = ~ID+Feeder+Rep, data=LRF, family = "gaussian")
# 
# summary(m3LRF)
# 
# FixEf3 <- m3LRF$Sol
# RanEf3 <- m3LRF$VCV
# posterior.mode((FixEf3))
# posterior.mode(as.mcmc(RanEf3))
# HPDinterval(FixEf3)
# HPDinterval(as.mcmc(RanEf3))
# 
# #repeatability
# ID3 <- RanEf3[,1]
# Resid3 <- RanEf3[,4]
# rvar3 <- ID3/(ID3 + Resid3) 
# posterior.mode(rvar3)
# HPDinterval(rvar3)
# 
# #Bayesian p-values 
# #p value Temperature:Visual
# counts3=if_else(FixEf3 [,8]<0, 1,0)
# p=sum(counts3)/length(FixEf3 [,8])

# Feeding rate (LMM + centered Latency as covariate) -------------------------------------
FR_Day$scaledLatency<-scale(FR_Day$Sec)

mHFR<- MCMCglmm(HFRcal~ -1+Sex+
                    Treatment+
                    TempAve:Treatment+scaledLatency,
                  random = ~ID+Feeder+Rep, data=FR_Day, family = "gaussian")

summary(mHFR)
#plot(mHFR)

FixEf_P <- mHFR$Sol
RanEf_P <- mHFR$VCV
posterior.mode((FixEf_P))
HPDinterval(FixEf_P)
posterior.mode(as.mcmc(RanEf_P))
HPDinterval(as.mcmc(RanEf_P))

#repeatability
ID_P <- RanEf_P[,1]
Resid_P <- RanEf_P[,4]
rvar_P <- ID_P/(ID_P + Resid_P) 
posterior.mode(rvar_P)
HPDinterval(rvar_P)

#Bayesian p Values
#TempControl
counts_P=if_else(FixEf_P [,7]>0, 1,0)
pP=sum(counts_P)/length(FixEf_P [,7])

#TempVisual
counts_P=if_else(FixEf_P [,9]>0, 1,0)
pP=sum(counts_P)/length(FixEf_P [,9])

#TempBoth
counts_P=if_else(FixEf_P [,10]>0, 1,0)
pP=sum(counts_P)/length(FixEf_P [,10])


# Figures -----------------------------------------------------------------

theme_set(theme_classic())
theme_update(legend.title=element_text(size = 24),legend.position="top",legend.text = element_text(size = 24),
             axis.title = element_text(size=32), axis.text = element_text(size=24))

#Prediction necessary to plot estimates of the model
LRF_Day$LRF <- predict(mLRF, newdata = LRF_Day, type= "response") 
LRF_Day$LRFMin <- exp(LRF_Day$LRF)/60

# Figures saved at 1200x806 pixels
FigLRFTemp= ggplot(LRF_Day, aes(x=TempDay,y=LRFMin,linetype=Treatment, colour=Treatment)) + 
  geom_smooth(method = "glm", size=1.25, alpha=0.15) +
  scale_linetype_manual("Treatment", values = c("Control"=1, "Acoustic"=3,"Visual"=2, "Both"=4) )+
  labs(x="\n Average Daily Temperature",y="Latency to Resume Feeding-Minutes\n") +
  scale_color_brewer(palette="Set1",aesthetics = "colour")+
  coord_cartesian(ylim=c(0,50))


FigLRFTemp


#Prediction necessary to plot estimates of the model
FR_Day$PreHFR=predict(mHFR,type = "response", newdata = FR_Day )
hist(FR_Day$MHFR)

# Figures saved at 1200x806 pixels
FigFRTemp= ggplot(FR_Day, aes(x=TempDay,y=PreHFR,linetype=Treatment, colour=Treatment)) +
  geom_smooth(method = "glm", size=1.25, alpha=0.15) +
  scale_linetype_manual("Treatment", values = c("Control"=1, "Acoustic"=3,"Visual"=2, "Both"=4) )+
  labs(x="\n Average Daily Temperature",y="Feeding Rate (visits/hour) after Return\n") +
  scale_color_brewer(palette="Set1",aesthetics = "colour")+
  coord_cartesian(ylim=c(0,20))

FigFRTemp


#### Fieldsite Map ####
# 
# setwd("C:/josue/Desktop/IME_BCCH/Map")
# 
# ###REFERENCE MAP to US and Canada level
# 
# #can0<-getData('GADM', country="CAN", level=0) # Canada
# can1<-getData('GADM', country="CAN", level=1) # provinces 
# #us1 <- getData('GADM', country="USA", level=1)
# 
# #Projection to WGS84
# newProj <- CRS("+proj=poly +lat_0=0 +lon_0=-100 +x_0=0 
#                +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
# 
# #mapExtentPr <- spTransform(SpatialPoints(mapExtent, proj4string=CRS("+proj=longlat")), newProj)
# can1Pr <- spTransform(can1, newProj)
# #us1Pr <- spTransform(us1, newProj) 
# 
# #zoomPr <- spTransform(SpatialPoints(zoom,proj4string=CRS("+proj=longlat")), newProj)
# 
# #Study Area limits
# Area= rbind(c(-113.763818,53.410839),c(-113.750457,53.399116))
# 
# bg_area = st_bbox(c(xmin = -113.763818, xmax = -113.750457,
#                     ymin = 53.399116, ymax = 53.410839),
#                   crs = st_crs(can1)) %>% 
#   st_as_sfc()
# 
# #zoom= rbind(c(-113.76,53.40),c(-113.74,53.41))
# #mapExtent <- rbind(c(-156, 80), c(-68, 40))  #(c(-156, 80), c(-68, 19)) for US & CAN
# AB <- c("Alberta")
# 
# ###Reference Figure
# 
# #plot(mapExtentPr, pch=NA) 
# #plot(can1Pr, border="white", col="lightgrey", add=TRUE) 
# #plot(us1Pr, border="white", col="lightgrey", add=TRUE) 
# #plot(can1Pr[can1Pr$NAME_1 %in% theseJurisdictions, ], border="white", col="darkgrey", add=TRUE) 
# #plot(zoomPr,pch=15,cex=1,col="black",add=T)
# 
# CAN=tm_shape(can1Pr) + tm_polygons() +
#   tm_shape(can1Pr[can1Pr$NAME_1 %in% AB, ]) +
#   tm_fill(col = "darkgrey" ) + 
#   tm_borders(lwd = 1,col="black") +
#   tm_shape(bg_area) + 
#   tm_borders(lwd = 5,col="black")
# 
# ###Shapefiles Botanic Garden and Alberta
# 
# #ABad=shapefile("shapes/AB_Admin/alberta_administrative.shp")
# 
# ABhw=shapefile("shapes/AB_highway/alberta_highway.shp")
# ABhw_sub <- ABhw[ABhw$TYPE=="primary" , ]
# 
# #ABloc=shapefile("shapes/AB_local/alberta_location.shp")
# #ABnt=shapefile("shapes/AB_Nature/alberta_natural.shp")
# #ABwa=shapefile("shapes/AB_water/alberta_water.shp")
# 
# #General KML reading
# 
# UABG=ogrListLayers("Google/UofA_BG.kml")
# attr(UABG, "driver")
# attr(UABG, "nlayers")
# 
# #Each layer
# 
# BGLimit=readOGR("Google/UofA_BG.kml","Limit")
# BGroads=readOGR("Google/UofA_BG.kml","Roads")
# BGFence=readOGR("Google/UofA_BG.kml","Inner_Fence")
# BGVisit=readOGR("Google/UofA_BG.kml","Visit")
# BGFeederA=readOGR("Google/UofA_BG.kml","Active")
# BGFeederN=readOGR("Google/UofA_BG.kml","Non-Active")
# 
# #plot(ABwa,border="white", col="lightgrey", add=TRUE)
# #Garden= rbind(c(-113.762525,53.410514),c(-113.750811,53.399743))
# 
# 
# ###Figure Study area
# 
# #plot(Area,pch=NA, bty="o",yaxt="n",xaxt="n",xlab=NA,ylab=NA)
# #plot(ABhw_sub, add=T)
# #plot(BGVisit,add=T, border="white", col="lightgrey")
# #plot(BGroads,add=T, col="darkgrey",lty=2)
# #plot(BGLimit,add=T, col="darkgrey",lty=1)
# #plot(BGFence,add=T, col="darkgrey",lty=1)
# #plot(BGFeederA,add=T, col="Black",pch=1,cex=3)
# #plot(BGFeederN,add=T, col="Black",pch=16,cex=3)
# #Inserting Scale bar in figure
# 
# 
# 
# SS = tm_shape(bg_area)+ tm_borders(col="white") +  
#   tm_shape(ABhw_sub) + tm_lines() +
#   tm_shape(BGVisit) + tm_borders() + tm_fill(col="lightgrey") +   
#   tm_shape(BGroads) + tm_lines(lty=2,col="darkgrey") + 
#   tm_shape(BGLimit) + tm_lines(lty=1,col="darkgrey") +
#   tm_shape(BGFence) + tm_lines(lty=1,col="darkgrey") +
#   tm_shape(BGFeederA) + tm_symbols(col="black",shape=16,size =2) +
#   #tm_shape(BGFeederN) + tm_symbols(col="black",shape=1,size=2) +
#   tm_scale_bar(breaks = c(0, .1, .2,.3,.4), size = 1, position = c(0.4,0.00001))
# SS   
# 
# #Insert map of Canada
# print(CAN ,vp=viewport(0.3415,0.105,width=0.175,height=0.175))
# 
# #scalebar(0.5,divs=5, xy=c(0.4,0.01),type = "bar",below="meters",lonlat=T,"500",cex=1.75) #type = "bar"
