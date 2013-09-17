trans360
========

Python script to transcode and/or remux video files to a format playable on the xbox 360. Depends on MP4Box (GPAC) and ffmpeg

usage: trans360.py [-h] [-o OUTDIR] [-i INDIR] [-c] [-s] [-f]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        Specify output directory (default is ./)
  -i INDIR, --indir INDIR
                        Specify input directory (default is ./)
  -c, --cleanup         Turn cleanup mode on (deletes original files)
  -s, --sort            Sort mode. Moves existing compliant files to OUTDIR
                        (Must be used with -o/--oudir)

