# Logstash

A flexible, open source data collection, enrichment, and
transportation pipeline. With connectors to common infrastructure for easy
integration, Logstash is designed to efficiently process a growing list of log,
event, and unstructured data sources for distribution into a variety of outputs,
including Elasticsearch.


## Usage

This charm makes use of `interface:java` which means you will need to deploy
a compatible JRE along with the Logstash application. This allows the consumer to
swap the version of java being used by configuring the system's java installation.

     juju deploy logstash
     juju deploy openjdk
     juju add-relation logstash openjdk


### This charm is bundled for your convenience.

Typically Logstash is deployed along side its companion products
Elasticsearch and Kibana. This suite of applications is known as the
ELK stack, and is deployable today:

    juju deploy ~containers/bundle/elk-stack

### Testing the deployment

The applications provide extended status reporting to indicate when they are
ready:

    juju status

This is particularly useful when combined with watch to track the on-going
progress of the deployment:

    watch juju status

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can use the provided
`generate-noise` action to test that the applications are working as expected:

    juju run-action logstash/0 generate-noise
    watch juju show-action-status

Once the action is complete, you can retrieve the results:

    juju show-action-output <action-id>

The &lt;action-id&gt; value will be in the `juju show-action-status`.

## Contact information

- Elasticsearch Charmers &lt;elasticsearch-charmers@lists.launchpad.net&gt;

# Need Help?

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju Community](https://jujucharms.com/community)
