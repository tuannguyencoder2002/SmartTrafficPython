from plexe import Plexe, ACC
import traci

sumo_cmd = ["sumo-gui", "-c", "sumo.cfg"]
traci.start(sumo_cmd)
plexe = Plexe()
traci.addStepListener(plexe)

traci.simulationStep()
plexe.set_active_controller("vehicle.0", ACC)
plexe.set_cc_desired_speed("vehicle.0", 30)
plexe.set_fixed_lane("vehicle.0", 0)