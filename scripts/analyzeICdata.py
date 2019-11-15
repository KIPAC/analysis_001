import numpy as np
import healpy as hp
import matplotlib.pyplot as plt


NSIDE = 128
filedirectory = '../'

# counts map in selected energy bins
map_logE_edge = np.linspace(2, 9, 8)
map_logE_center = (map_logE_edge[0:-1] + map_logE_edge[1:]) / 2.


# -------------- counts map --------------

AtmBG_file = np.loadtxt(filedirectory+'data/3year-data-release/IC86-2012-events.txt')


# countsmap has the shape (number of energy bins, healpy map size)
countsmap = np.zeros((len(map_logE_center), hp.pixelfunc.nside2npix(NSIDE)))

# get energy index of events
_index_map_logE = np.searchsorted(map_logE_edge, AtmBG_file[:, 1]) - 1
_index_map_logE[_index_map_logE == -1] = 0 # group logE < 2 events to bin 0

# convert event directions to pixel numbers
# pi - zenith_south_pole = zenith_regular
# assign random azimuthal angles
randomphi = np.random.random_sample(len(AtmBG_file)) * 2 * np.pi
_index_map_pixel = hp.pixelfunc.ang2pix(NSIDE, (180. - AtmBG_file[:,6]) * np.pi / 180., randomphi)

# put events into healpy maps
for i, e in enumerate(AtmBG_file):
    countsmap[_index_map_logE[i]][_index_map_pixel[i]] += 1
    
for i in np.arange(len(map_logE_center)):
    hp.fitsfunc.write_map(filedirectory + 'syntheticData/counts_atm' + str(i)+'.fits', countsmap[i])

    
for i in np.arange(len(map_logE_center)):
    fig = plt.figure(figsize=(8,6))
    a = hp.fitsfunc.read_map(filedirectory+'syntheticData/counts_atm' + str(i)+'.fits')
    hp.mollview(a)
    plt.savefig(filedirectory + 'syntheticData/counts_atm' + str(i) + '.pdf')





 
# -------------- exposure map --------------
Aeff_file = np.loadtxt(filedirectory + 'data/3year-data-release/IC86-2012-TabulatedAeff.txt')

# compute exposure map at the center of an energy bin
exposuremap = np.zeros((len(map_logE_center), hp.pixelfunc.nside2npix(NSIDE)))

# effective area, 200 in cos zenith, 70 in E
Aeff_table = Aeff_file[:,4] # np.reshape(Aeff_file[:,4], (70, 200))
Emin = np.reshape(Aeff_file[:,0], (70, 200))[:,0]
Emax = np.reshape(Aeff_file[:,1], (70, 200))[:,0]
cosZenith_min = np.reshape(Aeff_file[:,2], (70, 200))[0]
cosZenith_max = np.reshape(Aeff_file[:,3], (70, 200))[0]

exposuremap_theta, exposuremap_phi = hp.pixelfunc.pix2ang(NSIDE, np.arange(hp.pixelfunc.nside2npix(NSIDE)))
exposuremap_costheta = np.cos(np.pi - exposuremap_theta) # converting to South pole view
index_coszenith = np.searchsorted(cosZenith_min, exposuremap_costheta) - 1
index_E = np.searchsorted(np.log10(Emin), map_logE_center) - 1

 

for i in np.arange(len(map_logE_center)):
    exposuremap[i] = Aeff_table[index_E[i] * 200 + index_coszenith]
    hp.fitsfunc.write_map(filedirectory + 'syntheticData/Aeff' + str(i)+'.fits', exposuremap[i])


for i in np.arange(len(map_logE_center)):
    fig = plt.figure(figsize=(8,6))
    a = hp.fitsfunc.read_map(filedirectory + 'syntheticData/Aeff' + str(i)+'.fits')
    hp.mollview(a)
    plt.savefig(filedirectory + 'syntheticData/Aeff' + str(i) + '.pdf')




# -------------- coszenith distribution --------------
Nzenith_bin = 60
N_coszenith = np.zeros((len(map_logE_center), Nzenith_bin))



for file in [filedirectory+'data/3year-data-release/IC86-2012-events.txt', filedirectory+'data/3year-data-release/IC86-2011-events.txt', filedirectory+'data/3year-data-release/IC79-2010-events.txt']:
    AtmBG_file = np.loadtxt(file)
    _index_map_logE = np.searchsorted(map_logE_edge, AtmBG_file[:, 1]) - 1
    _index_map_logE[_index_map_logE == -1] = 0 # group logE < 2 events to bin 0
    
    for i in np.arange(len(map_logE_center)):
        N_coszenith_i, cosZenithBinEdges = np.histogram(np.cos(np.pi - AtmBG_file[:,6][_index_map_logE == i] * np.pi / 180.), Nzenith_bin, (-1, 1))
        N_coszenith[i] += N_coszenith_i


fig = plt.figure(figsize=(8,6))
for i in np.arange(len(map_logE_center)):
    plt.plot((cosZenithBinEdges[0:-1] + cosZenithBinEdges[1:])/2., N_coszenith[i], lw=2, label=str(i))
    np.savetxt(filedirectory + 'syntheticData/N_coszenith'+str(i)+'.txt', np.column_stack(((cosZenithBinEdges[0:-1] + cosZenithBinEdges[1:])/2., N_coszenith[i])))
plt.xlabel(r'$\cos\,\theta$')
plt.ylabel('Number of counts in 2010-2012 data')
plt.legend()
plt.savefig(filedirectory + 'syntheticData/N_coszenith.pdf')


# average count number per energy bin in IC86 one year data
eventnumber_Ebin = np.zeros(len(map_logE_center))
eventnumber_Ebin2 = np.zeros(len(map_logE_center))

 
for file in [filedirectory+'data/3year-data-release/IC86-2012-events.txt', filedirectory+'data/3year-data-release/IC86-2011-events.txt']:
    AtmBG_file = np.loadtxt(file)
    eventnumber_Ebin += np.histogram(AtmBG_file[:,1], map_logE_edge)[0]
    _index_map_logE = np.searchsorted(map_logE_edge, AtmBG_file[:, 1]) - 1
    #_index_map_logE[_index_map_logE == -1] = 0 # group logE < 2 events to bin 0
    eventnumber_Ebin2 += np.histogram(_index_map_logE, range(len(map_logE_edge)))[0]

  
#print eventnumber_Ebin
#print eventnumber_Ebin2
np.savetxt(filedirectory + 'syntheticData/eventNumber_Ebin_perIC86year.txt', eventnumber_Ebin / 2.)
#print np.sum(eventnumber_Ebin),   np.sum(eventnumber_Ebin2)
 

# ------------- check counts rate -----------
bgmap = np.zeros((len(map_logE_center), hp.pixelfunc.nside2npix(NSIDE)))
for i in np.arange(len(map_logE_center)):
     bgmap[i] = hp.fitsfunc.read_map('../syntheticData/counts_atm' + str(i)+'.fits', verbose=False)

# check rate per cos zenith bin
coszenith_bin = np.linspace(-1, 1, 20)
coszenith_bin_IC = np.cos(np.pi - np.arccos(coszenith_bin))
countsRate = np.zeros(len(coszenith_bin))
for i in range(len(coszenith_bin)-1):
    index_coszenith = np.where((np.cos(exposuremap_theta) < coszenith_bin[i+1]) & (np.cos(exposuremap_theta) > coszenith_bin[i]))
    for iE in range(len(map_logE_center)):
        countsRate[i] += np.sum(bgmap[iE][index_coszenith]) / (333 * 24 * 3600.)
    

fig = plt.figure(figsize=(8,6))
font = {  'family': 'Arial',  'weight' : 'normal',  'size'   : 20}
legendfont = {'fontsize' : 18, 'frameon' : False}

plt.rc('font', **font)
plt.rc('legend', **legendfont)
plt.plot(coszenith_bin_IC, countsRate, lw=2)
plt.yscale('log')
plt.ylim(1e-8, 1e-2)
plt.savefig(filedirectory + 'plots/countsRate.pdf')


