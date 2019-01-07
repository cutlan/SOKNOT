# Vegetation Health Index - Mt. Kilimanjaro World Heritage Site
import os
import sys
import json
import ee
import datetime
from datetime import date
from calendar import monthrange
from flask import jsonify

ee.Initialize()

lst = ee.ImageCollection('MODIS/006/MOD11A1')		#LST	MODIS/MYD11A1
evi = ee.ImageCollection('MODIS/MOD09GA_006_EVI')
ndvi = ee.ImageCollection('MODIS/MOD09GA_006_NDVI')
ndwi = ee.ImageCollection('MODIS/MOD09GA_006_NDWI')
#TANZANIA
#qdgc = ee.FeatureCollection('users/lmathew/TZA')
#Mt Kilimanjaro - 50Km Radius
qdgc = ee.FeatureCollection('users/lmathew/Kilimanjaro/mk_radius_50km')

datey1 = '2000-1-1'
datey2 = '2019-1-1'

lstminmax = lst.filterDate(datey1, datey2).select('LST_Day_1km').filterBounds(qdgc)
lstminmax = lst.filterDate(datey1, datey2).select('LST_Night_1km').filterBounds(qdgc)
lstmaxa = lstminmax.max()
lstmina = lstminmax.min()
lstmaxbb = lstmaxa.reduceRegion(ee.Reducer.max(), qdgc, 10000)
lstminbb = lstmina.reduceRegion(ee.Reducer.min(), qdgc, 10000)
lstmaxbbb = lstmaxbb.getInfo().values()[0]
lstminbbb = lstminbb.getInfo().values()[0]
lstmaxb = ee.Image.constant(lstmaxbbb)
lstminb = ee.Image.constant(lstminbbb)

ndwimaxb = ee.Image.constant(1)
ndwiminb = ee.Image.constant(-1)

for i in range(int(2015), int(2018)):
    for j in range(int(1), int(13)):
        dashi = "-"
        datedd = monthrange(i,j)[1]
        foo_name = 'TZA-VHI-' + str(i) + '-' + str(j)
        dateaymd1 = (str(i),str(j),str(1))
        dateaymd2 = dashi.join(dateaymd1)
        datebymd1 = (str(i),str(j),str(datedd))
        datebymd2 = dashi.join(datebymd1)
        evia = ee.ImageCollection(evi).filterDate(dateaymd2, datebymd2)
        lsta = ee.ImageCollection(lst).filterDate(dateaymd2, datebymd2)
        evib = evia.mean()
        lstb = lsta.mean()

        evic = evib.subtract(eviminb).divide(evimaxb.subtract(eviminb))
        lstc = lstmaxb.subtract(lstb).divide(lstmaxb.subtract(lstminb))

        evid = evic.multiply(100)
        lstd = lstc.multiply(100)

        foo_vhi = evid.multiply(0.5).add(lstd.multiply(0.5))

        task = ee.batch.Export.image.toDrive(
            image=foo_vhi,
            description=foo_name,
            folder="RS",
            fileNamePrefix=foo_name,
            region=qdgc.geometry().bounds().getInfo()["coordinates"],
            scale=1000)

        task.start()
        print "exporting:- " + foo_name


