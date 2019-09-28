# CityScoPy

### [=> Download latest release here <=](https://github.com/CityScope/CS_Scanner_Python/releases/)

## Table Initiation, Scanning & Networking Module for MIT CityScope Project in Python

CityScoPy is a tool for initiating a CityScope instance for any arbitrary geolocated area in the world. CityScoPy can create a GeoJSON grid, capture, key-stone, scan and send uniquely tagged arrays of 2-dimension physical bricks. This is a key component of the MIT CityScope platform for interaction.

---

## Usage

- install python 3.4^, clone this repo, install packages.
- tweak `__settings__.json` to fit your cityIO table setup. Read [cityIO documentation](https://github.com/cityscope/cs_cityio_backend/wiki) for proper data structure
- setup a path to your settings file

```
cityscopy_settings_path = "__path__/__settings__.json"
```

- initiate the `Cityscopy` class

```
cityscopy = Cityscopy(cityscopy_settings_path)
```

- use one or more of the main methods

| Method                     | Usage                                 | Blocking? |
| -------------------------- | ------------------------------------- | --------- |
| `cityscopy.keystone()`     | initial keystone and save to file     | x         |
| `cityscopy.gridMaker()`    | make GeoJSON grids and sent to CityIO |           |
| `cityscopy.scan()`         | main scanning and sending method      | x         |
| `cityscopy.udp_listener()` | emulate local UDP server listener     | x         |

- in terminal run the tool using `$ run.py`

---

## Class methods

### `Cityscopy.keystone()`

##### Initial keystone and save to file

- the tool will start given a cam is connected and working
- Select 4 corners [up right, up left, bottom right, bottom left, at this order] of keystone region
  Note: no need to exactly select the corners, as these are only initial guides for `scanner` method
- `keystone.txt` and close

### `Cityscopy.gridMaker()`

##### make GeoJSON grids and sent to CityIO

### `Cityscopy.scan()`

##### main scanning and sending method

Scanner will detect colors in arrays of 2d-pixel arrays. Than, these color arrays will be compared to list of `tags` attribute of a given `__settings__.json` file. Then the tool will return a list of `type` and `rotation` for each of the scanned arrays. This list is then converted to cityIO acceptable JSON format and can be sent using POST request.

##### options in `__settings__.json`

- `gui` turn on or of webcam display
- `interval` send rate to UDP/HTTP in ms
- `cityio` send to UDP or HTTP cityIO
- `tags` 16 digit strings of types being scanned [`1000000100000000`]

Tool will start scanning using whatever keystone data was stored in `keystone.txt`
make corrections to the key stone using the sliders or keyboard using `1,2,3,4` to select a corner and `[w,a,s,d]` to move `[up,left,down,right]` the selected corner. Press `k` to save change to file and `ctrl-c` twice [in the terminal window] to exit program

### `Cityscopy.udp_listener()`

##### emulates local UDP server listener

---

## License

Please see `LICENSE` file for more details.This tool may require libraries which are subject to own licensing.

## Contribution

Please use GitHub Issues and PR interface for contributions.

---

Maintained by [Ariel Noyman](http://arielnoyman.com)

[Repo contributors](https://github.com/CityScope/CS_Scanner_Python/graphs/contributors)
