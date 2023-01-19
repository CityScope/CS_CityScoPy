import cv2
import numpy as np
from .helpers import save_settings_to_file



############################################

def save_keystone_to_file(self, keystone_data_from_user_interaction):
    '''saves the keystone data from user interaction to the setting file as string'''
    str_keystone = str(keystone_data_from_user_interaction).replace('[','').replace(']','').replace(',',' ')
    # inject the keystone data to the settings object
    self.table_settings['keystone_points_list'] =  str_keystone

    # save the set  tings to file
  
    save_settings_to_file(self.CITYSCOPE_PRJ_NAME, self.table_settings)


############################################

def listen_to_UI_interaction(self, init_keystone):
    """
    listens to user interaction.
    Steps:
    listen to UI
    Args:
    Returns 4x2 array of points location for key-stoning
    """

    # keys to select corners
    corner_keys = ['1', '2', '3', '4']
    # keys to move corners
    move_keys = ['w', 'a', 's', 'd']
    # keys to increase/decrease distance moved by
    distance_keys = ['+', '-']
  

    # if the user presses a key, then save the key to the variable 'key_stroke' 
    KEY_STROKE = cv2.waitKey(100)

    if chr(KEY_STROKE & 255) in corner_keys:
        self.selected_corner = chr(KEY_STROKE & 255)
    
    # if the user presses the '+' or '-' key, then increase or decrease the distance moved by 5 pixels
    elif self.selected_corner != None and chr(KEY_STROKE & 255) in distance_keys:
        if chr(KEY_STROKE & 255) == '+':
            self.distance_value  = self.distance_value  + 5 if self.distance_value  < 200 else 200
        elif chr(KEY_STROKE & 255) == '-':
            self.distance_value  = self.distance_value  - 5 if self.distance_value  > 1 else 1
        print('distance [px] to move the keystone is: ', self.distance_value)

    
    # if the user presses the 'w', 'a', 's', or 'd' key, then move the selected corner in the direction pressed
    if self.selected_corner != None and chr(KEY_STROKE & 255) in move_keys:
        self.corner_direction = chr(KEY_STROKE & 255)

        if self.selected_corner == '1':
            if self.corner_direction == 'd':
                init_keystone[0] = init_keystone[0] - self.distance_value 
            elif self.corner_direction == 'a':
                init_keystone[0] = init_keystone[0] + self.distance_value 
            elif self.corner_direction == 'w':
                init_keystone[1] = init_keystone[1] + self.distance_value 
            elif self.corner_direction == 's':
                init_keystone[1] = init_keystone[1] - self.distance_value 

        elif self.selected_corner == '2':
            if self.corner_direction == 'd':
                init_keystone[2] = init_keystone[2] - self.distance_value 
            elif self.corner_direction == 'a':
                init_keystone[2] = init_keystone[2] + self.distance_value 
            elif self.corner_direction == 'w':
                init_keystone[3] = init_keystone[3] + self.distance_value 
            elif self.corner_direction == 's':
                init_keystone[3] = init_keystone[3] - self.distance_value 

        elif self.selected_corner == '3':
            if self.corner_direction == 'd':
                init_keystone[4] = init_keystone[4] - self.distance_value 
            elif self.corner_direction == 'a':
                init_keystone[4] = init_keystone[4] + self.distance_value 
            elif self.corner_direction == 'w':
                init_keystone[5] = init_keystone[5] + self.distance_value 
            elif self.corner_direction == 's':
                init_keystone[5] = init_keystone[5] - self.distance_value 

        elif self.selected_corner == '4':
            if self.corner_direction == 'd':
                init_keystone[6] = init_keystone[6] - self.distance_value 
            elif self.corner_direction == 'a':
                init_keystone[6] = init_keystone[6] + self.distance_value 
            elif self.corner_direction == 'w':
                init_keystone[7] = init_keystone[7] + self.distance_value 
            elif self.corner_direction == 's':
                init_keystone[7] = init_keystone[7] - self.distance_value 

    ulx = init_keystone[0]
    uly = init_keystone[1]
    urx = init_keystone[2]
    ury = init_keystone[3]
    blx = init_keystone[4]
    bly = init_keystone[5]
    brx = init_keystone[6]
    bry = init_keystone[7]


    # if 'q' key is pressed, then set self.selected_corner to None 
    if chr(KEY_STROKE & 255) == 'q':
        # reset selected corner
        self.selected_corner = None
        # save keystone to file
        # save_keystone_to_file(self, [ulx, uly, urx, ury, blx, bly, brx, bry])
        save_keystone_to_file(self, init_keystone)
       
    new_keystone = np.asarray([(ulx, uly), (urx, ury), (blx, bly), (brx, bry)], dtype=np.float32)
    return new_keystone

##################################################


def ui_selected_corner(self, x, y, vid):
    """prints text on video window"""

    mid = (int(x/2), int(y/2))
    if self.selected_corner is None:
        # font
        font = cv2.FONT_HERSHEY_SIMPLEX

        # fontScale
        fontScale = 1
        # Blue color in BGR
        color = (0, 0, 255)
        # Line thickness of 2 px
        thickness = 2
        cv2.putText(vid, 'select corners using 1,2,3,4 and move using A/W/S/D',
                    (5, int(y/2)), font,
                    fontScale, color, thickness, cv2.LINE_AA)
    else:
        case = {
            '1': [(0, 0), mid],
            '2':  [(x, 0), mid],
            '3':  [(0, y), mid],
            '4':  [(x, y), mid],
        }

        # print(type(self.selected_corner))
        cv2.arrowedLine(
            vid, case[self.selected_corner][0],
            case[self.selected_corner][1],
            (0, 0, 255), 2)

##################################################