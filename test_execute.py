from multiprocessing import Process
from library_bmp_to_binary import *



def main():
    video_file_name = "nyancat.mp4"       # Test Video 1
    # # video_file_name = "simpsons.mp4"      # Test Video 2
    # # video_file_name = "red_rectangle.mp4" # Test Video 3
    # # video_file_name = "neverplaythis.mp4"   # Test Video 4
    #
    # p1 = Process(target=wait_for_keyboard_input())      # Start listener for stop key (F6 for testing reasons)
    # p1.start()
    # p2 = Process(target=lt1_video(video_file_name))   # Layout type 1
    # # p2 = Process(target=lt2_video(video_file_name))   # Layout type 2
    # # p2 = Process(target=lt3_video(video_file_name))     # Layout type 3
    # p2.start()
    #
    # p1.join()   # Join processes
    # p2.join()   # Join processes

    # background_color = [255, 0, 0]
    # text = "Hello World"    # Text to put in the Video
    # scale = 0.5
    # text_color = (0, 255, 255)      # Text color
    # text_thickness = 1              # Text thickness
    # x = 0                           # X Position of text
    # y = 27                          # Y Position of text
    # create_frame_with_text(background_color, text, scale, text_color, text_thickness, x, y)

    # lt1_video(video_file_name)
    show_black()


if __name__ == '__main__':
    main()


