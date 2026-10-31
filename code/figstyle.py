"""House style for static figures: fonts (static instances cut from the variable Fraunces font in FONT_DIR,
written to WORK), colours, and the England and Wales outline in a simple equal-area-ish projection
(longitude scaled by cos 52.5 degrees)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
from common import *  # noqa

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    instancer.instantiateVariableFont(TTFont(f"{FONT_DIR}/FrauncesVar.ttf"), {"wght": 900, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-Black.ttf")
    instancer.instantiateVariableFont(TTFont(f"{FONT_DIR}/FrauncesVar.ttf"), {"wght": 600, "opsz": 36, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-Semi.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
SEMI = fm.FontProperties(fname=f"{FD}/Fraunces-Semi.ttf")
SERP = fm.FontProperties(fname=f"{FONT_DIR}/SourceSerif4-Regular.ttf")
fm.fontManager.addfont(f"{FONT_DIR}/IBMPlexMono-Regular.ttf")
fm.fontManager.addfont(f"{FONT_DIR}/IBMPlexMono-Medium.ttf")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": FG,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
TC = {k: v[1] for k, v in TIER.items()}
BANDC = {"North": "#9B1B30", "Midlands": "#D9752B", "London": "#2F5D8A", "South (outside London)": "#5FA0C8", "Wales": "#4C8A3E"}
BANDL = {"North": "North", "Midlands": "Midlands", "London": "London", "South (outside London)": "Rest of the South", "Wales": "Wales"}
K = math.cos(math.radians(52.5))
EW = jload(os.path.join(DATA, "england_wales.geojson"))


def proj(lon, lat):
    return lon * K, lat


def outline(ax, fc=LAND, ec="#FFFFFF", lw=.5):
    for f in EW["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = np.array(poly[0])
            ax.add_patch(MPoly(np.column_stack(proj(ring[:, 0], ring[:, 1])), closed=True, fc=fc, ec=ec, lw=lw))
    ax.set_xlim(-5.85 * K, 1.85 * K); ax.set_ylim(49.9, 55.85); ax.set_aspect("equal"); ax.axis("off")


def rad(avg, k=1.0):
    """marker size (points squared) proportional to crowd"""
    return np.where(np.asarray(avg) > 0, np.asarray(avg, dtype=float) / 1000 * 5.2 * k, 14 * k)


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
