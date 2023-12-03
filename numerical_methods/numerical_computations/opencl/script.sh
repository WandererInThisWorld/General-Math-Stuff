if [ "$#" -lt 2 ]; then
	echo "The number of arguments is less than 2"
else
	echo $1
	echo $2

	if [[ "$OSTYPE" == "darwin"* ]]; then
		echo "Compiling from Mac"
		# clang $2 -framework OpenCL -D CL_HPP_TARGET_OPENCL_VERSION=100 -o hello
		clang $2 -framework OpenCL -D CL_HPP_TARGET_OPENCL_VERSION=100	
	elif [[ "$OSTYPE" == "linux-gnu"* ]]; then	
		echo "Compiling from Linux"
		gcc -Wall -Wextra -D CL_TARGET_OPENCL_VERSION=100 temp.c -lOpenCL	
	fi
fi




