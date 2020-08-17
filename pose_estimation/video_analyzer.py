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

fps_time = 0

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=str, default=0)

    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')

    parser.add_argument('--tensorrt', type=str, default="False",
                        help='for tensorrt process.')
    args = parser.parse_args()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h), trt_bool=str2bool(args.tensorrt))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368), trt_bool=str2bool(args.tensorrt))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    useful_joints = ["nose_x", "nose_y", "neck_x", "neck_y", "r_shoulder_x", "r_shoulder_y", "r_elbow_x", "r_elbow_y", "r_wrist_x", "r_wrist_y", "l_shoulder_x",
    "l_shoulder_y", "l_elbow_x", "l_elbow_y", "l_wrist_x", "l_wrist_y", "r_hip_x", "r_hip_y", "r_knee_x", "r_knee_y", "r_ankle_x", "r_ankle_y", "l_hip_x", "l_hip_y",
    "l_knee_x", "l_knee_y", "l_ankle_x", "l_ankle_y"]

    coordinates_list = []

    while True:
        ret_val, image = cam.read()

        #logger.debug('image process+')
        try:
            humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
            human = humans[0]
        except:
            break

        #logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)

        num_useful_joints = 14

        joint_locations = []
        for joint_counter in range(num_useful_joints):
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
        coordinates_list.append(joint_locations)
        #coordinates = coordinates.append(pd.Series(joint_locations, useful_joints), ignore_index = True)


        logger.debug('show+')
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        if cv2.waitKey(1) == 27:
            break
        logger.debug('finished+')

    coordinates = pd.DataFrame(coordinates_list, columns = useful_joints)

    coordinates.to_csv('./body_position_results.csv')
    print(coordinates)
    cv2.destroyAllWindows()
