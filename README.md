# kinect-byob-online

A re-implementation of Kinect2Scratch for the online version of BYOB.

kinect-byob-online comes with two separate pieces -- a server that you need to 
run on your local machine, and a XML file that you need to import into the online 
version of BYOB.

# Setting up the server 

## Pre-requisites

1.  You need either a Windows 7 or Windows 8 PC (preferably a fast one).
2.  Download the correct drivers:
    a.  If you own "Kinect for Windows", download and install the MS Kinect 
        Runtime v1.8
    b.  If you own "Kinect for Xbox", download and install the MS Kinect SDK v1.8
3.  Setup your Kinect
    a.  You must own a powered Kinect -- one with its own electricity plug.
    b.  Plug the kinect 
    c.  Plug the USB lead on the Kinect into your PC. If you have other USB devices 
        plugged in, you may need to remove them.

## Running the server (exe)

Simply double-click "server.exe" inside the `exe` folder.

## Running the server (from source)

To run the server directly from the source code, you'll need to:

1.  Install `flask`, `flask-cors`, and `pykinect`. If you have `pip` installed, 
    you can simply run the following commands from the command line:
    
        pip install flask
        pip install flask-cors
        pip install pykinect 
        
2.  Navigate into the `kinect-byob-online` folder and run `python server.py`.
    You can then access `localhost:5000` to retrieve data 
    
# Setting up BYBO

1.  Open the online version of BYOB
2.  Click the icon on the upper-left of the page, then click "import".
3.  Navigate to the `block-definitions' folder and select `kinect.xml` to import it.
4.  The commands you need will now be placed under the "Sensing" category.

    