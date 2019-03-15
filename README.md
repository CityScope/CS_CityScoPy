# CityScoPy

## Scanning and Networking Module for MIT CityScope Project in Python

This tool is for capturing, key-stoning, scanning and sending uniquely tagged arrays of 2-dimension physical Lego bricks. CityScope Scanner will detect colors in arrays of 2d-pixel arrays. Than, these color arrays will be compared to list of `tags` attribute of a given `json` file located in `data` folder. At last, the tool will return a list of `type` and `rotation` for each of the scanned arrays. This list is then converted to cityIO acceptable JSON format and can be sent uding POST request.

## Quick-Run

- From terminal, run the tool using `$ run.py`
- Tool will start scanning using whatever keystone data was stored in `scanner/data`
- make corrections to the key stone using the sliders. Press `s` to save change to file and `ctrl-c` twice [in the terminal window] to exit program

Note: Running the tool in this way will involve some fail safe mechanisms that will auto-restart the tool when it crashes [such as camera disconnect, slider failure or networking issue]

## Setup and Calibration On First Time Usage | Full Setup

- get python 3.4 and above, clone this repo, install relevant libs [see main.py]
- tweek `DATA/cityio.json` to fit your cityIO table setup [read https://github.com/CityScope/CS_CityIO_Backend/wiki to understand cityIO data structure]
- Run with `$ python[3] main.py`. 
- Tool will start scanning using the key stone data created with`keystone.py`
- make corrections to the key stone using the sliders. Press `s` to save changes to file and `ctrl-c` to close program

### options in `cityio.json` , `objects` field
  - `gui` 0 or 1 -- turn on or of webcam display
  - `interval` 0 to inf -- send rate to UDP/HTTP in ms
- `cityio` 0 or 1 -- send to UDP [0] or HTTP cityIO[1]
- `tags` ["1000000100000000"] -- 16 digit strings, repesenting of the types of being scanned  

## Optional
- Run `keystone` with: `$ python[3] keystone.py`
- the tool will start, assuming a webcam is connected and working
- Select 4 corners [up right, up left, bottom right, bottom left, at this order] of keystone region
  Note: no need to exactly select the corners, as these are only initial guides for `scanner` tool
- `keystone.py` will create `keystone.txt` and close

## License

Please see `LICENSE` file for more details.This tool may require libraries which are subject to own licensing.

## Contribution

Please use GitHub Issues and PR interface for contributions.

---

Maintained by [Ariel Noyman](http://arielnoyman.com)

[Repo contributors](https://github.com/CityScope/CS_Scanner_Python/graphs/contributors)
