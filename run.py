#!/usr/bin/python
from subprocess import Popen
import time
import sys

while True:
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
'''
    )

    time.sleep(1)
    p = Popen("python " + 'scanner/main.py', shell=True)
    p.wait()
    time.sleep(1)
