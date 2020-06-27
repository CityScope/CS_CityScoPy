#!/usr/bin/python


from cityscopy import Cityscopy


if __name__ == '__main__':
    print(
        '''
>>>>>>>>>>>>> Starting CityScope Scanner >>>>>>>>>>>>


                    |||||||||||                        
                    |||||||||||                         
                            |||                           
                            |||                           
                            |||                       
                    |||      ||||||||||||   
                    |||      ||||||||||||    
                    |||               |||      
                    |||               ||| 
                    |||               |||                  
                    ||||||||||||      |||        
                    ||||||||||||      |||   


>>>>>>>>>>>>> Starting CityScope Scanner >>>>>>>>>>>>

Copyright (C) {{ 2018 }}  {{ Ariel Noyman }}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

"@context": "https://github.com/CityScope/", "@type": "Person", "address": {
"@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
"Cambridge", "addressRegion": "MA",},
"jobTitle": "Research Scientist", "name": "Ariel Noyman",
"alumniOf": "MIT", "url": "http://arielnoyman.com",
"https://www.linkedin.com/", "http://twitter.com/relno",
https://github.com/RELNO]


##################################################
CityScope Python Scanner
Keystone, decode and send over UDP/HTTTP a 2d array
of uniquely tagged LEGO array
##################################################
'''
    )

    CITYSCOPY_SETTINGS_PATH = "settings/cityscopy.json"
    # init cityscopy class
    cityscopy = Cityscopy(CITYSCOPY_SETTINGS_PATH)
    # run CityScopy main methods
    # keystone the scanned area
    # cityscopy.keystone()
    # scan the grid and send to cityIO
    cityscopy.scan()
    # start local UDP comms
    # # cityscopy.udp_listener()
