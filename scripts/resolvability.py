import os as _os
ROOT_ = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + "/"  # repository root (was a hard coded build path)
import tifffile, numpy as np, gzip, json, sys
sys.path.insert(0,ROOT_+'scripts')
from tile_stats import slope_deg, summarize
from scipy.signal import find_peaks
RAW=ROOT_+"data/raw/"
out={}
# ---------- tiles
A=tifffile.imread(RAW+"Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif").astype(np.float64)   # N23E053 (rows from 24.0N)
B=tifffile.imread(RAW+"Copernicus_DSM_COG_10_N22_00_E054_00_DEM.tif").astype(np.float64)   # N22E054 (rows from 23.0N)
def crop(a,top,left,lat0,lat1,lon0,lon1):
    r0=int(round((top-lat1)*3600)); r1=int(round((top-lat0)*3600)); c0=int(round((lon0-left)*3600)); c1=int(round((lon1-left)*3600))
    return a[r0:r1,c0:c1],r0,c0
# ---------- 1. COP30 vs official GLO-90 vs SRTM(skadi) on AOI A
g90=tifffile.imread(RAW+"Copernicus_DSM_COG_30_N23_00_E053_00_DEM.tif").astype(np.float64)  # 1200x1200 at 3"
s90full,_,_=slope_deg(g90,24.0,3/3600,3/3600)
r0,r1,c0,c1=int(round((24-23.17)/ (3/3600))),int(round((24-23.02)/(3/3600))),int(round((53.55-53)/(3/3600))),int(round((53.95-53)/(3/3600)))
out["GLO90_official_AOI_A"]=summarize(s90full[r0:r1,c0:c1],"GLO-90 official product, AOI A, central-diff slope")
srtm=np.frombuffer(gzip.open(RAW+"N23E053.hgt.gz").read(),dtype='>i2').reshape(3601,3601).astype(np.float64)
srtm[srtm==-32768]=np.nan
sS,_,_=slope_deg(srtm[:3600,:3600],24.0,1/3600,1/3600)
subA,ra,ca=crop(A,24.0,53.0,23.02,23.17,53.55,53.95)
sA,_,_=slope_deg(A,24.0,1/3600,1/3600)
sA=sA[ra:ra+subA.shape[0],ca:ca+subA.shape[1]]
sSa=sS[ra:ra+subA.shape[0],ca:ca+subA.shape[1]]
out["SRTM1_skadi_AOI_A"]=summarize(sSa,"SRTM 1-arcsec (skadi) AOI A")
out["COP30_AOI_A"]=summarize(sA,"COP30 AOI A")
# elevation differences SRTM(2000) - COP30(2011-15) in AOI A
Ssub=srtm[:3600,:3600][ra:ra+subA.shape[0],ca:ca+subA.shape[1]]
d=Ssub-subA
out["SRTM_minus_COP30_AOI_A"]={"mean":float(np.nanmean(d)),"std":float(np.nanstd(d)),"median":float(np.nanmedian(d)),
   "p5":float(np.nanpercentile(d,5)),"p95":float(np.nanpercentile(d,95)),"rmse":float(np.sqrt(np.nanmean(d**2))),
   "corr":float(np.corrcoef(Ssub[np.isfinite(Ssub)],subA[np.isfinite(Ssub)])[0,1])}
# note: skadi values are integers (1 m quantisation)
# ---------- 2. Cross-dune profile analysis (N-S profiles, AOI B) : peaks, heights, spacing, steep runs
subB,rb,cb=crop(B,23.0,54.0,22.20,22.50,54.20,54.60)
dy=np.deg2rad(1/3600)*6371008.8
heights=[];spacings=[];runs_len=[];runs_drop=[]
for j in range(0,subB.shape[1],7):
    p=subB[:,j]
    pk,pr=find_peaks(p,prominence=30)    # prominence 30 m (my threshold)
    if len(pk)>1: spacings+=list(np.diff(pk)*dy)
    heights+=list(pr['prominences'])
    g=np.degrees(np.arctan(np.abs(np.diff(p))/dy))   # forward-diff slope between adjacent posts
    steep=g>=25
    # runs of consecutive steep segments
    i=0
    while i<len(steep):
        if steep[i]:
            k=i
            while k<len(steep) and steep[k]: k+=1
            runs_len.append(k-i); runs_drop.append(abs(p[k]-p[i])); i=k
        else: i+=1
def q(x): 
    x=np.array(x); return {"n":int(x.size),"p10":float(np.percentile(x,10)),"median":float(np.median(x)),"p90":float(np.percentile(x,90)),"max":float(x.max())}
out["AOI_B_NS_profiles"]={"peak_prominence_ge30m_heights_m":q(heights),"adjacent_peak_spacing_m":q(spacings),
   "steep(>=25deg fwd-diff) run length in posts (30 m posting)":q(runs_len),"elev drop across steep run (m)":q(runs_drop)}
# fraction of steep runs that are single-post
rl=np.array(runs_len); out["AOI_B_NS_profiles"]["frac_runs_single_post"]=float((rl==1).mean())
out["AOI_B_NS_profiles"]["frac_runs_le2_posts"]=float((rl<=2).mean())
# ---------- 3. slopes above published repose angle = artefact indicator
for nm,arr in [("A",sA)]:
    out[f"AOI_{nm}_frac>34"]=float((arr>34).mean())
sB,_,_=slope_deg(B,23.0,1/3600,1/3600); sBb=sB[rb:rb+subB.shape[0],cb:cb+subB.shape[1]]
out["AOI_B_frac>34"]=float((sBb>34).mean()); out["AOI_B_frac>32"]=float((sBb>32).mean())
out["AOI_A_frac>32"]=float((sA>32).mean())
# ---------- 4. Synthetic planar 32-degree slip face of height H sampled at 30 m with random phase
rng=np.random.default_rng(0)
def sim(H,theta=32.0,dxp=30.0,lam=None,n=4000):
    run=H/np.tan(np.radians(theta)); res=[];res_cd=[]
    for _ in range(n):
        ph=rng.uniform(0,dxp)
        x=np.arange(-5*dxp,5*dxp+run+5*dxp,dxp)+ph
        z=np.clip(-(x)*np.tan(np.radians(theta))+H,0,H)*0  # placeholder
        # profile: flat crest at H for x<0, ramp down to 0 over 'run', flat 0 beyond
        z=np.where(x<0,H,np.where(x>run,0.0,H-x*np.tan(np.radians(theta))))
        fd=np.degrees(np.arctan(np.abs(np.diff(z))/dxp)).max()
        cd=np.degrees(np.arctan(np.abs(np.gradient(z,dxp))).max())
        res.append(fd);res_cd.append(cd)
    return {"H":H,"run_m":float(run),"fwd_diff_max_slope_median":float(np.median(res)),"fwd_diff_p10":float(np.percentile(res,10)),
            "central_diff_max_median":float(np.median(res_cd)),"central_diff_p10":float(np.percentile(res_cd,10))}
out["synthetic_32deg_slipface_30m"]=[sim(H) for H in (3,5,10,20,30,50,100)]
out["synthetic_32deg_slipface_90m"]=[sim(H,dxp=90.0) for H in (10,20,50,100)]
json.dump(out,open(ROOT_+"data/derived/resolvability.json","w"),indent=1)
print(json.dumps(out,indent=1))
