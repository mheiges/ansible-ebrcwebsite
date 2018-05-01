import os.path
import yaml
import json
import re
import urllib2
from ansible.utils.vars import merge_hash
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):

  TRANSFERS_FILES = False

  def _set_args(self):
    """ Set instance variables based on the arguments that were passed
    """

    self.VALID_ARGUMENTS = (
      'settings_file'
    )

    for arg in self._task.args:
      if arg not in self.VALID_ARGUMENTS:
        err_msg = '{0} is not a valid option in debug'.format(arg)
        raise AnsibleError(err_msg)

    self.settings_file = self._task.args.get('settings_file', None)

    if not self.settings_file:
      raise AnsibleError('settings_file not defined')

    if not os.path.isfile(self.settings_file):
      raise AnsibleError("settings_file '{}' not found".format(self.settings_file))


  def run(self, tmp=None, task_vars=None):
    self._set_args()
    if task_vars is None:
      task_vars = dict()
    result = super(ActionModule, self).run(tmp, task_vars)
    usersettings = self.load_settings_file(self.settings_file)
    dashboardsettings_file = self.fetch_dashboard_json_to_file(usersettings['dashboard'])
    dashboardsettings = self.load_settings_file(dashboardsettings_file)
    presettings = reduce(merge_hash, [dashboardsettings, usersettings])
    settings = reduce(merge_hash, [presettings, self.derived_settings(presettings)])
    result['ansible_facts'] = { 'ebrc': settings }
    return result

  def derived_settings(self, presettings):
    regex = re.compile(r'^jdbc:[^@]+@', re.IGNORECASE)
    return {
      'website': {
        '_path': '/var/www/' + presettings['wdk']['modelname'] + '/' + presettings['tomcat']['webapp']
      },
      'wdk': {
        'modelconfig': {
          'appdb': {'_alias': regex.sub('', presettings['wdk']['modelconfig']['appdb']['connectionurl']) },
          'userdb': {'_alias': regex.sub('', presettings['wdk']['modelconfig']['userdb']['connectionurl']) },
          'accountdb': {'_alias': regex.sub('', presettings['wdk']['modelconfig']['accountdb']['connectionurl']) },
        }
      }
    }

  def fetch_dashboard_json_to_file(self, dash_data):
    dash_host = dash_data['hostname']

    if 'token' in dash_data:
      dash_token = dash_data['token']
    else:
      dash_token = None

    dash_uri = "https://{}/dashboard/json".format(dash_host)

    try:
      request = urllib2.Request(dash_uri)
      if dash_token is not None:
        request.add_header("x-dashboard-security-token", dash_token)
      response = urllib2.urlopen(request)
      content = response.read()
    except urllib2.HTTPError, e:
      print "HTTPError with %s: %s" % (dash_uri, e)
      raise
    except Exception, e:
      print "Exception with %s: %s" % (dash_uri, e)
      raise

    try:
      data = json.loads(content)
    except Exception, e:
      print "Exception reading /dashboard json: %s" % (e)
      raise

    dashboard_file = dash_host + '_dashboard.json'
    dash_fh = open(dashboard_file, 'w')
    dash_fh.write(json.dumps(data, indent=2))
    return dashboard_file

  def load_settings_file(self, settings_file):
    with open(settings_file, 'r') as stream:
      try:
        usersettings = yaml.load(stream)
        return usersettings
      except yaml.YAMLError as exc:
        print(exc)
