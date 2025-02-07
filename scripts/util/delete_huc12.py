"""Delete all traces of a HUC12"""
import sys
import os
import glob

from pyiem.util import get_dbconn


def do_delete(huc12, scenario):
    """Delete all things."""
    pgconn = get_dbconn("idep")
    cursor = pgconn.cursor()

    # Remove any flowpath points
    cursor.execute(
        """
    delete from flowpath_points pts using flowpaths f where
    pts.flowpath = f.fid and f.huc_12 = %s and f.scenario = %s
    """,
        (huc12, scenario),
    )
    print("removed %s flowpath_points" % (cursor.rowcount,))

    # Remove any flowpaths
    cursor.execute(
        """
    DELETE from flowpaths where huc_12 = %s and scenario = %s
    """,
        (huc12, scenario),
    )
    print("removed %s flowpaths" % (cursor.rowcount,))

    # remove any results
    cursor.execute(
        """
    DELETE from results_by_huc12 where huc_12 = %s and scenario = %s
    """,
        (huc12, scenario),
    )
    print("removed %s results_by_huc12" % (cursor.rowcount,))

    # remove the huc12 from the baseline table
    cursor.execute(
        """
        DELETE from huc12 where huc_12 = %s and scenario = %s
    """,
        (huc12, scenario),
    )
    print("removed %s rows from huc12" % (cursor.rowcount,))

    # Remove some files
    for prefix in ["env", "error", "man", "prj", "run", "slp", "sol", "wb"]:
        dirname = "/i/%s/%s/%s/%s" % (scenario, prefix, huc12[:8], huc12[8:])
        if not os.path.isdir(dirname):
            continue
        os.chdir(dirname)
        files = glob.glob("*.*")
        for fn in files:
            os.unlink(fn)
        os.rmdir(dirname)
        print("Removed %s files from %s" % (len(files), dirname))

        # Try to remove the huc8 folder
        try:
            os.rmdir("/i/%s/%s/%s" % (scenario, prefix, huc12[:8]))
        except OSError:
            pass

    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    huc12 = argv[1]
    scenario = int(argv[2])
    do_delete(huc12, scenario)


if __name__ == "__main__":
    main(sys.argv)
