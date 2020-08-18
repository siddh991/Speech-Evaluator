import argparse
import logging
import time
import cv2
import numpy as np
import pandas as pd
import sys

sys.path.insert(0, "./tf_pose_estimation")

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
from tf_pose.runner import infer, Estimator, get_estimator


logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class Video_Analyzer():

    def __init__(self, filepath, resize='0x0', resize_out_ratio = 4.0, model='mobilenet_thin', show_process = False, tensorrt=False):
        self.filepath = filepath
        self.resize = resize
        self.resize_out_ratio = resize_out_ratio
        self.model = model
        self.show_process = show_process
        self.tensorrt = tensorrt

        self.fps_time = 0
        self.useful_joints = ["nose_x", "nose_y", "neck_x", "neck_y", "r_shoulder_x", "r_shoulder_y", "r_elbow_x", "r_elbow_y", "r_wrist_x", "r_wrist_y", "l_shoulder_x",
            "l_shoulder_y", "l_elbow_x", "l_elbow_y", "l_wrist_x", "l_wrist_y", "r_hip_x", "r_hip_y", "r_knee_x", "r_knee_y", "r_ankle_x", "r_ankle_y", "l_hip_x", "l_hip_y",
            "l_knee_x", "l_knee_y", "l_ankle_x", "l_ankle_y"]  
        self.num_useful_joints = 14
        self.coordinates_list = []

        logger.debug('initialization %s : %s' % (self.model, get_graph_path(self.model)))
        self.w, self.h = model_wh(self.resize)
        if self.w > 0 and self.h > 0:
            self.e = TfPoseEstimator(get_graph_path(self.model), target_size=(self.w, self.h), trt_bool=self.tensorrt)
        else:
            self.e = TfPoseEstimator(get_graph_path(self.model), target_size=(432, 368), trt_bool=self.tensorrt)
        logger.debug('cam read+')
        
        self.cam = cv2.VideoCapture(self.filepath)
        ret_val, image = self.cam.read()
        logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    def track_movement(self):

        while True:
            ret_val, image = self.cam.read()

            try:
                humans = self.e.inference(image, resize_to_default=(self.w > 0 and self.h > 0), upsample_size=self.resize_out_ratio)
                human = humans[0]
            except:
                break

            image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

            joint_locations = []
            for joint_counter in range(self.num_useful_joints):
                print(joint_counter)
                try:
                    joint = human.body_parts[joint_counter]
                    x = joint.x*image.shape[1]
                    y = joint.y*image.shape[0]

                    joint_locations.extend([x, y])
                    print("end")
                except:
                    pass

            print(joint_locations)
            self.coordinates_list.append(joint_locations)

            cv2.putText(image,
                        "FPS: %f" % (1.0 / (time.time() - self.fps_time)),
                        (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
            cv2.imshow('tf-pose-estimation result', image)
            self.fps_time = time.time()
            if cv2.waitKey(1) == 27:
                break
            logger.debug('finished+')

        coordinates = pd.DataFrame(self.coordinates_list, columns = self.useful_joints)

        coordinates.to_csv('./body_position_results.csv')
        print(coordinates)
        cv2.destroyAllWindows()

if __name__ == '__main__':
    video_analyzer = Video_Analyzer(filepath='../video_data/vid.mp4')
    video_analyzer.track_movement()