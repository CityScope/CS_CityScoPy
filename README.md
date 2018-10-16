# CityScope Scanner

#### [Python, openCV]

A tool for capturing, key-stoning, scanning and sending uniquely tagged arrays of 2-dimension physical colored bricks. Used by MIT CityScope project.

## Setup and First Time Usage

- get python ver. 3, clone this repo
- Install packages manually or using `pip` via `pip install -r requirements.txt`
- Run `keystone` with: `$ python3 keystone.py`
- the tool will start assuming a webcam is connected and working
- Select 4 corners [up left, up right, bottom left, bottom right, at this order] of keystone region
  Note: no need to exactly select the corners, as these are only initial guides for `scanner` tool

![-](IMG/keystone.gif "keystone")

- `keystone.py` will create `keystone.txt` and close
- Run `scanner` with `$ python3 scanner.py`. Tool will start scanning using the key stone data created with`keystone.py`
- make corrections to the key stone using the sliders. Press `s` to save changes to file and `q` to exit program

![-](IMG/scanner.gif "keystone")

## Running Regularly

- Run `scanner.py`. Tool will start scanning using the key stone data created with`keystone.py` or with iterations made on previous run
- make corrections to the key stone using the sliders. Press `s` to save change to file and `q` to exit program

## Optional

- Use `udp_listener.py` to emulate UDP server listener
- Tweak UDP endpoints or scanned colors under `modules.py`
- Scan multiple cameras/keystones areas using different `keystone.txt`, e.g: `keystone_cam_1.txt`, `keystone_cam_2.txt`

![-](IMG/multicam.png "multicam scanning and UDP")

## What is it good for?

- CityScope Scanner will detect the color [black or white, other might be added in `modules`] of arrays of 2d-pixel arrays [at sizes of 3x3, 2x2 or 4x4] Than, these color arrays will be compared to `tags` attribute of a given `json` file [should be located in `data` folder]. At last, the tool will return a list of `type` and `rotation` for each of the scanned arrays. This list can be sent over UDP for visualizing.
