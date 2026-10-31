# Reddit post

## Title

[OC] Who was big when? Every English league club since 1888, sized by its home crowd: 41.2 million at league games in 1948-49, 16.5 million in 1985-86, and 39 towns that lost their league club along the way

## Body

I rebuilt every Football League and Premier League table from 210,019 match results (1888-89 to 2024-25) and joined each club's average home league crowd, then mapped all 147 clubs season by season. The twelve founders were six Lancashire and six Midlands clubs; London had no league club until 1893-94. Before 1915 the North held 62% of top-flight places; since 2010, 36%. In 2024-25 the Premier League had 7 London clubs and 5 from the North, yet Northern clubs have won 87 of 126 titles. Crowds fell in 27 of 37 seasons after the 1948-49 peak and have recovered to 36.4 million. Caveats: crowds before the mid 1920s are estimates; no crowd data for 2020-21 or 2021-22; clubs drawn at their present or last ground.

Interactive version (season slider, play button, club search with a sparkline for every club): https://maps.tristanhotham.com/who-was-big-when/

## Source comment

Sources: match results from engsoccerdata by James P. Curley (https://github.com/jalapic/engsoccerdata), with 2022-23 from openfootball (https://github.com/openfootball/england, public domain). Average home league gates from englishfootballleaguetables.co.uk (credited; only per-club, per-season averages derived). ONS regions and county boundaries (OGL v3.0).

Tools: Python (pandas, geopandas, pyreadr, matplotlib); Leaflet for the interactive map. Tables rebuilt with 2 points for a win before 1981-82 and 3 after, goal average then goal difference, points deductions applied. Season crowd = average home league gate x home league games.

Interactive version: https://maps.tristanhotham.com/who-was-big-when/
Blog post: https://blog.tristanhotham.com/2026/10/31/who-was-big-when/
Paper: https://doi.org/10.5281/zenodo.23844507
