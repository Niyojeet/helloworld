# helloworld
A flask based python webapp

## Pulumi Setup
- mkdir pulumi-k3s
- cd pulumi-k3s/
- curl -fsSL https://get.pulumi.com | sh
- sudo apt install pipx
- pipx install pulumi pulumi-aws --include-deps
- pipx ensurepath

## Provisioning EC2 with k3s installed 
- aws configure
  - Create an access key pair in AWS console and configure it using aws cli
- Create a public-pvt key pair to be used for ssh into the ec2 instance
   - ssh-keygen -t rsa -b 4096 -f ~/.ssh/devops-key
   - chmod 400 ~/.ssh/devops-key
- Create an account in https://app.pulumi.com/ 
- Generate a token and copy it as it will be needed for setting up Pulumi project
- pulumi up
  - provide the necessary details as asked by pulumi and you will able to see the details of the infrastructure to be provisioned
  - The listed infrastructure as per your __main__.py will be created

## Setting Github Actions workflow
- Configurre Secrets
  -  DOCKER_USERNAME: Your Docker Hub username.
  -  DOCKER_PASSWORD: Your Docker Hub password or a personal access token.
  -  KUBECONFIG: Your Kubernetes configuration file, which contains the credentials and details for connecting to your Kubernetes cluster.
  -  EC2_HOST: Your EC2 instance public IP
  -  EC2_USER: Your EC2 instance username
  -  SSH_PRIVATE_KEY: Your SSH private key 
