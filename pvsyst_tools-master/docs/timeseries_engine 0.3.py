# -*- coding: utf-8 -*-
"""
@author: BAP
"""

import os, sys
import inspect
import numpy as np
import pandas as pd
from pandas import DataFrame
#%matplotlib inline 
import matplotlib.pyplot as plt
import matplotlib as mpl

# importação do pvsyst-tools (leitura automática dos arquivos .PAN)
cwd = os.getcwd()
print('current workign directory: {}'.format(cwd))
sys.path.append(os.path.dirname(cwd))  # append to path to be able to import module
import pvsyst
print('pvsyst module path: {}'.format(pvsyst.__file__))

# importação do pvlib
import pvlib
from pvlib.bifacial import pvfactors_timeseries
from pvlib import solarposition, tracking
from pvfactors.run import run_timeseries_engine
from pvfactors.engine import PVEngine
from pvfactors.geometry import OrderedPVArray
from datetime import datetime

# carregar TMY 
datapath = os.path.join(cwd, 'data', 'teste.csv') # path para arquivo

# Ler tmy
tmy_data, meta = pvlib.iotools.read_tmy3(datapath)
plt.figure(figsize=(16, 10))
plt.ylabel('GHI Irradiance (W/m**2)')

