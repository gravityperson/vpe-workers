# VK Profile Exporter

## Requirements
The following scripts have been tested using Python 3.9
 
To run these scripts you need such requirements.  
To satisfy them you should run the following:
```shell script
pip3 install -r requirements.txt
```
This will install dependencies the scripts needed

## Run Consumer
To run consumer that would log in and request needed information you have to run the following:
```shell script
clear; ./profile-info.py
```

## Run Producer
To test that consumers work you need to run the following:
```shell script
clear; ./post-message.py ${LOGIN} ${PASWWORD}
```
Where `${LOGIN}` and `${PASSWORD}` the credentials from VK correspondingly
