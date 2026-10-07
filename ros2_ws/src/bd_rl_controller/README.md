# bd_rl_controller

Low-level goal-conditioned policy (PPO/SAC): executes the active subgoal against
live LiDAR and pose, avoids obstacles. Never touches pixels or semantics — see
design doc §2.2 for why perception is split this way.

Status: not yet implemented. Trained headless (Gazebo server-only, no VLM in the
loop — see docs/Phase1_Environment_Build_Plan.docx §4, GPU budget policy) in
Phase 4, after WP-F (physics fidelity pass) is complete.
