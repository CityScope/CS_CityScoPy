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
    multiprocess_shared_dict['scan'] = [-1, -1]

    # defines a multiprocess for sending the data
    process_send_packet = Process(target=modules.create_data_json,
                                  args=([multiprocess_shared_dict]))
    # # start porcess
    process_send_packet.start()
    # # start camera on main thread due to multiprocces issue
    modules.scanner_function(multiprocess_shared_dict)
    # # join the two processes
    process_send_packet.join()
