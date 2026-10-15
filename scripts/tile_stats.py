import os as _os
ROOT_ = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) + "/"  # repository root (was a hard coded build path)
import tifffile, numpy as np, gzip, json, sys
R=6378137.0
def load_cop(path):
    a=tifffile.imread(path).astype(np.float64)
    return a
def slope_deg(a, lat_top, dlat_deg, dlon_deg):
    """central-difference slope (np.gradient) in degrees, metric spacing per row latitude (spherical approx)."""
    n=a.shape[0]
    lats=lat_top - (np.arange(n)+0.5)*dlat_deg   # pixel-is-area centres
    dy=np.deg2rad(dlat_deg)*6371008.8
    dx=np.deg2rad(dlon_deg)*6371008.8*np.cos(np.deg2rad(lats))
    gy,gx=np.gradient(a,dy,axis=0),np.gradient(a,axis=1)/dx[:,None]
    gy=-gy*1.0  # sign irrelevant
    return np.degrees(np.arctan(np.hypot(gx,gy))), dx, dy
def summarize(s,label):
    s=s[np.isfinite(s)]
    out={"label":label,"n":int(s.size),"mean":float(s.mean()),"median":float(np.median(s)),
         "p90":float(np.percentile(s,90)),"p99":float(np.percentile(s,99)),"p99.9":float(np.percentile(s,99.9)),"max":float(s.max())}
    for t in (10,15,20,25,30):
        out[f"frac>{t}"]=float((s>t).mean())
    return out
if __name__=="__main__":
    a=load_cop(ROOT_+"data/raw/Copernicus_DSM_COG_10_N23_00_E053_00_DEM.tif")
    s,dx,dy=slope_deg(a,24.0,1/3600,1/3600)
    print("cell dx range (m)",dx.min(),dx.max(),"dy",dy)
    print(json.dumps(summarize(s,"COP30 N23E053 whole tile"),indent=1))
