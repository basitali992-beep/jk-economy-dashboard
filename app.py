import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="J&K State Economy Dashboard",page_icon="🏔️",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background-color:#0a1f1f;color:#e0f7f5;}
.main{background-color:#0a1f1f;}.block-container{padding-top:1rem;padding-bottom:1rem;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a2e2e,#062020);border-right:1px solid #00b89c33;}
section[data-testid="stSidebar"] *{color:#e0f7f5 !important;}
.kpi-card{background:linear-gradient(135deg,#0f3535,#0a2a2a);border:1px solid #00b89c44;
  border-radius:14px;padding:18px 14px;text-align:center;box-shadow:0 4px 20px rgba(0,229,192,0.08);}
.kpi-label{font-size:13px;color:#7ecdc4;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;}
.kpi-value{font-size:28px;font-weight:700;color:#00e5c0;margin-bottom:6px;}
.kpi-delta{font-size:13px;color:#00e5c0;}
.section-header{font-size:15px;font-weight:600;color:#7ecdc4;letter-spacing:2px;text-transform:uppercase;
  border-left:4px solid #00e5c0;padding-left:12px;margin:20px 0 12px 0;}
.footer{background:linear-gradient(90deg,#0f3535,#062020);border-top:1px solid #00b89c33;border-radius:12px;
  padding:18px 24px;text-align:center;margin-top:20px;font-size:13px;color:#7ecdc4;}
.footer span{color:#00e5c0;font-weight:600;}
</style>""", unsafe_allow_html=True)

BG="#0a1f1f";CARD="#0f3535";T1="#00e5c0";T2="#00b89c";T3="#007a6b"
PUR="#9b59b6";YEL="#f1c40f";RED="#e74c3c";WHT="#e0f7f5";GRID="#1a4a4a"

def set_dark(ax,fig):
    fig.patch.set_facecolor(BG);ax.set_facecolor(CARD)
    ax.tick_params(colors=WHT,labelsize=11)
    ax.xaxis.label.set_color(WHT);ax.yaxis.label.set_color(WHT);ax.title.set_color(WHT)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID)
    ax.grid(color=GRID,linestyle="--",linewidth=0.5,alpha=0.7)

YEARS=["2011-12","2012-13","2013-14","2014-15","2015-16","2016-17",
       "2017-18","2018-19","2019-20","2020-21","2021-22","2022-23","2023-24","2024-25"]
YS=["11-12","12-13","13-14","14-15","15-16","16-17",
    "17-18","18-19","19-20","20-21","21-22","22-23","23-24","24-25"]
X=np.arange(len(YEARS))

GSDP_CUR=[78256,87138,95619,98367,117168,124848,139659,160464,164103,167793,188561,209816,236059,262458]
GSDP_CON=[78256,80767,85116,82372,97001,100199,106584,116352,113919,112400,115402,122640,133421,143649]
NSDP_CUR=[65320,72996,79692,81037,98409,104575,117026,134238,135107,135849,152018,167645,191309,213010]
NSDP_CON=[65320,67316,70536,67154,80602,82636,87551,95208,90767,87592,88908,94428,103754,112202]
PCI_CUR=[61852,67838,73322,74301,87172,91491,100808,114096,123730,125546,140038,154708,172810,190768]
PCI_CON=[61852,62878,65268,62219,72168,73427,76934,82730,85892,84100,85705,90429,97673,104411]
PRIM=[18.63,20.65,20.17,16.68,20.72,21.03,20.16,18.22,19.35,19.32,20.62,21.14,21.34,21.55]
SEC=[27.14,24.53,23.58,24.55,22.93,22.36,22.93,22.78,20.14,22.04,19.37,19.02,18.90,18.91]
TER=[54.23,54.82,56.25,58.77,56.35,56.60,56.91,59.00,60.51,58.64,60.01,59.84,59.75,59.53]
GROWTH=[round((GSDP_CUR[i]-GSDP_CUR[i-1])/GSDP_CUR[i-1]*100,1) for i in range(1,len(GSDP_CUR))]

IND_NAMES=["Agriculture","Mining","Manufacturing","Electricity","Construction",
           "Trade","Transport","Financial","Real Estate","Pub.Admin","Other Svcs"]
HM_IND=["Agriculture","Manufacturing","Electricity","Construction","Trade",
        "Transport","Financial","Real Estate","Pub.Admin","Other Svcs"]
HM_DATA=np.array([
    [17.47,16.22,16.11,14.90,15.92,16.23,15.76,14.86,15.36,15.68,15.37,16.07,16.03,15.85],
    [10.64,9.45,9.00,9.41,9.33,8.81,8.42,8.02,6.79,8.68,6.48,6.24,6.29,6.16],
    [8.24,7.14,6.02,6.29,5.95,5.33,5.69,5.95,5.32,5.70,5.21,5.01,4.68,4.52],
    [8.73,8.35,8.72,9.12,7.73,8.29,8.47,8.41,7.96,7.17,7.51,7.82,7.58,7.82],
    [8.92,9.67,9.98,9.77,9.68,10.21,10.92,10.80,11.14,8.71,9.73,10.83,10.55,10.72],
    [6.31,6.68,7.01,7.64,7.24,7.31,7.15,6.65,6.71,6.03,7.45,7.22,7.25,7.35],
    [3.02,3.21,3.58,4.03,4.11,3.99,3.14,3.18,3.45,3.76,3.32,3.55,3.46,3.47],
    [12.69,12.71,13.25,14.07,12.38,12.57,12.69,12.33,12.23,12.29,12.05,12.17,11.65,11.65],
    [15.08,14.67,13.43,13.70,14.78,14.28,14.84,16.81,17.93,19.76,19.37,17.99,18.49,18.07],
    [8.42,8.31,9.37,9.32,8.71,8.96,9.27,10.26,10.04,9.58,9.53,9.71,10.26,10.19],
])
IND_GSDP={
    "2024-25":[46869,1006,14714,10786,18668,25607,17543,8293,27821,43153,24343],
    "2023-24":[41985,910,13633,10157,16443,22879,15726,7493,25269,40084,22249],
    "2022-23":[37524,704,12267,9843,15367,21266,14174,6970,23906,35348,19065],
    "2021-22":[33614,465,11422,9183,13234,17160,13133,5858,21247,34148,16806],
    "2020-21":[28144,174,13422,8818,11093,13465,9332,5822,19008,30554,14821],
    "2019-20":[28095,247,10437,8188,12247,17142,10314,5307,18817,27584,15448],
}

# SIDEBAR
with st.sidebar:
    st.markdown("## 🏔️ J&K Economy")
    st.markdown("---")
    st.markdown("### 🔧 Filters")
    yr_range=st.select_slider("📅 Year Range",options=YEARS,value=(YEARS[0],YEARS[-1]))
    price_type=st.radio("💰 Price Basis",["Current Prices","Constant Prices (2011-12)","Both"],index=0)
    sector_sel=st.multiselect("🏭 Sectors",["Primary","Secondary","Tertiary"],default=["Primary","Secondary","Tertiary"])
    ind_year=st.selectbox("📊 Donut Chart Year",list(IND_GSDP.keys()),index=0)
    st.markdown("---")
    df_dl=pd.DataFrame({"Year":YEARS,"GSDP_Cur":GSDP_CUR,"GSDP_Con":GSDP_CON,
        "NSDP_Cur":NSDP_CUR,"PCI_Cur":PCI_CUR,"PCI_Con":PCI_CON,
        "Primary%":PRIM,"Secondary%":SEC,"Tertiary%":TER})
    st.download_button("⬇️ Download CSV",df_dl.to_csv(index=False).encode("utf-8"),"jk_economy.csv","text/csv")
    st.markdown("---")
    st.markdown("""<div style='font-size:12px;color:#7ecdc4;line-height:1.9'>
    <b style='color:#00e5c0'>Data Source</b><br>DES, Govt of J&K<br><br>
    <b style='color:#00e5c0'>Dashboard By</b><br>Basit Ali<br>
    Official Statistical Section<br>DES, J&K</div>""",unsafe_allow_html=True)

# SLICE
si=YEARS.index(yr_range[0]);ei=YEARS.index(yr_range[1])+1
ys=YS[si:ei];xi=np.arange(len(ys))
gc=GSDP_CUR[si:ei];gco=GSDP_CON[si:ei]
nc=NSDP_CUR[si:ei];nco=NSDP_CON[si:ei]
pc=PCI_CUR[si:ei];pco=PCI_CON[si:ei]
pr=PRIM[si:ei];sc_d=SEC[si:ei];tr=TER[si:ei]
gr_ys=ys[1:];gr=GROWTH[si:ei-1] if ei>1 else []
hm_sl=HM_DATA[:,si:ei]

# HEADER
st.markdown("""
<div style="background:linear-gradient(135deg,#0f3535,#062020);border:1px solid #00b89c44;
border-radius:14px;padding:22px 32px;margin-bottom:20px;">
<div style="display:flex;justify-content:space-between;align-items:center;">
  <div>
    <div style="font-size:32px;font-weight:700;color:#00e5c0;letter-spacing:1px">
      🏔️ J&K State Economy Dashboard</div>
    <div style="font-size:15px;color:#7ecdc4;margin-top:6px">
      GSDP &middot; NSDP &middot; Per Capita Income &middot; Sectoral Analysis &middot; 2024-25</div>
  </div>
  <div style="text-align:right;font-size:13px;color:#7ecdc4">
    <div style="color:#00e5c0;font-weight:700;font-size:15px">Official Statistical Section</div>
    Directorate of Economics &amp; Statistics, J&amp;K<br>
    Dashboard by <b style="color:#00e5c0;font-size:14px">Basit Ali</b>
  </div>
</div></div>""",unsafe_allow_html=True)

# KPI CARDS — 6 cards
gsdp_g=round((GSDP_CUR[-1]-GSDP_CUR[-2])/GSDP_CUR[-2]*100,1)
nsdp_g=round((NSDP_CUR[-1]-NSDP_CUR[-2])/NSDP_CUR[-2]*100,1)
pci_g=round((PCI_CUR[-1]-PCI_CUR[-2])/PCI_CUR[-2]*100,1)
sec_chg=round(SEC[-1]-SEC[-2],2)
ter_chg=round(TER[-1]-TER[-2],2)
pri_chg=round(PRIM[-1]-PRIM[-2],2)

k1,k2,k3,k4,k5,k6=st.columns(6)
kpi_data=[
    (k1,"GSDP 2024-25",f"&#8377;{GSDP_CUR[-1]/100000:.2f}L Cr",f"&#9650; {gsdp_g}% YoY"),
    (k2,"NSDP 2024-25",f"&#8377;{NSDP_CUR[-1]/100000:.2f}L Cr",f"&#9650; {nsdp_g}% YoY"),
    (k3,"Per Capita",f"&#8377;{PCI_CUR[-1]:,}",f"&#9650; {pci_g}% YoY"),
    (k4,"Tertiary Share",f"{TER[-1]}%",f"{'+' if ter_chg>=0 else ''}{ter_chg} pts"),
    (k5,"Secondary Share",f"{SEC[-1]}%",f"{'+' if sec_chg>=0 else ''}{sec_chg} pts"),
    (k6,"Primary Share",f"{PRIM[-1]}%",f"{'+' if pri_chg>=0 else ''}{pri_chg} pts"),
]
for col,lbl,val,dlt in kpi_data:
    col.markdown(f'<div class="kpi-card"><div class="kpi-label">{lbl}</div>'
                 f'<div class="kpi-value">{val}</div>'
                 f'<div class="kpi-delta">{dlt}</div></div>',unsafe_allow_html=True)

st.markdown("<br>",unsafe_allow_html=True)

def mfig(w=11,h=5):
    fig,ax=plt.subplots(figsize=(w,h));set_dark(ax,fig);return fig,ax

# ── CHART 1 & 2
st.markdown('<div class="section-header">📈 Economic Growth Trends</div>',unsafe_allow_html=True)
c1,c2=st.columns(2)

with c1:
    fig,ax=mfig()
    if price_type in ["Current Prices","Both"]:
        ax.plot(xi,[v/1000 for v in gc],color=T1,lw=2.5,marker="o",ms=6,label="GSDP Current")
        ax.fill_between(xi,[v/1000 for v in gc],alpha=0.1,color=T1)
        ax.plot(xi,[v/1000 for v in nc],color=T2,lw=2,marker="s",ms=5,ls="--",label="NSDP Current")
        for i in range(0,len(xi),3):
            ax.annotate(f"₹{gc[i]//1000}k",xy=(xi[i],gc[i]/1000),
                textcoords="offset points",xytext=(0,10),ha="center",fontsize=9,color=T1,fontweight="bold")
    if price_type in ["Constant Prices (2011-12)","Both"]:
        ax.plot(xi,[v/1000 for v in gco],color=PUR,lw=2,marker="^",ms=5,label="GSDP Constant")
        ax.plot(xi,[v/1000 for v in nco],color="#c39bd3",lw=1.5,marker="v",ms=4,ls=":",label="NSDP Constant")
    ax.set_xticks(xi);ax.set_xticklabels(ys,rotation=45,ha="right",fontsize=10)
    ax.set_xlabel("Year",color=WHT,fontsize=12);ax.set_ylabel("Rs. '000 Cr",color=WHT,fontsize=12)
    ax.set_title("GSDP & NSDP Trend",color=WHT,fontsize=16,fontweight="bold",pad=12)
    ax.legend(loc="upper left",fontsize=10,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
    plt.tight_layout();st.pyplot(fig);plt.close()

with c2:
    fig,ax=mfig()
    p_a=np.array(pr);s_a=np.array(sc_d);t_a=np.array(tr)
    ax.bar(xi,p_a,color=T1,label="Primary",width=0.6)
    ax.bar(xi,s_a,bottom=p_a,color=PUR,label="Secondary",width=0.6)
    ax.bar(xi,t_a,bottom=p_a+s_a,color=T2,label="Tertiary",width=0.6,alpha=0.85)
    for i,v in enumerate(t_a):
        ax.text(xi[i],p_a[i]+s_a[i]+v+0.8,f"{v:.0f}%",
            ha="center",va="bottom",fontsize=9,color=WHT,fontweight="bold")
    ax.set_xticks(xi);ax.set_xticklabels(ys,rotation=45,ha="right",fontsize=10)
    ax.set_xlabel("Year",color=WHT,fontsize=12);ax.set_ylabel("Share (%)",color=WHT,fontsize=12)
    ax.set_ylim(0,118)
    ax.set_title("Sector-wise NSDP Share (%)",color=WHT,fontsize=16,fontweight="bold",pad=12)
    ax.legend(loc="upper right",fontsize=10,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
    plt.tight_layout();st.pyplot(fig);plt.close()

# ── CHART 3: HEATMAP
st.markdown('<div class="section-header">🔥 Industry Contribution Heatmap</div>',unsafe_allow_html=True)
fig,ax=plt.subplots(figsize=(15,5.5))
fig.patch.set_facecolor(BG);ax.set_facecolor(BG)
cmap=LinearSegmentedColormap.from_list("teal_dark",["#0a1515","#005a50","#00b89c","#00e5c0"])
sns.heatmap(hm_sl,ax=ax,xticklabels=ys,yticklabels=HM_IND,
    cmap=cmap,annot=True,fmt=".1f",annot_kws={"size":9.5,"color":WHT},
    linewidths=0.5,linecolor=BG,
    cbar_kws={"label":"Share %","shrink":0.8})
ax.set_title("Industry-wise GSDP Share Heatmap — % at Constant 2011-12 Prices",
    color=WHT,fontsize=15,fontweight="bold",pad=14)
ax.tick_params(axis="x",colors=WHT,labelsize=10,rotation=45)
ax.tick_params(axis="y",colors=WHT,labelsize=11,rotation=0)
cbar=ax.collections[0].colorbar
cbar.ax.tick_params(labelcolor=WHT,labelsize=10)
cbar.set_label("Share %",color=WHT,fontsize=11)
plt.tight_layout();st.pyplot(fig);plt.close()

# ── CHART 4 & 6
st.markdown('<div class="section-header">💰 Per Capita Income & YoY Growth</div>',unsafe_allow_html=True)
c3,c4=st.columns(2)

with c3:
    fig,ax=mfig()
    if price_type in ["Current Prices","Both"]:
        ax.plot(xi,pc,color=T1,lw=2.5,marker="o",ms=6,label="Current Prices")
        ax.fill_between(xi,pc,alpha=0.08,color=T1)
        for i in range(0,len(xi),2):
            ax.annotate(f"₹{pc[i]//1000}k",xy=(xi[i],pc[i]),
                textcoords="offset points",xytext=(0,10),ha="center",fontsize=9,color=T1,fontweight="bold")
    if price_type in ["Constant Prices (2011-12)","Both"]:
        ax.plot(xi,pco,color=PUR,lw=2,marker="s",ms=5,ls="--",label="Constant Prices")
        for i in range(0,len(xi),2):
            ax.annotate(f"₹{pco[i]//1000}k",xy=(xi[i],pco[i]),
                textcoords="offset points",xytext=(0,-14),ha="center",fontsize=9,color=PUR)
    ax.set_xticks(xi);ax.set_xticklabels(ys,rotation=45,ha="right",fontsize=10)
    ax.set_xlabel("Year",color=WHT,fontsize=12);ax.set_ylabel("Rs. per Capita",color=WHT,fontsize=12)
    ax.set_title("Per Capita Income Trend",color=WHT,fontsize=16,fontweight="bold",pad=12)
    ax.legend(loc="upper left",fontsize=10,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
    plt.tight_layout();st.pyplot(fig);plt.close()

with c4:
    fig,ax=mfig()
    gr_xi=np.arange(len(gr_ys))
    bar_c=[T1 if v>=0 else RED for v in gr]
    bars=ax.bar(gr_xi,gr,color=bar_c,width=0.6,edgecolor=BG,linewidth=0.5)
    for bar,val in zip(bars,gr):
        ypos=val+0.25 if val>=0 else val-0.8
        ax.text(bar.get_x()+bar.get_width()/2,ypos,f"{val}%",
            ha="center",va="bottom",fontsize=9,color=WHT,fontweight="bold")
    ax.axhline(0,color=WHT,lw=0.8,ls="--",alpha=0.5)
    ax.set_xticks(gr_xi);ax.set_xticklabels(gr_ys,rotation=45,ha="right",fontsize=10)
    ax.set_xlabel("Year",color=WHT,fontsize=12);ax.set_ylabel("Growth (%)",color=WHT,fontsize=12)
    ax.set_title("GSDP YoY Growth Rate (%)",color=WHT,fontsize=16,fontweight="bold",pad=12)
    p1=mpatches.Patch(color=T1,label="Positive Growth")
    p2=mpatches.Patch(color=RED,label="Decline")
    ax.legend(handles=[p1,p2],loc="upper right",fontsize=10,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
    plt.tight_layout();st.pyplot(fig);plt.close()

# ── CHART 5 & 7
st.markdown('<div class="section-header">🏭 Industry Structure & GSDP Correlation</div>',unsafe_allow_html=True)
c5,c6=st.columns([1.05,0.95])

with c5:
    ind_vals=IND_GSDP[ind_year]
    colors_d=[T1,T2,T3,"#00544a",PUR,"#c39bd3",YEL,"#e67e22",WHT,"#5dade2","#abebc6"]
    fig,ax=plt.subplots(figsize=(7,5.5))
    fig.patch.set_facecolor(BG);ax.set_facecolor(BG)
    wedges,texts,autotexts=ax.pie(
        ind_vals,labels=None,autopct="%1.1f%%",colors=colors_d,startangle=140,
        wedgeprops=dict(width=0.55,edgecolor=BG,linewidth=1.5),
        pctdistance=0.78,textprops=dict(color=BG,fontsize=9,fontweight="bold"))
    for at in autotexts: at.set_fontsize(8.5)
    total=sum(ind_vals)
    ax.text(0,0,f"Rs.{total/100000:.2f}\nL Cr",ha="center",va="center",
        fontsize=13,color=T1,fontweight="bold")
    ax.legend(wedges,IND_NAMES,loc="center left",bbox_to_anchor=(1,0.5),
        fontsize=9,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
    ax.set_title(f"GSDP Industry Breakdown — {ind_year}",
        color=WHT,fontsize=14,fontweight="bold",pad=14)
    plt.tight_layout();st.pyplot(fig);plt.close()

with c6:
    fig,ax=mfig(8,5.5)
    z=np.polyfit(GSDP_CUR,PCI_CUR,1)
    xs_fit=np.linspace(min(GSDP_CUR),max(GSDP_CUR),100)
    ax.plot(xs_fit,np.poly1d(z)(xs_fit),color=YEL,lw=1.5,ls="--",label="Trend",alpha=0.8)
    for i,(gx,py,yr) in enumerate(zip(GSDP_CUR,PCI_CUR,YS)):
        col=T1 if i>=len(GSDP_CUR)-3 else T2 if i>=len(GSDP_CUR)-7 else T3
        ax.scatter(gx,py,color=col,s=80,zorder=5,edgecolors=BG,linewidths=0.8)
        ax.annotate(yr,xy=(gx,py),textcoords="offset points",xytext=(4,4),fontsize=8,color=T1)
    ax.set_xlabel("GSDP (Rs Cr)",color=WHT,fontsize=12)
    ax.set_ylabel("Per Capita Income (Rs)",color=WHT,fontsize=12)
    ax.set_title("GSDP vs Per Capita Income",color=WHT,fontsize=15,fontweight="bold",pad=12)
    p1=mpatches.Patch(color=T1,label="Recent (2022-25)")
    p2=mpatches.Patch(color=T2,label="Mid (2018-21)")
    p3=mpatches.Patch(color=T3,label="Early (2011-17)")
    ax.legend(handles=[p1,p2,p3,mpatches.Patch(color=YEL,label="Trend")],
        fontsize=10,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
    plt.tight_layout();st.pyplot(fig);plt.close()

# ── CHART 8: DEFLATION GAP
st.markdown('<div class="section-header">🌊 Price Deflation Gap Analysis</div>',unsafe_allow_html=True)
fig,ax=mfig(15,4.8)
ax.fill_between(xi,[v/1000 for v in gc],alpha=0.2,color=T1)
ax.fill_between(xi,[v/1000 for v in gco],alpha=0.25,color=PUR)
ax.plot(xi,[v/1000 for v in gc],color=T1,lw=2.5,marker="o",ms=5,label="GSDP Current Prices")
ax.plot(xi,[v/1000 for v in gco],color=PUR,lw=2.5,marker="s",ms=5,label="GSDP Constant 2011-12")
ax.fill_between(xi,[v/1000 for v in gc],[v/1000 for v in gco],alpha=0.12,color=YEL,label="Inflation Gap")
for i in range(0,len(xi),3):
    ax.annotate(f"₹{gc[i]//1000}k",xy=(xi[i],gc[i]/1000),
        textcoords="offset points",xytext=(0,10),ha="center",fontsize=9.5,color=T1,fontweight="bold")
ax.set_xticks(xi);ax.set_xticklabels(ys,rotation=45,ha="right",fontsize=10)
ax.set_xlabel("Year",color=WHT,fontsize=13);ax.set_ylabel("Rs. '000 Cr",color=WHT,fontsize=13)
ax.set_title("GSDP: Current vs Constant Prices — Deflation Gap",
    color=WHT,fontsize=16,fontweight="bold",pad=14)
ax.legend(loc="upper left",fontsize=11,facecolor=CARD,labelcolor=WHT,edgecolor=GRID)
plt.tight_layout();st.pyplot(fig);plt.close()

# FOOTER
st.markdown("""
<div class="footer">
  <span>Official Statistics Section &middot; Directorate of Economics &amp; Statistics, Government of J&amp;K</span><br>
  Dashboard Designed &amp; Developed by <span>Basit Ali</span> &nbsp;|&nbsp;
  Data Source: DES J&K &mdash; Digest of Statistics 2024-25 &nbsp;|&nbsp;
  <span>&copy; 2026 All Rights Reserved</span>
</div>""",unsafe_allow_html=True)