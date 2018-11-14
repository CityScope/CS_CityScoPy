# CityScope Scanner

#### [Python, openCV, NumPy]

A tool for capturing, key-stoning, scanning and sending uniquely tagged arrays of 2-dimension physical colored bricks. Used by MIT CityScope project.

## What is it good for?

CityScope Scanner will detect the color [black or white, other might be added in `modules`] of arrays of 2d-pixel arrays [at sizes of 3x3, 2x2 or 4x4] Than, these color arrays will be compared to `tags` attribute of a given `json` file [should be located in `data` folder]. At last, the tool will return a list of `type` and `rotation` for each of the scanned arrays. This list can be sent over UDP for visualizing.

## Setup and Calibration On First Time Usage

- get python ver. 3, clone this repo
- Install packages manually or using `pip` via `pip install -r requirements.txt`
- Run `keystone` with: `$ python3 keystone.py`
- the tool will start assuming a webcam is connected and working
- Select 4 corners [up right, up left, bottom right, bottom left, at this order] of keystone region
  Note: no need to exactly select the corners, as these are only initial guides for `scanner` tool

![-](IMG/keystone.gif "keystone")

- `keystone.py` will create `keystone.txt` and close
- Run `scanner` with `$ python3 scanner.py`. Tool will start scanning using the key stone data created with`keystone.py`
- make corrections to the key stone using the sliders. Press `s` to save changes to file and `q` to exit the scanner loop or `ctrl-c` to fully close program

![-](IMG/scanner.gif "keystone")

## Running Regularly

- Open Terminal in the app folder
- Run `$ ./run`
- Tool will start scanning using the key stone data created with`keystone.py` or with iterations made on previous run
- make corrections to the key stone using the sliders. Press `s` to save change to file and `q` to exit program

## Optional

- Use `udp_listener.py` to emulate UDP server listener
- Tweak UDP endpoints or scanned colors under `modules.py`

---

# Specific for CH project

clone submodule current state [i.e, last time it was updated in parent] into its folder at parent repo:

`git submodule update --init --recursive Scanner`

Then, update submodule to last commit of origin:

`$ cd Scanner`

`$ git checkout master`

[if this is the desired commit]
