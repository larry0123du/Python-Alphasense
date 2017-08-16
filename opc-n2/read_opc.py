# Description: This script retrieves PM size distribution data from Alphasense OPC-N2 via SPI communication
# Author: Ruihang Du
# Email: du113@purdue.edu

import usbiss
import opc
import time
import datetime
import pytz
import re
import pprint
import os
import numpy as np
import argparse

#import datetime
#import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('destfile', help='the destination file the data should be stored in')
args = parser.parse_args()
filename = args.destfile

spi = usbiss.USBISS("/dev/ttyACM0", "spi", spi_mode = 2, freq = 500000)
e = 1

while e != None:
    try:
        print "Try connecting to OPC-N2"
        e = None
        alpha = opc.OPCN2(spi)
    except Exception as e:
        time.sleep(5)

config = alpha.config()

# Specify the timezone of current location
lc_tz = pytz.timezone("America/New_York")
bins = ["timestamp", "0.38"]


for i in range(15):
    bins.append(str(alpha.lookup_bin_boundary(config["Bin Boundary {}".format(i)])))

bins += ["pm1", "pm2.5", "pm10", "flow rate"]
#df = pd.DataFrame(columns=bins)

path = "/mnt/data/opcn2.csv"
# path = "opcn2.csv"
if os.path.exists(path):
    f = open(path, "a+")
    if f.readlines == []:
        f.write(",".join(bins)+"\n")
        f.flush()
else:
    f = open(path, 'a')
    f.write(",".join(bins)+"\n")
    f.flush()
        
data_buffer = []
#with open("opcn2.csv", "ab") as f2:
try:
    while True:
        #start = time.time()
        loc_time = datetime.datetime.now() #.strftime("%Y-%m-%dT%H:%M:%S")
        #convert local time to UTC
        local_dt = lc_tz.localize(loc_time, is_dst=None)
        #utc_time = local_dt.astimezone(pytz.utc)
        row = [local_dt.isoformat()]

        for i in range(3000):
            data_line = []
            data = alpha.histogram()
            for j in range(16):
                data_line.append(data["Bin {}".format(j)])
            data_line += [data["PM1"],data["PM2.5"],data["PM10"],data["SFR"]]
            data_buffer.append(data_line)

        data_buffer = np.mean(np.array(data_buffer), axis=0)

        row += list(data_buffer.astype('|S7'))
        f.writelines(",".join(row)+"\n")
        f.flush()
        data_buffer = []
        #print "time span:", time.time() - start
        # time.sleep(10)
except Exception as e:
    print str(e)
    f.close()
