# DO280 Study Notes _OCP4 Operations_


## 1. Deinitions 
[OCP4.6 Docs](https://docs.openshift.com/container-platform/4.6/welcome/oke_about.html)

Features:
```
$ OpenShift Container Platform
$ OpenShift Dedicated
$ OpenShift Online
$ OpenShift Kubernetes Engine
$ OpenShift Container Platform
![Feature Chart](FeatureChart.png "Feature Chart")
$ Allows for : Logging, Monitoring, Service Discovery, Load Balacing, HA, Scaling, ApplicationControl, Storage
```
OCP Resources:
```
$ CRI-O           [systemd]
$ Kubelet         [systemd]
$ etcd            [static pod]
$ kube-scheduller [static pod]
$ kueb-controller [static pod]
$ Kube-apiserver  [static pod] -> openshift-apiserver <- openshift-oauth
```
Cluster Operators:
```
$ Define Operators, OperatorSDK, OperatorHub, OLM, RedHat MarketPlace, CRD
$ oc get clusteroperators (co)
• openshift-authentication
• openshift-apiserver
• openshift-controller-manager
• authentication
• cloud-credential
• cluster-autoscaler
• console
• dns
• ingress
• image-registry
• machine-config
• monitoring
• network
• storage
```

## 2. Cluster State 

Types of Installers:
```
$ full-stack automation (IPI)
$ pre-existing infra (UPI)
```
OCP Resources:
```
$ oc login -u $user1 -p $pass1 --insecure-skip-tls-verify=true
$ oc get clusterversion
$ oc get co
$ oc get nodes --show-labels
$ oc adm top nodes
$ oc describe node $node1
$ oc get events --sort-by='metadata.creationTimestamp'
$ oc adm node-logs -u crio|kubelet $node1
$ oc debug node/$node1
$ crictl ps
$ ssh -l core $node1
```
Apps troubleshoot:
```
$ oc status
$ oc get pod|deployment/$app1
$ oc describe pod|deployment/$app1 (selectors, events, etc)
$ oc debug pod|deployment/$app1
$ podman login $registry1 -u $rh_reg -p $rh_token
$ skopeo inspect docker://$image1
$ oc edit deployment/$app1
$ oc get storageclass (sc)
$ oc set volumes deployment/$app1 --add --name $pvc_name --type pvc --claim-name $pvc_name --claim-mode rwo|rwx|rox --claim-size 5Gi --mount-path /mnt/data
$ oc set env deployment/$app1 --from=secret/$app1_sec --prefix=MYSQL_ROOT_
$ oc set resource deployment/$app1 
```

## 2. AuthN & AuthZ
```
$ User, Identity, ServiceAccount, Group, Role, Binding
$ Identity Providers: HTPasswd, Keystore(openstack), LDAP, GitHub, OpenID
```

### Create Identity Provider (HTPasswd)
```
Create HTPassword provider in WebGUI then edit it!
$ touch $htp_full_path
$ htpasswd -b $htp_full_path $user1 $pass1
$ htpasswd -b $htp_full_path $user2 $pass2
$ oc create secret generic $idp_secret --from-file=htpasswd=$htp_full_path -n openshift-config
$ oc edit oauth/cluster #update name, secret_name
Add user
$ oc extract secret generic $idp_secret -n openshift-config --to /tmp/$idp_secret
$ htpasswd -b /tmp/$idp_secret $user3 $pass3
$ oc set data secret/$idp_secret --from-file=htpasswd=/tmp/$idp_secret -n openshift-config
Delete user
$ oc extract secret generic $idp_secret -n openshift-config --to /tmp/$idp_secret
$ htpasswd -D /tmp/$idp_secret $user3 $pass3
$ oc set data secret/$idp_secret --from-file=htpasswd=/tmp/$idp_secret -n openshift-config
$ oc delete user/$user3
$ oc delete identity/$idp_name:$user3
Check state of Auth!!!
$ watch oc get pods -n openshift-authentication
Update User's Name
$ oc get users
$ oc edit user/$user1 #Update with full-name, etc
$ oc get identity #
$ oc login -u $user1 -p $pass1 $ocp_api
$ oc login -u $user2 -p $pass2 $ocp_api
```
### Create groups
```
$ oc adm groups new $group1 $user1 $user3
$ oc adm groups new $group2 $user2 $user4
$ oc adm groups add-users $group2 $user5 $user6
$ oc get groups
```
### Create Cluster Admin & remove kubeadmin
```
$ oc adm policy add-cluster-role-to-user cluster-admin $user1
$ oc delete secrete kubeadmin -n kube-system
```
### Remove the Capability to Create Projects for All Regular Users
Removing the `self-provisioner` cluster role from authenticated users and groups denies permissions for self-provisioning any new projects:
```
$ oc get clusterrolebinging | grep self
$ oc adm policy remove-cluster-role-from-group self-provisioner system:authenticated:oauth
$ oc adm policy add-cluster-role-to-group self-provisioner $group1
```

### Create a New Project
Create two new projects:
```
$ oc new-project $project1 --description=$project1_desc --display-name=$project1_display
$ oc describe project/$project1 #name, description, labels, selector, node-selector, quota 
```

### Managing User permissions
To manage local policies, the following roles are available:
* **cluster-admin** - User with superuser access
* **cluster-status** - User can get status on all cluster resources
* **admin** - users in the role can manage all resources in a project, including granting access to other users to the project. 
* **edit** - users in the role can create, change and delete common application resources from the project. Cannot manage access permissions to the project. 
* **view** - users in the role have read access to the project.
* **basic-user** - users in the role have read access to the project.
* **self-provisioner** - users in the role can create new projects. This is a cluster role, not a project role.

```
$ oc policy add-role-to-user admin $user1 -n $project1
$ oc policy add-role-to-user edit $user2 -n $project1
$ oc policy add-role-to-user view $user3 -n $project1
$ oc get rolebindings -n $project1
$ oc describe rolebindings -n $project1
```
### Create serviceaccounts
```
$ oc create serviceaccount $sa1 -n $project1
$ oc create sa $sa2 -n $project1
```

### Security Context Constraints (SCCs)
List security context constraints
```
$ oc get scc | awk '{ print $1 }'
NAME
anyuid
hostaccess
hostmount-anyuid
hostnetwork
nonroot
privileged
restricted
```
Associate the new service account with the `anyuid` security context:
```
$ oc adm policy add-scc-to-user anyuid -z $sa1
$ oc get rolebindings -n $project1
```
Update Deployment to use Service Account:
```
$ oc set sa deployment/$app1 $sa 
$ oc edit dc/apache
```
Add the service account definition:
```
spec:
  template:
    spec:
      serviceAccountName: apache-account
```

## 3. Secrets & ConfigMaps

```
$ oc create secret generic|tls
$ oc create secret generic $app1 --from-literal $key1=$vaule1 --from-literal $key2=$vaule2 
$ oc create secret generic $sskkey1 --from-file id_rsa=$fullpathidrsa --from-file id_rsa.pub=$fullpathidrsapub
$ oc create secret tls $app1 --cert $fullpathcert --key $fullpathcertkey
```

Add the service account definition:
```
env:
  - name: $app1
    vauleFrom:
      secretKeyRef:
        name: $app1
        key: $key1
$ oc set env deployment/$app1 --from=secret/$app1
$ oc set env deployment/$app1 --from=secret/$app1 --prefix MYSQL_
$ oc set vault deployment/$app1 --add --type secret --secret-name $app1 --mount-path $app1_sec_mnt
```
```
$ oc create configmap $app1 --from-literal $key1=$vaule1 --from-literal $key2=$vaule2 
$ oc set env deployment/$app1 --from=cm/$app1
```

```
$ oc extract data secret/$app1 --to /tmp --confirm
$ oc set data secret/$app1 --from-file $fullpathNewSec
# Use case htpasswd update/replace
$ htpasswd -b $fullpath_htpasswdfile $user20 $pass20
$ oc set data secret/$idpdata -n openshift-config --from-file $fullpath_htpasswdfile 
```
```
$ oc get scc -o name | awk '{print $2}' FS="/" | sort
$ oc describe scc/anyuid
$ oc describe pod $app1 | grep scc
***$ oc get pod $app1 | oc adm policy scc-subject-review -f -
$ oc create sa ${app1}-sa
$ oc adm policy add-scc-to-user anyuid -z ${app1}-sa 
$ oc set sa deployment/$app1 ${app1}-sa
```

## 4. Networking
SDN, services, DNS CO, routes, ingress, NetworkPolicies

Some SDNs used with CNI plugins:
• OpenShift SDN
• OVN-Kubernetes
• Kuryr

### Services
```
Services 
- rely on selectors (labels) that indicate which pods receive the traffic
- acts as a load balancer in front of one or more pods
```
### DNS
```
OpenShift run CoreDNS by default. All resources first check the "local" cluster DNS before checking externally
To review the configuration:
$ oc describe dns.operator/default
Example of CoreDNS record:
<port-name>.<port-protocol>.<svc-name>.<namespace>.svc.<cluster-domain>
```

### External Network Access
```
Expose your applications to external networks through: 
- Route: OpenShift native router plugin
- Ingress: Kubernets native 
- External LB: routing to specific IP
- Service external IP: NAT service
- NodePort: static assign node bound IP to a resource

$ oc expose service $app1 --hostname ${app1}.${ocp_wildcard}
# Better to create via WebConsole
$ oc create route edge --service $app1 --hostname ${app1}.${ocp_wildcard} --port $appport --key $fullpathcertkey --cert $fullpathcert
# Set pod with cert/key mounted volume and ensure SUBJECT matches $hostname --port $appport
$ oc create route passthrough --service $app1 --hostname ${app1}.${ocp_wildcard} 
```

### Network Policies
Network policy that take a list of objects can either be combined in the same object or listed as multiple objects. 
If combined, the conditions are combined with a logical AND.
If separated in a list, the conditions are combined with a logical OR. 
The logic options allow you to create very specific policy rules.
```
$ oc label namespace $project1 name=network-1
```
AND vs OR
AND: 
```
ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: dev
      podSelector:
        matchLabels:
          app: mobile
```
OR:
```
ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: dev
    - podSelector:
        matchLabels:
          app: mobile
```

Default Block: Basically just add a policy with blank podSelector and **no** igress rules which will block anything
```
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: default-deny
spec:
  podSelector: {}
```

Allow only from router: Make sure to tag the router with the specific tag (default in OCP)
```
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: allow-from-ingress
spec:
  podSelector: {}
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          - network.openshift.io/policy-group: ingress
          - network.openshift.io/policy-group: monitoring
```

## 4. Schedulling
Red Hat OpenShift Container Platform supports the common data center concepts of zones and regions by using 
• Node labels
• Affinity rules
• Anti-Affinity rules
The process to schedule a node follow filtering nodes (based on selector/tolerations), filtering based on resource availability, filtering based on HW requirements(gpu).  
Then priotizing the filterd node list based on affinity/anti-affinity and finally selecting the best fit for pod scheduling based on overall node score or round-robin selection.
This is performed by the scheduller 

### Leveraging Labeling
This is why Labing nodes based on Region/Zones is critical. 

```
Add a label:
$ oc label node $node1 region=infra
Overwrite a label:
$ oc label node $node1 region=apps --overwrite=true
Remove a label:
$ oc label node $node1 region-
Show labels
$ oc get nodes -L region
$ oc get nodes --show-labels
```
```
Label using machinesets
$ oc get machinesets -n openshift-machine-api
$ oc edit machineset $machineset1 -n openshift-machine-api
spec:
  metadata:
    labels:
      env: apps
```
```
Project: 
Place all pods in a namespace
$ oc annotate namespace $project1 openshift.io/node-selector="env=apps" --overwrite

Deployment: 
Place pods in a deployment
$ oc patch deployment/$app1 --patch '{"spec":{"template":{"spec":{"nodeSelector":{"env":"apps"}}}}}'
$ oc edit deployment/$app1
spec:
  nodeSelector:
    env: apps
```

### Quota and Limits

You can control the use of resouce based on a deplo
A project can contain multiple `ResourceQuota` objects.

A `LimitRange` resource, also called a limit, defines the default, minimum, and maximum values for compute resource requests and limits for a single pod or for a single container defined inside the project.

```
$ oc get quota
$ oc create quota ${project1}-quota --hard=memory=2Gi,cpu=200m,pods=10 -n $project1
$ oc describe quota -n project1
$ oc delete quota ${project1}-quota -n $project1
```
Create Limits
$ oc get limits

No `oc` command to create limit-ranges. See sample yaml below that defines limits by type of resource
```
apiVersion: "v1"
kind: "LimitRange"
metadata:
  name: "project1-resource-limits"
spec:
  limits:
    - type: "Pod"
      max:
        cpu: "2"
        memory: "1Gi"
      min:
        cpu: "200m"
        memory: "16Mi"
    - type: "Container"
      max:
        cpu: "2"
        memory: "1Gi"
      min:
        cpu: "100m"
        memory: "8Mi"
      default:
        cpu: "300m"
        memory: "200Mi"
      defaultRequest:
        cpu: "200m"
        memory: "100Mi"
      maxLimitRequestRatio:
        cpu: "10"
```
```
$ oc create -f project1-resource-limits.yaml -n $project1
$ oc describe limits -n $project1
$ oc delete limit project1-resource-limits -n $project1
```
### Project Template
Creating project templates creates a standard way to apply previous constraints on a namespace in a general manner
Tying all the previous things together to apply Quotas, Limits, Network Policies

Creating a templete yaml
```
$ oc adm create-bootstrap-project-template -o yaml > project_template.yaml
```
This can be populated to enforce 
- labling
- quota 
- limits
- network polocies
Update each section to include (yaml list) each resouce item. 

### Scaling 
How to increase the pods in your dc/deployment
Manually
```
$ oc scale --replicas 4  deployment/$app1
```
AutoScale
```
$ oc autoscale deployment/$app1 --min 2 --max 10 --cpu-percent 80
$ oc get hpa
```

## 7. Cluster updates

### Updating a cluster with internet access
```
$ oc get clusterversion
$ oc adm upgrade --to=<version>
$ watch -n30 oc get clusterversion
$ oc describe clusterversion
```
### Updating a cluster restricted network access
```
$ oc get clusterversion
$ oc adm upgrade --to-image=$uri_to_image_location --allow-eplicit-upgrade --force 
$ watch -n30 oc get clusterversion
$ oc describe clusterversion
```

## 8. WebConsole

### Key Items & why
```
```

## 9. TroubleShooting

### Key Items & why
```
```

## Misc. 
### Make Node Schedulable
```
$ oc edit schedulers.config.openshift.io cluster
spec:
  mastersSchedulable: true 
  policy:
    name: ""
```
### Unschedule, Drain, Delete Node
```
$ oc adm cordon $node1
$ oc adm drain $node1 $node2 --delete-local-data --force=true  --dry-run=true
$ oc adm delete node $node1
$ oc adm uncordon $node1
$ oc scale --replicas=2 machineset $ms_name -n openshift-machine-api
```

### Create a private key, CSR and certificate.

```
$ openssl genrsa -out php.key 2048
```
```
$ openssl req -new -key php.key -out php.csr  \
  -subj "/C=GB/ST=London/L=London/O=IT/OU=IT/CN=www.example.com"
```
```
$ openssl x509 -req -days 366 -in php.csr  \
      -signkey php.key -out php.crt
```
Generate a route using the above certificate and key:
```
$ oc get svc
$ oc create route edge --service=my-php-service \
    --hostname=www.example.com \
    --key=php.key --cert=php.crt \
    --insecure-policy=Redirect
```
