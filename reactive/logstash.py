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
    units = elasticsearch.list_unit_data()
    hosts = []
    for unit in units:
        print(unit['host'])
        hosts.append('"{0}:{1}"'.format(unit['host'], unit['port']))
    context = {'hosts': ', '.join(hosts)}
    source = 'output-elasticsearch.conf'
    target = '/etc/logstash/conf.d/output-elasticsearch.conf'
    # Render the template
    render(source, target, context)
    # Set up the configration file for logstash
    set_state('logstash.elasticsearch.configured')


@when_file_changed('/etc/logstash/conf.d/output-elasticsearch.conf', '/etc/logstash/conf.d/input.conf')  # noqa
def recycle_logstash_service():
    host.service_restart('logstash')


@when('client.connected')
def configure_logstash_input(client):
    '''Configure the logstash input parameters.'''
    # Send the port data to the clients.
    client.provide_data(config('tcp_port'), config('udp_port'))
    source = 'input.conf'
    target = '/etc/logstash/conf.d/input.conf'
    render(source, target, config())
