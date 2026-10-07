# bd_interfaces

Custom ROS2 message/service definitions shared across nodes — most importantly the
structured subgoal schema the VLM planner emits and the RL controller consumes
(relative waypoint/heading, semantic target label, termination condition), per
`docs/Black_Dragon_VLM_RL_Navigation_Design.docx` §2.4.

Status: not yet implemented. Package scaffolding (package.xml, CMakeLists.txt,
msg/srv files) is created once the ROS2 distro is chosen (Phase 1, WP-B).
