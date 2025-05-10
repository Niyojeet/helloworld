"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws
# Create a key pair using the public key
key_pair = aws.ec2.KeyPair("k3s-key",
  public_key=open("/root/.ssh/devops-key.pub").read()
)
#hard coding aws-region, can be commented out to use the default region as per client machine
aws.config.region = "ap-south-1"
# 1. Use Ubuntu 22.04 AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical (Ubuntu)
    filters=[{
      "name": "name",
      "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
    }],
 )

# 2. Create a security group allowing SSH and HTTP
sec_group = aws.ec2.SecurityGroup("k3s-sec-group",
    description="Allow SSH and HTTP",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 443, "to_port": 443, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{
        "protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],
    }]
)

#installing k3s in ec2 instancce
user_data = """#!/bin/bash
exec > /var/log/user-data.log 2>&1
set -xe

# Wait for network to be ready
sleep 15

# Update and install dependencies
apt-get update -y
apt-get install -y curl

sleep 10

# Install k3s
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh -

# Wait for kubeconfig to be generated
sleep 10

# Setup kubeconfig for ubuntu user
mkdir -p /home/ubuntu/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
chown -R ubuntu:ubuntu /home/ubuntu/.kube
"""


# 4. Create EC2 instance
ec2 = aws.ec2.Instance("k3s-node",
    instance_type="t3a.small", 
    vpc_security_group_ids=[sec_group.id],
    ami=ami.id,
    user_data=user_data,
    key_name=key_pair.key_name,  
    tags={"Name": "Pulumi-K3s"},
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=20,              
        volume_type="gp3",            
        delete_on_termination=True
    )
)

# 5. Export the public IP
pulumi.export("k3s_node_ip", ec2.public_ip)
