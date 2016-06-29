from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface


@view_defaults(renderer='json')
class Users:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	#5 List configurations for specific user
	@view_config(route_name='configurations', request_method="GET")
	def configurations_GET(self):
	#Also adds the user to the DB if it doesn't exist
		json = self.request.json_body
		username = self.request.headers['username']
		password = self.request.headers['password']
		userData = {'username': username, 'password': password}
		user = self.DB.checkUser(userData)
		self.DB.assignUserToExperiments(user.id)
		confs = self.DB.getConfigurationForUser(user.id)
		configurations = []
		for conf in confs:
			configurations.append({'key':conf.key, 'value':conf.value})
		return {'configurations': configurations}

	#6 List all users
	@view_config(route_name='users', request_method="GET", renderer='../templates/all_users.jinja2')
	def users_GET(self):
		return {'users': self.DB.getAllUsers()}

	#8 List all experiments for specific user 
	@view_config(route_name='experiments_for_user', request_method="GET", renderer='../templates/experiments_for_user.jinja2')
	def experiments_for_user_GET(self):
		id = self.request.matchdict['id']
		return {'user': self.DB.getUser(id), 'experiments': self.DB.getExperimentsUserParticipates(id)}

	#9 Save experiment data
	@view_config(route_name='events', request_method="POST")
	def events_POST(self):
		json = self.request.json_body
		value = json['value']
		username = self.request.headers['username']
		user = self.DB.getUserByUsername(username)
		self.DB.createDataitem({'user': user.id, 'value': value})

#curl -H "Content-Type: application/json" -H "id: 1" -X POST -d '{"value":"5"}' http://0.0.0.0:6543/events

	#10 Delete user
	@view_config(route_name='user', request_method="DELETE")
	def user_DELETE(self):
		#Browser need to refresh after deleting
		self.DB.deleteUser(self.request.matchdict['id'])

	@view_config(route_name='user', request_method="GET", renderer='../templates/user.jinja2')
	def user_GET(self):
		userId = self.request.matchdict['id']
		user = self.DB.getUser(userId)
		dataitems = self.DB.getDataitemsForUser(userId)
		experimentgroups = self.DB.getExperimentgroupsForUser(userId)
		return {'user':user, 'dataitems': dataitems, 'experimentgroups': experimentgroups}
	













	