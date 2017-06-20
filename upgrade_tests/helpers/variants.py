"""All the variants those changes during upgrade and the helper functions"""

import os


class VersionError(Exception):
    """Error due to Unsupported Satellite Version"""


supported_ver = ['6.1', '6.2']
from_ver = os.environ.get('FROM_VERSION')
to_ver = os.environ.get('TO_VERSION')

if from_ver not in supported_ver:
    raise VersionError(
        'Unsupported preupgrade version {} provided for '
        'entity variants existence tests'.format(from_ver))

if to_ver not in supported_ver:
    raise VersionError(
        'Unsupported postupgrade version {} provided for '
        'entity variants existence tests'.format(to_ver))


# The dictionary of entity variants where the key is a component name
# and value is list of all the component entity variants list those changes
# during satellite versions
#
# Structure of variants directory:
# {'component_name_e.g_filter,repository':
#        [
#        [variant1_6.1, variant1_6.2],
#        [variant2_6.1, variant2_6.2],
#        ]
# }
#
# Note: The variants should be listed from 6.1 onwards
entity_varients = {
    'filter': [
        ['lookupkey', 'variablelookupkey'],
        ['(miscellaneous)', 'foremanopenscap::arfreport'],
        ['organization', 'katello::subscription'],
        ['configtemplate', 'provisioningtemplate'],
        ['view_templates, create_templates, edit_templates, '
         'destroy_templates, deploy_templates',
         'view_provisioning_templates, create_provisioning_templates, '
         'edit_provisioning_templates, destroy_provisioning_templates, '
         'deploy_provisioning_templates']
    ]
}


def assert_varients(component, pre, post):
    """Alternates the result of assert if the value of entity attribute is
    'expected' to change during upgrade

    It takes help from the entity_varients directory above for known changes

    e.g IF filters resource type 'lookupkey' in 6.1 is expected to change to
    'variablelookupkey' when upgraded to 6.2, then
    It returns true to pass the test as its expected

    :param string component: The sat component name of which entity attribute
        values are expected to varied during upgrade
    :param string pre: The preupgrade value of attribute
    :param string post: The postupgrade value of attribute
    :returns bool: Returns True, If the preupgrade and postupgrade values are
        expected changes and listed in entity variants directory.
        Else compares the actual preupgrade and postupgrade values and returns
        True/False accordingly
    """
    for single_list in entity_varients[component]:
        if pre == single_list[supported_ver.index(from_ver)]:
            if post == single_list[supported_ver.index(to_ver)]:
                return True
    else:
        return pre == post
