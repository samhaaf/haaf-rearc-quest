# Haaf-Rearc-Quest

This repo solves the Rearc Data Quest: https://github.com/rearc-data/quest

You can find the mirror in this S3 bucket: "haaf-rearc-quest"

This is developed to be built from an Amazon Linux 2 environment. I use Cloud9.

To install the deps and requirements:

```
git clone https://github.com/samhaaf/haaf-rearc-quest.git
cd ./haaf-rearc-quest
make install
```

If this doesn't work right away, you may need to install python3.9 and set an alias:

```
sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel bzip2-devel libffi-devel
sudo yum -y install wget
wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz
tar xvf Python-3.9.10.tgz
cd Python-*/
./configure --enable-optimizations
sudo make altinstall
echo "alias python=python3.9" >> ~/.bashrc
source ~/.bashrc
```

Then, to test individual modules locally:

```
make test-csvs
make test-api
make test-scrape
make test-report
```

And to deploy the whole thing to aws:

```
make apply
```

If you get an error here regarding an IAM role, you might need to (disable managed credentials)[https://github.com/aws-samples/aws-workshop-for-kubernetes/issues/391] and then write new ones to ~/.aws/credentials.

Finally, to tear it all back down:

```
make clean
```

EOF
