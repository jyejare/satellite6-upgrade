"""All the variants those changes during upgrade and the helper functions"""

import os


class VersionError(Exception):
    """Error due to Unsupported Satellite Version"""


_VERSION_NAMES_DIFF = {}
_VERSION_NAMES_DIFF['6.1'] = {
    'filter': {
        'lookupkey': 'variablelookupkey',
        '(miscellaneous)': 'foremanopenscap::arfreport',
        'organization': 'katello::subscription',
        'configtemplate': 'provisioningtemplate',
        'view_templates, create_templates, edit_templates, '
        'destroy_templates, deploy_templates':
            'view_provisioning_templates, create_provisioning_templates, '
            'edit_provisioning_templates, destroy_provisioning_templates, '
            'deploy_provisioning_templates'
    }
}

_VERSION_NAMES_DIFF['6.2'] = {
    'filter': {
        'variablelookupkey': 'variablelookupkey6.3',
    },
    'another': {'foo': 'bar'}
}
_VERSION_NAMES_DIFF['6.3'] = {}


def _increasing_versions(from_version, to_version):
    major, from_minor = from_version.split('.')
    to_minor = to_version.split('.')[-1]
    from_minor = int(from_minor)
    to_minor = int(to_minor)

    for minor in range(from_minor, to_minor):
        minor = str(minor)
        yield '.'.join([major, minor])


def map_name_change(component, pre, from_version=None, to_version=None):
    """If a component property changes from one version (_FROM_VERSION) to
    another (_TO_VERSION) this function returns the respective changed name
    on the destination version.
    Otherwise returns the unchanged name. This way, to check if a property is
    present after upgrade the test can (suppose upgrade from 6.1 to 6.2):
    >>> map_name_change('filter', 'lookupkey')
    'variablelookupkey'

    :param component: str
    :param pre: str
    :param from_version: version origin of upgrade. If None value will be
        extracted from 'FROM_VERSION' env var
    :param to_version: version destination of upgrade. If None value will be
        extracted from 'TO_VERSION' env var
    :return: str
    """
    from_version = from_version or os.environ.get('FROM_VERSION')
    to_version = to_version or os.environ.get('TO_VERSION')

    _validate_versions(from_version, to_version)

    name = pre

    for current_version in _increasing_versions(from_version, to_version):
        diff_dict = _VERSION_NAMES_DIFF[current_version]
        if component in diff_dict:
            name = diff_dict[component].get(name, name)
    return name


def _validate_versions(from_version, to_version):
    if from_version not in _VERSION_NAMES_DIFF:
        raise VersionError(
            'Unsupported preupgrade version {} provided for '
            'entity variants existence tests'.format(from_version))
    if to_version not in _VERSION_NAMES_DIFF:
        raise VersionError(
            'Unsupported postupgrade version {} provided for '
            'entity variants existence tests'.format(to_version))


def test_61_to_62_diff():
    assert 'variablelookupkey' == map_name_change(
        'filter', 'lookupkey', '6.1', '6.2')


def test_61_to_62_no_diff():
    assert 'foo' == map_name_change('filter', 'foo', '6.1', '6.2')


def test_61_to_62_no_component():
    assert 'foo' == map_name_change('non existent component', 'foo', '6.1',
                                    '6.2')


def test_62_to_63_diff():
    assert 'variablelookupkey6.3' == map_name_change(
        'filter', 'variablelookupkey', '6.2', '6.3')
    assert 'bar' == map_name_change('another', 'foo', '6.2', '6.3')


def test_62_to_63_no_diff():
    assert 'foo' == map_name_change('filter', 'foo', '6.2', '6.3')


def test_62_to_63_no_component():
    assert 'foo' == map_name_change(
        'non existent component', 'foo', '6.2', '6.3')


def test_61_to_63_diff():
    assert 'variablelookupkey6.3' == map_name_change(
        'filter', 'lookupkey', '6.1', '6.3')
    assert 'bar' == map_name_change('another', 'foo', '6.1', '6.3')


def test_61_to_63_no_diff():
    assert 'foo' == map_name_change('filter', 'foo', '6.1', '6.3')


def test_61_to_63_no_component():
    assert 'foo' == map_name_change(
        'non existent component', 'foo', '6.1', '6.3')
