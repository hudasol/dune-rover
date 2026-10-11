import tifffile,numpy as np,json,sys
sys.path.insert(0,'/home/claude/dune-rover/scripts')
from tile_stats import slope_deg,summarize
from scipy.signal import find_peaks
A=tifffile.imread("/home/claude/dune-rover/data/raw/Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif").astype(float)
s,_,dy=slope_deg(A,24.0,1/3600,1/3600)
r0,r1=int(round((24-23.45)*3600)),int(round((24-23.25)*3600)); c0,c1=int(round(.55*3600)),int(round(.95*3600))
sub=A[r0:r1,c0:c1]; ss=s[r0:r1,c0:c1]
o=summarize(ss,"COP30 A_north (23.25-23.45N,53.55-53.95E)"); o["elev_min"]=float(sub.min());o["elev_max"]=float(sub.max())
sp=[];hh=[]
for j in range(0,sub.shape[1],7):
    pk,pr=find_peaks(sub[:,j],prominence=8); 
    if len(pk)>1: sp+=list(np.diff(pk)*dy)
    hh+=list(pr['prominences'])
o["peak_prominence_ge8m"]={"n":len(hh),"median":float(np.median(hh)),"p10":float(np.percentile(hh,10)),"p90":float(np.percentile(hh,90))}
o["peak_spacing_m"]={"median":float(np.median(sp)),"p10":float(np.percentile(sp,10)),"p90":float(np.percentile(sp,90))}
print(json.dumps(o,indent=1)); json.dump(o,open('/home/claude/dune-rover/data/derived/A_north_stats.json','w'),indent=1)
