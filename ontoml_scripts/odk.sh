#!/bin/sh
# Wrapper script for docker.
#
# This is used primarily for wrapping the GNU Make workflow.
# Instead of typing "make TARGET", type "./run.sh make TARGET".
# This will run the make workflow within a docker container.
#
# The assumption is that you are working in the src/ontology folder;
# we therefore map the whole repo (../..) to a docker volume.
#
# See README-editors.md for more details.
AWS_CONFIG=~/.aws/credentials
if [ ! -f $AWS_CONFIG ]; then
    echo "Can't find aws config file ${AWS_CONFIG}! Output from run will not be pushed to S3"
fi
docker run -e ROBOT_JAVA_ARGS='-Xmx25G' -e JAVA_OPTS='-Xmx25G' -v $PWD/:/work -v $AWS_CONFIG:/root/.aws/credentials -w /work --rm -ti monarchinitiative/ontoml "$@"
