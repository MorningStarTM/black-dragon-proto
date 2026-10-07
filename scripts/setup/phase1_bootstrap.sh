#!/usr/bin/env bash
# Phase 1 bootstrap: ROS2 Jazzy + Gazebo Harmonic + ros_gz bridge on Ubuntu 24.04 (WSL2).
# Run as root (or with sudo) inside the Ubuntu-24.04 WSL distro.
# Corresponds to WP-A3/A4 (GPU env), WP-B1 (ROS2), WP-C1/C2 (Gazebo + ros_gz)
# in docs/Phase1_Environment_Build_Plan.docx.
set -euo pipefail

echo "== WP-A: GPU rendering env =="
# Default Vulkan/GL driver probing on this WSL2 + NVIDIA stack picks software
# llvmpipe unless GALLIUM_DRIVER=d3d12 is forced. Verified: without it, glxinfo
# reports "Accelerated: no"; with it, "D3D12 (NVIDIA GeForce GTX 1650 Ti ...)".
if ! grep -q "GALLIUM_DRIVER=d3d12" /etc/environment 2>/dev/null; then
  echo "GALLIUM_DRIVER=d3d12" | tee -a /etc/environment
fi

echo "== WP-B1: ROS2 Jazzy =="
apt-get update -qq
apt-get install -y -qq locales software-properties-common curl
locale-gen en_US en_US.UTF-8
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
add-apt-repository -y universe

ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
VERSION_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.${VERSION_CODENAME}_all.deb"
apt-get install -y -qq /tmp/ros2-apt-source.deb
apt-get update -qq
apt-get install -y ros-jazzy-desktop python3-colcon-common-extensions

echo "== WP-C1/C2: Gazebo Harmonic + ros_gz bridge =="
apt-get install -y -qq lsb-release gnupg
curl -s https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
  | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
apt-get update -qq
apt-get install -y gz-harmonic ros-jazzy-ros-gz

echo "== done =="
echo "source /opt/ros/jazzy/setup.bash" >> /etc/profile.d/ros_jazzy.sh
