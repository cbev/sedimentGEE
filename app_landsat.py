# %%
"""
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/geemap/tree/master/examples/template/template.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/geemap/blob/master/examples/template/template.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://mybinder.org/v2/gh/giswqs/geemap/master?filepath=examples/template/template.ipynb"><img width=58px src="https://mybinder.org/static/images/logo_social.png" />Run in binder</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/geemap/blob/master/examples/template/template.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
</table>
"""

# %%
"""
## Install Earth Engine API and geemap
Install the [Earth Engine Python API](https://developers.google.com/earth-engine/python_install) and [geemap](https://github.com/giswqs/geemap). The **geemap** Python package is built upon the [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) and [folium](https://github.com/python-visualization/folium) packages and implements several methods for interacting with Earth Engine data layers, such as `Map.addLayer()`, `Map.setCenter()`, and `Map.centerObject()`.
The following script checks if the geemap package has been installed. If not, it will install geemap, which automatically installs its [dependencies](https://github.com/giswqs/geemap#dependencies), including earthengine-api, folium, and ipyleaflet.

**Important note**: A key difference between folium and ipyleaflet is that ipyleaflet is built upon ipywidgets and allows bidirectional communication between the front-end and the backend enabling the use of the map to capture user input, while folium is meant for displaying static data only ([source](https://blog.jupyter.org/interactive-gis-in-jupyter-with-ipyleaflet-52f9657fa7a)). Note that [Google Colab](https://colab.research.google.com/) currently does not support ipyleaflet ([source](https://github.com/googlecolab/colabtools/issues/60#issuecomment-596225619)). Therefore, if you are using geemap with Google Colab, you should use [`import geemap.eefolium`](https://github.com/giswqs/geemap/blob/master/geemap/eefolium.py). If you are using geemap with [binder](https://mybinder.org/) or a local Jupyter notebook server, you can use [`import geemap`](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py), which provides more functionalities for capturing user input (e.g., mouse-clicking and moving).
"""

# %%
# Installs geemap package
import subprocess

try:
    import geemap
except ImportError:
    print('geemap package not installed. Installing ...')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'geemap'])

# Checks whether this notebook is running on Google Colab
try:
    import google.colab
    import geemap.eefolium as emap
except:
    import geemap as emap

# Authenticates and initializes Earth Engine
import ee

try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()  

# %%
"""
## Create an interactive map 
The default basemap is `Google Satellite`. [Additional basemaps](https://github.com/giswqs/geemap/blob/master/geemap/geemap.py#L13) can be added using the `Map.add_basemap()` function. 
"""

# %%
Map = emap.Map(center=[40,-100], zoom=4)
Map.add_basemap('ROADMAP') # Add Google Map
Map

# %%
"""
## Add Earth Engine Python script 
"""

# %%
# Add Earth Engine dataset
import math


#### Options###########
startDate = ee.Date('2015-01-01') # ee.Date('1987-01-01')
endDate =ee.Date('2017-01-01') # ee.Date(Date.now())

# Set the range for the SSC color bar
scale_min=0
scale_max=2700

# REGRESSION EQUAIONS: UNCOMMENT THE OPTIONS YOU PREFER!

# # Use ~2700 as max SSC:
# L8_SSC='27537.074*red+22898.273*green-26233.377*blue-15220.77*nir-2369.382+1500' # multi-linear regression
# L5L7_SSC='27537.074*red+22898.273*green-26233.377*blue-15220.77*nir-2369.382+1500'# multi-linear regression

# # Use ~1500 as max SSC
# L8_SSC='2852.492*(red/green)-2438.943+700'# Baruria - wet season calibration
# L5L7_SSC='2852.492*(red/green)-2438.943+700'# Baruria - wet season calibration

# Use ~1500 as max SSC
L8_SSC='0.3*exp(5.44*(red/green)+1.98)';# Baruria
L5L7_SSC='0.3*exp(5.44*(red/green)+1.98)';# Baruria


# # Use ~1000 as max SSC:
# L8_SSC='69.39*red*100-201' # Islam et al (2001)
# L5L7_SSC='69.39*red*100-201' # Islam et al (2001)

# # 1. Use ~800 as max SSC:
# L8_SSC='524.729*red/blue-425.191'# Baruria - all season calibration
# L5L7_SSC='524.729*red/blue-425.191'# Baruria - all season calibration

##################/

cloud_thresh = ee.Number(0.3); # min percent of non-cloudy
ref_thresh_L5L7= ee.Number(0.4); # for red+blue band
ref_thresh_L8= ee.Number(0.4); # for red+blue band
red_thresh= ee.Number(0.4); # for red band

soil_dataset = ee.Image('OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02')
soil_layer = soil_dataset.select('b0'); # b0, b10, b30, b60, b100, b200
soil_palette= ["d5c36b", "b96947", "9d3706", "ae868f", "f86714", "46d143", "368f20", "3e5a14","ffd557","fff72e", "ff5a9d", "ff005b"]
soil_names= ['SiCl','SaCl','ClLo', 'SiClLo', 'SaClLo', 'Lo', 'SiLo', 'SaLo', 'Si','LoSa', 'Sa']
Map.setCenter(89.790282, 24.065000,8)

places = {'Baruria':baruria,
              'Mawa': mawa,
              'Hardinge_Bridge': hardinge_bridge,
              'Bahadurabad': bahadurabad,
              'Naria': naria}

select = ui.Select({
  'items': Object.keys(places),
  'onChange': function(key) {
    ROI = places[key]
    Map.centerObject(ROI)

    #****Round Time***************************************************************************
    def Roundtime(img):
      I = ee.Image(img)
      time = ee.Number(I.get('system:time_start')).round()
      return I.set('system:time_start',time)

    #****Convert Scale of Surface Reflectance Estimates**************************************
    def Convert_scale(img):
      I = ee.Image(img)
      correct_scale = I.select(['blue','green','red','nir','swir1','swir2']).multiply(0.0001)
      return I.addBands(correct_scale,['blue','green','red','nir','swir1','swir2'],True)


    #****Calculate Area**********************************************************************
    def calcArea(img):
      I = ee.Image(img)
      count = I.reduceRegion({
        'reducer': ee.Reducer.count(),
        'geometry': ROI,
        'scale': 90,
        'maxPixels': 6098838800,
      })
      area = ee.Number(count.get('green')).multiply(8100)
      return I.set('ROI_area',area)


    #****Define Cloud Masking*************************************************************
    # function to mask out cloudy pixels.
    def getCloudsL8(img):
      I = ee.Image(img)
      qa = I.select('pixel_qa').int64()
  ## Landsat default
      # mask = I.select('blue').add(I.select('red')).lt(ref_thresh_L8)
      #   .And(I.select('red').lt(red_thresh))
      #   .And(I.select('green').lt(red_thresh))
      #   .And(I.select('blue').lt(red_thresh))
      #   .And(I.select('nir').lt(red_thresh))
      #   .And(qa.bitwiseAnd(8).eq(0).And(qa.bitwiseAnd(32).eq(0)))
  ## More restrictive [1]
      # mask = qa.bitwiseAnd(32).eq(0)# masks clouds
      # .And(qa.bitwiseAnd(8).eq(0))# masks cloud shadows
      # .And(qa.bitwiseAnd(16).eq(0))# masks snow
      # .And(qa.bitwiseAnd(1).eq(0))  # masks fill
      # .And(I.select('red').lt(red_thresh))
      # .And(I.select('green').lt(red_thresh))
      # .And(I.select('blue').lt(red_thresh))
      # .And(I.select('nir').lt(red_thresh))
      # .And(I.select('blue').add(I.select('red')).lt(ref_thresh_L8))
  ## Most restrictive cloud mask [2]
      mask=qa.eq(324).Or(qa.eq(322)) #pixel qa bands for clear land and clear water \
                .And(I.select('red').lt(red_thresh)) \
                .And(I.select('green').lt(red_thresh)) \
                .And(I.select('blue').lt(red_thresh)) \
                .And(I.select('nir').lt(red_thresh)) \
                .And(I.select('blue').add(I.select('red')).lt(ref_thresh_L8)) 

      mask=mask.rename('clear')
      sum = mask.reduceRegion({
        'reducer': ee.Reducer.sum(),
        'geometry': ROI,
        'scale': 90,
        'maxPixels': 6098838800,
      })
      I = I.set("clear_pixels",sum.get('clear'))
      I = I.addBands(mask.rename('clear_mask'))
      return I


    #****Define Cloud Masking*************************************************************
    def getCloudsL5L7(img):
      I = ee.Image(img)
      qa = I.select('pixel_qa')
  ## Landsat default
    # If the cloud bit (5) is set and the cloud confidence (7) is high
    # or the cloud shadow bit is set (3), then it's a bad pixel.
    # cloud =I.select('blue').add(I.select('red')).gt(ref_thresh_L5L7)
    # .And(I.select('red').gt(red_thresh))
    # .And(I.select('green').gt(red_thresh))
    # .And(I.select('blue').gt(red_thresh))
    # .And(I.select('nir').gt(red_thresh))
    # .And(qa.bitwiseAnd(1 << 5)
    # .And(qa.bitwiseAnd(1 << 7))
    # .Or(qa.bitwiseAnd(1 << 3)))
    # mask=cloud.Not()
  # # More restrictive [1]
  #     mask = qa.bitwiseAnd(32).eq(0)# masks clouds
  #       .And(qa.bitwiseAnd(8).eq(0))# masks cloud shadows
  #       .And(qa.bitwiseAnd(16).eq(0))# masks snow
  #       .And(qa.bitwiseAnd(1).eq(0))  # masks fill
  #       .And(I.select('red').lt(red_thresh))
  #       .And(I.select('green').lt(red_thresh))
  #       .And(I.select('blue').lt(red_thresh))
  #       .And(I.select('nir').lt(red_thresh))
  #       .And(I.select('blue').add(I.select('red')).lt(ref_thresh_L5L7))
  ## Most restrictive [2]
      mask =qa.eq(68).Or(qa.eq(66)) \
        .And(I.select('red').lt(red_thresh)) \
        .And(I.select('red').lt(red_thresh)) \
        .And(I.select('green').lt(red_thresh)) \
        .And(I.select('blue').lt(red_thresh)) \
        .And(I.select('nir').lt(red_thresh)) \
        .And(I.select('blue').add(I.select('red')).lt(ref_thresh_L5L7))

      mask=mask.rename('clear')
      sum = mask.reduceRegion({
        'reducer': ee.Reducer.sum(),
        'geometry': ROI,
        'scale': 90,
        'maxPixels': 6098838800,
        })
      I = I.set("clear_pixels",sum.get('clear'))
      I = I.addBands(mask.rename('clear_mask'))
      return I



    def maskClouds(img):
      I = ee.Image(img)
      return I.updateMask(I.select('clear_mask'))
      

    #****Define Index Calculation*********************************************************
    def calcIndex(img):
      I = ee.Image(img)

      MNDWI = I.normalizedDifference(['green','swir1'])
      MNDWI = MNDWI.rename('MNDWI')

      MBSRV = I.select('green').add(I.select('blue'))
      MBSRV = MBSRV.rename('MBSRV')

      MBSRN = I.select('swir1').add(I.select('nir'))
      MBSRN = MBSRN.rename('MBSRN')

      AWEsh = I.select('blue') \
        .add(I.select('green').multiply(2.5)) \
        .add(MBSRN).multiply(-1.5) \
        .add(I.select('swir2').multiply(-0.25))
      AWEsh = AWEsh.rename('AWEsh')

      I = I.addBands(MNDWI)
      I = I.addBands(MBSRV)
      I = I.addBands(MBSRN)
      I = I.addBands(AWEsh)
      return I

    #****Define DSWE water classification ************************************************
    def WaterTests(img):
      I = ee.Image(img)
      MNDWI = I.select('MNDWI')
      MBSRN = I.select('MBSRN')
      MBSRV = I.select('MBSRV')
      AWEsh = I.select('AWEsh')

      #MNDWI > 0.0123
      Test1 = MNDWI.gt(0.0123)

      #mbsrv > mbsrn
      Test2 = MBSRV.gt(MBSRN)

      #awesh > 0.0
      Test3 = AWEsh.gt(0)

      #mndwi > -0.5 && SWIR1 < 1000 && NIR < 1500
      subTest1 = MNDWI.gt(-0.5)
      subTest2 = I.select('swir1').lt(0.1)
      subTest3 = I.select('nir').lt(0.15)
      Test4 = (subTest1.add(subTest2).add(subTest3)).eq(3)

      #mndwi > -0.5 && SWIR2 < 1000 && NIR < 2000
      subTest4 = MNDWI.gt(-0.5)
      subTest5 = I.select('swir2').lt(0.1)
      subTest6 = I.select('nir').lt(0.2)
      Test5 = (subTest4.add(subTest5).add(subTest6)).eq(3)

      TestSum = Test1.add(Test2).add(Test3).add(Test4).add(Test5)
      Class1 = TestSum.gte(4)
      Class2_1 = TestSum.eq(3)

      Class1 = Class1.rename('Water')
      sum = Class1.reduceRegion({
        'reducer': ee.Reducer.sum(),
        'geometry': ROI,
        'scale': 90,
        'maxPixels': 6098838800,
      })
      I = I.set('water_pixels',sum.get('Water'))
      return I.addBands(Class1)


    #****Define Land Masking***************************************************************
    def maskLand(img):
      I = ee.Image(img)
      mask = I.select('Water').gt(0)
      return I.updateMask(mask)


    #****Define Ratio Between Cloud and Water**********************************************
    def calc_watercloud_ratio(img):
      I = ee.Image(img)
      ratio = ee.Number(I.get('clear_pixels')).divide(ee.Number(I.get('water_pixels')))
      return I.set('water_cloud_ratio',ratio)


    def calcCloudAreaRatio(img):
      I = ee.Image(img)
      cloudArea = ee.Number(I.get('clear_pixels')).multiply(8100)
      return I.set('CloudAreaRatio',cloudArea.divide(I.get('ROI_area')))



    #*****Calc SSC************************************************************
    def calcSSCL8(img):
      I=ee.Image(img)
      ssc=I.expression(L8_SSC,
      {'blue':I.select('blue'), 'green': I.select('green'), 'red': I.select('red'), 'nir': I.select('nir')})
      ssc=ssc.rename('ssc')
      I=I.addBands(ssc)
      return I

    def calcSSCL5L7(img):
      I=ee.Image(img)
      ssc=I.expression(L5L7_SSC,
      {'blue':I.select('blue'), 'green': I.select('green'), 'red': I.select('red'), 'nir': I.select('nir')})
      ssc=ssc.rename('ssc')
      I=I.addBands(ssc)
      return I

    def avgSSC= function(img):
      I = ee.Image(img)
      temp=I.select('ssc')
      avgSSC = temp.reduceRegion({
        'reducer': ee.Reducer.mean(),
        'geometry': ROI,
        'scale': 90,
        'maxPixels': 6098838800,
      })
      return I.set('avgSSC',avgSSC.get('ssc'))


    coefficients = {
    'etm2oli_ols_not_nir': {
      'itcps': ee.Image.constant([0.0003, 0.0088, 0.0061, 0, 0.0254, 0.0172]),
      'slopes': ee.Image.constant([0.8474, 0.8483, 0.9047, 1, 0.8937, 0.9071])
      },
      'etm2oli_ols': {
      'itcps': ee.Image.constant([0.0003, 0.0088, 0.0061, 0.0412, 0.0254, 0.0172]),
      'slopes': ee.Image.constant([0.8474, 0.8483, 0.9047, 0.8462, 0.8937, 0.9071])
      },
    'oli2etm_ols': {
      'itcps': ee.Image.constant([0.0183, 0.0123, 0.0123, 0.0448, 0.0306, 0.0116]),
      'slopes': ee.Image.constant([0.885, 0.9317, 0.9372, 0.8339, 0.8639, 0.9165])
      },
    'rma': {
      'itcps': ee.Image.constant([-0.0095, -0.0016, -0.0022, -0.0021, -0.0030, 0.0029]),
      'slopes': ee.Image.constant([0.9785, 0.9542, 0.9825, 1.0073, 1.0171, 0.9949])
      }
        }

    # Define function to apply harmonization transformation.
    def etm2oli= (img):
      I = ee.Image(img)
      convert = I.select(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']) \
        .multiply(coefficients.etm2oli_ols_not_nir.slopes) \
        .add(coefficients.etm2oli_ols_not_nir.itcps)
      return I.addBands(convert,['blue', 'green', 'red', 'nir', 'swir1', 'swir2'],True)



    # Landsat 8
    L8imgs = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') # get all images in the date range and areas \
      .filterDate(startDate, endDate) \
      .filterBounds(gange_brahm)
    L8imgs = L8imgs.map(Roundtime)
    L8imgs=L8imgs.select(['B2', 'B3','B4','B5','B6','B7','pixel_qa'],
      ['blue', 'green', 'red', 'nir', 'swir1','swir2','pixel_qa'])
    L8imgs = L8imgs.map(Convert_scale)
    L8imgs = L8imgs.map(calcArea)
    L8imgs = L8imgs.map(getCloudsL8)
    L8imgs=L8imgs.select(['blue', 'green', 'red', 'nir', 'swir1','swir2', 'clear_mask', 'pixel_qa'])
    L8natural = L8imgs.select(['nir','red','green','blue', 'pixel_qa'])
    L8imgs = L8imgs.map(maskClouds)
    L8imgs = L8imgs.map(calcIndex)
    L8imgs = L8imgs.map(WaterTests)
    L8imgs = L8imgs.map(maskLand)
    #L8imgs = L8imgs.map(calc_watercloud_ratio)
    L8imgs = L8imgs.map(calcCloudAreaRatio)
    L8imgs = L8imgs.map(calcSSCL8)
    L8imgs = L8imgs.map(avgSSC)
    L8imgs=L8imgs.select(['blue', 'green', 'red', 'nir', 'swir1','swir2', 'clear_mask', 'pixel_qa','ssc'])
    L8imgs_ROI = L8imgs.filter(ee.Filter.gt('ROI_area',ee.Number(ROI.area()).multiply(0.9)))
    L8imgs_ROI = L8imgs_ROI.filter(ee.Filter.gt('CloudAreaRatio',cloud_thresh)) \
      .filter(ee.Filter.gt('water_pixels',0))

  # Landsat 7
    L7imgs = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR') \
      .filterDate(startDate, endDate) \
      .filterBounds(gange_brahm)
    L7imgs = L7imgs.map(Roundtime)
    L7imgs=L7imgs.select(['B1', 'B2', 'B3','B4','B5','B7', 'sr_cloud_qa','pixel_qa'],
      ['blue', 'green', 'red', 'nir', 'swir1','swir2', 'sr_cloud_qa','pixel_qa'])
    L7imgs = L7imgs.map(Convert_scale)
    L7imgs = L7imgs.map(etm2oli)
    L7imgs = L7imgs.map(calcArea)
    L7imgs = L7imgs.map(getCloudsL5L7)
    L7imgs=L7imgs.select(['blue', 'green', 'red', 'nir', 'swir1','swir2', 'clear_mask', 'sr_cloud_qa','pixel_qa'])
    L7natural = L7imgs.select(['nir','red','green','blue', 'pixel_qa'])
    L7imgs = L7imgs.map(maskClouds)
    L7imgs = L7imgs.map(calcIndex)
    L7imgs = L7imgs.map(WaterTests)
    L7imgs = L7imgs.map(maskLand)
    #L7imgs = L7imgs.map(calc_watercloud_ratio)
    L7imgs = L7imgs.map(calcCloudAreaRatio)
    L7imgs = L7imgs.map(calcSSCL5L7)
    L7imgs = L7imgs.map(avgSSC)
    L7imgs=L7imgs.select(['blue', 'green', 'red', 'nir', 'swir1','swir2', 'clear_mask', 'pixel_qa','ssc'])
    L7imgs_ROI = L7imgs.filter(ee.Filter.gt('ROI_area',ee.Number(ROI.area()).multiply(0.9)))
    L7imgs_ROI = L7imgs_ROI.filter(ee.Filter.gt('CloudAreaRatio',cloud_thresh)) \
      .filter(ee.Filter.gt('water_pixels',0))

  # Landsat 5
    L5imgs = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR') \
      .filterDate(startDate, endDate) \
      .filterBounds(gange_brahm)
    L5imgs = L5imgs.map(Roundtime)
    L5imgs=L5imgs.select(['B1', 'B2', 'B3','B4','B5','B7', 'sr_cloud_qa','pixel_qa'],
      ['blue', 'green', 'red', 'nir', 'swir1','swir2', 'sr_cloud_qa','pixel_qa'])
    L5imgs = L5imgs.map(Convert_scale)
    L5imgs = L5imgs.map(etm2oli)
    L5imgs = L5imgs.map(calcArea)
    L5imgs = L5imgs.map(getCloudsL5L7)
    L5natural = L5imgs.select(['nir','red','green','blue', 'pixel_qa'])
    L5imgs=L5imgs.select(['blue', 'green', 'red', 'nir', 'swir1','swir2', 'clear_mask', 'pixel_qa'])
    L5imgs = L5imgs.map(maskClouds)
    L5imgs = L5imgs.map(calcIndex)
    L5imgs = L5imgs.map(WaterTests)
    L5imgs = L5imgs.map(maskLand)
    #L5imgs = L5imgs.map(calc_watercloud_ratio)
    L5imgs = L5imgs.map(calcCloudAreaRatio)
    L5imgs = L5imgs.map(calcSSCL5L7)
    L5imgs = L5imgs.map(avgSSC)
    L5imgs=L5imgs.select(['blue', 'green', 'red', 'nir', 'swir1','swir2', 'clear_mask', 'pixel_qa','ssc'])
    L5imgs_ROI = L5imgs.filter(ee.Filter.gt('ROI_area',ee.Number(ROI.area()).multiply(0.9)))
    L5imgs_ROI = L5imgs_ROI.filter(ee.Filter.gt('CloudAreaRatio',cloud_thresh)) \
      .filter(ee.Filter.gt('water_pixels',0))

  # Merge
    combine_ROI=L8imgs_ROI.merge(L7imgs_ROI).merge(L5imgs_ROI) # merge(L4imgs)
    combine=L8imgs.merge(L7imgs).merge(L5imgs) # merge(L4imgs)
    combine_nat=L8natural.merge(L7natural).merge(L5natural) #merge(L4natural).
    combine_ROI=combine_ROI.sort('system:time_start')
    combine=combine.sort('system:time_start')
    combine_nat=combine_nat.sort('system:time_start')
    print(combine)
    PlotTimeSeries(combine, combine_ROI, combine_nat, ROI)
  }})

# Set a place holder.
select.setPlaceholder('Choose a location...')
select.style().set('position', 'top-center')
Map.add(select)

def PlotTimeSeries= (satImgs, satImgs_ROI, satTerrain, ROI):
#****Plot Timeseries*********************************************************************
  #WaterArea = ee.Array(satImgs_ROI.aggregate_array('water_pixels')).multiply(0.0081); #Conversion to km^2
  time = satImgs_ROI.aggregate_array('system:time_start')
  CloudCover = ee.Array(satImgs_ROI.aggregate_array('CLOUD_COVER'))
  AverageSSC=ee.Array(satImgs_ROI.aggregate_array('avgSSC'))

  # Create an image time series chart.
  chart = ui.Chart.array.values(AverageSSC,0,time) \
    .setOptions({
      'title': 'Surface Suspended Sediment Concentration (SSSC) Time Series',
      'pointSize': 4,
      'hAxis': {'title': 'Date'},
      'vAxis': {'title': 'SSSC (mg/L)'},
      'legend': '{position': 'top'},
      'lineWidth': 1
    })

  # Add the chart to the map.
  chart.style().set({
    'position': 'bottom-right',
    'width': '550px',
    'height':'300px'
  })
  Map.add(chart)

  # Create a label on the map.
  label = ui.Label('Click a point on the chart to show the image for that date.')
  Map.add(label)

  # SSC legend
  ssc_legend = ui.Panel({
    'style': {
    'position': 'bottom-left',
    'padding': '8px 10px'}})

    # SSC legend title
  ssc_legendTitle = ui.Label({
    'value': 'SSC (mg/L)',
    'style': {
    'fontWeight': 'bold',
    'fontSize': '18px',
    'margin': '0 0 4px 0',
    'padding': '0'}})
  ssc_legend.add(ssc_legendTitle)

    # create text on top of SSC legend for max value
  max_ssc = ui.Panel({
    'widgets': [
    ui.Label('Max SSC')],})
  ssc_legend.add(max_ssc)

  # Create gradient
  viz={'min': 0, 'max':1000,
  'palette': ['042333','2c3395','744992','b15f82','eb7958','fbb43d','e8fa5b']}
  lon = ee.Image.pixelLonLat().select('latitude')
  gradient = lon.multiply((viz.max-viz.min)/100.0).add(viz.min)
  ssc_legendImage = gradient.visualize(viz)

  # create gradient thumbnail from the image
  thumbnail = ui.Thumbnail({
    'image': ssc_legendImage,
    'params': '{bbox':'0, 0, 10, 100', 'dimensions':'10x200'},
    'style': '{padding': '1px', 'position': 'bottom-center'}
    })
  ssc_legend.add(thumbnail)

  # create text on bottom of legend for min value
  min_ssc = ui.Panel({
  'widgets': [ui.Label('0')],})

  ssc_legend.add(min_ssc)
  Map.add(ssc_legend)

  #Add Soil Legend
  # set position of panel
  soil_legend = ui.Panel({
    'style': {
      'position': 'bottom-left',
      'padding': '8px 15px'}})

  # Create legend title
  soil_legendTitle = ui.Label({
    'value': 'Soil Texture',
    'style': {
      'fontWeight': 'bold',
      'fontSize': '18px',
      'margin': '0 0 4px 0',
      'padding': '0'
      }
  })

  # Add the title to the panel
  soil_legend.add(soil_legendTitle)

  # Creates and styles 1 row of the legend.
  def makeRow(color, name):

        # Create the label that is actually the colored box.
        colorBox = ui.Label({
          'style': {
            'backgroundColor': '#' + color,
            # Use padding to give the box height and width.
            'padding': '8px',
            'margin': '0 0 4px 0'
          }
        })

        # Create the label filled with the description text.
        description = ui.Label({
          'value': name,
          'style': '{margin': '0 0 4px 6px'}
        })

        # return the panel
        return ui.Panel({
          'widgets': [colorBox, description],
          'layout': ui.Panel.Layout.Flow('horizontal')
        })
  


  # Add color and and names
  for i in range(0, 11, 1):
    soil_legend.add(makeRow(soil_palette[i], soil_names[i]))


  # add legend to map (alternatively you can also print the legend to the console)
  Map.add(soil_legend)


  # When the chart is clicked, update the map and label.
  chart.onClick(function(xValue, yValue, seriesName) {
    if (!xValue) return;  # Selection was cleared.
    # Show the terrain  image for the clicked date.
    start = ee.Date(xValue).advance(ee.Number(-2),'day')
    end = ee.Date(xValue).advance(ee.Number(2),'day')
    image =satImgs.filterDate(start, end).qualityMosaic('pixel_qa')
    natural_image = satTerrain.filterDate(start, end).qualityMosaic('pixel_qa')
    terrainLayer = ui.Map.Layer(natural_image, {
      'bands': ['red','green','blue'],
      'max': 0.18,
      'min': 0}, 'Terrain')
    Map.layers().reset([terrainLayer])

     # Add soil layer and legend
    Map.addLayer(soil_layer, {'min':1, 'max':12, 'palette': soil_palette}, 'Soil texture', False)


    # Update SSC legned
    ssc_legend.remove(max_ssc)
    ssc_legend.remove(thumbnail)
    ssc_legend.remove(min_ssc)
    scale_max=yValue*2.1
    viz={'min': 0, 'max':scale_max,
      'palette': ['042333','2c3395','744992','b15f82','eb7958','fbb43d','e8fa5b']}

    max_ssc = ui.Panel({
      'widgets': [
      ui.Label(math.round(scale_max))],})
    ssc_legend.add(max_ssc)
    ssc_legend.add(thumbnail)
    ssc_legend.add(min_ssc)

    # Add SSC map
    I=image.clip(gange_brahm)
    Map.addLayer(I.select('ssc'), viz,'SSC')

    # Show a label with the date on the map.
    #label.setValue((new Date(xValue)).toLocaleString())
    label.setValue((new Date(xValue)).toUTCString())

    })

    print(chart.getChartType())




# %%
"""
## Display Earth Engine data layers 
"""

# %%
Map.addLayerControl() # This line is not needed for ipyleaflet-based Map.
Map