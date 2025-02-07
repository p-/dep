"""Apply arbitrary multiplier to baseline precip.

see GH #39
"""
import os
import sys
from multiprocessing.pool import ThreadPool

from tqdm import tqdm


def conservative_adjust(times, accum, multipler):
    """Adjust times to conserve precip, but change intensity, tricky."""
    # We can't adjust by more than 50%
    assert 0.5 < multipler < 1.5
    # If this was a drizzle event, do nothing.
    if accum[-1] < 5:
        return times
    # An algorithm was attempted whereby the peak rate was modified, this
    # yielded no meaningful change.
    # Attempt 2: Take a blunt hammer to the time axis.
    # sometimes there is a danagling midnight
    if times[-1] > 23.95 and times[-2] < 23:
        times[-1] = times[-2] + 0.1
    newtimes = [0]
    for i in range(1, len(times)):
        dt = times[i] - times[i - 1]
        rate = (accum[i] - accum[i - 1]) / dt
        # only modify rates over 22mm/hr
        if rate > 22:
            newtimes.append(newtimes[-1] + dt / multipler)
        else:
            newtimes.append(newtimes[-1] + dt)
    # algo-fail
    if newtimes[-1] >= 23.99:
        return times
    return newtimes


def editor(arg):
    """Do the editing."""
    fn, scenario, multiplier, conserve_total = arg
    newfn = fn.replace("/i/0/", f"/i/{scenario}/")
    newdir = os.path.dirname(newfn)
    if not os.path.isdir(newdir):
        try:
            # subject to race conditions
            os.makedirs(newdir)
        except FileExistsError:
            pass
    with open(newfn, "w", encoding="utf8") as fp:
        with open(fn, encoding="utf8") as fpin:
            linenum = 0
            lines = fpin.readlines()
            while linenum < len(lines):
                line = lines[linenum].strip()
                if linenum < 15:
                    fp.write(f"{line}\n")
                    linenum += 1
                    continue
                tokens = line.split()
                if len(tokens) < 3:
                    fp.write(f"{line}\n")
                    linenum += 1
                    continue
                breakpoints = int(tokens[3])
                if breakpoints == 0:
                    fp.write(f"{line}\n")
                    linenum += 1
                    continue
                times = []
                accum = []
                for _ in range(breakpoints):
                    linenum += 1
                    tokens = lines[linenum].split()
                    times.append(float(tokens[0]))
                    accum.append(float(tokens[1]))
                if conserve_total:
                    times = conservative_adjust(times, accum, multiplier)
                else:
                    accum = [x * multiplier for x in accum]
                fp.write(f"{line}\n")
                for i in range(breakpoints):
                    fp.write(f"{times[i]:.4f} {accum[i]:.2f}\n")
                linenum += 1


def finder(scenario, multiplier, conserve_total):
    """yield what we can find."""
    res = []
    for dirname, _dirpath, filenames in os.walk("/i/0/cli"):
        for fn in filenames:
            res.append(
                [f"{dirname}/{fn}", scenario, multiplier, conserve_total]
            )
    return res


def main(argv):
    """Go Main Go."""
    scenario = int(argv[1])
    if scenario == 0:
        print("NO!")
        return
    multiplier = float(argv[2])
    conserve_total = argv[3].lower() == "y"
    queue = finder(scenario, multiplier, conserve_total)
    print(f"Applying {multiplier:.2f} multiplier for scenario {scenario}")
    with ThreadPool() as pool:
        for _ in tqdm(pool.imap_unordered(editor, queue), total=len(queue)):
            pass


if __name__ == "__main__":
    main(sys.argv)


def test_conservative_adjust():
    """Test conservative adjust."""
    times = [0, 1, 2]
    accum = [1, 30, 40]
    newtimes = conservative_adjust(times, accum, 0.6)
    assert abs(newtimes[1] - 1.666) < 0.001
    newtimes = conservative_adjust(times, accum, 1.4)
    assert abs(newtimes[1] - 0.714) < 0.001


def test_endofday_bug():
    """Found this bug with actual values."""
    times = [0.53, 0.80, 23.76, 23.86, 23.96, 23.98]
    accum = [0, 2.37, 4.59, 6.75, 8.92, 9.64]
    newtimes = conservative_adjust(times, accum, 0.8)
    assert (newtimes[-1] - newtimes[-2]) > 0.001


def test_endofday_bug2():
    """Found another edge case."""
    times = [16.8, 17.56, 19.06, 21.63, 22.63, 22.90, 23.06, 23.10]
    accum = [0, 2.03, 4.22, 6.44, 8.47, 10.73, 13.3, 14.0]
    newtimes = conservative_adjust(times, accum, 0.8)
    assert (newtimes[-1] - newtimes[-2]) > 0.001
