#!/usr/bin/python
import subprocess
import os
import sys
import argparse
import shutil
import shlex
try:
	import simplejson as json
except ImportError:
	import json

outdir = '.'
indir = '.'
sort = False
cleanup = False
coedc_aac = None

# Get arguments and flags
parser =  argparse.ArgumentParser()
parser.add_argument("-o", "--outdir", help="Specify output directory (default is ./)")
parser.add_argument("-i", "--indir", help="Specify input directory (default is ./)")
parser.add_argument("-c", "--cleanup", help="Turn cleanup mode on (deletes original files)", action="store_true")
parser.add_argument("-s", "--sort", help="Sort mode. Moves existing compliant files to OUTDIR (Must be used with -o/--oudir)", action="store_true")
args = parser.parse_args()

if args.sort and args.outdir:
	sort = True
	print "Sort mode on. Moving compliant files to: " + outdir
elif args.sort and not args.outdir:
	sys.exit("Invalid option. Sort mode requires OUTDIR to be set")

if args.indir:
	indir = args.indir
else:
	print "No input directory specified. Using " + os.getcwd()

if args.outdir:
	outdir = args.outdir
else:
	print "No output directory specified. Using " + os.getcwd()

if args.cleanup:
	cleanup = True
	print "Cleanup mode on"

#Class for multi-level dicts
class nd(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, nd())

# Check for ffmpeg and get compile-time flags for codec availability.
def getffmpeg():
	try:
		v=subprocess.check_output(["ffmpeg","-version"])
		try:
			v.index('--enable-libfdk-aac')
			codec_aac = "libfdk_aac -vbr 4 -ac 2" # Indicates presence of libfdk_aac. Highest quality encoder - preferred.
		except ValueError:
			try:
				v.index('--enable-libfaac')
			except ValueError:
				codec_aac = "libfaac -ac 2" # Indicates presence of libfaac. Proceed with FAAC.
			codec_aac = "aac -strict experimental -b:a 160 -ac 2" # Indicates absence of libfdk_aac or libfaac. Proceed with native aac encoder (poor quality).
	except OSError:
		sys.exit("FFmpeg not found. Please check PATH and/or install FFmpeg.")
	return codec_aac

# Transcoding/Remuxing function
def transmux(file,streams):
	print file + " is entering the transmuxer"
	astream = None
	mode = None
	out = file[:-4]
	acodec = getffmpeg()
	if acodec != 1:
		for aud in streams['Audio']:
			if streams['Audio'][aud] == 'aac' and streams['AC'][aud] == 2:
				astream = "-c:a:" + str(aud)
				acodec = "copy"
			else:
				astream = "-c:a"

		command = "ffmpeg -i '" + indir + "/" + file + "' -c:v copy " + astream + " " + acodec + " '" + outdir + "/" + out + ".mp4'"
		subprocess.call(shlex.split(command))

	else:
		pass

	if cleanup == True:
		os.remove(file)
	else:
		pass

# Filter ffprobe output into a friendlier format
def getstreams(info):
	i=int(0)
	streams = nd()
	while i != None:
		try:
			if info['streams'][i]['codec_type'] == 'video':
				streams['Video'][i] = info['streams'][i]['codec_name']
			elif info['streams'][i]['codec_type'] == 'audio':
				streams['Audio'][i] = info['streams'][i]['codec_name']
				streams['AC'][i] = info['streams'][i]['channels']
			else:
				try: streams['Misc'][i] = info['streams'][i]['codec_name']
				except KeyError: pass
		except IndexError:
			break
		i+=1
	return streams

# Loops through all files in dir and performs appropriate function
DEVNULL = open(os.devnull, 'wb')
for file in os.listdir(indir):
	if file.endswith(".m4v") or file.endswith(".mp4") or file.endswith(".mkv"):
		raw=subprocess.check_output(["ffprobe", "-print_format", "json", "-show_streams", indir+"/"+file], stderr=DEVNULL)
		info=json.loads(raw)
		streams=getstreams(info)
		if streams != {'AC': {1: 2}, 'Audio': {1: u'aac'}, 'Video': {0: u'h264'}}:
			for vid in streams['Video']:
				if streams['Video'][vid] == 'h264':
					transmux(file,streams)
				else:
					print "video must be converted"
		else:
			print file + " is properly formatted"
			if sort == True:
				shutil.move(file, outdir)
			else:
				pass
	else:
		print "Unsupported file type " + os.path.splitext(file)[1]
