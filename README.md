# CRC Data Visualization Website Template

## Overview
This template is created for the researchers and students at Rice University.
This template is used for building a visualization website powered by ploty dash for time-series data of CRC. The template only support line and scatter plot currently.
This template will automatically generating line and scatter plots of the given data with group by and filter supported regardless of the schema of the data as long as the data meets the following requirements. 

## Dataset Requirements
The template can embed the data and build a website on it as long as the dataset:
* is structural.
* is in .csv form.
* is well-preprocessed. This template does not support data cleaning module.
* is a time-series data with at least one column to indicate the time.
* has the time column in "yyyy-mm-dd" format.

Note: the data schema is similar to a time-series data with one column indicating the time and multiple other numerical columns indicating the values. So basically we expect the data can be well represented by a line plot or scatter plot with the horizontal coordinate of time.

## Get Started

### Setup a Orion VM
At first, the users of this template need to have an Orion account setup.
Once you have one, [login to your orion account](https://orion.crc.rice.edu/)

#### Add public ssh key.
- click your name in the top right corner
- click "settings" and click the "Update SSH Key" panel
- put in the contents of your public ssh key in the box and click "Update SSH Key"

#### Create a virtual machine.
- go to VMs in the left-hand navigation
- click on the green button with a plus sign icon
- select "rocky 8.9 cloud vm - small" in the list
- click the "create" button
- give the instance a name ("netid-project" or something)
- leave the rest of the default settings
- find your vm instance in the dashboard and click on it
- remember the instance's ip address

when you first instantiate a vm, there are some post-deploy scripts that will run to perform some extra configuration (including creating a user account with your netid with sudo access and inserting your public key). You might want to wait five minutes or so before trying to connect the first time.

you should be able to access the vm through vnc in the orion web ui by clicking the button with the monitor icon and selecting "vnc". you'll be taken to a vnc session with the instance.
you can also ssh to the instance using ssh <netid>@<ip>. depending on your ssh configuration, you may have to use the -i option to specify the location of your private key. For example: `ssh -i ~/.ssh/<key> <user>@<ip>`

#### Connect to the RDF share in the VM
The vm template in orion is already configured to mount the rdf share. you can do so by entering `mount /rdf` on the command line which mounts the top-level of the share. you can navigate down to your folder at `/rdf/crc/<netid>`.

#### Deleting the VM
- log back in to https://orion.crc.rice.edu
- find your vm instance and click on it
- click the red button with the trash can icon and click "terminate"

### Configure Docker in the VM
First, make sure you ssh to your VM. And inside your VM do:
```shell
### Install Docker engine

sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf config-manager --setopt="docker-ce-stable.baseurl=https://download.docker.com/linux/centos/8/x86_64/stable" --save
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo systemctl enable docker --now
sudo systemctl enable containerd --now

### Add the user to the Docker group

sudo usermod -aG docker $USER
```

### Fork and Clone this Tempelate Repository to your VM
When you are at this [repository](https://github.com/cs185/crc-datasite-template), just click the "Fork" button on the top-right hand.
In the new page pops up, click the green button with "Create Fork".
Then once you confirm that there is a same repo under your github account:
- ssh to your VM
- try following to clone the repo to your home directory:
```shell
git clone https://github.com/<github-username>/crc-datasite-template $HOME/crc-datasite-template
```

### Get the Data Source You Want to Visualize with the Template
Firstly, you need to make a directory `resource/` under `src/`.
To visualize the data, you need to put the data to the `src/resource/` folder where the program will get the data from.
There are two ways you can do this depending on where the data is from
#### Get it from an Online Data Provider Using Curl
```shell
curl -o ~/src/resrouce/<dataset-name>.csv https://<example.com>/<data>/<dataset-name>.csv
```

#### Upload it to VM from your local machine
If you are using Mac, go to finder > go > connect to server > and enter
[smb://smb.rdf.rice.edu/research/crc/<netid>]
you'll be prompted for your netid credentials. Once you're connected, make sure you can create a file in your directory and delete the file
Now you can do:
- put the data source, say `dataset-name.csv` into this file on your local machine
- ssh to your VM
- try
```shell
cp /rdf/crc/<netid>/dataset-name.csv ~/crc-datasite-template/src/resource/
```

### .env configuration file
After having the dataset, in most cases, the only thing that needs to be modified is the .env file if the logic behind the template works fine
There are five fields in the file related to a given data and have a big impact on the representation of the data:
* DATA_DIR -- the path to the data source, usually `./src/resource/<dataset-name>.csv`
* DATE_COL -- for specifying the time column of the data
* RATIO_COLS -- for specifying the columns which contain several groups of the data and can be used in "group by" manner in visualization
* DROP_DOWN_COL -- for specifying the column which contain several categories for the data and can be used as data filters
* SITE_NAME -- the name of the website
* AUTHOR -- the author

Note: the RATIO_COLS and DROP_DOWN_COL can be left with no value specified if we do not need them. It will not influence the data visualization.
Example on what to put in this file is given below.

### Build the Docker image and run the container

```shell
cd ~/crc-datasite-template
docker compose up --build -d
```
the -d option here means you want your containers running in detach mode in the background without interrupting the current shell. If unneseccary, remove the -d option.

If no error comes out, now you can access to the app via [<ip-of-your-vm>:8000]

### Stop the container when done

```shell
cd ~/crc-datasite-template
docker compose down
```

## Example of the application running
In this example, we use the [covid mortality dataset](https://data.cdc.gov/api/views/xkkf-xrst/rows.csv?accessType=DOWNLOAD&bom=true&format=true%20target=)
The application showing the visualization of the dataset is running on http://10.134.196.74:8000
In this web page, the "Target" dropdown can choose the a value and the data shown will be the entries whose value of a specific column (the one you specified at the `DROP_DOWN_COL` in the `.env` file) equals to the chosen value.

In this example, if I choose "Ohio", the data shown would only be the entries with "State" column equals to "Ohio".
<img width="187" alt="image" src="https://github.com/cs185/crc-datasite-template/assets/142818430/bcbb99ff-6e92-4c78-af82-8d84b4bbe7b6">

The "Date Range" picker can choose the date range within which you want your shown data is. The date values come from the field of the data you specified at the `DATE_COL` in the `.env` file. Here I picked this value.
<img width="230" alt="image" src="https://github.com/cs185/crc-datasite-template/assets/142818430/3b6e38cb-0cdd-4780-985b-8eafb1458016">

The "Data Options" picker can choose the fields of the data you want to show in the plot. And the result of the above option would be:
<img width="1420" alt="image" src="https://github.com/cs185/crc-datasite-template/assets/142818430/a8f9a90d-6982-4dfa-988d-8f4cc2f7d186">

If I choose all the five fields in the "Data Options":
<img width="1420" alt="image" src="https://github.com/cs185/crc-datasite-template/assets/142818430/3ec7a87c-c6c2-4d5f-bdd7-f3ba44236e5c">

The "Group by" Selector can choose a field. And the data will be grouped by the values in the field. Here is an example with "Group by" selected as "State":
<img width="1420" alt="image" src="https://github.com/cs185/crc-datasite-template/assets/142818430/cc7104e5-db9c-4ead-92d6-f7673653c6d8">

If we choose "Disable", the group by function will be disabled:
<img width="1420" alt="image" src="https://github.com/cs185/crc-datasite-template/assets/142818430/0c603fd8-c75e-4e3d-85af-e45130bb1ae1">



