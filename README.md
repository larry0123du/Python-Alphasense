# RasPyAlpha
Python scripts that retrieve data from Alphasense gas and OPC sensors

Setup for OPC:
* Go to opc-n2 directory
* Connect OPC to Raspberry Pi with a SPI-USB cable
* ~~~
  pip3 install py-opc
  ~~~
* Manually install py-usbiss
  * ~~~
    git clone https://github.com/DancingQuanta/pyusbiss.git
    cd pyusbiss
    python setup.py install
    ~~~
* Run the program: 
~~~
python read_opc.py DESTFILE
~~~
* opcn2.csv is a sample data file

Setup for Alphasense B-type sensors:
* Go to alpha directory
* Connect all sensors to Pi using ASD1115 Analog-to-Digital Converters
* Install ASD1115 python package
* Run the program: 
~~~
python read_alpha.py DESTDIR
~~~
* the csv files are sample data file
