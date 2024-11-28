execute_process(COMMAND "/home/hik/Masaüstü/ros/görev-1/hik-görev_1/build/geographic_info/geodesy/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/hik/Masaüstü/ros/görev-1/hik-görev_1/build/geographic_info/geodesy/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
