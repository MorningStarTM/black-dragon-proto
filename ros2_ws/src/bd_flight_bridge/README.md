# bd_flight_bridge

The PX4 <-> ROS2 bridge (WP-E of docs/Phase1_Environment_Build_Plan.docx):
micro-xrce-dds-agent configuration and launch files connecting PX4 SITL's
uXRCE-DDS client to ROS2 topics, plus the first manual arm/takeoff/velocity
smoke test (the Phase 1 exit criterion).

Chosen over MAVROS: PX4 now recommends uXRCE-DDS as its native ROS2 path, and
this project only targets PX4 (MAVROS's multi-autopilot support is not needed).

Status: not yet implemented. This is the current work item — built once the
ROS2 distro (Humble vs Jazzy) is chosen.
