
# coding: utf-8

# In[202]:


import numpy as np
import pandas as pd
import urllib
import datetime

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
thermal[-1] = [1.0, '#767474'] ### replace highest color value with white (so all data at extreme + end is white)

def rgb2hex(r,g,b):
    hex = "#{:02x}{:02x}{:02x}".format(r,g,b)
    return hex

def color_normalize(cmin,cmax,value):
    return (value-cmin)/(cmax-cmin)


"""--------------------- Get ArgosData  ------------------------------------"""

class ARGOS_SERVICE(object):
    r"""Download and parse data from the ARGOS Archive"""

    @staticmethod
    def get_data(filename=None, ARGOS_Type=None):
        r"""
        Basic Method to open files.  Specific actions can be passes as kwargs for instruments
        """

        fobj = open(filename)
        data = fobj.read()


        buf = data
        return BytesIO(buf.strip())

    @staticmethod
    def drifter_parse(fobj):
        r"""

        """
        argo_to_datetime =lambda date: datetime.datetime.strptime(date, '%Y %j %H%M')

        header=['argosid','lat','lon','year','doy','hhmm','s1','s2','s3','s4','s5','s6','s7','s8']
        df = pd.read_csv(fobj,delimiter='\s+',header=0,
          names=header,index_col=False,
          dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
          parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime)

        df.set_index(pd.DatetimeIndex(df['year_doy_hhmm']),inplace=True)
        df.drop('year_doy_hhmm',axis=1,inplace=True)

        return df

def sst_argos(s1,s2):
    try:
        output = int(format(int(s1,16),'08b')[6:] + format(int(s2,16),'08b'),2) 
        output = (output * 0.04) - 2.0   
    except:
        output = 1e35
    return output

def strain_argos(s1,manufacter='MetOcean'):
    try:
      converted_word = int(format(int(s1,16),'08b'),2)
      if manufacter == 'MetOcean':
        output = converted_word
      else:
        output = converted_word / 100.
    except:
      output = 1e35
    return output

def voltage_argos(s1):
    try:
        converted_word = int(format(int(s1,16),'08b')[:6],2)
        output = (converted_word * 0.2) + 5   
    except:
        output = 1e35
    return output

def checksum_argos(s1,s2,s3,s4):
    try:
        converted_word = int(format(int(s1,16),'08b'),2) + \
                         int(format(int(s2,16),'08b'),2) + \
                         int(format(int(s3,16),'08b'),2)
        checksum_test = converted_word % 256 
        if  checksum_test == int(format(int(s4,16),'08b'),2):
          output = True
        else:
          output = False
    except:
        output = 1e35
    return output

## Data is read in from raw drifter id files
argo_to_datetime =lambda date: datetime.datetime.strptime(date, '%Y %j %H%M')

header=['argosid','lat','lon','year','doy','hhmm','s1','s2','s3','s4','s5','s6','s7','s8']
df_122537 = pd.read_csv('data/drifters/122537.y2017',delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime,error_bad_lines=False)

df_122537.set_index(pd.DatetimeIndex(df_122537['year_doy_hhmm']),inplace=True)
df_122537.drop('year_doy_hhmm',axis=1,inplace=True)

df_122537['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df_122537.index]
df_122537['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df_122537.index]
df_122537['doyfrac'] = df_122537['doy'] + df_122537['fracday']

##
df_122541 = pd.read_csv('data/drifters/122541.y2017',delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime,error_bad_lines=False)

df_122541.set_index(pd.DatetimeIndex(df_122541['year_doy_hhmm']),inplace=True)
df_122541.drop('year_doy_hhmm',axis=1,inplace=True)

df_122541['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df_122541.index]
df_122541['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df_122541.index]
df_122541['doyfrac'] = df_122541['doy'] + df_122541['fracday']

##
df_122542 = pd.read_csv('data/drifters/122542.y2017',delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime,error_bad_lines=False)

df_122542.set_index(pd.DatetimeIndex(df_122542['year_doy_hhmm']),inplace=True)
df_122542.drop('year_doy_hhmm',axis=1,inplace=True)

df_122542['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df_122542.index]
df_122542['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df_122542.index]
df_122542['doyfrac'] = df_122542['doy'] + df_122542['fracday']

##
df_136868 = pd.read_csv('data/drifters/136868.y2017',delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime,error_bad_lines=False)

df_136868.set_index(pd.DatetimeIndex(df_136868['year_doy_hhmm']),inplace=True)
df_136868.drop('year_doy_hhmm',axis=1,inplace=True)

df_136868['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df_136868.index]
df_136868['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df_136868.index]
df_136868['doyfrac'] = df_136868['doy'] + df_136868['fracday']

##
df_136869 = pd.read_csv('data/drifters/136869.y2017',delimiter='\s+',header=0,
  names=header,index_col=False,
  dtype={'year':str,'doy':str,'hhmm':str,'s1':str,'s2':str,'s3':str,'s4':str,'s5':str,'s6':str,'s7':str,'s8':str},
  parse_dates=[['year','doy','hhmm']],date_parser=argo_to_datetime,error_bad_lines=False)

df_136869.set_index(pd.DatetimeIndex(df_136869['year_doy_hhmm']),inplace=True)
df_136869.drop('year_doy_hhmm',axis=1,inplace=True)

df_136869['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df_136869.index]
df_136869['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df_136869.index]
df_136869['doyfrac'] = df_136869['doy'] + df_136869['fracday']


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
dfgbc['index_name'] = dfgbc.index
dfgbc = dfgbc.round(4)
dfgbc.drop(['REFERENCE_DATE_TIME','FLOAT_SERIAL_NO'], axis=1, inplace=True)
## resample and interpolate
dfgbc = dfgbc.set_index('time (UTC)')
dfgbc_t = dfgbc.resample('12H').mean()
dfgbc_t['TEMP (degree_Celsius)'].replace(np.nan,1000,inplace=True)
dfgbc_t=dfgbc_t.interpolate()
dfgbc_t['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in dfgbc_t.index]
dfgbc_t['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in dfgbc_t.index]
dfgbc_t['doyfrac'] = dfgbc_t['doy'] + dfgbc_t['fracday']

df2 = get_profile(9076,'2016-08-01','2016-12-31')
df2group = df2.groupby('CYCLE_NUMBER')
df2gbc = df2group.mean()
df2gbc['time (UTC)'] = df2group.first()['time (UTC)']
df2gbc['index_name'] = df2gbc.index
df2gbc = df2gbc.round(4)
df2gbc.drop(['REFERENCE_DATE_TIME','FLOAT_SERIAL_NO'], axis=1, inplace=True)
## resample and interpolate
df2gbc = df2gbc.set_index('time (UTC)')
df2gbc_t = df2gbc.resample('12H').mean()
df2gbc_t['TEMP (degree_Celsius)'].replace(np.nan,1000,inplace=True)
df2gbc_t=df2gbc_t.interpolate()
df2gbc_t['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df2gbc_t.index]
df2gbc_t['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df2gbc_t.index]
df2gbc_t['doyfrac'] = df2gbc_t['doy'] + df2gbc_t['fracday']

df3 = get_profile(9085,'2016-08-01','2016-12-31')
df3group = df3.groupby('CYCLE_NUMBER')
df3gbc = df3group.mean()
df3gbc['time (UTC)'] = df3group.first()['time (UTC)']
df3gbc['index_name'] = df3gbc.index
df3gbc = df3gbc.round(4)
df3gbc.drop(['REFERENCE_DATE_TIME','FLOAT_SERIAL_NO'], axis=1, inplace=True)
## resample and interpolate
df3gbc = df3gbc.set_index('time (UTC)')
df3gbc_t = df3gbc.resample('12H').mean()
df3gbc_t['TEMP (degree_Celsius)'].replace(np.nan,1000,inplace=True)
df3gbc_t=df3gbc_t.interpolate()
df3gbc_t['doy'] = [x.to_pydatetime().timetuple().tm_yday for x in df3gbc_t.index]
df3gbc_t['fracday'] = [((x.to_pydatetime().timetuple().tm_hour*60.) + x.to_pydatetime().timetuple().tm_min)/1440. for x in df3gbc_t.index]
df3gbc_t['doyfrac'] = df3gbc_t['doy'] + df3gbc_t['fracday']


# In[189]:


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

tol = .00001



# In[221]:
browser = webdriver.Chrome()

for doymax in range(255,365,1):
    for hourmax in range(0,24,12):
        f = folium.map.FeatureGroup()
        
        dfgbc_p = dfgbc_t[dfgbc_t['doyfrac'] <= (doymax + hourmax/24.0)]

        
        f1 = folium.map.FeatureGroup()
        f1s = folium.map.FeatureGroup()

        if not dfgbc_p.empty:
            lats = dfgbc_p['latitude (degrees_north)'].values
            lngs = dfgbc_p['longitude (degrees_east)'].values
            colors = dfgbc_p['TEMP (degree_Celsius)'].values
            for lat, lng, color in zip(lats, lngs, colors):
                nval = find_nearest(np.array([x[0] for x in thermal]),color_normalize(-2.,7.,color))
                f1.add_child(
                    folium.features.CircleMarker(
                        [lat, lng],
                        radius=1,
                        color=thermal[nval][1],
                    )
                    )
                
            
    
            try:
                lats = dfgbc_p['latitude (degrees_north)'].values[-1]
                lngs = dfgbc_p['longitude (degrees_east)'].values[-1]
            except:
                #seattle
                lats = 47.6
                lons = -122.33
    
            f1s.add_child(
                folium.features.CircleMarker(
                    [lats, lngs],
                    radius=4,
                    color='#41897F'
                    )
                    )
        
        
        # In[218]:
        
        
        f2 = folium.map.FeatureGroup()
        
        df2gbc_p = df2gbc_t[df2gbc_t['doyfrac'] <= (doymax + hourmax/24.0)]

        f2 = folium.map.FeatureGroup()
        f2s = folium.map.FeatureGroup()
        
        if not df2gbc_p.empty:
            lats = df2gbc_p['latitude (degrees_north)'].values
            lngs = df2gbc_p['longitude (degrees_east)'].values
            colors = df2gbc_p['TEMP (degree_Celsius)'].values
            for lat, lng, color in zip(lats, lngs, colors):
                nval = find_nearest(np.array([x[0] for x in thermal]),color_normalize(-2.,7.,color))
                f2.add_child(
                    folium.features.CircleMarker(
                        [lat, lng],
                        radius=1,
                        color=thermal[nval][1],
                    )
                    )
                
    
            try:
                lats = df2gbc_p['latitude (degrees_north)'].values[-1]
                lngs = df2gbc_p['longitude (degrees_east)'].values[-1]
            except:
                #seattle
                lats = 47.6
                lons = -122.33
    
            f2s.add_child(
                folium.features.CircleMarker(
                    [lats, lngs],
                    radius=4,
                    color='#18389A'
                    )
                    )
            
        
        # In[219]:
        
        df3gbc_p = df3gbc_t[df3gbc_t['doyfrac'] <= (doymax + hourmax/24.0)]

        f3 = folium.map.FeatureGroup()
        f3s = folium.map.FeatureGroup()
        
        if not df3gbc_p.empty:
            lats = df3gbc_p['latitude (degrees_north)'].values
            lngs = df3gbc_p['longitude (degrees_east)'].values
            colors = df3gbc_p['TEMP (degree_Celsius)'].values
            for lat, lng, color in zip(lats, lngs, colors):
                nval = find_nearest(np.array([x[0] for x in thermal]),color_normalize(-2.,7.,color))
                f3.add_child(
                    folium.features.CircleMarker(
                        [lat, lng],
                        radius=1,
                        color=thermal[nval][1],
                    )
                    )
                
    
            try:
                lats = df3gbc_p['latitude (degrees_north)'].values[-1]
                lngs = df3gbc_p['longitude (degrees_east)'].values[-1]
            except:
                #seattle
                lats = 47.6
                lons = -122.33
    
            f3s.add_child(
                folium.features.CircleMarker(
                    [lats, lngs],
                    radius=4,
                    color='#ED7F33'
                    )
                    )
        
        ### resample to fixed time grid and fill interpolated temperatures with large value
        
        df_122537_t = df_122537.resample('12H').mean()
        df_122537_t=df_122537_t[df_122537_t.index >= datetime.datetime(2017,9,15)]
        df_122537_t = df_122537_t[df_122537_t['doyfrac'] <= (doymax + hourmax/24.0)]
        df_122537_t=df_122537_t.interpolate()
        
        f1a = folium.map.FeatureGroup()

        if not df_122537_t.empty:
            lats = df_122537_t['lat'].values
            lngs = df_122537_t['lon'].values
            
            for lat, lng in zip(lats, lngs):
                f1a.add_child(
                    folium.features.CircleMarker(
                        [lat, lng],
                        radius=.1,
                        color='#000000',
                    )
                    )        

        df_122542_t = df_122542.resample('12H').mean()
        df_122542_t=df_122542_t[df_122542_t.index >= datetime.datetime(2017,9,15)]
        df_122542_t = df_122542_t[df_122542_t['doyfrac'] <= (doymax + hourmax/24.0)]
        df_122542_t=df_122542_t.interpolate()

        f2a = folium.map.FeatureGroup()

        lats = df_122542_t['lat'].values
        lngs = df_122542_t['lon'].values

        for lat, lng in zip(lats, lngs):
            f2a.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=.1,
                    color='#000000',
                )
                )

        df_122541_t = df_122541.resample('12H').mean()
        df_122541_t=df_122541_t[df_122541_t.index >= datetime.datetime(2017,9,15)]
        df_122541_t = df_122541_t[df_122541_t['doyfrac'] <= (doymax + hourmax/24.0)]
        df_122541_t=df_122541_t.interpolate()

        f3a = folium.map.FeatureGroup()

        lats = df_122541_t['lat'].values
        lngs = df_122541_t['lon'].values

        for lat, lng in zip(lats, lngs):
            f3a.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=.1,
                    color='#000000',
                )
                )

        df_136868_t = df_136868.resample('12H').mean()
        df_136868_t=df_136868_t[df_136868_t.index >= datetime.datetime(2017,9,15)]
        df_136868_t = df_136868_t[df_136868_t['doyfrac'] <= (doymax + hourmax/24.0)]
        df_136868_t = df_136868_t.interpolate()

        f4a = folium.map.FeatureGroup()

        lats = df_136868_t['lat'].values
        lngs = df_136868_t['lon'].values

        for lat, lng in zip(lats, lngs):
            f4a.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=.1,
                    color='#000000',
                )
                )        

        df_136869_t = df_136869.resample('12H').mean()
        df_136869_t=df_136869_t[df_136869_t.index >= datetime.datetime(2017,9,15)]
        df_136869_t = df_136869_t[df_136869_t['doyfrac'] <= (doymax + hourmax/24.0)]
        df_136869_t = df_136869_t.interpolate()

        f5a = folium.map.FeatureGroup()

        lats = df_136869_t['lat'].values
        lngs = df_136869_t['lon'].values

        for lat, lng in zip(lats, lngs):
            f5a.add_child(
                folium.features.CircleMarker(
                    [lat, lng],
                    radius=.1,
                    color='#000000',
                )
                )


        ##
        m = folium.Map(location=[71,-165],
                      tiles='https://api.mapbox.com/styles/v1/sbell/cj48p13bt265k2qvucuielhm7/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1Ijoic2JlbGwiLCJhIjoiY2lqbGlpaHBkMDAyanV5bHhqMTdjYTd5aiJ9.04PwNcY3Piny-YtIg5cIJA',
                      attr='North Star - MapBox',
                      zoom_start=6,
                      png_enabled=True)
        m.add_child(f1)
        m.add_child(f1s)
        m.add_child(f1a)
#        m.add_child(f2)
#        m.add_child(f2s)
        m.add_child(f2a)
#        m.add_child(f3)
#        m.add_child(f3s)
        m.add_child(f3a)
        m.add_child(f4a)
        m.add_child(f5a)
        
        # In[220]:
        
        fn = '{doy}{hour}'.format(doy=doymax,hour=str(hourmax).zfill(2))
        tmpurl='file://{path}/{mapfile}.html'.format(path=os.getcwd(),mapfile=fn)
        
        m.save(fn+'.html')
        browser.get(tmpurl)
        #Give the map tiles some time to load
        #time.sleep(.001)
        browser.save_screenshot('images/'+fn+'.png')
browser.quit()