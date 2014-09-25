# kinect-2-snap

A re-implementation of [Kinect2Scratch](http://scratch.saorog.com/) for the online 
version of [Snap/BYOB/Scratch](http://snap.berkeley.edu/).

`kinect-2-snap` comes with two separate pieces -- a server that you need to 
run on your local machine, and a XML file that you need to import into the online 
version of BYOB. You will need to set up both in order to use this project.

Note: this project is currently still under active development and may still contain
bugs or missing features.

## Setting up 

### Prerequisites

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

### Running the server

1.  Download and extract the latest release from 
    [https://github.com/Michael0x2a/kinect-2-snap/releases](https://github.com/Michael0x2a/kinect-2-snap/releases)
2.  Navigate to the `kinect_server` folder.
3.  Double-click on "kinect_server.exe"
4.  You can verify that the server is running by navigating to 
    `http://localhost:5000/demo` in your web browser, and standing in front of 
    the Kinect.

### Importing the XML File 

1.  Open the online Snap editor (located at 
    [http://snap.berkeley.edu/](http://snap.berkeley.edu/))
2.  Click the icon on the upper-left of the page, then click "import".
3.  Navigate to the `block_definitions' folder and select `kinect.xml` to import it.
4.  The commands you need will now be placed under the "Sensing" category.

### Running the server from source (optional)

To run the server directly from the source code, you'll need to:

1.  Clone this repo:

        git clone https://github.com/Michael0x2a/kinect-2-snap.git

2.  Install `flask`, `flask-cors`, and `pykinect`. If you have `pip` installed, 
    you can simply run the following commands from the command line:
    
        pip install flask
        pip install flask-cors
        pip install pykinect 
        
3.  Navigate into the `kinect_server` folder and run `python server.py`.
    You can then access `localhost:5000` to retrieve data.
    
    
## Troubleshooting

If the Kinect server fails for any reason, here are some things you can try.

-   **Make sure the Kinect is set up correctly.**

    The Kinect should be plugged into the power outlet and be plugged into your 
    computer via USB. A green light should be shining on the Kinect.
    
-   **Make sure you've installed the correct SDKs**
    
    If you own Kinect for Windows, you must install "MS Kinect Runtime v1.8". If 
    you own Kinect for Windows, you must install "MS Kinect SDK v1.8". If you're 
    not certain which one you own, install both.
    
    Do _not_ install the 2.0 SDK.
    
-   **Unplug any other USB devices**

    Unplug anything hooked up to your computer via USB, except for the Kinect, and 
    try again.
    
-   **Wait a few seconds, and retry**
    
    If you've just plugged the Kinect in, then it'll take a few seconds for it to
    be ready. If the server fails for no apparent reason, then try again one or two
    times.
    
-   **Unplug the Kinect, and reconnect it**

    Sometimes, unplugging the Kinect from your computer and plugging it back in will
    resolve any bizarre issues.
    
-   **Email me**

    michael.lee.0x2a@gmail.com 

## API Reference 

The Kinect server is accessible at `localhost:5000` and provides the following 
endpoints. Currently, if you call the endpoints as-is, the data will be returned 
in a format that's designed to be easy for BYOB/Snap to parse. More information 
about this data format will follow below.

If you add the query parameter `?format=json` to the end of the string, then the 
data will be returned in JSON format.

-   **`localhost:5000`**

    Returns all skeletal data from the Kinect.
    
-   **`localhost:5000/demo`**

    Displays skeletal data on the screen. Requires Javascript.
    
-   **`localhost:5000/num_tracked`**
    
    Returns the number of skeletons currently being tracked. Typically ranges 
    from 0 to 2.
    
-   **`localhost:5000/skeletons`**
    
    Returns data for all skeletons being tracked.
    
-   **`localhost:5000/skeletons/<num>`**

    Returns data for that particular skeleton. Valid values are `1` or `2`.

-   **`localhost:5000/skeletons/<num>/<joint>`**

    Returns data for that particular joint for that particular skeleton. Valid 
    values are:
    
    -   FootLeft
    -   FootRight
    -   AnkleLeft
    -   AnkleRight
    -   KneeLeft
    -   KneeRight
    -   HipCenter
    -   HipLeft
    -   HipRight
    -   Spine
    -   HandLeft
    -   HandRight
    -   WristLeft
    -   WristRight
    -   ElbowLeft
    -   ElbowRight
    -   ShoulderCenter
    -   ShoulderLeft
    -   ShoulderRight
    -   Head
    
    The match is case insensitive, and will ignore any dashes and underscores. For 
    example, the following queries will behave identically:
    
        http://localhost:5000/skeletons/1/AnkleLeft
        http://localhost:5000/skeletons/1/ankleleft
        http://localhost:5000/skeletons/1/ankle_left
        http://localhost:5000/skeletons/1/a-n-k-l-e_l-e-f-t
        
-   **`localhost:5000/skeletons/<num>/<joint>/<coord>`**

    Returns the value of that particular axis on the joint. Valid values are X, Y, 
    Z, and W. The X coordinate will range from about -240 to 240, and the Y coordinate 
    will range from about -180 to 180. The Z coordinate is the distance of the 
    joint from the Kinect camera in millimeters. The W coordinate is returned unchanged 
    from the Kinect SDK.
  
  
### Data Return Format

When calling an endpoint to get skeletal data, the data will be returned with the x, y, z, 
and w coordinates of each joint separated by a space, and each joint separated by a 
newline. The joints will always be provided in the following format:

1.  FootLeft
2.  FootRight
3.  AnkleLeft
4.  AnkleRight
5.  KneeLeft
6.  KneeRight
7.  HipCenter
8.  HipLeft
9.  HipRight
10. Spine
11. HandLeft
12. HandRight
13. WristLeft
14. WristRight
15. ElbowLeft
16. ElbowRight
17. ShoulderCenter
18. ShoulderLeft
19. ShoulderRight
20. Head