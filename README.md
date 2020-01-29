# Easy2Monitor

Easy2Monitor is a small tool to regularly check http, smtp and imap connections for availability.
It's meant to be simply and easy to configure as well as easy to use. 

## Usage
After cloning the repository, copy or rename `/.env_dist` to `/.env`

### With docker-compose (recommended way) 
Just run `docker-compose up`. Once the project was built and runs, visit 
`http://localhost:8000`. After a couple of seconds, first data should be visible. 

### With python
You have to set the needed environment-variables which are defined in `/.env_dist` before running the application. In `/set_env.sh` there's an example how to do this.

Once the environment variables are set, either run `/src/runApp.sh` or `python /src/server.py`
Be aware that you'll ned to run an rabbitmq server on your own and configure the app accordingly.

## Check-Configuration
To add or remove checks, there are three configuration files, one for each supported protocol:
- `/check_definitions/http_check_definitions.json`
- `/check_definitions/imap_check_definitions.json`
- `/check_definitions/smtp_check_definitions.json`

Examples for the configuration are in the files. 

## Advanced usage
Easy2Monitor is built in a way which makes it possible to run the checking processes almost everywhere and while 
we run them just as separate threads in the default configuration, it's easy to spread them out to several different 
machines, making it possible to monitor, for example, from different networks. 

Utilizing amqp protocol, the monitoring threads are just sending their check-results to a central rabbitmq server. 
This central server then adds all monitoring results from the queue to it's database and provides access with a simple api-call.
That said, it's obvious that you'd should run the amqp server in a HA setup for production usage.    