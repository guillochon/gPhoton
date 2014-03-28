# This file defines common queries that are passed to the GALEX photon database at MAST.
from MCUtils import manage_requests

# Defines the basic path information to the database.
# If the database ever "moves" or if someone builds a mirror, you should
#  be able to just change this string and everything else will still work.
baseURL = 'http://masttest.stsci.edu/portal/Mashup/MashupQuery.asmx/GalexPhotonListQueryTest?query='
# Or a sometimes used dev server.
#baseURL = 'http://mastdev.stsci.edu/portal/Mashup/MashupQuery.asmx/GalexPhotonListQuery?query='

# Defines the standard return format and timeout
formatURL = '&format=json&timeout={}'

def getValue(query,verbose=0):
	if verbose>2:
		print query
	try:
		out = float(manage_requests(query).json()['Tables'][0]['Rows'][0][0])
	except:
		print 'CONNECTION TIMEOUT'
	return out

def getArray(query,verbose=0): 
	if verbose>2:
		print query
	try:
		out = manage_requests(query).json()['Tables'][0]['Rows']
	except:
		print 'CONNECTION TIMEOUT'
	return out

def mcat_sources(band,ra0,dec0,radius,maglimit=20):
	# 1=nuv, 2=fuv, 3=both
	bandflag = 1 if band=='NUV' else 2
	# fgetnearbyobjeq takes radius in arcminutes
	# add a buffer to the radius to catch stars just outside
	return str(baseURL)+'select ra, dec, nuv_mag, fuv_mag, fov_radius, nuv_skybg, fuv_skybg, nuv_fwhm_world, fuv_fwhm_world from Gr6plus7.Dbo.photoobjall as p inner join Gr6plus7.Dbo.photoextract as pe on p.photoextractid=pe.photoextractid inner join gr6plus7.dbo.fgetnearbyobjeq('+str(ra0)+', '+str(dec0)+', '+str(radius*60.+0.02*60.)+') as nb on p.objid=nb.objid and (band=3 or band='+str(bandflag)+') and '+str(band)+'_mag<'+str(maglimit)+str(formatURL)

def exposure_ranges(band,ra0,dec0,t0=1,t1=10000000000000,tscale=1000.,detsize=1.25):
	return str(baseURL)+'SELECT DISTINCT a.time FROM aspect AS a INNER JOIN fGetNearbyAspectNTimeEq('+str(ra0)+','+str(dec0)+',(('+str(detsize)+'/2.0)*60.0),'+str(long(t0*tscale))+','+str(long(t1*tscale))+') AS nb ON a.htmID=nb.htmID AND a.eclipse IN (SELECT eclipse FROM PLCoverageV) WHERE time BETWEEN '+str(long(t0*tscale))+' AND '+str(long(t1*tscale))+' AND flag%2=0 ORDER by time'+str(formatURL)

# Find time ranges for which data exists at a position
def exposure_range(band,ra0,dec0,t0=1,t1=10000000000000):
	return str(baseURL)+'select startTimeRange, endTimeRange from fGetTimeRanges('+str(int(t0))+','+str(int(t1))+','+repr(ra0)+','+repr(dec0)+') where band=\''+str(band)+'\''+str(formatURL)

# Perform a sum over an aperture for a position, time, and radius
def aperture(band,ra0,dec0,t0,t1,radius,tscale=1000.):
	return str(baseURL)+'Select  sum(photonCount) from dbo.fGetNearbyObjEqCount'+str(band)+'('+repr(ra0)+','+repr(dec0)+','+str(radius)+','+str(long(t0*tscale))+','+str(long(t1*tscale))+',0)'+str(formatURL)

# Returns global counts for non-null data
def deadtime1(band,t0,t1,tscale=1000.):
	return str(baseURL)+'select count(*) from '+str(band)+'PhotonsV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+str(formatURL)

# Returns global counts for null data
def deadtime2(band,t0,t1,tscale=1000.):
	return str(baseURL)+'select count(*) from '+str(band)+'PhotonsNULLV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+str(formatURL)

# Returns the empirically determined deadtime correction
def deadtime(band,t0,t1,tscale=1000.):
	return str(baseURL)+'select sum(dt) * 0.0000057142857142857145 / ('+repr(t1)+'-'+repr(t0)+') from(select count(*) as dt from '+str(band)+'PhotonsNULLV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' union all select count(*) as dt from '+str(band)+'PhotonsV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+') x'+str(formatURL)


# Find the number of events inside of a box defined by an x range and a y range
#  in detector space coordinates
def boxcount(band,t0,t1,xr,yr,tscale=1000.):
	return str(baseURL)+'select count(*) from NUVPhotonsNULLV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and x between '+str(xr[0])+' and '+str(xr[1])+' and y between '+str(yr[0])+' and '+str(yr[1])+str(formatURL)

# Find the mean position of events inside of a box in detector space
def boxcentroid(band,t0,t1,xr,yr,tscale=1000.):
	return str(baseURL)+'select avg(x), avg(y) from NUVPhotonsNULLV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and x between '+str(xr[0])+' and '+str(xr[1])+' and y between '+str(yr[0])+' and '+str(yr[1])+str(formatURL)

# Get the list of times for events inside of a box in detector space
def boxtimes(band,t0,t1,xr,yr,tscale=1000.):
        return str(baseURL)+'select time from NUVPhotonsNULLV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and x between '+str(xr[0])+' and '+str(xr[1])+' and y between '+str(yr[0])+' and '+str(yr[1])+str(formatURL)

def centroid(band,ra0,dec0,t0,t1,radius,tscale=1000.):
	return str(baseURL)+'select avg(ra), avg(dec) from NUVPhotonsV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and ra between '+repr(ra0-radius)+' and '+repr(ra0+radius)+' and dec between '+repr(dec0-radius)+' and '+repr(dec0+radius)+str(formatURL)

# Return time and RA/Dec position for every event in the aperture
def allphotons(band,ra0,dec0,t0,t1,radius,tscale=1000.):
	return str(baseURL)+'select time, ra, dec from NUVPhotonsV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and ra between '+repr(ra0-radius)+' and '+repr(ra0+radius)+' and dec between '+repr(dec0-radius)+' and '+repr(dec0+radius)+str(formatURL)

# Shutter correction
#  i.e. number of 0.05s gaps in data
def shutter(band,t0,t1,tscale=1000.):
	return str(baseURL)+'select * from fGet'+str(band)+'Shutter('+str(long(t0*tscale))+','+str(long(t1*tscale))+')'+str(formatURL)

def shutdead(band,t0,t1,tscale=1000.):
	return str(baseURL)+'SELECT shutter*0.05 FROM fGetNUVShutter('+str(long(t0*tscale))+','+str(long(t1*tscale))+') AS time UNION ALL SELECT SUM(dt) * 0.0000057142857142857145 / ('+repr(t1)+'-'+repr(t0)+') AS dead FROM(SELECT count(*) AS dt FROM NUVPhotonsNULLV WHERE time BETWEEN '+str(long(t0*tscale))+' AND '+str(long(t1*tscale))+' UNION ALL SELECT count(*) AS dt FROM NUVPhotonsV WHERE time BETWEEN '+str(long(t0*tscale))+' AND '+str(long(t1*tscale))+') x'+str(formatURL)

def exptime(band,t0,t1,stepsz=1.,tscale=1000.):
	return str(baseURL)+'select * from fGet'+str(band)+'EffectiveExposureTime('+str(long(t0*tscale))+','+str(long(t1*tscale))+','+str(stepsz)+')'+str(formatURL)

# Return the aspect information based on time range
def aspect(t0,t1,tscale=1000.):
	return str(baseURL)+'select eclipse, filename, time, ra, dec, twist, flag, ra0, dec0, twist0 from aspect where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' order by time'+str(formatURL)

# Return the aspect information based on eclipse
def aspect_ecl(eclipse):
	return str(baseURL)+'select eclipse, filename, time, ra, dec, twist, flag, ra0, dec0, twist0 from aspect where eclipse='+str(eclipse)+' order by time'+str(formatURL)

# Return data within a box centered on ra0, dec0 with sides of length 2*radius
def box(band,ra0,dec0,t0,t1,radius,tscale=1000.):
	return str(baseURL)+'select time,ra,dec from '+str(band)+'PhotonsV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and ra between '+repr(ra0-radius)+' and '+repr(ra0+radius)+' and dec between '+repr(dec0-radius)+' and '+repr(dec0+radius)+' and flag=0'+str(formatURL)

# Return data within a rectangle centered on ra0, dec0
def rect(band,ra0,dec0,t0,t1,ra,dec,tscale=1000.):
	return str(baseURL)+'select time,ra,dec from '+str(band)+'PhotonsV where time between '+str(long(t0*tscale))+' and '+str(long(t1*tscale))+' and ra between '+repr(ra0-ra/2.)+' and '+repr(ra0+ra/2.)+' and dec between '+repr(dec0-dec/2.)+' and '+repr(dec0+dec/2.)+' and flag=0'+str(formatURL)


