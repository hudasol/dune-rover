import tifffile, numpy as np, json, gzip, sys
sys.path.insert(0,'/home/claude/dune-rover/scripts')
from tile_stats import slope_deg, summarize
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
RAW="/home/claude/dune-rover/data/raw/"
tiles={"N23E053":(23,53),"N22E053":(22,53),"N22E054":(22,54)}
D={}
for k,(la,lo) in tiles.items():
    D[k]=tifffile.imread(RAW+f"Copernicus_DSM_COG_10_{k[:3]}_00_{k[3:]}_00_DEM.tif").astype(np.float64)
res=[]
for k,a in D.items():
    la,lo=tiles[k]
    s,dx,dy=slope_deg(a,la+1,1/3600,1/3600)
    res.append(summarize(s,f"COP30 {k} whole tile"))
# AOI definitions: (name, tile, lat0,lat1, lon0,lon1)
AOIS=[("A_Liwa_crescent","N23E053",23.02,23.17,53.55,53.95),
      ("B_RubAlKhali_megadunes","N22E054",22.20,22.50,54.20,54.60)]
def crop(a,la,lo,lat0,lat1,lon0,lon1):
    r0=int(round((la+1-lat1)*3600)); r1=int(round((la+1-lat0)*3600)); c0=int(round((lon0-lo)*3600)); c1=int(round((lon1-lo)*3600))
    return a[r0:r1,c0:c1], r0,c0
def hillshade(a,dx,dy,az=315,alt=40):
    gy,gx=np.gradient(a,dy,axis=0),np.gradient(a,axis=1)/dx[:,None]
    slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
    azr=np.radians(az);alr=np.radians(alt)
    return np.sin(alr)*np.cos(slope)+np.cos(alr)*np.sin(slope)*np.cos(azr-aspect)
prof={}
for name,k,lat0,lat1,lon0,lon1 in AOIS:
    la,lo=tiles[k]; a=D[k]
    sub,r0,c0=crop(a,la,lo,lat0,lat1,lon0,lon1)
    s_full,dxf,dy=slope_deg(a,la+1,1/3600,1/3600)
    s=s_full[r0:r0+sub.shape[0],c0:c0+sub.shape[1]]
    dxs=dxf[r0:r0+sub.shape[0]]
    r=summarize(s,f"COP30 {name} ({lat0}-{lat1}N,{lon0}-{lon1}E) 30m")
    r["elev_min"]=float(sub.min());r["elev_max"]=float(sub.max());r["relief"]=float(np.ptp(sub))
    # coarsen to 90 m (3x3 block mean) and recompute
    h,w=(sub.shape[0]//3)*3,(sub.shape[1]//3)*3
    c90=sub[:h,:w].reshape(h//3,3,w//3,3).mean(axis=(1,3))
    la_top=la+1-r0/3600
    s90,_,_=slope_deg(c90,la_top,3/3600,3/3600)
    r2=summarize(s90,f"COP30 {name} block-mean to 90 m (my resampling, NOT GLO-90 product)")
    res+= [r,r2]
    # hillshade png
    hs=hillshade(sub,dxs,dy)
    fig,ax=plt.subplots(1,2,figsize=(14,6.6))
    ax[0].imshow(hs,cmap="gray",extent=[lon0,lon1,lat0,lat1]); ax[0].set_title(f"{name} hillshade (COP30, 30 m)")
    im=ax[1].imshow(s,cmap="magma",vmin=0,vmax=35,extent=[lon0,lon1,lat0,lat1]); ax[1].set_title("slope deg (central diff, 30 m)")
    plt.colorbar(im,ax=ax[1],shrink=.8); plt.tight_layout(); plt.savefig(f"/home/claude/dune-rover/data/derived/{name}_hillshade_slope.png",dpi=80); plt.close()
    # slope histogram bins
    hist,edges=np.histogram(s,bins=np.arange(0,46,5))
    r["hist_5deg_bins"]=[int(x) for x in hist]
    # cross-section profile through relief max row  (west-east)
    # profile along row at median rows
    rr=sub.shape[0]//2
    prof[name]=sub[rr,:].tolist()
json.dump(res,open("/home/claude/dune-rover/data/derived/slope_stats.json","w"),indent=1)
for r in res: print(json.dumps(r))
