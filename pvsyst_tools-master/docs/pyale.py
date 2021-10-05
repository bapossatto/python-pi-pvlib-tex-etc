# %load_ext autoreload
%autoreload 2

import os, sys

import pvlib
from pvlib import pvsystem
print('pvlib version: {}'.format(pvlib.__version__))

# import pvsyst module based on ipython running in /docs/
cwd = os.getcwd()
print('current workign directory: {}'.format(cwd))
sys.path.append(os.path.dirname(cwd))  # append to path to be able to import module
sys.path.append(os.path.dirname(os.path.dirname(cwd))) # append to path to be able to import module

import pvsyst
print('pvsyst module path: {}'.format(pvsyst.__file__))

%matplotlib inline
import matplotlib.pyplot as plt
plt.figure(figsize=(18,18))

import numpy as np

# set PAN file path
import logging
logger = logging.getLogger('pysyst')
logger.setLevel(10)  # 5 for Verbose 10 for Debug

pan_dir = r'data'  # directory of PAN files}
pan = os.path.join(pan_dir,'TSM_430DEG17MC_20_II_.PAN')  # example PAN file

# parse .PAN file into dict 
module_parameters = pvsyst.pan_to_module_param(pan)  # return two dicts

print(module_parameters)

module_parameters["IAM"]

# example single diode model using calcparams_pvsyst
#return IV curve plot
def iplot_iv_vs_irradiances(module_parameters, irradiances = range(0,1300,200), Tcell = 25):
    #IV curve compute paramaters
    Gs = irradiances
    IV = [None]*len(Gs)

    for idx, g in enumerate(Gs):
        IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_pvsyst(effective_irradiance = g, temp_cell = Tcell,
                                                         alpha_sc = module_parameters['alpha_sc'],
                                                         gamma_ref = module_parameters['gamma_ref'],
                                                         mu_gamma = module_parameters['mu_gamma'],
                                                         I_L_ref = module_parameters['I_L_ref'],
                                                         I_o_ref = module_parameters['I_o_ref'],
                                                         R_sh_ref = module_parameters['R_sh_ref'],
                                                         R_sh_0 = module_parameters['R_sh_0'],
                                                         R_s = module_parameters['R_s'],
                                                         cells_in_series = module_parameters['cells_in_series'])
        
        IV[idx] = pvsystem.singlediode(IL, I0, Rs, Rsh, nNsVth, ivcurve_pnts=50)

    # Print IV Curves     
    plt.figure(figsize=(16, 10))
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (A)')
    plt.title('{} IV curves @ {} DegC'.format(module_parameters['module_name'], Tcell))

    labels = []
    for idx, v in enumerate(IV):
        plt.plot(v['v'],v['i'])
        labels.append('{} W.m2'.format(Gs[idx]))
    # Customize the major grid
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
    # Customize the minor grid
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')

    plt.legend(labels, ncol=1, loc='upper right', 
               bbox_to_anchor=[1, 1], 
               columnspacing=2.0, labelspacing=0.25,
               handletextpad=0.0, handlelength=2,
               fancybox=False, shadow=False)

    plt.show()
    
    
iplot_iv_vs_irradiances(module_parameters)

#return plotly object of gamma optimisatino mu_gamma
def iplot_gamma_coef(module_parameters):

    #Display mu_Pmax optimizatino
    temperatures = range(-10,60,5)

    g = 1000
    #IV curve compute paramaters

    IV = [None]*len(temperatures)
    for idx, t in enumerate(temperatures):
        IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_pvsyst(effective_irradiance = g, temp_cell = temperatures[idx],
                                                         alpha_sc = module_parameters['alpha_sc'],
                                                         gamma_ref = module_parameters['gamma_ref'],
                                                         mu_gamma = module_parameters['mu_gamma'],
                                                         I_L_ref = module_parameters['I_L_ref'],
                                                         I_o_ref = module_parameters['I_o_ref'],
                                                         R_sh_ref = module_parameters['R_sh_ref'],
                                                         R_sh_0 = module_parameters['R_sh_0'],
                                                         R_s = module_parameters['R_s'],
                                                         cells_in_series = module_parameters['cells_in_series'])

        IV[idx] = pvsystem.singlediode(IL, I0, Rs, Rsh, nNsVth, ivcurve_pnts=50)
        print('Temp:{} C IL:{:0.3f} I0:{} Rs:{:0.3f} Rsh:{:0.3f} nNsVth:{:0.3f}'.format(t,IL,I0,Rs,Rsh,nNsVth))
        print('    {:4.0f}W/m2 | Voc:{:5.2f}V | Isc:{:5.2f}A | Pmp:{:5.2f}W | Vmp:{:5.2f}V | Imp:{:5.2f}A'.format(g,
                                                                                   IV[idx]['v_oc'],
                                                                                   IV[idx]['i_sc'],
                                                                                   IV[idx]['p_mp'],
                                                                                   IV[idx]['v_mp'],
                                                                                   IV[idx]['i_mp']))

    #print pf percent Pmp / Temp    
    
    x = [None]*len(temperatures)
    y = [None]*len(temperatures) #for slingle diode model values
    y1 = [None]*len(temperatures) #for reference value

    for idx, v in enumerate(IV):
        # print the name of the regiment
        x[idx] = temperatures[idx]
        y[idx] = v['p_mp']
        y1[idx] = module_parameters['Pmpp'] * (1+(module_parameters['mPmpp']/100)*(temperatures[idx] - 25))

    plt.figure(figsize=(16, 8))
    plt.xlabel('Temperature')
    plt.ylabel('Power')
    plt.title('{} muPmp @ {} W/m2'.format(module_parameters['module_name'],g))

    labels = []
    plt.plot(x,y)
    labels.append('muPmax')
    plt.plot(x,y1)
    labels.append('muPmaxRef') 
    # Customize the major grid
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
    # Customize the minor grid
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')

    plt.legend(labels, ncol=1, loc='upper right', 
               bbox_to_anchor=[1, 1], 
               columnspacing=2.0, labelspacing=0.25,
               handletextpad=0.0, handlelength=2,
               fancybox=False, shadow=False)

    plt.show()


    #Print ERROR % of Pmp / Rmp Expected
    x = [None]*len(temperatures)
    y = [None]*len(temperatures) #for slingle diode model values
    y1 = [None]*len(temperatures) #for reference value

    for idx, v in enumerate(IV):
        # print the name of the regiment
        x[idx] = temperatures[idx]
        actual = v['p_mp']
        reference = module_parameters['Pmpp'] * (1+((module_parameters['mPmpp']/100)*(temperatures[idx] - 25)))
        y[idx] = ((actual - reference)/reference)*100


    plt.figure(figsize=(16, 8))
    plt.xlabel('Temperature')
    plt.ylabel('Pmp Error in %')
    plt.title('{} muPmp @ {} W/m2'.format(module_parameters['module_name'],g))

    labels = []
    plt.plot(x,y)
    labels.append('muPmax Error %')

    # Customize the major grid
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
    # Customize the minor grid
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')

    plt.legend(labels, ncol=1, loc='upper right', 
               bbox_to_anchor=[1, 1], 
               columnspacing=2.0, labelspacing=0.25,
               handletextpad=0.0, handlelength=2,
               fancybox=False, shadow=False)

    plt.show()
    
iplot_gamma_coef(module_parameters)

# IAM profile
from scipy.interpolate import interp1d

x = module_parameters['IAM'][0]
y = module_parameters['IAM'][1]

plt.figure(figsize=(16, 8))
plt.xlabel('Angle')
plt.ylabel('Eff %')
plt.title('{} IAM Profile'.format(module_parameters['module_name']))

plt.plot(x,y,'o')

# Customize the major grid
plt.grid(which='major', linestyle='-', linewidth='0.5', color='grey')

xcs = np.linspace(x.min(), x.max(), num=90, endpoint=True)

cs = interp1d(x, y, kind='cubic')
plt.plot(xcs,cs(xcs))

plt.show()
