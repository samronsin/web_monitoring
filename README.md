Simple cron-based tool to test health of web applications.

## Installing a new application to test

### 1. Create a new subdirectory in the services directory and a config.json file inside
Your directory tree should look like this:
```tree
web_monitoring
+--check_webservice.py
+--services  
   +--example
      +--config.json
```
### 2. Edit the config.json file in this directory
The file config.json should look like this:
```json
{
	"alert": {
		"sender": {
			"address": "example@example.com",
			"login": "example",
			"password": "xxxxxxxxx",
      "server": "smtp.example.com",
      "port": 587
		},
		"receivers": ["target@example.com"]
	},
	"checks": {
		"is_alive": {
			"urls": ["http://www.example.com"],
			"state_ok_message": "Subject: service is up\n",
			"state_problem_message": "Subject: service is down\n"
		},
		"thorough": {
			"urls": ["http://www.example.com/test1, http://www.example.com/test2"],
			"state_ok_message": "Subject: service has issues\n",
			"state_problem_message": "Subject: service issues resolved\n"
		}
	}
}
```
`is_alive` and `thorough` are examples of checks that can be called in turn by `check_webservice.py`, you can configure as many services and as many checks per service.

### 3. Test your configuration
`web_monitoring/check_webservice.py --service example --check is_alive`
If your configuration valid and your service is up, you should receive an email.
### 4. Install a new cron tab
`$ crontab -e`  
`*    * * * *   	~/web_monitoring/check_webservice.py --service example --check is_alive`
