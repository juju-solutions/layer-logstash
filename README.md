# Layer Logstash

This is a charm layer for logstash.


### This charm is not stand-alone

This charm makes use of `interface:java` which means you will need to deploy
a compatible JRE along with the logstash service. This allows the consumer to
swap the version of java being used by configuring the system's java installation.

     juju deploy logstash
     juju deploy openjdk
     juju add-relation logstash openjdk
 
