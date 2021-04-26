from Arm import Arm
from Board import Board
from Camera import Camera
import json
import time

from Exceptions import CalibrationMarkerNotVisible
from Log import Log
from Marker import Marker
from RpiMotorLib import RpiMotorLib

"""
Initialize global objects using the config file.
"""
Log.info('Initializing components.')
# Read the config file
f = open("config.json")
config = json.load(f)
f.close()
# Init the camera
camera = Camera(
    index=0,
    width=1920,
    height=1080,
    k=config['camera']['calibration']['k'],
    d=config['camera']['calibration']['d'],
    distance_calibration=config['camera']['calibration']['distance']
)
# Init the board
board = Board(
    tl_fid=config['board-corner-fid-mapping']['top-left'],
    tr_fid=config['board-corner-fid-mapping']['top-right'],
    bl_fid=config['board-corner-fid-mapping']['bottom-left'],
    br_fid=config['board-corner-fid-mapping']['bottom-right'],
    fid_to_piece_map=config["fid-piece-mapping"]
)
# Init the arm
arm = Arm(
    x_size=config['arm']['x-size'],
    y_size=config['arm']['y-size'],
    x_stp=8,
    x_dir=7,
    y_stp=15,
    y_dir=16
)


"""
Execute main function.
"""

if __name__ == "__main__":
    for x in range(5):
        arm.x_stepper.motor_go(steps=200)
        time.sleep(2)
    arm.cleanup()
    # Perform mechanical calibration
    arm.calibrate()
    # Perform camera distance calibration
    while True:
        try:
            camera.calibrate_observed_distances()
            break
        except CalibrationMarkerNotVisible:
            input('\nExecution paused, press any key to continue.')
            print()
    # Temporary sequence - move the arm to the given marker
    target_fid = "5"
    while True:
        # Take snapshot to get all of the markers present
        markers, center = camera.take_snapshot()
        # If marker is not present, move to random location and try again
        if target_fid not in markers:
            arm.move_to_random_position()
            continue
        # Calculate the vector between the current position and the target markers position
        movement_vector = markers[target_fid].center - center
        Log.debug(movement_vector)

        time.sleep(1)
