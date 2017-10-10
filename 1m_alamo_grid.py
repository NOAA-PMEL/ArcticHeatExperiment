#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 10:37:40 2017

@author: bell
"""

import pandas as pd
import numpy as np

data = pd.read_csv('/Volumes/WDC_internal/Users/bell/in_and_outbox/2017/wood/2016_ArcticHeat/AlamoFloat_9085_all.csv',delimiter='\t')

dcn = data.groupby('CycleNumber')
for i in range(0,253,1):
    try:
        print dcn.get_group(i).groupby(pd.cut(dcn.get_group(i)["Pressure"], np.arange(0, 100, 1))).mean().T.to_csv()
    except KeyError:
        continue