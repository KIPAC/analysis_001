"""Test utility for Likelihood fitting"""

import os

import numpy as np

import healpy as hp

from scipy.optimize import minimize

import emcee

from KIPAC.nuXgal import Defaults

from KIPAC.nuXgal.EventGenerator import EventGenerator

from KIPAC.nuXgal.Analyze import Analyze

from KIPAC.nuXgal.Likelihood import Likelihood

from KIPAC.nuXgal.file_utils import read_maps_from_fits, write_maps_to_fits

from KIPAC.nuXgal.hp_utils import vector_apply_mask

from KIPAC.nuXgal.plot_utils import FigureDict

from Utils import MAKE_TEST_PLOTS


testfigpath = os.path.join(Defaults.NUXGAL_PLOT_DIR, 'test')
N_yr = 3

llh = Likelihood(N_yr=N_yr)#, computeATM=True, computeASTRO =True, N_re=10)





def showDataModel(datamap, energyBin):
    datamap = vector_apply_mask(datamap, Defaults.mask_muon, copy=False)
    w_data = llh.cf.crossCorrelationFromCountsmap(datamap)

    if MAKE_TEST_PLOTS:
        figs = FigureDict()
        o_dict = figs.setup_figure('test_w_CL', xlabel='$l$', ylabel='$C_l$', figsize=(8, 6))
        fig = o_dict['fig']
        axes = o_dict['axes']
        axes.set_ylim(-3e-4, 3e-4)
        axes.set_xlim(0, 400)

        axes.plot(llh.cf.l, llh.cf.cl_galaxy * 0.6 ** 0.5, 'r')
        axes.errorbar(llh.cf.l_cl,  w_data[energyBin], yerr=llh.w_atm_std[0] * (llh.Ncount_atm[0] / np.sum(datamap[energyBin]))**0.5, markersize=4, color='grey', fmt='s', capthick=2)

        figs.save_all(testfigpath, 'pdf')




def plotLnL(w_data, Ncount, lmin, energyBin):
    figs = FigureDict()
    o_dict = figs.setup_figure('test__lnL', xlabel='$l$', ylabel='$C_l$', figsize=(8, 6))
    fig = o_dict['fig']
    axes = o_dict['axes']
    ftest = np.linspace(0, 1, 50)
    lnL_f = []
    for _f in ftest:
        lnL_f.append(llh.lnL([_f], w_data, Ncount, lmin, energyBin, energyBin+1))
    axes.plot(ftest, lnL_f)
    figs.save_all(testfigpath, 'pdf')


def test_STDdependence(energyBin, energyBin2):
    figs = FigureDict()
    o_dict = figs.setup_figure('compare_std', xlabel='$l$', ylabel='$C_l$', figsize=(8, 6))
    fig = o_dict['fig']
    axes = o_dict['axes']
    axes.set_yscale('log')
    axes.set_ylim(1e-6, 1e-2)

    axes.plot(llh.cf.l_cl, llh.w_astro_std[energyBin], label='actual')
    axes.plot(llh.cf.l_cl, llh.w_atm_std[energyBin2] * (llh.Ncount_atm[energyBin2] / llh.Ncount_astro[energyBin])**0.5, label='est')
    #print (llh.Ncount_astro)

    #axes.plot(llh.cf.l_cl, llh.w_atm_std[energyBin], label='atm')
    #axes.plot(llh.cf.l_cl, llh.w_atm_std[energyBin2] * (llh.Ncount_atm[energyBin2] / llh.Ncount_atm[energyBin])**0.5, label='atm2')


    fig.legend()
    figs.save_all(testfigpath, 'pdf')


def getEbinmax():
    Ebinmax = 3
    N_nonzero = 1
    while (N_nonzero > 0) & (Ebinmax < Defaults.NEbin - 1) :
        Ebinmax += 1
        N_nonzero = len(np.where(llh.w_astro_std_square[Ebinmax] > 0)[0])

    print (Ebinmax, N_nonzero)
    return Ebinmax

def TS_test_Gal(N_re = 200, lmin = 20):
    TS_array = np.zeros(N_re)
    for i in range(N_re):
        if i % 10 == 0:
            print (i)
        datamap = generateData(1.0, 0.6, N_yr, fromGalaxy=True, seed=103 + i * 7)
        datamap = vector_apply_mask(datamap, Defaults.mask_muon, copy=False)
        w_data = llh.cf.crossCorrelationFromCountsmap(datamap)
        Ncount = np.sum(datamap, axis=1)
        Ebinmax = np.min([np.where(Ncount != 0)[0][-1]+1, 5])
        TS_array[i] = (llh.minimize__lnL(w_data, Ncount, lmin, 0, Ebinmax))[-1]

    print (TS_array)
    np.savetxt(os.path.join(Defaults.NUXGAL_SYNTHETICDATA_DIR,'TS_Gal.txt'), TS_array)

def TS_test_atm(N_re = 200, lmin = 20):
    TS_array = np.zeros(N_re)
    for i in range(N_re):
        if i % 10 == 0:
            print (i)
        datamap = generateData(0.0, 0.6, N_yr, fromGalaxy=False, seed=109 + i * 7)
        datamap = vector_apply_mask(datamap, Defaults.mask_muon, copy=False)
        w_data = llh.cf.crossCorrelationFromCountsmap(datamap)
        Ncount = np.sum(datamap, axis=1)
        Ebinmax = np.min([np.where(Ncount != 0)[0][-1]+1, 5])
        TS_array[i] = (llh.minimize__lnL(w_data, Ncount, lmin, 0, Ebinmax))[-1]

    print (TS_array)
    np.savetxt(os.path.join(Defaults.NUXGAL_SYNTHETICDATA_DIR,'TS_atm.txt'), TS_array)

def TS_test_nonGal(N_re = 200, lmin = 20):
    TS_array = np.zeros(N_re)
    for i in range(N_re):
        if i % 10 == 0:
            print (i)
        datamap = generateData(1.0, 0.6, N_yr, fromGalaxy=False, seed=103 + i * 7)
        datamap = vector_apply_mask(datamap, Defaults.mask_muon, copy=False)
        w_data = llh.cf.crossCorrelationFromCountsmap(datamap)
        Ncount = np.sum(datamap, axis=1)
        Ebinmax = np.min([np.where(Ncount != 0)[0][-1]+1, 5])
        TS_array[i] = (llh.minimize__lnL(w_data, Ncount, lmin, 0, Ebinmax))[-1]

    print (TS_array)
    np.savetxt(os.path.join(Defaults.NUXGAL_SYNTHETICDATA_DIR,'TS_nonGal.txt'), TS_array)


def test_TS_distribution(readfile = True):
    if not readfile:
        TS_test_atm()
        TS_test_nonGal()
        TS_test_Gal()

    TS_atm = np.loadtxt(os.path.join(Defaults.NUXGAL_SYNTHETICDATA_DIR,'TS_atm.txt'))
    TS_nonGal = np.loadtxt(os.path.join(Defaults.NUXGAL_SYNTHETICDATA_DIR,'TS_nonGal.txt'))
    TS_Gal = np.loadtxt(os.path.join(Defaults.NUXGAL_SYNTHETICDATA_DIR,'TS_Gal.txt'))

    TS_bins = np.linspace(0, 100, 101)
    TS_bins_c = (TS_bins[0:-1] + TS_bins[1:]) / 2.
    p_atm, _ = np.histogram(TS_atm, TS_bins, density=True)
    p_nonGal, _ = np.histogram(TS_nonGal, TS_bins, density=True)
    p_Gal, _ = np.histogram(TS_Gal, TS_bins, density=True)


    figs = FigureDict()
    o_dict = figs.setup_figure('TS_distribution', xlabel='TS', ylabel='cumulative probability', figsize=(8, 6))
    fig = o_dict['fig']
    axes = o_dict['axes']
    axes.set_xlim(-5, 40)

    axes.plot(TS_bins_c, 1 - np.cumsum(p_atm), lw=2, label='atm')
    axes.plot(TS_bins_c, 1 - np.cumsum(p_nonGal), lw=2, label='nonGal')
    axes.plot(TS_bins_c, np.cumsum(p_Gal), lw=3, label='Gal')

    fig.legend()
    figs.save_all(testfigpath, 'pdf')




def testMCMC():
    datamap = llh.eg.computeSyntheticData(N_yr, fromGalaxy=False)
    datamap = vector_apply_mask(datamap, Defaults.mask_muon, copy=False)
    w_data = llh.cf.crossCorrelationFromCountsmap(datamap)
    Ncount = np.sum(datamap, axis=1)
    Ebinmax = np.min([np.where(Ncount != 0)[0][-1]+1, 5])
    print (Ncount)
    print ((llh.minimize__lnL(w_data, Ncount, lmin=20, Ebinmin=0, Ebinmax=Ebinmax))[-1])

    llh.runMCMC(w_data, Ncount, lmin=20, Ebinmin=0, Ebinmax=Ebinmax, Nwalker=640, Nstep=500)

    ndim = Ebinmax
    labels = []
    truths = []
    for i in range(ndim):
        labels.append('f' + str(i))
        truths.append(1)
    llh.plotMCMCchain(ndim, labels, truths)



if __name__ == '__main__':


    #test_STDdependence(2, 0)
    testMCMC()

    #lmin = 20
    #energyBin = 3
    #showDataModel(datamap, energyBin)
    #plotLnL(w_data, Ncount, lmin, energyBin)
