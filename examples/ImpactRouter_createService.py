#!/usr/bin/env python

from zenApiImpactRouterHelper import (
    zenApiImpactRouterHelper,
    IMPACT_ROOT
)

api = zenApiImpactRouterHelper()

def createExampleService():
    print "Creating organizer: extra_example_org"
    org = api.create_organizer(IMPACT_ROOT, 'extra_example_org')
    if not org['success']:
        raise Exception("Unable to create organizer extra_example_org")

    print "Creating services"
    orgUid = org['data']['uid']
    api.create_service(orgUid, 'extra_examples')
    api.create_service(orgUid, 'extra_example_1')
    api.create_service(orgUid, 'extra_example_2')

    print "Adding impacts"
    orgPath = orgUid + '/services/'
    api.add_impact(orgPath + 'extra_examples', orgPath + 'extra_example_1')
    api.add_impact(orgPath + 'extra_examples', orgPath + 'extra_example_2')

    print "Finished creating sample graph in organizer 'extra_examples'.\n"

if __name__ == '__main__':
    createExampleService()
