#! /bin/bash
sudo mkdir /tmp/bucket
sudo mkdir /tmp/output

apt-get update
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

apt-get update
apt-get install gcsfuse -y
gcsfuse -o nonempty bctv-storage /tmp/bucket

# apt-get install python-pip -y
apt-get install python3-pandas -y
apt-get install python3-sklearn -y
# apt-get install python-pandas -y
# apt-get install python-sklearn -y

sudo python3 /tmp/bucket/model.py