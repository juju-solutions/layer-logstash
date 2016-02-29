from charms.reactive import set_state
from charms.reactive import when
from charms.reactive import when_not
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set 
from charmhelpers.fetch import configure_sources
from charmhelpers.fetch import apt_install
from charmhelpers.fetch import apt_update


@when_not('java.ready')
def messaging():
    status_set('blocked', 'Missing JRE')

# this is declared in the JRE provider. 
@when('java.ready')
@when_not('logstash.installed')
def fetch_and_install(logstash):
    configure_sources(config('apt-url'), config('apt-key'))
    apt_update()
    apt_install('logstash', fatal=True)
    set_state('logstash.installed')
    status_set('active', 'logstash installed')
