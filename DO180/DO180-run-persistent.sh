#!/bin/bash
if [ ! -d /tmp/docker/work ]; then
  mkdir -p /tmp/docker/work
  sudo semanage fcontext -a -t container_file_t '/tmp/docker/work(/.*)?'
  sudo restorecon -R /tmp/docker/work
  sudo chown 1001:1001 /tmp/docker/work
fi

sudo podman run -d -v /tmp/docker/work:/opt/nexus/sonatype-work nexus
sudo podman inspect cfd233e7454f | egrep -i 'ip|port|network|tcp'
