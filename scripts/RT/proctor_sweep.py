"""Proctor script for running the SWEEP model.

See dailyerosion/dep#36 for generally more details.

I looked at the measured data again, and realized that a better date would
be June 1 or June 2, 2018; or potentially June 10, 2018.

The lat-long for the site is:
Latitude: 46.78
Longitude: -100.95

Output fields (kg/m2)
-------------
  - total soil loss
  - saltation/creep soil loss
  - suspended soil loss
  - PM10 soil loss
  - PM2.5 soil loss
"""
import argparse
import sys
import datetime
import os
import shutil
import subprocess
from multiprocessing import Pool

from pyiem.dep import man2df, read_man
from pyiem.util import get_sqlalchemy_conn, logger
import pandas as pd
import requests
from tqdm import tqdm

HUC12S = ["090201081101", "090201081102", "090201060605"]
LOG = logger()
IEMRE = "http://mesonet.agron.iastate.edu/iemre/hourly"


def run_command(cmd: str) -> bool:
    """Common command running logic."""
    with subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        (stdout, stderr) = proc.communicate()
        if proc.returncode != 0:
            LOG.error(
                "Command %s failed with %s\n%s",
                cmd,
                stdout.decode("utf-8"),
                stderr.decode("utf-8"),
            )
            return False
    return True


def get_wind_obs(date, lon, lat):
    """Get what we need from IEMRE."""
    uri = f"{IEMRE}/{date:%Y-%m-%d}/{lat:.2f}/{lon:.2f}/json"
    try:
        res = requests.get(uri).json()
    except Exception as exp:
        print(uri)
        LOG.exception(exp)
        sys.exit()
    hourly = []
    for entry in res["data"]:
        try:
            vel = (entry["uwnd_mps"] ** 2 + entry["vwnd_mps"] ** 2) ** 0.5
        except Exception:
            vel = 1.0
        hourly.append(vel)
    for _i in range(len(hourly), 24):
        hourly.append(1.0)
    return hourly


def compute_crop(manfn: str, year: int) -> str:
    """Compute the crop code used for magic.R in sweep workflow."""
    try:
        mandf = man2df(read_man(manfn), 2007)
    except Exception as exp:
        LOG.info("%s generated %s", manfn, exp)
        return "0"
    cropname = (
        mandf.query(f"year == {year} and ofe == 1")
        .iloc[0]["crop_name"]
        .lower()
    )
    cropcode = "0"
    if cropname.startswith("Cor"):
        cropcode = "C"
    elif cropname.startswith("Soy"):
        cropcode = "B"
    return cropcode


def workflow(arg):
    """Do what we need to do."""
    (idx, row) = arg
    # 1. Replace wind information in each sweepin file
    sweepinfn = (
        f"/i/{row['scenario']}/sweepin/{row['huc_12'][:8]}/"
        f"{row['huc_12'][8:12]}/{row['huc_12']}_{row['fpath']}.sweepin"
    )
    cropcode = compute_crop(
        sweepinfn.replace("sweepin", "man"),
        row["date"].year,
    )
    # Compute the management df to get the crop code needed for downstream
    if not os.path.isfile(sweepinfn):
        LOG.warning("%s does not exist, copying template", sweepinfn)
        shutil.copyfile("sweepin_template.txt", sweepinfn)
    sweepoutfn = sweepinfn.replace("sweepin", "sweepout")
    # sweep arbitarily sets the erod output file to be the same as the
    # sweepin, but with a erod extension.
    erodfn = sweepinfn.replace(".sweepin", ".erod")
    windobs = get_wind_obs(row["date"], row["lon"], row["lat"])
    with open(sweepinfn, "r", encoding="utf-8") as fh:
        lines = list(fh.readlines())
    found = False
    for linenum, line in enumerate(lines):
        if not found and line.find(" awu(i)") > -1:
            found = True
            continue
        if found and not line.startswith("#"):
            for i in range(4):
                sl = slice(i * 6, (i + 1) * 6)
                lines[linenum + i] = (
                    " ".join([str(round(x, 2)) for x in windobs[sl]]) + "\n"
                )
            break
    with open(sweepinfn, "w", encoding="utf-8") as fh:
        fh.write("".join(lines))
    # 2. Run Rscript to replace grph file content
    cmd = (
        f"Rscript --vanilla magic.R {sweepinfn} "
        f"{sweepinfn.replace('sweepin', 'grph')} "
        f"{sweepinfn.replace('sweepin', 'sol')} {row['date'].year} "
        f"{row['date']:%j} {cropcode}"
    )
    if not run_command(cmd):
        return None, None
    # 3. Run sweep with given sweepin file, writing to sweepout
    cmd = f'~/bin/sweep -i"{sweepinfn}" -Erod'
    if not run_command(cmd):
        return None, None
    # Move the erod file into the sweepout directory
    shutil.move(erodfn, sweepoutfn)
    # 4. Harvest the result and profit.
    erosion = None
    with open(sweepoutfn, encoding="utf-8") as fh:
        tokens = fh.read().strip().split()
        # total soil loss, saltation loss, suspension loss, PM10 loss
        # TODO: units
        erosion = float(tokens[0])
    return idx, erosion


def usage():
    """Create the argparse instance."""
    parser = argparse.ArgumentParser("Send WEPP env info to the database")
    parser.add_argument("-s", "--scenario", required=True, type=int)
    parser.add_argument("-d", "--date", required=True)
    return parser


def main(argv):
    """Go Main Go."""
    parser = usage()
    args = parser.parse_args(argv[1:])
    with get_sqlalchemy_conn("idep") as conn:
        df = pd.read_sql(
            """
            SELECT huc_12, fpath, scenario,
            ST_x(ST_Transform(ST_PointN(geom, 1), 4326)) as lon,
            ST_y(ST_Transform(ST_PointN(geom, 1), 4326)) as lat
            from flowpaths where scenario = %s
            and huc_12 in %s
        """,
            conn,
            params=(args.scenario, tuple(HUC12S)),
            index_col=None,
        )
    date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
    df["date"] = pd.Timestamp(date)
    df["erosion"] = -1
    LOG.info("found %s flowpaths to run for %s", len(df.index), date)
    jobs = list(df.iterrows())
    with Pool() as pool:
        progress = tqdm(
            pool.imap_unordered(workflow, jobs),
            total=len(df.index),
            disable=not sys.stdout.isatty(),
        )
        for idx, erosion in progress:
            if erosion is None:
                break
            df.at[idx, "erosion"] = erosion

    print(df[["huc_12", "erosion"]].groupby("huc_12").describe())


if __name__ == "__main__":
    main(sys.argv)
