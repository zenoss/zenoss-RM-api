#!/usr/bin/env python

from zenApiImpactRouterHelper import (
    zenApiImpactRouterHelper,
    IMPACT_ROOT
)

api = zenApiImpactRouterHelper()

def setPolicies():
    # Here is where you would iterate through a list of services to set policies on
    # or in this example, set one service
    #
    # The serviceUid needs to be the full path to the service, in the format:
    #  '/zport/dmd/DynamicServices/extra_examples/services/extra_examples/'
    # Run 'ImpactRouter_createService.py' to create those services.
  
    serviceOrganizer='/extra_example_org'
    serviceName='/extra_examples'
    serviceUid=IMPACT_ROOT+serviceOrganizer+'/services'+serviceName

    api.set_policy(
        serviceUid=serviceUid,
        contextUid='global', 
        policyType='Availability', 
        dependentState='DOWN', 
        state='DOWN', 
        threshold='100', 
        triggerType='policyPercentageTrigger'
        )

    api.set_policy(
        serviceUid=serviceUid,
        contextUid='global', 
        policyType='Availability', 
        dependentState='DOWN', 
        state='DEGRADED', 
        threshold='50', 
        triggerType='policyPercentageTrigger'
        )

    api.set_policy(
        serviceUid=serviceUid,
        contextUid='global', 
        policyType='Availability', 
        dependentState='DOWN', 
        state='ATRISK', 
        threshold='25', 
        triggerType='policyPercentageTrigger'
        )

if __name__ == '__main__':
    setPolicies()
