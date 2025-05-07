# helloworld
A flask based python webapp

## Pulumi Setup
mkdir pulumi-k3s
cd pulumi-k3s/
curl -fsSL https://get.pulumi.com | sh
sudo apt install pipx
pipx install pulumi pulumi-aws --include-deps
pipx ensurepath
