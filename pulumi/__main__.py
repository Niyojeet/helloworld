import pulumi
import pulumi_aws as aws

# ---------- CONFIG ----------
aws.config.region = "ap-south-1"

# ---------- SSH Key ----------
key_pair = aws.ec2.KeyPair("k3s-key",
    public_key=open("/root/.ssh/devops-key.pub").read()
)

# ---------- VPC ----------
vpc = aws.ec2.Vpc("k3s-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={"Name": "k3s-vpc"}
)

# ---------- Internet Gateway ----------
igw = aws.ec2.InternetGateway("k3s-igw",
    vpc_id=vpc.id,
    tags={"Name": "k3s-igw"}
)

# ---------- Subnet ----------
subnet = aws.ec2.Subnet("k3s-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="ap-south-1a",
    tags={"Name": "k3s-subnet"}
)

# ---------- Route Table ----------
route_table = aws.ec2.RouteTable("k3s-rt",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id,
    }],
    tags={"Name": "k3s-rt"}
)

# ---------- Associate Route Table ----------
aws.ec2.RouteTableAssociation("k3s-rta",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# ---------- Security Group ----------
sec_group = aws.ec2.SecurityGroup("k3s-sg",
    description="Allow SSH/HTTP/HTTPS",
    vpc_id=vpc.id,
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 443, "to_port": 443, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{
        "protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],
    }]
)

# ---------- AMI for Ubuntu 22.04 in ap-south-1 ----------
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],
    filters=[{
        "name": "name",
        "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
    }]
)

# ---------- User Data to install K3s ----------
user_data = """#!/bin/bash
exec > /var/log/user-data.log 2>&1

curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644" sh -

mkdir -p /home/ubuntu/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
chown -R ubuntu:ubuntu /home/ubuntu/.kube
"""

# ---------- EC2 Instance ----------
instance = aws.ec2.Instance("k3s-node",
    instance_type="t3a.small",
    ami=ami.id,
    subnet_id=subnet.id,
    associate_public_ip_address=True,
    vpc_security_group_ids=[sec_group.id],
    key_name=key_pair.key_name,
    user_data=user_data,
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=20,
        volume_type="gp3",
        delete_on_termination=True
    ),
    tags={"Name": "Pulumi-K3s"}
)

# ---------- Export Public IP ----------
pulumi.export("public_ip", instance.public_ip)
pulumi.export("k3s_node", instance.id)
