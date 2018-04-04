#!/usr/bin/env python
#
# Zenoss JSON API example to interact with Impact
#
# This will copy the impact policy gates from one specified service 
# to a separate specified service.
#
# To run type:
#     python impact_api_copy_paste_policy_gates.py


from zenApiImpactRouterHelper import (
    zenApiImpactRouterHelper,
    IMPACT_ROOT
)
from pprint import pprint

api = zenApiImpactRouterHelper()

def getPolicies(serviceOrganizer, serviceName, contextUid, policyType):
    # Here is where you would iterate through a list of services to set policies on
    # or in this example, set one service
    #
    # The serviceUid needs to be the full path to the service, in the format:
    #  '/zport/dmd/DynamicServices/extra_examples/services/extra_examples/'

    #example output of the 'get'
    # Getting policies for /zport/dmd/DynamicServices/Payroll/services/Application
    #{u'data': [{u'dependentState': u'DOWN',
    #            u'id': u'a8010926-383e-486a-91e3-0d8a70eabed3',
    #            u'metaTypes': [],
    #            u'properties': {u'threshold': u'50'},
    #            u'state': u'ATRISK',
    #            u'triggerType': u'policyPercentageTrigger'},
    #           {u'dependentState': u'DOWN',
    #            u'id': u'7a733308-f97b-44a6-9937-1849df575461',
    #            u'metaTypes': [],
    #            u'properties': {u'threshold': u'100'},
    #            u'state': u'DOWN',
    #            u'triggerType': u'policyPercentageTrigger'}],
    # u'stateIsDown': False,
    # u'stateIsNormal': True,
    # u'success': True}

    serviceUid=IMPACT_ROOT+serviceOrganizer+'/services'+serviceName
    return api.get_policies(
        serviceUid=serviceUid,
        contextUid=contextUid,
        policyType=policyType
        )



def setPolicies(copyPolicyData, serviceOrganizer, serviceName, contextUid, policyType):
    # Here is where you would iterate through a list of services to set policies on
    # or in this example, set one service
    #
    # The serviceUid needs to be the full path to the service, in the format:
    #  '/zport/dmd/DynamicServices/extra_examples/services/extra_examples/'


    #Example output of 'set'
    # setting policy: {u'triggerType': u'policyPercentageTrigger', u'dependentState': u'DOWN', 
    #       u'id': u'a8010926-383e-486a-91e3-0d8a70eabed3', u'state': u'ATRISK', u'metaTypes': [], 
    #       u'properties': {u'threshold': u'50'}}
    # setting policy: {u'triggerType': u'policyPercentageTrigger', u'dependentState': u'DOWN', 
    #       u'id': u'7a733308-f97b-44a6-9937-1849df575461', u'state': u'DOWN', u'metaTypes': [], 
    #       u'properties': {u'threshold': u'100'}}

    for policy in copyPolicyData:
        print '\nSetting policy: %s' % policy
        api.set_policy(
            serviceUid=IMPACT_ROOT+serviceOrganizer+'/services'+serviceName,
            contextUid=contextUid, 
            policyType=policyType, 
            dependentState=policy['dependentState'], 
            state=policy['state'], 
            threshold=policy['properties']['threshold'], 
            triggerType=policy['triggerType']
        )

def copyPoliciesToServices():
    #### OPTIONS
    # contextUid options:  'global' or 'contextual'
    contextUid='global'
    
    # policyType options: 'Availability' or 'Performance'
    policyType='Availability'

    # The organizer & service name that the policies should be copied from
    # in my lab this is Dynamic Services/Payroll/Application
    copyFromOrganizer='/Payroll'
    copyFromService='/Application'

    # The organizer that contains the services that the policies should be copied to
    # in my lab this is Dynamic Services/Payroll/Databases/  which contains three services
    # Database, Database2, Database3
    copyToOrganizer='/Payroll/Databases'    
    copyToServices=['/Database', '/Database2', '/Database3']

    for toService in copyToServices:
        # Copy the policies from the specified organizer & service name
        copyPolicies=getPolicies(copyFromOrganizer, copyFromService, contextUid, policyType)
    
        # Print the current policies for the current source and target services
        print '\nCopied Policies from %s%s:' % (copyFromOrganizer, copyFromService)
        pprint(copyPolicies)

        #print '\nCurrent Policies on %s%s:' % (copyToOrganizer, copyToService)
        pprint(getPolicies(copyToOrganizer, toService, contextUid, policyType))

        # apply the policies copied from the source service to the target service(s) 
        setPolicies(copyPolicies['data'], copyToOrganizer, toService, contextUid, policyType)

        # print the target service's new policies for audit purposes
        print '\nNew Policies on %s%s:' % (copyToOrganizer, toService)
        pprint(getPolicies(copyToOrganizer, toService, contextUid, policyType))

if __name__ == '__main__':
    copyPoliciesToServices()





