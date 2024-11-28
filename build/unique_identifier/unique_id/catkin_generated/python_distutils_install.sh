#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/unique_identifier/unique_id"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/hik/Masaüstü/ros/görev-1/hik-görev_1/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/hik/Masaüstü/ros/görev-1/hik-görev_1/install/lib/python3/dist-packages:/home/hik/Masaüstü/ros/görev-1/hik-görev_1/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/hik/Masaüstü/ros/görev-1/hik-görev_1/build" \
    "/usr/bin/python3" \
    "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/src/unique_identifier/unique_id/setup.py" \
    egg_info --egg-base /home/hik/Masaüstü/ros/görev-1/hik-görev_1/build/unique_identifier/unique_id \
    build --build-base "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/build/unique_identifier/unique_id" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/hik/Masaüstü/ros/görev-1/hik-görev_1/install" --install-scripts="/home/hik/Masaüstü/ros/görev-1/hik-görev_1/install/bin"
