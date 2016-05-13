"""
Dummy classes that can be shared across test cases
"""

from __future__ import absolute_import, division, unicode_literals

import uuid

from zope.interface import implementer

from twisted.plugin import IPlugin
from twisted.web.resource import Resource

from mimic.catalog import Entry
from mimic.catalog import Endpoint
from mimic.imimic import IAPIMock, IAPIDomainMock, IEndpointTemplate
from mimic.model.identity_objects import ExternalApiStore


class ExampleResource(Resource):
    """
    Simple resource that returns a string as the response
    """
    isLeaf = True

    def __init__(self, response_message):
        """
        Has a response message to return when rendered
        """
        self.response_message = response_message

    def render_GET(self, request):
        """
        Render whatever message was passed in
        """
        return self.response_message


@implementer(IAPIMock, IPlugin)
class ExampleAPI(object):
    """
    Example API that returns NoResource
    """
    def __init__(self, response_message="default message", regions_and_versions=[('ORD', 'v1')]):
        """
        Has a dictionary to store information from calls, for testing
        purposes
        """
        self.store = {}
        self.regions_and_versions = regions_and_versions
        self.response_message = response_message

    def catalog_entries(self, tenant_id):
        """
        List catalog entries for the Nova API.
        """
        endpoints = [Endpoint(tenant_id, each[0], 'uuid', each[1]) for each in self.regions_and_versions]
        return [Entry(tenant_id, "serviceType", "serviceName", endpoints)]

    def resource_for_region(self, region, uri_prefix, session_store):
        """
        Return no resource.
        """
        self.store['uri_prefix'] = uri_prefix
        return ExampleResource(self.response_message)


@implementer(IAPIDomainMock, IPlugin)
class ExampleDomainAPI(object):
    """
    Example domain API the return nothing.
    """

    def __init__(self, domain=u"api.example.com", response=b'"test-value"'):
        """
        Create an :obj:`ExampleDomainAPI`.

        :param text_type domain: the domain to respond with
        :param bytes response: the HTTP response body for all contained
            resources
        """
        self._domain = domain
        self._response = response

    def domain(self):
        """
        The domain for the ExampleDomainAPI.
        """
        return self._domain

    def resource(self):
        """
        The resource for the ExampleDomainAPI.
        """
        example_resource = ExampleResource(self._response)
        return example_resource


@implementer(IEndpointTemplate)
class ExampleEndpointTemplate(object):
    """
    Example End-Point Template
    """

    def __init__(self, name=u"example", region="EXTERNAL", version="v1",
                 url="https://api.external.example.com:8080",
                 publicURL=None, internalURL=None, adminURL=None,
                 versionInfoURL=None, versionListURL=None,
                 type_id=u"example", enabled=False, uuid=uuid.uuid4(),
                 tenantid_alias="%tenant_id%"
                 ):
        """
        Create an :obj:`ExampleEndPoindTemplate`.

        :param text_type name: name of the service provided, e.g Cloud Files.
        :param text_type region: region the service is provided in, e.g ORD.
        :param text_type version: version of the service, e.g v1.
        :param text_type url: basic URL of the service in the region.
        :param text_type publicURL: public URL of the service in the region.
        :param text_type internalURL: internal URL of the service in
            the region.
        :param text_type adminURL: administrative URL for the service in
            the region.
        :param text_type versionInfoURL: URL to get the version information
            of the service.
        :param text_type versionListURL: URL to get the list of supported
            versions by the service.
        :param text_type type_id: service type, e.g object-store
        :param boolean enabled: whether or not the service is enabled
            for all users. Services can be disabled for all tenants but still
            be enabled on a per-tenant basis.
        :param text_type uuid: unique ID for the endpoint within the service.
        :param text_type tenantid_alias: by default the system uses the text
            '%tenant_id%' for what to replace in the URLs with the tenantid.
            This value allows the service adminstrator to use a different
            textual value. Note: This is not presently used by Mimic which
            just appends the tenant-id for internally hosted services, and
            simply uses the URLs as is for externally hosted services.
        """
        self.id_key = uuid
        self.region_key = region
        self.type_key = type_id
        self.name_key = name
        self.enabled_key = enabled
        self.publicURL = publicURL if publicURL is not None else url
        self.internalURL = internalURL if internalURL is not None else url
        self.adminURL = adminURL if adminURL is not None else url
        self.tenantAlias = tenantid_alias
        self.versionId = version
        self.versionInfo = (versionInfoURL
                            if versionInfoURL is not None
                            else url + '/versionInfo')
        self.versionList = (versionListURL
                            if versionListURL is not None
                            else url + '/versions')


def make_example_external_api(name=u"example",
                              endpoint_templates=[ExampleEndpointTemplate()],
                              set_enabled=None):
    """
    Initialize an :obj:`ExternalApiStore` for a given name.

    :param text_type name: user-visible name of the service.
    :param list endpoint_templates: list of endpoint templates to
        initialize the API store with.
    :param boolean or None set_enabled: If none, the endpoint templates
        are used AS-IS. If a boolean type, then it sets all the templates
        to have the same default accessibility for all tenants.

    Note: The service-type of the first endpoint template is used as the
        service type for the entire Api Store, and is enforced that all
        endpoint templates have the same service-type.

    :returns: an instance of :obj:`ExternalApiStore`.
    :raises: ValueError if the service-type does not match between all the
        endpoint templates.
    """
    service_type = endpoint_templates[0].type_key
    for ept in endpoint_templates:
        ept.name_key = name
        if ept.type_key != service_type:
            raise ValueError(
                'Service Types do not match. {0} != {1}'.format(
                    ept.type_key,
                    service_type
                )
            )

        if set_enabled is not None and isinstance(set_enabled, bool):
            ept.enabled_key = set_enabled

    return ExternalApiStore(
        "uuid-" + name,
        name,
        service_type,
        endpoint_templates
    )
