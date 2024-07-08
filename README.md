# ESP32-IMU-Project
This is my participation for a research project that uses multiple MPU6050s to get the acceleration and 3-axis gyroscope data for different body parts, My role is to set up the hardware and write the code that is needed to get the measurements.

The files in the repositry should be all that you need to replicate the experiment with you own kit, the main files are the umqttsimple.py which is a library necessary for this project, MqttSubs which is the susbscriber code and lastly is he BootCode which is going to be the publisher code, this is what is going to be run to collect data and send it over to the subscriber.
