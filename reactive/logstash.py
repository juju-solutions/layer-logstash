from charms.reactive import set_state
from charms.reactive import when
from charms.reactive import when_not
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.templating.jinja2 import render
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

@when('logstash.installed', 'elasticsearch.available')
@when_not('logstash.elasticsearch.configured')
def configure_logstash(elasticsearch):
    '''Configure logstash to push data to other sources.'''

    # Set up the configration file for logstash.
    # Get cluster-name, host, port from the relationship object.
    units = elasticsearch.list_units()
    hosts = []
    for unit in units():
        print(unit.host())
        hosts.append('"{0}:{1}"'.format(unit.host(), unit.port()))
    ', '.join(hosts)
    context = {'hosts': ', '.join(hosts)}
    source = 'output-elasticsearch.conf'
    target = '/etc/logstash/conf.d/output-elasticsearch.conf'
    # Render the template
    render(source, target, context)

    set_state('logstash.elasticsearch.configured')
