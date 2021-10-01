export nexus_template=/home/student/DO180/labs/comprehensive-review/deploy/openshift/resources/nexus-template.json
source /home/student/myconfig
source /usr/local/etc/ocp.config
export RHT_OCP4_QUAY_USER=fernandesselwyn0

#OCP Login
oc login -u ${ocp_user} -p ${ocp_pass} ${ocp_url}

#Create Namespace
export new_project=${ocp_user}-review
oc new-project ${new_project}

#process template
oc process -f ${nexus_template} \
	-p NAMESPACE=${new_project} \
	-p RHT_OCP4_QUAY_USER=${RHT_OCP4_QUAY_USER} \
	 >deploy.yaml
#create deployment
oc create -f deploy.yaml
sleep 30
#create route 
oc expose service nexus --hostname nexus-${ocp_user}-review.${RHT_OCP4_WILDCARD_DOMAIN}

