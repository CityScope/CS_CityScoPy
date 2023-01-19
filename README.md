# CityScoPy

A tool for scanning interactions with a tangible LEGO grid and networking MIT CityScope Projects in Python.
Documentation: https://cityscope.media.mit.edu/UI/CityScoPy

# Example

Basic example:

- create a new CityScope project on the [CityScope Editor](https://cityscope.media.mit.edu/?editor) and name it `test`
- Go to this new project on [CityScopeJS Web App](https://cityscope.media.mit.edu/CS_cityscopeJS/?cityscope=test) and make sure it is running (a map and 3d grid should be visible)
- keep the project open on the browser and open a new terminal window
- Go to the CS_CityScoPy folder on your system [after cloning, and installing dependenices]
  - to set up the table type: `python cityscopy.py --cityscopy setup --table_name test`
  - to scan the table grid type: `python cityscopy.py --cityscopy scan --table_name test`
- If all goes well, you should see updates on [`GEOGRIDDATA` in cityIO](https://cityio.media.mit.edu/api/table/test/GEOGRIDDATA/)
- Go back to the [CityScopeJS Web App](https://cityscope.media.mit.edu/CS_cityscopeJS/?cityscope=test) and see if the grid updates based on the scan
