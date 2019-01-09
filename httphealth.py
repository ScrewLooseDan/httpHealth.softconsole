# httphealth.py was unabashedly stolen directly from networkhealth.py by  Screw Loose Dan
# Only additional import was requests and also modified the logsupport

# See bottom of script for usage

import config
import alerttasks
from logsupport import ConsoleDetail, ConsoleWarning, ConsoleInfo
import logsupport
import requests
from stores import valuestore

class httpHealth(object):
	def __init__(self):
		self.LastState = {}

	@staticmethod
	def httpGET(dest):
		ok = False
		headers = {'User-Agent': 'SoftConsole.httpHealth.1.0'}
		try:
			r = requests.get(dest, headers=headers, timeout=5)
			status = str(r.status_code)
			if (r.status_code == 200):
				logsupport.Logs.Log(dest + " returned status -  " + status, severity=ConsoleDetail)
				ok = True
			else:
				logsupport.Logs.Log(dest + " returned status -  " + status, severity=ConsoleInfo)
		except requests.ConnectionError:
			logsupport.Logs.Log("Connection Error! - " + dest, severity=ConsoleInfo)
		except requests.exceptions.Timeout:
			logsupport.Logs.Log("Timeout getting to " + dest, severity=ConsoleInfo)
		except requests.exceptions.RequestException as e:
			# Hopefully this catches all other errors
			logsupport.Logs.Log("RequestException " + dest + " error: " + e, severity=ConsoleInfo)
		return ok

	def Do_GET(self, alert):
		# set variable name to 0 if ipaddr was accessible and now is not
		var = valuestore.InternalizeVarName(alert.param[1])
		if alert.param[0] not in self.LastState:
			self.LastState[alert.param[0]] = True  # assume up to start
		config.DS.Tasks.StartLongOp()
		if self.httpGET(alert.param[0]):
			if not self.LastState[alert.param[0]]:
				self.LastState[alert.param[0]] = True
				valuestore.SetVal(var,1)
				logsupport.Logs.Log("http GET successful to: " + alert.param[0], severity=ConsoleDetail)
		else:
			if self.LastState[alert.param[0]]:
				# was up now down
				self.LastState[alert.param[0]] = False
				valuestore.SetVal(var, 0) # Set down seen
				logsupport.Logs.Log("http GET NOT successul to: " + alert.param[0], severity=ConsoleWarning)
		config.DS.Tasks.EndLongOp()


alerttasks.alertprocs["httpHealth"] = httpHealth

""" #### Usage Notes ####

# Please remember to be kind to your system admins, and don't flood them.
###########
# If it's not your server, you probably don't want to be using this.
###########
# I'll show two different examples...
# You'll need to define local variables in a config file.  These can be anything, just make them logical for yourself:

[Variables]
InternetSiteUp = 1
LocalSiteUp = 1


# And define the alerts like:

[Alerts]
[[InternetSite]]
Type = Periodic
Interval = 300 seconds
Invoke = httpHealth.Do_GET
Parameter = 'https://www.example.com/',LocalVars:InternetSiteUp
          [[InternetSiteAlert]]
          Type = VarChange
          Var = LocalVars:InternetSiteUp
Test = NE
Value = 1
Invoke = InternetSiteScreen

[[LocalServer]]
Type = Periodic
Interval = 60 seconds
Invoke = httpHealth.Do_GET
Parameter = 'http://192.168.0.0.1/',LocalVars:LocalSiteUp
          [[LocalServerAlert]]
          Type = VarChange
          Var = LocalVars:LocalSiteUp
Test = NE
Value = 1
Invoke = LocalServerScreen


# And define what you want the alert screens to look like:

[InternetSiteScreen]
type = Alert
BackgroundColor = white
MessageBack = maroon
CharColor = black
Message = Internet Site, Unreachable
CharSize = 30,
DeferTime = 10
BlinkTime = 1
KeyColor = maroon
	[[Action]] 	# NOTE - I can't actually get the acknowledge feature to work
	type = SETVAR
	Var = LocalVars:InternetSiteUp
	label = Acknowledge, Outage

[LocalServerScreen]
type = Alert
BackgroundColor = white
MessageBack = maroon
CharColor = black
Message = Local Server, Unreachable
CharSize = 30,
DeferTime = 10
BlinkTime = 1
KeyColor = maroon
	[[Action]]
	type = SETVAR
	Var = LocalVars:LocalSiteUp
	label = Acknowledge, Outage

# I think that should do it for the examples.  

#################################################
Just note, the parameter should be defined like:
Parameter = '<Full URL>',<VARIABLE>
#################################################
And remember - keep the interval sane!!
#################################################

"""

