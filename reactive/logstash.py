from charms.reactive import set_state
from charms.reactive import when
from charms.reactive import when_not
from charmhelpers.core.fetch import configure_sources
from charmhelpers.core.fetch import apt_install
from charmhelpers.core.fetch import apt_update
from charmhelpers.core.hookenv import config


@when_not('logstash.installed')
def fetch_and_install():
    configure_sources(config('apt-url'), config('apt-key'))
    apt_update()
    apt_install('logstash', fatal=True)
    set_state('logstash.installed')
