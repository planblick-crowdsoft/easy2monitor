# Easy2Monitor
![alt Easy2Monitor Screenshot](https://crowdsoft.net/cdn/images/e2m_screenshot.png)

Easy2Monitor is a small tool to regularly check http, smtp and imap connections for availability.
It's meant to be simply and easy to configure as well as easy to use. 

## Usage
After cloning the repository, copy or rename `/.env_dist` to `/.env` and adjust `.env` to your like.

### With docker-compose (recommended way) 
Just run `docker-compose up`. Once the project was built and runs, visit 
`http://localhost:8000`. After a couple of seconds, first data should be visible. 

### Directly from linux bash (not fully tested yet)
Make sure you have python as well as needed python packages installed (`pip3 install -r requirements.txt`)
`cd /src` and run `./runAppManually.sh`
Be aware that you'll need to run an rabbitmq server on your own and configure the app accordingly.

### Directly from windows cmd
Make sure you have python, pip and the needed python packages installed (`pip install -r requirements.txt`)
`cd /src` and run `./runApp.bat` 
Be aware that you'll need to run an rabbitmq server on your own and configure the app accordingly

## Check-Configuration
To add or remove checks, there are three configuration files, one for each supported protocol:
- `/check_definitions/http_check_definitions.json`
- `/check_definitions/imap_check_definitions.json`
- `/check_definitions/smtp_check_definitions.json`

Examples for the configuration are in the files. 
