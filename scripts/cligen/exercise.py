from daily_clifile_editor import compute_breakpoint
import pandas as pd
import subprocess
import numpy as np
import matplotlib.pyplot as plt

# Jun 11 2015
precip = [
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.02, 0.02, 0.02, 0.02,
 0.02, 0.02, 0.09, 0.09, 0.12, 0.09, 0.09, 0.14, 0.14, 0.14, 0.09, 0.36, 1.34,
 1.34, 1.34, 0.89, 0.38, 0.38, 0.12, 0.09, 0.09, 0.14, 0.14, 0.17, 0.15, 0.15,
 0.30, 0.27, 0.27, 0.60, 0.60, 0.60, 0.27, 0.27, 0.20, 0.20, 0.21, 0.20, 0.20,
 0.29, 0.35, 0.35, 0.23, 0.09, 0.06, 0.06, 0.05, 0.05, 0.05, 0.03, 0.03, 0.06,
 0.06, 0.06, 0.08, 0.08, 0.11, 0.14, 0.14, 0.06, 0.06, 0.06, 0.09, 0.09, 0.12,
 0.15, 0.15, 0.14, 0.14, 0.14, 0.11, 0.14, 0.11, 0.11, 0.11, 0.14, 0.14, 0.20,
 0.29, 0.29, 0.23, 0.20, 0.17, 0.17, 0.17, 0.14, 0.12, 0.12, 0.11, 0.18, 0.18,
 0.21, 0.20, 0.21, 0.20, 0.20, 0.26, 0.21, 0.05, 0.05, 0.08, 0.08, 0.08, 0.08,
 0.11, 0.11, 0.12, 0.12, 0.12, 0.21, 0.21, 0.20, 0.18, 0.18, 0.14, 0.14, 0.14,
 0.15, 0.15, 0.15, 0.15, 0.15, 0.14, 0.14, 0.14, 0.12, 0.12, 0.09, 0.09, 0.09,
 0.05, 0.03, 0.06, 0.06, 0.06, 0.06, 0.06, 0.12, 0.12, 0.15, 0.17, 0.17, 0.14,
 0.14, 0.09, 0.09, 0.14, 0.14, 0.17, 0.17, 0.15, 0.12, 0.12, 0.15, 0.15, 0.26,
 0.29, 0.38, 0.38, 0.50, 0.42, 0.35, 0.35, 0.50, 0.50, 0.42, 0.42, 0.45, 0.44,
 0.44, 0.50, 0.56, 0.57, 0.53, 0.53, 0.36, 0.24, 0.24, 0.09, 0.09, 0.08, 0.09,
 0.09, 0.06, 0.03, 0.05, 0.11, 0.11, 0.20, 0.41, 0.41, 0.14, 0.14, 0.12, 0.11,
 0.11, 0.09, 0.09, 0.09, 0.11, 0.11, 0.12, 0.14, 0.14, 0.06, 0.06, 0.06, 0.03,
 0.03, 0.11, 0.15, 0.15, 0.12, 0.12, 0.12, 0.06, 0.06, 0.20, 0.20, 0.20, 0.12,
 0.12, 1.35, 2.68, 2.68, 3.62, 3.62, 2.46, 0.38, 0.38, 1.05, 1.05, 1.04, 0.59,
 0.59, 0.86, 0.90, 0.90, 0.51, 0.51, 0.41, 0.23, 0.23, 0.59, 0.59, 1.41, 2.19,
 2.19, 2.16, 1.41, 1.41, 1.02, 1.02, 1.02, 1.04, 1.04, 1.71, 1.71, 1.71, 0.92,
 0.92, 0.92, 0.72, 0.72, 0.63, 0.29, 0.29, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02,
 0.02, 0.02, 0.02, 0, 0, 0, 0, 0, 0, 0, 0, 0.02, 0.02,
 0.02, 0.05, 0.05, 0.03, 0.02, 0.02, 0.05, 0.05, 0.03, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0, 0, 0.03, 0.03, 0.03,
 0.05, 0.24, 0.24, 1.01, 0.92, 0.24, 0.45, 0.45, 1.34, 1.34, 1.34, 1.34, 1.34,
 2.06, 2.06, 1.94, 0, 0.02, 0.02, 0.02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0.11, 0.11, 0.24, 0.24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.05,
 0.06, 0.06, 0.03, 0.03, 0.03, 0.02, 0.02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def get_results():
    for line in open('/i/0/env/10240010/0109/102400100109_44.env'):
        tokens = line.strip().split()
        if tokens[0] == '11' and tokens[1] == '6' and tokens[2] == '9':
            return dict(runoff=float(tokens[4]), loss=float(tokens[5]),
                        delivery=float(tokens[12]))


def get_maxrate(bpdata):
    t = []
    r = []
    for line in bpdata:
        tokens = line.split()
        if len(tokens) != 2:
            continue
        t.append(float(tokens[0]))
        r.append(float(tokens[1]))

    maxr = 0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        dr = r[i] - r[i-1]
        rate = (dr / dt)
        if rate > maxr:
            maxr = rate
    return maxr


def edit(bpdata):
    o = open('/i/0/cli/095x041/094.86x040.84.cli').read()
    pos1 = o.find("11\t6\t2015")
    pos2 = o.find("12\t6\t2015")
    out = open('/i/0/cli/095x041/094.86x040.84.cli', 'w')
    newdata = ("11\t6\t2015\t%(points)s\t25.0\t20.0\t269\t4.2\t0\t20.0\n"
               "%(bp)s\n") % dict(points=len(bpdata), bp=("\n".join(bpdata)))
    out.write(o[:pos1] + newdata + o[pos2:])
    out.close()


def run():
    print("%2s %2s %2s %6s %6s %6s %6s" % ("I", "A", "SZ", "MAXR", "RUNOF",
                                           "LOSS", "DELIV"))
    rows = []
    for intensityThres in range(1, 21):
        for accumThres in range(1, 21):
            bpdata = compute_breakpoint(precip, accumThreshold=accumThres,
                                        intensityThreshold=intensityThres)
            edit(bpdata)
            maxr = get_maxrate(bpdata)
            cmd = "~/bin/wepp < /i/0/run/10240010/0109/102400100109_44.run"
            subprocess.call(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
            res = get_results()
            print(("%2i %2i %2i %6.2f %6.2f %6.3f %6.3f"
                   ) % (intensityThres, accumThres, len(bpdata),
                        maxr, res['runoff'], res['loss'], res['delivery']))
            rows.append(dict(intensitythres=intensityThres,
                             accumthres=accumThres,
                             points=len(bpdata),
                             maxrate=maxr,
                             runoff=res['runoff'],
                             loss=res['loss'],
                             delivery=res['delivery']))
    df = pd.DataFrame(rows)
    df.to_pickle('exercise.pickle')


def plot():
    df = pd.read_pickle("exercise.pickle")

    units = {'loss': 'kg m-2', 'points': 'count', 'maxrate': 'mm hr-1',
             'runoff': 'mm', 'delivery': 'kg m-1'}
    titles = {'loss': 'Soil Loss', 'points': 'Number of Break Points',
              'maxrate': 'Maximum Precip Rate',
              'runoff': 'Runoff', 'delivery': 'Soil Delivery'}
    for varname in ['loss', 'points', 'maxrate', 'runoff', 'delivery']:
        print("Processing %s" % (varname,))
        (fig, ax) = plt.subplots(1, 1)
        data = np.zeros((20, 20))
        for _, row in df.iterrows():
            data[row['intensitythres'] - 1,
                 row['accumthres'] - 1] = row[varname]
        maxval = np.max(data)
        res = ax.imshow(data / maxval, interpolation='nearest',
                        extent=[0.5, 20.5, 20.5, 0.5],
                        cmap=plt.get_cmap("GnBu"))
        ax.set_xlabel("Accumuluation Threshold")
        ax.set_ylabel("Intensity Threshold")
        ax.set_ylim(0.5, 20.5)
        ax.grid(True)
        ax.set_title("%s (Max: %.3f %s)" % (titles[varname], maxval,
                                            units[varname]))
        fig.colorbar(res, label='Normalized')
        fig.savefig('%s_experiment.png' % (varname,))
        plt.close()

plot()
