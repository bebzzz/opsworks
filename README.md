# opsworks
test task for opsworks


Write idempotent python3 or ruby2 or php7 script which should:  
Create ec2 instance in existing VPC.  
Create security group which allows only 22 and 80 inbound ports and attach it to the instance.  
Create new EBS volume with "magnetic" type, 1GB size and attach it to the instance.  
Connect to the instance via ssh, format and mount additional volume.  
Clone/pull github repository (where this script is stored) into the mounted volume.  
Execute itself with an additional parameter to start self-written http service on port 80: this service should provide basic auth (login/pass) and output current git commit and resource usage of itself (cpu, memory) on GET request. Do not use nginx, apache or any other software.  
Any change during git pull should restart http service.  
  
It should be possible to execute this script in completely new and clean environment any number of times without any errors and http service should restart if there are any changes. Each resource should be created only once.  
  
Output: 
Link to public GitHub repository which should contain script source code.  
Web service URL with auth credentials.  
   
