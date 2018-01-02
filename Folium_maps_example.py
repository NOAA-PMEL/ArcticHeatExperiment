
# coding: utf-8

# In[202]:


import numpy as np
import pandas as pd
import urllib

import cmocean
import folium

from selenium import webdriver
import os, time

def cmocean_to_leaflet(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    
    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, "#{:02x}{:02x}{:02x}".format(C[0], C[1], C[2])])
        
    return pl_colorscale

thermal = cmocean_to_leaflet(cmocean.cm.thermal, 1000)

def rgb2hex(r,g,b):
    hex = "#{:02x}{:02x}{:02x}".format(r,g,b)
    return hex

def color_normalize(cmin,cmax,value):
    return (value-cmin)/(cmax-cmin)


# In[66]:


"""--------------------- Get Data  -----------------------------------------"""

### using code from https://ioos.github.io/notebooks_demos/notebooks/2017-03-21-ERDDAP_IOOS_Sensor_Map/
import requests
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def encode_erddap(urlbase, fname, columns, params):
    """
    urlbase: the base string for the endpoint
             (e.g.: https://erddap.axiomdatascience.com/erddap/tabledap).
    fname: the data source (e.g.: `sensor_service`) and the response (e.g.: `.csvp` for CSV).
    columns: the columns of the return table.
    params: the parameters for the query.

    Returns a valid ERDDAP endpoint.
    """
    urlbase = urlbase.rstrip('/')
    if not urlbase.lower().startswith(('http:', 'https:')):
        msg = 'Expected valid URL but got {}'.format
        raise ValueError(msg(urlbase))

    columns = ','.join(columns)
    params = urlencode(params)
    endpoint = '{urlbase}/{fname}?{columns}&{params}'.format

    url = endpoint(urlbase=urlbase, fname=fname,
                   columns=columns, params=params)
    r = requests.get(url)
    r.raise_for_status()
    return url

try:
    from urllib.parse import unquote
except ImportError:
    from urllib2 import unquote

# return profile for float id
def get_profile(alamo_id,starttime,endtime):
    
    urlbase = 'http://ferret.pmel.noaa.gov/alamo/erddap/tabledap'

    fname = 'arctic_heat_alamo_profiles_'+str(alamo_id)+'.csvp'

    columns = ('profileid',
               'FLOAT_SERIAL_NO',
               'CYCLE_NUMBER',
               'REFERENCE_DATE_TIME',
               'JULD',
               'time',
               'latitude',
               'longitude',
               'PRES',
               'TEMP',
               'PSAL')
    params = {
        # Inequalities do not exist in HTTP parameters,
        # so we need to hardcode the `>` in the time key to get a '>='.
        # Note that a '>' or '<' cannot be encoded with `urlencode`, only `>=` and `<=`.
        'time>': starttime+'T00:00:00Z',
        'time<': endtime+'T00:00:00Z',
        'PRES>': 0.5,
        'PRES<': 35,
    }

    url = encode_erddap(urlbase, fname, columns, params)

    df = pd.read_csv(url, index_col=0, parse_dates=['time (UTC)'])
    
    return df

## Data is ingested from ERDDAP Server to PANDAS

df = get_profile(9119,'2017-08-01','2017-12-31')
dfgroup = df.groupby('CYCLE_NUMBER')
dfgbc = dfgroup.mean()
dfgbc['time (UTC)'] = dfgroup.first()['time (UTC)']
dfgbc['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in dfgroup.first()['time (UTC)']]
dfgbc['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in dfgroup.first()['time (UTC)']]
dfgbc['doyfrac'] = dfgbc['doy'] + dfgbc['fracday']
dfgbc['index_name'] = dfgbc.index
dfgbc = dfgbc.round(4)
dfgbc.drop(['REFERENCE_DATE_TIME','FLOAT_SERIAL_NO'], axis=1, inplace=True)

df2 = get_profile(9076,'2016-08-01','2017-12-31')
df2group = df2.groupby('CYCLE_NUMBER')
df2gbc = df2group.mean()
df2gbc['time (UTC)'] = df2group.first()['time (UTC)']
df2gbc['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df2group.first()['time (UTC)']]
df2gbc['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df2group.first()['time (UTC)']]
df2gbc['doyfrac'] = df2gbc['doy'] + df2gbc['fracday']
df2gbc['index_name'] = df2gbc.index
df2gbc = df2gbc.round(4)
df2gbc.drop(['REFERENCE_DATE_TIME','FLOAT_SERIAL_NO'], axis=1, inplace=True)

df3 = get_profile(9085,'2016-08-01','2017-12-31')
df3group = df3.groupby('CYCLE_NUMBER')
df3gbc = df3group.mean()
df3gbc['time (UTC)'] = df3group.first()['time (UTC)']
df3gbc['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df3group.first()['time (UTC)']]
df3gbc['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df3group.first()['time (UTC)']]
df3gbc['doyfrac'] = df3gbc['doy'] + df3gbc['fracday']
df3gbc['index_name'] = df3gbc.index
df3gbc = df3gbc.round(4)
df3gbc.drop(['REFERENCE_DATE_TIME','FLOAT_SERIAL_NO'], axis=1, inplace=True)


# In[189]:


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

tol = .00001



# In[221]:
browser = webdriver.Chrome()

for doymax in range(300,366,1):
    for hourmax in range(0,24,12):
        f1 = folium.map.FeatureGroup()
        
        dfgbc_sub= dfgbc[(dfgbc['doyfrac'] < doymax + (hourmax*60.)/1440.)]
        lats = dfgbc_sub['latitude (degrees_north)'].values
        lngs = dfgbc_sub['longitude (degrees_east)'].values
        colors = dfgbc_sub['TEMP (degree_Celsius)'].values
        for lat, lng, color in zip(lats, lngs, colors):
            nval = find_nearest(np.array([x[0] for x in thermal]),color_normalize(-2.,10.,color))
            f1.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=1,
                    color=thermal[nval][1],
                )
                )
        
        
        # In[218]:
        
        
        f2 = folium.map.FeatureGroup()
        
        df2gbc_sub= df2gbc[(df2gbc['doyfrac'] < doymax + (hourmax*60.)/1440.)]

        lats = df2gbc_sub['latitude (degrees_north)'].values
        lngs = df2gbc_sub['longitude (degrees_east)'].values
        colors = df2gbc_sub['TEMP (degree_Celsius)'].values
        for lat, lng, color in zip(lats, lngs, colors):
            nval = find_nearest(np.array([x[0] for x in thermal]),color_normalize(-2.,10.,color))
            f2.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=1,
                    color=thermal[nval][1],
                )
                )
        
        
        # In[219]:
        
        
        f3 = folium.map.FeatureGroup()

        df3gbc_sub= df3gbc[(df3gbc['doyfrac'] < doymax + (hourmax*60.)/1440.)]
        
        lats = df3gbc_sub['latitude (degrees_north)'].values
        lngs = df3gbc_sub['longitude (degrees_east)'].values
        colors = df3gbc_sub['TEMP (degree_Celsius)'].values
        for lat, lng, color in zip(lats, lngs, colors):
            nval = find_nearest(np.array([x[0] for x in thermal]),color_normalize(-2.,10.,color))
            f3.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=1,
                    color=thermal[nval][1],
                )
                )
        
        
        # In[222]:
        
        
        m = folium.Map(location=[71,-165],
                      tiles='https://api.mapbox.com/styles/v1/sbell/cj48p13bt265k2qvucuielhm7/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1Ijoic2JlbGwiLCJhIjoiY2lqbGlpaHBkMDAyanV5bHhqMTdjYTd5aiJ9.04PwNcY3Piny-YtIg5cIJA',
                      attr='North Star - MapBox',
                      zoom_start=6,
                      png_enabled=True)
        m.add_child(f1)
        m.add_child(f2)
        m.add_child(f3)
        
        # In[220]:
        
        fn = '{doy}{hour}'.format(doy=doymax,hour=str(hourmax).zfill(2))
        tmpurl='file://{path}/{mapfile}.html'.format(path=os.getcwd(),mapfile=fn)
        
        m.save(fn+'.html')
        browser.get(tmpurl)
        #Give the map tiles some time to load
        #time.sleep(.001)
        browser.save_screenshot(fn+'.png')
browser.quit()