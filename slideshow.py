#!/usr/local/bin/python3

import cv2
import subprocess
import copy, argparse

SWIPE = 1
DISSOLVE = 2

parser = argparse.ArgumentParser(description='Create a slideshow with basic transition')
parser.add_argument('--image_stay', action='store', type=int, dest='image_stay', default=3, help='how long (in secs) an image should stay in the slidehow')
parser.add_argument('--transition_stay', action='store', type=float, dest='transition_stay', default=1, help='how long (in secs) to change to next image in the slidehow')
parser.add_argument('--fps', action='store', type=int, dest='fps', default=24, help='frames per second of the slideshow video')
parser.add_argument('--transition_type', action='store', type=int, dest='transition_type', default=SWIPE, help="type of transition between images. Select 1 for SWIPE, 2 for DISSOLVE")
parser.add_argument('--video_name', action='store', type=str, dest='video_name', default='slideshow', help='name of slideshow video (without the extension)')
opt = parser.parse_args()

images_path = 'images/'
p = subprocess.Popen(['ls {}'.format(images_path)], stdout=subprocess.PIPE, shell=True)

communicate = p.communicate()
if communicate[1] == None:
    images_name = communicate[0].decode("utf-8").strip('\n').split('\n')
else:
    print("Error: " + communicate[1])
    exit()

fps = opt.fps #frames_per_second
image_duration_in_secs = opt.image_stay
total_images = len(images_name)
transition_time_in_secs = opt.transition_stay
images_time = image_duration_in_secs*total_images
transitions_time = transition_time_in_secs*(total_images-1)
transition_type = opt.transition_type
duration_in_secs = images_time + transitions_time
no_of_frames = duration_in_secs*fps
video_name = opt.video_name
video_ext = 'mp4'
final_width = 1920 #in px
final_height = 1080 #in px

frames = []
image_array = []
for image in images_name:
    img = cv2.imread(images_path+image)
    img = cv2.resize(img,(final_width, final_height))
    image_array.append(img)

for idx in range(len(images_name)):
    img = image_array[idx]
    for _ in range(image_duration_in_secs*fps):
        frames.append(img)
    if idx != len(images_name)-1:
        if transition_type == SWIPE:
            frames_needed = transition_time_in_secs*fps
            width_chunks = final_width/frames_needed
            width_chunks = int(width_chunks)
            temp = copy.deepcopy(img)
            next_image = image_array[idx+1]
            # for right to left transition
            for i in range(int(frames_needed)):
                temp[:, :-1*width_chunks] = temp[:, width_chunks:]
                temp[:, -1*width_chunks:] = next_image[:, i*width_chunks:(i+1)*width_chunks]
                temp=copy.deepcopy(temp)
                frames.append(temp)
        elif transition_type == DISSOLVE:
            next_image = image_array[idx+1]
            frames_needed = transition_time_in_secs*fps
            alpha_step = 1/float(frames_needed)
            alpha = 1
            for i in range(int(frames_needed)):
                temp = cv2.addWeighted(img, alpha, next_image, 1-alpha, 0)
                alpha = alpha-alpha_step
                frames.append(temp)
        else:
            assert False, "Transition type is not defined"

out = cv2.VideoWriter(video_name+'.'+video_ext, cv2.VideoWriter_fourcc(*'mp4v'), fps, (final_width, final_height))

for i in range(len(frames)):
    out.write(frames[i])
out.release()

