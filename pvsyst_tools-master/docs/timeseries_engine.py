# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 09:22:37 2021

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
from datetime import datetime

# carregar TMY 
datapath = os.path.join(cwd, 'data', 'teste.csv') # path para arquivo

# Ler tmy
tmy_data, meta = pvlib.iotools.read_tmy3(datapath)
plt.figure(figsize=(16, 10))
plt.ylabel('GHI Irradiance (W/m**2)')

# criar objeto pvlib Location baseado nos metadados do arquivo TMY! Alterar!
loc = pvlib.location.Location.from_tmy(meta)
#print(loc)
loc.latitude=-5.2
loc.longitude=-37.9
loc.tz=-3
plt.plot(tmy_data['GHI'])
plt.show()
solpos = solarposition.get_solarposition(tmy_data.index, loc.latitude, loc.longitude)

backtracking_angles = tracking.singleaxis(
    apparent_zenith=solpos['apparent_zenith'],
    apparent_azimuth=solpos['azimuth'],
    axis_tilt=0,
    axis_azimuth=180,
    max_angle=90,
    backtrack=True,
    gcr=0.33)

backtracking_position = backtracking_angles['tracker_theta'].fillna(0)

def pvfactor_build_report(pvarray):
        return {
                'total_inc_back': pvarray.ts_pvrows[1].back.get_param_weighted('qinc').tolist(),
                'total_inc_front': pvarray.ts_pvrows[1].front.get_param_weighted('qinc').tolist()
                 }

pvarray_parameters = {
                                          'n_pvrows': 10,
                                            'index_observed_pvrow': 4,
                                            'axis_azimuth': 0,
                                            'pvrow_height': 2.35,
                                            'pvrow_width': 4.6,
                                            'gcr': 0.3,
                                            'rho_front_pvrow': 0.01,
                                            'rho_back_pvrow': 0.03,
                                            'horizon_band_angle': 15
                                            }

pvfactor = run_timeseries_engine(pvfactor_build_report,
                                                            pvarray_parameters, # ok?
                                                              tmy_data.index, #ok?
                                                              dni=tmy_data['DNI'], # ok?
                                                              dhi=tmy_data['DHI'], # ok?
                                                              solar_zenith=solpos['apparent_zenith'], # ok?
                                                              solar_azimuth=solpos['azimuth'], # ok?
                                                              surface_tilt=backtracking_angles['surface_tilt'] , # ok?
                                                              surface_azimuth=backtracking_angles['surface_azimuth'], # ok?
                                                              albedo=0.153                                                     # you can change the number
                                                              )

print(pvfactor)

back_irrad=pd.DataFrame(pvfactor['total_inc_back'],columns=['total_inc_back'])
front_irrad=pd.DataFrame(pvfactor['total_inc_front'],columns=['total_inc_front'])
total_irrad=front_irrad.join(back_irrad)
total_irrad['bifaciality_factor']=total_irrad['total_inc_back']/total_irrad['total_inc_front']

pvfactor=pd.DataFrame(pvfactor, tmy_data.index)

dni_extra = pd.Series(pvlib.irradiance.get_extra_radiation(tmy_data.index),
                      index=tmy_data.index)

airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])

poa_sky_diffuse = pvlib.irradiance.perez(surface_tilt=backtracking_angles['surface_tilt'], 
                                        surface_azimuth=backtracking_angles['surface_azimuth'],
                                        dhi=tmy_data['DHI'], 
                                        dni=tmy_data['DNI'], 
                                        dni_extra=dni_extra,
                                        solar_zenith=solpos['apparent_zenith'], 
                                        solar_azimuth=solpos['azimuth'],
                                        airmass=airmass)

poa_ground_diffuse = pvlib.irradiance.get_ground_diffuse(backtracking_angles['surface_tilt'], tmy_data['GHI'], albedo=0.153)

aoi = pvlib.irradiance.aoi(backtracking_angles['surface_tilt'], backtracking_angles['surface_azimuth'], solpos['apparent_zenith'], solpos['azimuth'])
poa_irrad = pvlib.irradiance.poa_components(aoi, tmy_data['DNI'], poa_sky_diffuse, poa_ground_diffuse)

iam = pvlib.pvsystem.ashraeiam(aoi, b=0.05) # pvlib.pvsystem.PVSystem.get_iam(aoi, iam_model='physical') #  # TODO work on applying ['IAM'] paramter 

poa_irrad['effective'] = (poa_irrad['poa_direct']*iam) + poa_irrad['poa_diffuse']

iam_loss  = (poa_irrad['effective'].sum()/(poa_irrad['poa_global'].sum()))-1
print('iam loss {} %'.format(iam_loss*100))

yearly_poa = poa_irrad['poa_global'].sum() / 1000.0  # kWh
yearly_ghi = tmy_data['GHI'].sum() / 1000.0  # kWh
monthly = poa_irrad['poa_global'].resample('M').sum() / 1000.0
print('annual ghi = {} kWh/m2/yr'.format(yearly_ghi))
print('annual poa = {} kWh/m2/yr'.format(yearly_poa))
print('transposition gain = {} %'.format(((yearly_poa/yearly_ghi)-1)*100))

plt.figure(figsize=(16, 10))
plt.ylabel('Irradiance (W/m**2)')
plt.title('POA Irradiance')
plt.plot(poa_irrad[['effective','poa_diffuse']])
plt.show()

# calculate cell temperaure
pvtemps = pvlib.pvsystem.pvsyst_celltemp(poa_irrad['poa_global'], tmy_data['DryBulb'])

plt.figure(figsize=(16, 10))
plt.ylabel('Temperature (C)')
plt.plot(pvtemps)
plt.plot(tmy_data['DryBulb'])
plt.show()

# Definir caminho para diretório contendo arquivo .PAN
pan_dir = r'data'  # diretório do .PAN
pan = os.path.join(pan_dir,'TSM_430DEG17MC_20_II_.PAN')  # arquivo .PAN
# ler .PAN 
module_parameters = pvsyst.pan_to_module_param(pan)

print(module_parameters)

# calcular potência DC do módulo
IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_pvsyst(effective_irradiance = poa_irrad['poa_global'], temp_cell = pvtemps,
                                                         alpha_sc = module_parameters['alpha_sc'],
                                                         gamma_ref = module_parameters['gamma_ref'],
                                                         mu_gamma = module_parameters['mu_gamma'],
                                                         I_L_ref = module_parameters['I_L_ref'],
                                                         I_o_ref = module_parameters['I_o_ref'],
                                                         R_sh_ref = module_parameters['R_sh_ref'],
                                                         R_sh_0 = module_parameters['R_sh_0'],
                                                         R_s = module_parameters['R_s'],
                                                         cells_in_series = module_parameters['cells_in_series'])
        
dc = pvlib.pvsystem.singlediode(IL, I0, Rs, Rsh, nNsVth)

plt.figure(figsize=(16, 10))
plt.plot(dc.p_mp)
plt.show()

plt.figure(figsize=(16, 10))
plt.plot(dc['19000610':'19000618'])
plt.show()

yearly_dc = dc.p_mp.sum() / 1000.0  # kWh - soma anual

print('annual dc = {} kWh/yr'.format(yearly_dc))
print('dc annual yield = {} kWh/kWp/yr'.format(yearly_dc/(module_parameters['Pmpp']/1000)))
