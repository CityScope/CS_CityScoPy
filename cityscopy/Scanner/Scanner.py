'''
##################################################
CityScope Python Scanner
##################################################
'''


import cv2
import json
import numpy as np
import time
from multiprocessing import Process, Manager
from ..utils import parse_json_file, get_folder_path
from .helpers import create_data_json, np_string_tags
from .ui_tools import listen_to_UI_interaction, ui_selected_corner, get_init_keystone


class Scanner:

    def __init__(self, CITYSCOPE_PRJ_NAME):
        self.CITYSCOPE_PRJ_NAME = CITYSCOPE_PRJ_NAME
        self.table_settings = parse_json_file(CITYSCOPE_PRJ_NAME)
        self.GEOGRIDDATA = self.load_GEOGRIDDATA()
        self.CITYIO_URL = self.table_settings['CITYIO_API_URL']
        self.keystone_points_list = self.table_settings['keystone_points_list']
        self.selected_corner = None
        self.corner_direction = None
        self.FRAME = None
        self.POINT_INDEX = None
        self.POINTS = None
        self.MOUSE_POSITION = None
        self.distance_value = 5

    def load_GEOGRIDDATA(self):
        with open(get_folder_path() + 'settings/GEOGRIDDATA.json') as d:
            print('GEOGRIDDATA.json loaded to memory')
            return json.load(d)

    def scan(self):
        MANAGER = Manager()
        self.multiprocess_shared_dict = MANAGER.dict()
        self.multiprocess_shared_dict['scan'] = [[-1, -1]]

        self.process_send_packet = Process(target=create_data_json,
                                           args=([self, self.multiprocess_shared_dict]))
        self.process_send_packet.start()
        self.scanner_function(self.multiprocess_shared_dict)

    def scanner_function(self, multiprocess_shared_dict):
        self.init_keystone = get_init_keystone(self)
        grid_dimensions_x = self.table_settings['ncols']
        grid_dimensions_y = self.table_settings['nrows']

        binary_tags_list = []
        array_of_maps_form_json = []
        for i in self.table_settings['types']:
            binary_tags_list.append(
                self.table_settings['types'][i]['cityscopy_pattern'])
            array_of_maps_form_json.append(
                self.table_settings['types'][i]['name'])

        array_of_tags_from_json = np_string_tags(self, binary_tags_list)
        cell_gap = self.table_settings['cell_gap']

        TYPES_LIST = []
        OLD_CELL_COLORS_ARRAY = []

        camPos = self.table_settings['camId']
        video_capture = cv2.VideoCapture(camPos)
        time.sleep(1)

        if grid_dimensions_y < grid_dimensions_x:
            grid_ratio = grid_dimensions_y / grid_dimensions_x
            video_resolution_x = int(video_capture.get(3))
            video_resolution_y = int(video_capture.get(3) * grid_ratio)
        else:
            grid_ratio = grid_dimensions_x / grid_dimensions_y
            video_resolution_x = int(video_capture.get(3) * grid_ratio)
            video_resolution_y = int(video_capture.get(3))

        cv2.namedWindow('scanner_gui_window', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('scanner_gui_window', 400, 400)
        cv2.moveWindow('scanner_gui_window', 10, 100)

        DICTIONARY_COLORS = {
            0: (0, 0, 0),
            1: (255, 255, 255)
        }

        x_ratio = int(video_resolution_x / (grid_dimensions_x * 4))
        y_ratio = int(video_resolution_y / (grid_dimensions_y * 4))
        scanner_square_size = np.minimum(x_ratio, y_ratio)

        array_of_scanner_points_locations = self.get_scanner_pixel_coordinates(
            grid_dimensions_x, grid_dimensions_y, cell_gap, video_resolution_x,
            video_resolution_y, scanner_square_size)

        video_resolution_x += grid_dimensions_x * cell_gap
        video_resolution_y += grid_dimensions_y * cell_gap

        while True:
            keystone_data = self.transform_matrix(
                video_resolution_x, video_resolution_y, listen_to_UI_interaction(self, self.init_keystone))

            CELL_COLORS_ARRAY = []

            RET, this_frame = video_capture.read()
            if RET is False:
                pass
            else:
                if self.table_settings['mirror_cam'] is True:
                    this_frame = cv2.flip(this_frame, 1)
                keystoned_video = cv2.warpPerspective(
                    this_frame, keystone_data, (video_resolution_x, video_resolution_y))

            count = 0
            for this_scanner_location in array_of_scanner_points_locations:
                x = this_scanner_location[0]
                y = this_scanner_location[1]

                this_scanner_max_dimension = int(scanner_square_size)
                scanner_reduction = int(scanner_square_size / 4)
                x_red = x + this_scanner_max_dimension - scanner_reduction
                y_red = y + this_scanner_max_dimension - scanner_reduction

                this_scanner_size = keystoned_video[y + scanner_reduction:y_red,
                                                    x + scanner_reduction:x_red]

                mean_color = cv2.mean(this_scanner_size)
                color_b, color_g, color_r, _ = np.uint8(mean_color)
                mean_color_RGB = np.uint8([[[color_b, color_g, color_r]]])

                scannerCol = self.select_color_by_mean_value(mean_color_RGB)
                CELL_COLORS_ARRAY.append(scannerCol)
                thisColor = DICTIONARY_COLORS[scannerCol]

                if self.table_settings['gui'] is True:
                    cv2.rectangle(keystoned_video,
                                  (x + scanner_reduction,
                                   y + scanner_reduction),
                                  (x_red, y_red),
                                  thisColor, 1)

                count += 1

            if CELL_COLORS_ARRAY != OLD_CELL_COLORS_ARRAY:
                TYPES_LIST = self.find_type_in_tags_array(
                    CELL_COLORS_ARRAY, array_of_tags_from_json,
                    array_of_maps_form_json,
                    grid_dimensions_x, grid_dimensions_y)

                OLD_CELL_COLORS_ARRAY = CELL_COLORS_ARRAY
                multiprocess_shared_dict['scan'] = TYPES_LIST
            else:
                pass

            if self.table_settings['gui'] is True:
                ui_selected_corner(self,
                                   video_resolution_x, video_resolution_y, keystoned_video)
                cv2.imshow("scanner_gui_window", keystoned_video)

    def get_scanner_pixel_coordinates(self, grid_dimensions_x, grid_dimensions_y, cell_gap, video_res_x, video_res_y, scanner_square_size):
        grid_x_offset = int(
            0.5 * (video_res_x - (grid_dimensions_x * scanner_square_size * 4)))
        grid_y_offset = int(
            0.5 * (video_res_y - (grid_dimensions_y * scanner_square_size * 4)))

        pixel_coordinates_list = []

        for y in range(0, grid_dimensions_y):
            for x in range(0, grid_dimensions_x):
                x_positions = x * (scanner_square_size * 4 + cell_gap)
                y_positions = y * (scanner_square_size * 4 + cell_gap)

                for i in range(0, 4):
                    for j in range(0, 4):
                        pixel_coordinates_list.append(
                            [grid_x_offset + x_positions + (i * scanner_square_size),
                             grid_y_offset + y_positions + (j * scanner_square_size)])
        return pixel_coordinates_list

    def transform_matrix(self, video_resolution_x, video_resolution_y, keyStonePts):
        video_aspect_ratio = (video_resolution_y, video_resolution_x)
        keystone_origin_points_array = np.float32(
            [
                [0, 0],
                [video_aspect_ratio[1], 0],
                [0, video_aspect_ratio[0]],
                [video_aspect_ratio[1], video_aspect_ratio[0]]
            ])
        transfromed_matrix = cv2.getPerspectiveTransform(
            keyStonePts, keystone_origin_points_array)

        return transfromed_matrix

    def select_color_by_mean_value(self, mean_color_RGB):
        bgr_to_grayscale = cv2.cvtColor(mean_color_RGB, cv2.COLOR_BGR2GRAY)
        if int(bgr_to_grayscale) < 125:
            this_color = 0
        else:
            this_color = 1
        return this_color

    def find_type_in_tags_array(self, cellColorsArray, tagsArray, mapArray,
                                grid_dimensions_x, grid_dimensions_y):
        scan_results_array = []
        np_array_of_scanned_colors = np.reshape(
            cellColorsArray, (grid_dimensions_x * grid_dimensions_y, 16))

        for this_16_bits in np_array_of_scanned_colors:
            result_tag = self.brick_rotation_check(
                this_16_bits, tagsArray, mapArray)

            if result_tag is None:
                result_tag = [-1, -1]

            scan_results_array.append(result_tag)
        return scan_results_array

    def brick_rotation_check(self, this_16_bits, tagsArray, mapArray):
        tags_array_counter = 0
        for this_tag in tagsArray:
            if np.array_equal(this_16_bits, this_tag):
                return [tags_array_counter, 0]
            brk_4x4 = np.reshape(this_16_bits, (4, 4))
            brk_4x4_270 = np.reshape((np.rot90(brk_4x4)), 16)
            if np.array_equal(brk_4x4_270, this_tag):
                return [tags_array_counter, 1]
            brk_4x4_180 = np.reshape((np.rot90(np.rot90(brk_4x4))), 16)
            if np.array_equal(brk_4x4_180, this_tag):
                return [tags_array_counter, 2]
            brk_4x4_90 = np.reshape(
                (np.rot90(np.rot90(np.rot90(brk_4x4)))), 16)
            if np.array_equal(brk_4x4_90, this_tag):
                return [tags_array_counter, 3]
            tags_array_counter += 1
