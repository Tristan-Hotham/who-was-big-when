"""Step 3. Clubs, places and outlines.

Each club gets a display name, a town (written by hand below, the place the club stands for; for the big
cities the city), the point of its present or last ground from engsoccerdata's england_club_data (two
corrected: Coventry City carried Birmingham City's point, Harrogate Town had none), and the ONS region,
ceremonial county and nation that point falls in. Output: WORK/clubs.json, data/clubs.csv,
data/england_wales.geojson (counties of England and Wales, simplified), WORK/towns.json (place names for the
map, from the OS Open Names and GeoNames town list published with the dark-skies study).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import pandas as pd
import geopandas as gpd
import pyreadr, warnings
warnings.filterwarnings("ignore", "Geometry is in a geographic CRS")
from shapely.geometry import Point

T = pd.read_csv(os.path.join(WORK, "tables.csv"))
C = pyreadr.read_r(os.path.join(ESD, "england_club_data.rda"))["england_club_data"]
C["team"] = C.team.astype(str)
C = C.set_index("team")
FIX = {"Coventry City": (52.448056, -1.495556), "Harrogate Town A.F.C.": (53.984583, -1.525194)}
NAME = {"Accrington F.C.": "Accrington", "Accrington Stanley": "Accrington Stanley (1891 club)", "Accrington": "Accrington Stanley",
        "Cheltenham": "Cheltenham Town", "Yeovil": "Yeovil Town", "Macclesfield": "Macclesfield Town", "Harrogate Town A.F.C.": "Harrogate Town",
        "Stevenage Borough": "Stevenage", "Chester": "Chester City", "Thames": "Thames Association", "Dagenham and Redbridge": "Dagenham & Redbridge"}
TOWN = {
    "AFC Bournemouth": "Bournemouth", "AFC Wimbledon": "Wimbledon", "Aberdare Athletic": "Aberdare", "Accrington": "Accrington",
    "Accrington F.C.": "Accrington", "Accrington Stanley": "Accrington", "Aldershot": "Aldershot", "Arsenal": "London", "Ashington": "Ashington",
    "Aston Villa": "Birmingham", "Barnet": "Barnet", "Barnsley": "Barnsley", "Barrow": "Barrow-in-Furness", "Birmingham City": "Birmingham",
    "Blackburn Rovers": "Blackburn", "Blackpool": "Blackpool", "Bolton Wanderers": "Bolton", "Bootle": "Bootle", "Boston United": "Boston",
    "Bradford City": "Bradford", "Bradford Park Avenue": "Bradford", "Brentford": "London", "Brighton & Hove Albion": "Brighton",
    "Bristol City": "Bristol", "Bristol Rovers": "Bristol", "Bromley": "London", "Burnley": "Burnley", "Burton Albion": "Burton upon Trent",
    "Burton Swifts": "Burton upon Trent", "Burton United": "Burton upon Trent", "Burton Wanderers": "Burton upon Trent", "Bury": "Bury",
    "Cambridge United": "Cambridge", "Cardiff City": "Cardiff", "Carlisle United": "Carlisle", "Charlton Athletic": "London", "Chelsea": "London",
    "Cheltenham": "Cheltenham", "Chester": "Chester", "Chesterfield": "Chesterfield", "Colchester United": "Colchester", "Coventry City": "Coventry",
    "Crawley Town": "Crawley", "Crewe Alexandra": "Crewe", "Crystal Palace": "London", "Dagenham and Redbridge": "London",
    "Darlington": "Darlington", "Darwen": "Darwen", "Derby County": "Derby", "Doncaster Rovers": "Doncaster", "Durham City": "Durham",
    "Everton": "Liverpool", "Exeter City": "Exeter", "Fleetwood Town": "Fleetwood", "Forest Green Rovers": "Nailsworth", "Fulham": "London",
    "Gainsborough Trinity": "Gainsborough", "Gateshead": "Gateshead", "Gillingham": "Gillingham", "Glossop North End": "Glossop",
    "Grimsby Town": "Grimsby", "Halifax Town": "Halifax", "Harrogate Town A.F.C.": "Harrogate", "Hartlepool United": "Hartlepool",
    "Hereford United": "Hereford", "Huddersfield Town": "Huddersfield", "Hull City": "Hull", "Ipswich Town": "Ipswich",
    "Kidderminster Harriers": "Kidderminster", "Leeds City": "Leeds", "Leeds United": "Leeds", "Leicester City": "Leicester",
    "Leyton Orient": "London", "Lincoln City": "Lincoln", "Liverpool": "Liverpool", "Loughborough": "Loughborough", "Luton Town": "Luton",
    "Macclesfield": "Macclesfield", "Maidstone United": "Maidstone", "Manchester City": "Manchester", "Manchester United": "Manchester",
    "Mansfield Town": "Mansfield", "Merthyr Town": "Merthyr Tydfil", "Middlesbrough": "Middlesbrough", "Middlesbrough Ironopolis": "Middlesbrough",
    "Millwall": "London", "Milton Keynes Dons": "Milton Keynes", "Morecambe": "Morecambe", "Nelson": "Nelson", "New Brighton": "New Brighton",
    "New Brighton Tower": "New Brighton", "Newcastle United": "Newcastle upon Tyne", "Newport County": "Newport", "Northampton Town": "Northampton",
    "Northwich Victoria": "Northwich", "Norwich City": "Norwich", "Nottingham Forest": "Nottingham", "Notts County": "Nottingham",
    "Oldham Athletic": "Oldham", "Oxford United": "Oxford", "Peterborough United": "Peterborough", "Plymouth Argyle": "Plymouth",
    "Port Vale": "Stoke-on-Trent", "Portsmouth": "Portsmouth", "Preston North End": "Preston", "Queens Park Rangers": "London",
    "Reading": "Reading", "Rochdale": "Rochdale", "Rotherham County": "Rotherham", "Rotherham Town": "Rotherham", "Rotherham United": "Rotherham",
    "Rushden & Diamonds": "Rushden", "Salford City": "Salford", "Scarborough": "Scarborough", "Scunthorpe United": "Scunthorpe",
    "Sheffield United": "Sheffield", "Sheffield Wednesday": "Sheffield", "Shrewsbury Town": "Shrewsbury", "South Shields": "South Shields",
    "Southampton": "Southampton", "Southend United": "Southend-on-Sea", "Southport": "Southport", "Stalybridge Celtic": "Stalybridge",
    "Stevenage Borough": "Stevenage", "Stockport County": "Stockport", "Stoke City": "Stoke-on-Trent", "Sunderland": "Sunderland",
    "Sutton United": "London", "Swansea City": "Swansea", "Swindon Town": "Swindon", "Thames": "London", "Torquay United": "Torquay",
    "Tottenham Hotspur": "London", "Tranmere Rovers": "Birkenhead", "Walsall": "Walsall", "Watford": "Watford", "West Bromwich Albion": "West Bromwich",
    "West Ham United": "London", "Wigan Athletic": "Wigan", "Wigan Borough": "Wigan", "Wimbledon": "Wimbledon", "Wolverhampton Wanderers": "Wolverhampton",
    "Workington": "Workington", "Wrexham": "Wrexham", "Wycombe Wanderers": "High Wycombe", "Yeovil": "Yeovil", "York City": "York",
}
# Barnet, Wimbledon and Bromley are London boroughs; they are counted in London for the London story but keep
# their own town name for the 'towns that lost league football' list, where Wimbledon's case matters.
LONDON_TOWNS = {"Barnet", "Wimbledon"}

teams = sorted(T.team.unique())
assert set(teams) == set(TOWN), (set(teams) ^ set(TOWN))
cty = gpd.read_file(os.path.join(GEO, "counties_uk.geojson"))
cty = cty[cty.nation.isin(["England", "Wales"])].reset_index(drop=True)
rgn = gpd.read_file(os.path.join(GEO, "uk_topo.json"), layer="rgn").set_crs(4326, allow_override=True)
ctry = gpd.read_file(os.path.join(GEO, "uk_topo.json"), layer="ctry").set_crs(4326, allow_override=True)
clubs = []
for t in teams:
    lat, lon = FIX.get(t) or (float(C.loc[t, "lat"]), float(C.loc[t, "lon"]))
    p = Point(lon, lat)
    reg = rgn[rgn.contains(p)].areanm.tolist()
    nat = ctry[ctry.contains(p)].areanm.tolist()
    cn = cty[cty.contains(p)].county.tolist()
    if not cn:   # a ground on the coast just outside a simplified outline
        cn = [cty.loc[cty.distance(p).idxmin(), "county"]]
    if not reg:
        reg = [rgn.loc[rgn.distance(p).idxmin(), "areanm"]]
        nat = [ctry.loc[ctry.distance(p).idxmin(), "areanm"]]
    if t == "Chester":   # the Deva Stadium straddles the border, its pitch in Wales; the club is Chester's, so England
        reg, nat, cn = ["North West"], ["England"], ["Cheshire"]
    region = "Wales" if nat[0] == "Wales" else reg[0]
    s = T[T.team == t]
    clubs.append({"key": t, "name": NAME.get(t, t), "town": TOWN[t], "lat": round(lat, 5), "lon": round(lon, 5), "region": region,
                  "band": band(region), "county": cn[0], "nation": nat[0], "first": int(s.season.min()), "last": int(s.season.max()),
                  "seasons": int(s.season.nunique())})
for c in clubs:
    assert c["nation"] in ("England", "Wales"), c
wales = sorted(c["name"] for c in clubs if c["nation"] == "Wales")
assert wales == ["Aberdare Athletic", "Cardiff City", "Merthyr Town", "Newport County", "Swansea City", "Wrexham"], wales
assert all(c["region"] == "London" for c in clubs if c["town"] == "London" or c["town"] in LONDON_TOWNS), [c for c in clubs if c["town"] == "London" and c["region"] != "London"]
jsave(clubs, os.path.join(WORK, "clubs.json"), indent=0)
pd.DataFrame(clubs).drop(columns=["key"]).assign(engsoccerdata_name=[c["key"] for c in clubs])[
    ["name", "engsoccerdata_name", "town", "county", "region", "nation", "lat", "lon", "first", "last", "seasons"]].to_csv(os.path.join(DATA, "clubs.csv"), index=False)

# outlines for the page and figures
g = cty.copy()
g["geometry"] = g.geometry.simplify(0.004, preserve_topology=True)
g[["county", "nation", "geometry"]].to_file(os.path.join(DATA, "england_wales.geojson"), driver="GeoJSON", COORDINATE_PRECISION=4)
rg = rgn.copy(); rg = rg[rg.areanm.str.len() > 0]
ew = rg[["areanm", "geometry"]]
ew = ew[ew.areanm.isin(NORTH + MIDLANDS + SOUTH + ["Wales"])]
assert len(ew) == 10, ew.areanm.tolist()
gpd.GeoDataFrame(ew).to_file(os.path.join(WORK, "regions_full.geojson"), driver="GeoJSON")

# place names: towns and cities of England and Wales, plus every club town
tw = pd.read_csv("/home/claude/ref/dark-skies/data/uk_towns.csv")
tw = tw[tw.kind.isin(["City", "Town"]) & ~tw.region.isin(["Scotland", "Northern Ireland"])]
towns = [{"n": r.name, "k": 0 if r.kind == "City" else 1, "lat": round(r.lat, 4), "lon": round(r.lon, 4)} for r in tw.itertuples()]
jsave(towns, os.path.join(WORK, "towns.json"))
print(len(clubs), "clubs;", len(towns), "towns;", os.path.getsize(os.path.join(DATA, "england_wales.geojson")) // 1024, "KB outlines")
print(pd.DataFrame(clubs).groupby("region").size())
