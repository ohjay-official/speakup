import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
BG="#0B3D2E"; FR="#E8604F"; LG="#4FB58C"; W="#FFFFFF"; SOFT="#CFE3D8"; AMB="#F2A541"
fig=plt.figure(figsize=(16,9),dpi=120); fig.patch.set_facecolor(BG)
serif={"family":"DejaVu Serif"}
fig.text(0.05,0.86,"SpeakUp",color=W,fontsize=58,fontweight="bold",**serif)
fig.text(0.05,0.76,"Asked to help, an open model drops its warning",color=SOFT,fontsize=21)
fig.text(0.05,0.715,"on 29% of investment-fraud requests it can identify",color=SOFT,fontsize=21)
stats=[("29%","of fraud requests lost\ntheir warning",FR),("97%","fraud likelihood it gave the\nsame schemes in a fresh chat",W),("100%","warned on legitimate products\ntoo, when asked for advice",AMB)]
for i,(n,l,c) in enumerate(stats):
    y=0.50-i*0.17
    fig.text(0.05,y,n,color=c,fontsize=46,fontweight="bold",**serif)
    fig.text(0.235,y+0.005,l,color=SOFT,fontsize=16,va="bottom")
ax=fig.add_axes([0.58,0.17,0.38,0.47]); ax.set_facecolor(BG)
cats=["Advice","Returns\ntable","Family\ninvite","Uncle\nloan"]; f=[100,95,58,61]; l=[100,67,5,5]
x=range(4); w=0.38
b1=ax.bar([i-w/2-0.01 for i in x],f,w,color=FR,label="Frauds")
b2=ax.bar([i+w/2+0.01 for i in x],l,w,color=LG,label="Legitimate products")
for bars in (b1,b2):
    for b in bars: ax.text(b.get_x()+b.get_width()/2,b.get_height()+2,f"{b.get_height():.0f}%",ha="center",color=W,fontsize=14)
ax.set_xticks(list(x)); ax.set_xticklabels(cats,color=SOFT,fontsize=14)
ax.set_ylim(0,112); ax.set_yticks([])
for s in ("top","right","left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(SOFT); ax.tick_params(length=0)
fig.legend(frameon=False,labelcolor=W,fontsize=14,loc="upper left",bbox_to_anchor=(0.575,0.735),ncol=2)
fig.text(0.58,0.76,"Qwen3.8-27B: share of replies that warn",color=W,fontsize=17,fontweight="bold")
fig.text(0.05,0.045,"Apart Research · AI x Epistemics Research Sprint · November 2026 · Faithful Adejoh",color="#9FC5B3",fontsize=13)
fig.text(0.95,0.045,"github.com/ohjay-official/speakup",color=AMB,fontsize=13,ha="right")
fig.savefig("SpeakUp_card.png",facecolor=BG); print("ok")
