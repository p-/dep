"""results.py"""
import sys

import numpy as np
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn

years = 8.0
scenario = int(sys.argv[1])
varname = sys.argv[2]
pgconn = get_dbconn("idep")

titles = {
    "detach": "Soil Detachment [tons/acre]",
    "delivery": "Soil Delivery [tons/acre]",
    "runoff": "Runoff [inch]",
}
titles2 = {7: "4", 9: "3", 10: "4", 11: "3"}
extra = {10: "(no-till)", 11: "(no-till)"}

df = read_sql(
    """SELECT r.huc_12, r.scenario,
    sum(avg_loss) * 4.463 as detach, sum(avg_delivery) * 4.463 as delivery,
    sum(avg_runoff) / 25.4 as runoff
    from results_by_huc12 r
    , huc12 h WHERE r.huc_12 = h.huc_12 and h.states ~* 'IA'
    and r.scenario in (0, %s) and h.scenario = 0 and r.valid < '2016-01-01'
    and r.valid > '2008-01-01'
    GROUP by r.scenario, r.huc_12
    ORDER by """
    + varname
    + """ DESC
    """,
    pgconn,
    params=(scenario,),
    index_col=None,
)

s0 = df[df["scenario"] == 0].copy()
s0 = s0.set_index("huc_12")
s0 = s0.rename(
    columns={
        "detach": "detach_s0",
        "delivery": "delivery_s0",
        "scenario": "scenario_s0",
        "runoff": "runoff_s0",
    },
)
s7 = df[df["scenario"] == scenario].copy()
s7 = s7.set_index("huc_12")
s7 = s7.rename(
    columns={
        "detach": "detach_s7",
        "delivery": "delivery_s7",
        "scenario": "scenario_s7",
        "runoff": "runoff_s7",
    },
)

df = s0.join(s7)
df = df.sort_values(by=varname + "_s0", ascending=False)
print(df.head(5))

d0 = np.copy(df[varname + "_s0"].values)
dbaseline = np.copy(df[varname + "_s0"].values)
d7 = df[varname + "_s7"].values

sz = len(df.index)
x = np.arange(0, sz)
y = []
scenario_y = []
baseline_y = []
key = sz / 4
minval = [0, 1000.0]
for i in range(0, sz):
    d0[i] = d7[i]
    scenario_y.append(np.average(d7[:i]) / years)
    baseline_y.append(np.average(dbaseline[:i]) / years)
    thisy = np.average(d0) / years
    y.append(thisy)
    if thisy < minval[1]:
        minval = [i, thisy]
    if i == key:
        print(
            "%s %s %s %s" % ("25%", y[0], y[i], (y[0] - y[i]) / y[0] * 100.0)
        )

print(
    "%s %s"
    % (minval[0] / float(sz) * 100.0, (y[0] - minval[1]) / y[0] * 100.0)
)

(fig, ax) = plt.subplots(1, 1)

ax.set_ylabel("Yearly %s" % (titles[varname],))
ax.set_xlabel("Sequential HUC12 Inclusion [%]")
ax.set_title(
    (
        "Iowa Daily Erosion Project :: UCS %s Year Scenario %s\n"
        "Sequential replacement of most erosive HUC12s with scenario"
    )
    % (titles2[scenario], extra.get(scenario, ""))
)
ax.plot(x / float(x[-1]) * 100.0, y, label="Conversion")
# ax.plot(x / float(x[-1]) * 100., scenario_y, label='Scenario Accum')
# ax.plot(x / float(x[-1]) * 100., baseline_y, label='Baseline Accum')
ax.grid(True)
ax.set_xticks([0, 5, 10, 25, 50, 75, 90, 95, 100])
ax.legend(loc="best")

fig.savefig("test.png")
