from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.applications import Application

###
# Range Constraint validation functions
###
def is_valid_value(rconst):
    """
    Is value-type valid. Expects either integer or float
    :param rconst: RangoConstraint to be validated
    :return: is value-type valid
    """
    from experiment_server.utils.configuration_tools import is_valid_type_value

    return is_valid_type_value('integer', rconst.value) or is_valid_type_value('float', rconst.value)


def exists_app_and_ck(app_id, configkey_id):
    """
    Checks connection between Application and ConfigurationKey
    :param app_id:
    :param configkey_id:
    :return: Does ConfigurationKey exist in given Application
    """
    return ConfigurationKey.get(configkey_id).application_id == app_id


def is_valid_operator(rconst):
    """
    Checks that operator is one of the following: 1 - equals, 2 - less or equal than, 3 - less than,
    4 - greater or equal than, 5 - greater than, 6 - not equal
    :param rconst: RangeConstraint to be validated
    :return: Is valid operator
    """
    return rconst.operator_id <= 6



def is_valid_rangeconstraint(app_id, configkey_id, rconst):
    """
    Range Constraint validation. Only this function should be called during validation.
    :param app_id: Application in which configurationkey belongs to
    :param configkey_id: Configurationkey on range is being set
    :param rconst: RangeConstraint to be validated
    :return: True: RangeConstraint is valid, False: RangeConstraint is not valid
    """
    return exists_app_and_ck(app_id, configkey_id) and is_valid_value(rconst) and is_valid_operator(rconst)

###
# RangeConstraint controller-functions
###
@view_defaults(renderer='json')
class RangeConstraints(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        CORS-options
    """
    @view_config(route_name='rangeconstraints', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='rangeconstraint', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='rangeconstraints', request_method="GET")
    def rangeconstraints_GET(self):
        """ List all rangeconstraints for ConfigurationKey with GET method """
        app_id = self.request.swagger_data['appid']
        confkey_id = self.request.swagger_data['ckid']
        rangeconstraints = RangeConstraint.query()\
            .join(ConfigurationKey)\
            .filter(ConfigurationKey.id == confkey_id)\
            .join(Application)\
            .filter(Application.id == app_id)
        return list(map(lambda _: _.as_dict(), rangeconstraints))

    @view_config(route_name='rangeconstraint', request_method="DELETE")
    def rangecontraints_DELETE_one(self):
        """ Find and delete one rangeconstraint by id with DELETE method """
        app_id = self.request.swagger_data['appid']
        confkey_id = self.request.swagger_data['ckid']
        rc_id = self.request.swagger_data['rcid']
        rangeconstraint = RangeConstraint.get(rc_id)

        try:
            # Checks if ConfigurationKey exists with given Application
            if not ConfigurationKey.get(confkey_id).application_id == app_id:
                raise Exception('Application with id %s does not have' % app_id +
                    ' ConfigurationKey with id %s' % confkey_id)
            # Checks if given RangeConstraint is owned by ConfigurationKey
            elif not rangeconstraint.configurationkey_id == confkey_id:
                raise Exception('ConfigurationKey with id %s does not' % confkey_id +
                    ' have RangeConstraint with id %s' % rc_id)

            RangeConstraint.destroy(rangeconstraint)
        except Exception as e:
            print(e)
            print_log(datetime.datetime.now(), 'DELETE', '/rangeconstraint/' + str(rc_id),
                      'Delete rangeconstraint', 'Failed')
            return self.createResponse(None, 400)

        print_log(datetime.datetime.now(), 'DELETE', '/rangeconstranit/' + str(rc_id),
                  'Delete rangeconstraint', 'Succeeded')
        return {}

    @view_config(route_name='rangeconstraints', request_method="POST")
    def rangecontraints_POST(self):
        """ Create new rangeconstraint for specific configurationkey """
        req_rangec = self.request.swagger_data['rangeconstraint']
        configkey_id = self.request.swagger_data['ckid']
        app_id = self.request.swagger_data['appid']

        rconstraint = RangeConstraint(
            configurationkey_id=configkey_id,
            operator_id=req_rangec.operator_id,
            value=req_rangec.value
        )

        try:
            # Checks if Configuration with such connection to Application exists
            if not is_valid_rangeconstraint(app_id, configkey_id, rconstraint):
                raise Exception('Application with id %s does not have' % app_id +
                    ' ConfigurationKey with id %s' % configkey_id)
            RangeConstraint.save(rconstraint)
        except Exception as e:
            print_log(datetime.datetime.now(), 'POST', '/applications/%s/' % app_id +
                'configurationkeys/%s/rangeconstraints' % configkey_id,
                'Create new rangeconstraint for configurationkey', 'Failed: %s' % e)
            return self.createResponse({}, 400)

        print_log(datetime.datetime.now(), 'POST', '/applications/%s' % app_id +
            '/configurationkeys/%s/rangeconstraints' % configkey_id,
            'Create new rangeconstraint for configurationkey', 'Succeeded')
        return rconstraint.as_dict()

    @view_config(route_name='rangeconstraints', request_method="DELETE")
    def rangeconstraints_for_configuratinkey_DELETE(self):
        """
            Delete all rangeconstraints of one specific configurationkey
            To include all the database connection checks which rangecontraints_DELETE_one contains, it is used in this
            function.
        """
        configkey_id = self.request.swagger_data['ckid']
        app_id = self.request.swagger_data['appid']
        configurationkey = ConfigurationKey.get(configkey_id)
        errors = 0

        try:
            for rc in configurationkey.rangeconstraints:
                # Set rangeconstraint's id, so rangecontraints_DELETE_one can use it
                self.request.swagger_data['rcid'] = rc.id
                if not self.rangecontraints_DELETE_one() == {}:
                    errors += 1
        except Exception as e:
            print(e)
            errors += 1
        finally:
            if (errors > 0):
                print_log(datetime.datetime.now(), 'DELETE', '/application/%s' % app_id +
                    '/configurationkeys/' + str(configkey_id) +'/rangeconstraints',
                    'Delete rangeconstraints of configurationkey', 'Failed')
                return self.createResponse(None, 400)

        return {}
