from charms.reactive import set_state
from charms.reactive import remove_state
from charms.reactive import when
from charms.reactive import when_not
from charms.reactive import when_file_changed
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set
from charmhelpers.core import host
from charmhelpers.core.templating import render
from charmhelpers.fetch import configure_sources
from charmhelpers.fetch import apt_install
from charmhelpers.fetch import apt_update
from charmhelpers.core.unitdata import kv

CONF_DIR = "/etc/logstash/conf.d"


@when_not('java.ready')
def messaging():
    status_set('blocked', 'Missing JRE')


# this is declared in the JRE provider.
@when('java.ready')
@when_not('logstash.installed')
def fetch_and_install(java):
    configure_sources()
    apt_update()
    apt_install('logstash', fatal=True)
    set_state('logstash.installed')
    status_set('active', 'logstash installed')


@when('elasticsearch.connected')
def trigger_logstash_service_recycle(elasticsearch):
    remove_state('logstash.elasticsearch.configured')


@when('logstash.installed', 'elasticsearch.available')
@when_not('logstash.elasticsearch.configured')
def configure_logstash(elasticsearch):
    '''Configure logstash to push data to other sources.'''
    # Get cluster-name, host, port from the relationship object.
    cache = kv()
    units = elasticsearch.list_unit_data()
    if cache.get('logstash.elasticsearch'):
        hosts = cache.get('logstash.elasticsearch')
    else:
        hosts = []

    for unit in units:
        host_string = "{0}:{1}".format(unit['host'], unit['port'])
        if host_string not in hosts:
            hosts.append(host_string)

    cache.set('logstash.elasticsearch', hosts)
    set_state('logstash.render')
    set_state('logstash.elasticsearch.configured')


@when_file_changed('/etc/logstash/conf.d/legacy.conf',
                   '/etc/logstash/conf.d/beats.conf')
def recycle_logstash_service():
    host.service_restart('logstash')


@when('logstash.render')
def config_changed():
    render_without_context('beats.conf', '{}/beats.conf'.format(CONF_DIR))
    render_without_context('legacy.conf', '{}/legacy.conf'.format(CONF_DIR))
    remove_state('logstash.render')


@when('client.connected')
def configure_logstash_input(client):
    '''Configure the legacy logstash clients.'''
    # Send the port data to the clients.
    client.provide_data(config('tcp_port'), config('udp_port'))
    set_state('logstash.render')


@when('beat.connected')
def configure_filebeat_input(filebeat):
    '''Configure the logstash beat clients.'''
    filebeat.provide_data(config('beats_port'))
    set_state('logstash.render')


def render_without_context(source, target):
    ''' Convenience method to re-render a target template with cached data.
        Useful during config-changed cycles without needing to re-iterate The
        relationship interfaces. '''
    context = config()
    cache = kv()
    esearch = cache.get('logstash.elasticsearch')
    if esearch:
        context.update({'elasticsearch': ', '.join(esearch)})
    render(source, target, context)
