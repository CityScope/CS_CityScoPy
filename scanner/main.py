# {{ CityScope Python Scanner }}
# Copyright (C) {{ 2018 }}  {{ Ariel Noyman }}

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]


##################################################

# CityScope Python Scanner
# Keystone, decode and send over UDP/HTTTP a 2d array
# of uniquely tagged LEGO array

##################################################

from multiprocessing import Process, Manager
import modules


##################################################
################RUN MULTITHREADED#################
##################################################
# https://kite.com/python/docs/multiprocessing.Manager


if __name__ == '__main__':

    # define global list manager
    MANAGER = Manager()
    # create shared global list to work with both processes
    multiprocess_shared_dict = MANAGER.dict()
    # init this dict's props with one value
    multiprocess_shared_dict['grid'] = [-1]
    multiprocess_shared_dict['rotations'] = [-1]

    # defines a multiprocess for sending the data
    process_send_packet = Process(target=modules.create_data_json,
                                  args=([multiprocess_shared_dict]))
    # # start porcess
    process_send_packet.start()
    # # start camera on main thread due to multiprocces issue
    modules.scanner_function(multiprocess_shared_dict)
    # # join the two processes
    process_send_packet.join()
