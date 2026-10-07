# bd_vlm_planner

High-level planner: a small VLM decomposes the mission goal into an ordered
sequence of structured subgoals using the drone's RGB camera feed and pose, and
detects arrival (design doc §2.1, §2.4). Emits JSON under constrained decoding
against the bd_interfaces subgoal schema.

Status: not yet implemented. Attached at inference time only, in Phase 5, after
the RL controller (bd_rl_controller) is trained in isolation. Model candidates
and the 4-bit quantization requirement are in the design doc §5.
