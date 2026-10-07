# bd_bringup

Launch files and configs that bring up the full node graph together (Gazebo
world + PX4 SITL + bd_flight_bridge + whichever of the bd_* nodes exist at a
given phase). Keeps individual packages launchable standalone for testing while
giving the project one command to bring up the whole stack.

Status: not yet implemented. First version lands in Phase 2 (full node graph
with placeholder models, per the roadmap in the design doc §6).
