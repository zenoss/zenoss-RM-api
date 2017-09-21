#!/usr/bin/env python


class RouterEndpointMap():
    '''
    This class isn't incredibly pretty but it's basic. It's used to
    provide the path to the router you need. Feed it a name, get what
    you need to build your URL for your API request.
    '''
    def __init__(self):
        self.map = {'AWSRouter': '/zport/dmd/aws_router',
                    'ApplicationRouter': '/zport/dmd/application_router',
                    'AzureRouter': '/zport/dmd/azure_router',
                    'CallhomeRouter': '/zport/dmd/callhome_router',
                    'CiscoUCSRouter': '/zport/dmd/ciscoucs_router',
                    'ComponentGroupRouter': '/zport/dmd/componentgroup_router',
                    'DashboardRouter': '/zport/dmd/dashboard_router',
                    'DetailNavRouter': '/zport/dmd/detailnav_router',
                    'DeviceDumpLoadRouter': '/zport/dmd/devicedumpload_router',
                    'DeviceManagementRouter': '/zport/dmd/devicemanagement_router',
                    'DeviceRouter': '/zport/dmd/device_router',
                    'DiagramRouter': '/zport/dmd/diagram_router',
                    'DistributedCollectorRouter': '/zport/dmd/dc_router',
                    'DynamicViewRouter': '/zport/dmd/dynamicservice_router',
                    'ElementPoolRouter': '/zport/dmd/elementpool_router',
                    'EnterpriseServicesRouter': '/zport/dmd/enterpriseservices_compat_router',
                    'EtlRouter': '/zport/dmd/etl_router',
                    'EventClassesRouter': '/zport/dmd/evclasses_router',
                    'EventsRouter': '/zport/dmd/evconsole_router',
                    'HostRouter': '/zport/dmd/host_router',
                    'HyperVRouter': '/zport/dmd/hyperv_router',
                    'ImpactRouter': '/zport/dmd/enterpriseservices_router',
                    'InsightRouter': '/zport/dmd/insight_router',
                    'IntrospectionRouter': '/zport/dmd/introspection_router',
                    'JobsRouter': '/zport/dmd/jobs_router',
                    'LDAPRouter': '/zport/dmd/ldap_router',
                    'LicensingRouter': '/zport/dmd/licensing_router',
                    'LogicalNodeRouter': '/zport/dmd/logicalnode_router',
                    'ManufacturersRouter': '/zport/dmd/manufacturers_router',
                    'MessagingRouter': '/zport/dmd/messaging_router',
                    'MibRouter': '/zport/dmd/mib_router',
                    'MonitorRouter': '/zport/dmd/monitor_router',
                    'MultiRealmRouter': '/zport/dmd/multirealm_router',
                    'Network6Router': '/zport/dmd/network_6_router',
                    'NetworkRouter': '/zport/dmd/network_router',
                    'OpenStackInfrastructureRouter': '/zport/dmd/openstackinfrastructure_router',
                    'OpenStackRouter': '/zport/dmd/openstack_router',
                    'ProcessRouter': '/zport/dmd/process_router',
                    'PropertiesRouter': '/zport/dmd/properties_router',
                    'PropertyMonitorRouter': '/zport/dmd/propertymonitor_router',
                    'RelatedEventsRouter': '/zport/dmd/relatedevents_router',
                    'ReportRouter': '/zport/dmd/report_router',
                    'SAMLIdPRouter': '/zport/dmd/SAMLIdPRouter',
                    'SearchRouter': '/zport/dmd/search_router',
                    'ServiceRouter': '/zport/dmd/service_router',
                    'ServiceTemplatesRouter': '/zport/dmd/servicetemplates_router',
                    'SettingsRouter': '/zport/dmd/settings_router',
                    'StorageBaseRouter': '/zport/dmd/storage_router',
                    'SupportRouter': '/zport/dmd/support_router',
                    'TemplateRouter': '/zport/dmd/template_router',
                    'TriggersRouter': '/zport/dmd/triggers_router',
                    'UsersRouter': '/zport/dmd/users_router',
                    'VCloudRouter': '/zport/dmd/vcloud_router',
                    'ZenPackRouter': '/zport/dmd/zenpack_router',
                    'ZenWebTxRouter': '/zport/dmd/zenwebtx_router',
                    'vSphereRouter': '/zport/dmd/vsphere_router'}

    def getEndpoint(self, router):
        if router in self.map.keys():
            return self.map.get(router)
        else:
            raise Exception('Router not found')
