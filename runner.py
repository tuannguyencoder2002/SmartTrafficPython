import os
import sys
import random
from math import sqrt
from utils import communicate

# Kiểm tra và thiết lập đường dẫn cho SUMO_HOME
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
from plexe import Plexe, ACC, CACC

# Cấu hình cơ bản
VEHICLE_LENGTH = 5
DISTANCE = 6
LANE_NUM = 12
PLATOON_SIZE = 1
SPEED = 30
V2I_RANGE = 200
PLATOON_LENGTH = VEHICLE_LENGTH * PLATOON_SIZE + DISTANCE * (PLATOON_SIZE - 1)
ADD_PLATOON_PRO = 0.3
ADD_PLATOON_STEP = 600
MAX_ACCEL = 2.6
STOP_LINE = 15.0

# Tỉ lệ xuất hiện xe hơi và xe máy
CAR_PROBABILITY = 0.7
BIKE_PROBABILITY = 0.3

def add_vehicle(plexe, topology, step, lane, vehicle_type):
    vid = f"{vehicle_type}.{step // ADD_PLATOON_STEP}.{lane}.{random.randint(0, 1000)}"
    routeID = f"route_{lane}"
    traci.vehicle.add(vid, routeID, typeID=vehicle_type, departPos="free", departSpeed="max")
    if vehicle_type == "vtypeauto":
        configure_auto(plexe, vid, lane)  # Truyền thêm biến lane vào đây
    elif vehicle_type == "motorbike":
        configure_motorbike(plexe, vid, lane)  # Giả sử rằng bạn muốn cấu hình riêng cho xe máy tương tự

def configure_auto(plexe, vid, lane):  # Nhận biến lane
    plexe.set_path_cacc_parameters(vid, DISTANCE, 2, 1, 0.5)
    plexe.set_cc_desired_speed(vid, SPEED)
    plexe.set_acc_headway_time(vid, 1.5)
    plexe.use_controller_acceleration(vid, False)
    plexe.set_fixed_lane(vid, lane % 3, False)  # Sử dụng biến lane ở đây
    traci.vehicle.setSpeedMode(vid, 31)

def configure_motorbike(plexe, vid, lane):  # Nhận biến lane, nếu cần
    # Cấu hình cụ thể cho xe máy có thể điền vào đây
    traci.vehicle.setSpeedMode(vid, 31)

def add_platoons(plexe, topology, step):
    for lane in range(LANE_NUM):
        if random.random() < ADD_PLATOON_PRO:
            if random.random() < CAR_PROBABILITY:
                add_vehicle(plexe, topology, step, lane, "vtypeauto")
            else:
                add_vehicle(plexe, topology, step, lane, "motorbike")


def main():
    sumo_cmd = ['sumo-gui', '--duration-log.statistics', '--tripinfo-output', 'output_file.xml', '-c', 'traditional_traffic.sumo.cfg']
    traci.start(sumo_cmd)
    plexe = Plexe()
    traci.addStepListener(plexe)

    step = 0
    topology = {}

    while step < 360000:  # 1 hour simulation
        traci.simulationStep()
        if step % ADD_PLATOON_STEP == 0:
            add_platoons(plexe, topology, step)
        if step % 10 == 0:
            communicate(plexe, topology)
        step += 1

    traci.close()

if __name__ == "__main__":
    main()
