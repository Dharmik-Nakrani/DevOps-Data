#!/bin/bash

# Generate filename with the current date
filename=$(date +'%d-%m-%Y')
echo "Creating Jenkins backup: jenkins_${filename}.tar"

# Create a tarball of the Jenkins directory
sudo tar -cvf /home/server/Jenkins/jenkins_${filename}.tar /var/lib/jenkins/

--------------------------------------------
#!/bin/bash

# Generate filename for backups older than 7 days
filename=$(date -d "-7 days" +'%d-%m-%Y')
echo "Removing old Jenkins backup: jenkins_${filename}.tar"

# Remove the old Jenkins backup file
sudo rm /home/server/Jenkins/jenkins_${filename}.tar
