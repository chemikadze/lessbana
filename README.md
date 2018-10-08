CLI for LogStash indexes
========================

Kibana is cool, but sometimes it is more handy to work with logs in console.
For this cases, no more pain with direct file browsing -- you can still use centralized
log storage in ElasticSearch and use CLI tools for processing them, just use lessbana!

Look, examples!
===============

    (.venv)chemikadze ~/programming/lessbana $ lessbana show /all.log
    2016-05-14T10:31:55.763Z test
    2016-05-14T10:32:01.834Z test
    2016-05-14T19:17:21.398Z hello
    2016-05-14T19:17:39.293Z hello2
    (.venv)chemikadze ~/programming/lessbana $ lessbana show --order desc /all.log
    2016-05-14T19:17:39.293Z hello2
    2016-05-14T19:17:21.398Z hello
    2016-05-14T10:32:01.834Z test
    2016-05-14T10:31:55.763Z test
    (.venv)chemikadze ~/programming/lessbana $ lessbana show /all.log
    2016-05-14T10:31:55.763Z test
    2016-05-14T10:32:01.834Z test
    2016-05-14T19:17:21.398Z hello
    2016-05-14T19:17:39.293Z hello2
    (.venv)chemikadze ~/programming/lessbana $ lessbana show /hosts/all.log
    2016-05-14T10:31:55.763Z MacBook-Air-Nikolaj.local test
    2016-05-14T10:32:01.834Z MacBook-Air-Nikolaj.local test
    2016-05-14T19:17:21.398Z 1234 hello
    2016-05-14T19:17:39.293Z 4321 hello2
    (.venv)chemikadze ~/programming/lessbana $ lessbana show /hosts/1234
    2016-05-14T19:17:21.398Z hello

And yes, it is configurable
===========================

Here is example config file:

    # this is default values appied to for every pattern
    default:
        elasticsearch_url: localhost
        index: logstash-*
        sort:
            "@timestamp": "asc"
        # lines are described as Jinja2 templates
        # __at_timestamp is metavar for @timestamp
        format: "{{ __at_timestamp }} {{ message }}"

    patterns:

        # patterns can refer just to default value
        - /all.log:

        # or override individual fields
        - /hosts/all.log:
            format: "{{ __at_timestamp }} {{ host|default('unknown') }} {{ message }}"

        # and query part is recursive Jinja2 template where named captures are available
        - /hosts/(?P<host>.*):
            query:
                term:
                    host: '{{ host }}'
