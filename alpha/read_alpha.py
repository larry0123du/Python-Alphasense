# Description: This Python script retrieves data from four Alphasense gas sensors
# Author: Ruihang Du
# Email: du113@purdue.edu

import Adafruit_ADS1x15 as ads
import time
import datetime
import pytz
import threading
import argparse

# define gain as default
# define timeframe as 30 seconds (reference to https://github.com/waagsociety/making-sensor
# ISB serial number: 202311221
# define necessary parameters for calculation
GAIN = 1
TIMEFRAME = 60

TZ = pytz.timezone("America/New_York")

sensors = {'o3':{'sn':'204290854', \
        'addr':0x48, \
        'we_e':231, \
        'we_t':230, \
        'aux_e':235, \
        'aux_t':234, \
        'sens_e':235, \
        'sens_t':0.326}, \
        'no2':{'sn':'202311221', \
        'addr':0x49, \
        'we_e':245, \
        'we_t':236, \
        'aux_e':248, \
        'aux_t':244, \
        'sens_e':-393, \
        'sens_t':0.287}, \
        'no':{'sn':'160290019', \
        'addr':0x4a, \
        'we_e':286, \
        'we_t':349, \
        'aux_e':272, \
        'aux_t':358, \
        'sens_e':648, \
        'sens_t':0.518}, \
        'co':{'sn':'162291519', \
        'addr':0x4b, \
        'we_e':330, \
        'we_t':331, \
        'aux_e':349, \
        'aux_t':347, \
        'sens_e':557, \
        'sens_t':0.446}}

ADS_TO_V = 4.096 / float(32767)


def get_data(name, dirname, info_dict):
    s = Sensor(name, dirname, info_dict['addr'], info_dict['we_e'], \
            info_dict['we_t'], info_dict['aux_e'], info_dict['aux_t'], \
            info_dict['sens_e'], info_dict['sens_t'])
    s.read_data()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('destdir', help='The destination directory to which the data should be stored')
    args = parser.parse_args()
    dirname = args.destdir

    thread_list = []
    for key in sensors.keys():
        t = threading.Thread(target=get_data, args=(key, dirname, sensors[key]))
        thread_list.append(t)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
#     for key in sensors.keys():
#         get_data(key, sensors[key])

# create an ADS1115 instance
# adc = ads.ADS1115()

class Sensor:
    def __init__(self, stype, dirname, addr, we_e, we_t, \
            aux_e, aux_t, sens_e, sens_t):
        self.stype = stype
        self.adc = ads.ADS1115(address=addr)
        self.we_e = we_e
        self.we_t = we_t
        self.aux_e = aux_e
        self.aux_t = aux_t
        self.sens_e = sens_e
        self.sens_t = sens_t
    def read_data(self):
        accu_read_1 = 0
        accu_read_2 = 0
        # counter for 30 samples
        counter = 0

        f = open(dirname+self.stype+"_conc.csv", "a+")
        # variables: t
        if f.readlines() == []:
            f.write("timestamp,{}\n".format(self.stype))

        try:
            while True:
                lc_time = datetime.datetime.now()
                lc_dt = TZ.localize(lc_time, is_dst=None)

                accu_read_1 += self.adc.read_adc_difference(0, gain=GAIN) 
                accu_read_2 += self.adc.read_adc_difference(3, gain=GAIN)

                if counter != 0 and counter % TIMEFRAME == 0:
                    conc = self.calc_conc(float(accu_read_1) \
                            / TIMEFRAME, float(accu_read_2) / TIMEFRAME)
                    f.write("{},{}\n".format(lc_dt.isoformat(),conc))
                    f.flush()

                    accu_read_1 = 0
                    accu_read_2 = 0
                counter += 1
                time.sleep(5)
        except Exception as e:
            f.close()

    def calc_conc(self, read_1, read_2):
        we_u = read_1 * ADS_TO_V
        ae_u = read_2 * ADS_TO_V

        if self.stype == "o3":
            # equation 3
            return (we_u - ae_u) / self.sens_t
        elif self.stype == "no2":
            # equation 1
            return (we_u - 0.6 * ae_u) / self.sens_t
        elif self.stype == "no":
            # equation 2
            return (we_u - (63.0 / 86.0) * ae_u) / self.sens_t
        elif self.stype == "co":
            # equation 1
            return (we_u - 3.0 * ae_u) / self.sens_t


if __name__ == "__main__":
    main()
