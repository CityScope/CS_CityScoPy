# CityScope Scanner and Networker

### for Cooper Hewitt, Smithsonian Design Museum “The Road Ahead: Reimagining Mobility” exhibition Dec. 14 through March 31, 2019

#### [Python, openCV, NumPy]

## What is it good for?

This is a tool for capturing, key-stoning, scanning and sending uniquely tagged arrays of 2-dimension physical colored bricks. As well this tool networks the slider, scanner, projection and simulation tools. CityScope Scanner will detect colors in arrays of 2d-pixel arrays at sizes of 3x3. Than, these color arrays will be compared to `tags` attribute of a given `json` file [should be located in `data` folder]. At last, the tool will return a list of `type` and `rotation` for each of the scanned arrays. This list can be sent over UDP for visualizing.

## Running Regularly / Quick-Run

- Clone this repo, start Terminal at the project's folder
- Run using `$ ./run`
- Tool will start scanning using whatever keystone data was stored in `scanner/data`
- make corrections to the key stone using the sliders. Press `s` to save change to file and `ctrl-c` twice [in the terminal window] to exit program

Note: Running the tool in this way will involve some fail safe mechanisms that will auto-restart the tool when it crashes [such as camera disconnect, slider failure or networking issue]

## Setup and Calibration On First Time Usage / Full Setup

- get python 3.4 and above, clone this repo
- Install packages manually or using `pip` via `pip install -r requirements.txt`
- Run `keystone` with: `$ python3 keystone.py`
- the tool will start, assuming a webcam is connected and working
- Select 4 corners [up right, up left, bottom right, bottom left, at this order] of keystone region
  Note: no need to exactly select the corners, as these are only initial guides for `scanner` tool
- `keystone.py` will create `keystone.txt` and close

![-](scanner/IMG/keystone.gif "keystone")

- Run `scanner` with `$ python3 scanner.py`. Tool will start scanning using the key stone data created with`keystone.py`
- make corrections to the key stone using the sliders. Press `s` to save changes to file and `ctrl-c` to close program

![-](scanner/IMG/scanner.gif "keystone")

## Scan results [With slider]:

```
{"grid":[[-1, -1], [1, 0], [16, 3], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [2, 2], [-1, -1], [-1, -1], [-1, -1], [-1, -1]],"slider":[0.451]}
```

## Optional

- Use `udp_listener.py` to emulate UDP server listener and test received string

## Troubleshoot

If you encounter any issue with the tool, please cite the error appearing in the terminal window and send it to @RELNO
