# black-dragon-proto
Hierarchical VLM planner + RL controller for autonomous drone navigation

See `docs/Black_Dragon_VLM_RL_Navigation_Design.docx` for the full design and
`docs/Phase1_Environment_Build_Plan.docx` for the current phase's task breakdown.

## Repo structure

```
docs/                   Design doc + per-phase plans (docx)
ros2_ws/src/            ROS2 packages, one per node from the design doc:
  bd_interfaces/           shared msg/srv defs (the planner<->controller subgoal schema)
  bd_mission_command/      parses the user's NL command into a mission goal
  bd_vlm_planner/          VLM: decomposes goal into subgoals, detects arrival
  bd_rl_controller/        goal-conditioned PPO/SAC policy over LiDAR + pose
  bd_flight_bridge/        PX4 <-> ROS2 bridge (uXRCE-DDS) + manual control test
  bd_swarm_coordination/   multi-drone task handoff/deconfliction
  bd_bringup/              launch files that bring the node graph up together
sim/
  worlds/                  Gazebo SDF worlds
  models/                  drone + building models (SDF/GLB)
  px4_config/              PX4 SITL version pin + airframe parameter overrides
assets/blender/         source .blend files for the semantic world (Phase 3+)
training/
  rl/                      PPO/SAC training scripts & configs (Phase 4)
  vlm/                     second-stage VLM fine-tuning (Phase 5)
scripts/
  setup/                   reproducible environment setup
  benchmarks/              GPU/VRAM benchmarking (see GPU budget policy, docs/Phase1_Environment_Build_Plan.docx §4)
```

Every directory has its own README stating what goes there and which roadmap
phase builds it — most are empty scaffolding right now. Current work is Phase 1
(`bd_flight_bridge`, `sim/`, `scripts/setup`, `scripts/benchmarks`); see the
Phase 1 doc for the task-by-task breakdown and open decisions.
