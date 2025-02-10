FROM osrf/ros:jazzy-desktop-full
ARG USERNAME=USERNAME
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Delete user if it exists in container (e.g Ubuntu Noble: ubuntu)
RUN if id -u $USER_UID ; then userdel `id -un $USER_UID` ; fi

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
RUN apt update && apt upgrade -y
RUN apt install -y \
    python3-pip \
    python3-venv \
    librdkafka-dev
RUN apt install -y \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-rosidl-generator-dds-idl 
ENV SHELL=/bin/bash

#RUN pip3 install \
#    confluent-kafka==2.8.0 \
#    fastavro==1.10.0 

#RUN pip3 install -i https://nexus.basys.dfki.dev/repository/pypi-group/simple libavro==0.0.1


# ********************************************************
# * Anything else you want to do like clean up goes here *
# ********************************************************

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME
CMD ["/bin/bash"]