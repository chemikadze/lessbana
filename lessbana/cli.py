import click
from router import Router
from elasticsearch import Elasticsearch
from os.path import expanduser
import logging
from jinja2 import Template

@click.group()
@click.option('--config', metavar='CONFIG', type=click.STRING, default=expanduser('~/.lessbana.cfg'))
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, config, debug):
    """
    CLI for accessing LogStash logs. For completion:

        eval "$(_LESSBANA_COMPLETE=source lessbana)"
    """
    ctx.obj['CONFIG'] = config
    if debug:
        logging.basicConfig(level=logging.DEBUG)

@cli.command('show-config')
@click.pass_context
def show_config(ctx):
    router = Router(open(ctx.obj['CONFIG']))
    for route in router._routes:
        print route

@cli.command('show')
@click.argument('path')
@click.option('--order', help="asc, desc")
@click.pass_context
def show(ctx, path, order):
    router = Router(open(ctx.obj['CONFIG']))
    route = router.match(path)
    logging.debug("Matched route: %s" % route)
    if not route:
        print 'No queries matched'
        return
    es = Elasticsearch(hosts=route.get('elasticsearch_url'))
    request_body = {}
    for non_mandatory_key in ['sort', 'query']:
        value = route.get(non_mandatory_key)
        if value:
            request_body[non_mandatory_key] = value
    if order == 'asc':
        request_body['sort'] = {'@timestamp': 'asc'}
    elif order == 'desc':
        request_body['sort'] = {'@timestamp': 'desc'}
    elif order:
        click.echo("Unknown order format: %s" % order, err=True)
        return 1
    logging.debug("Query: %s" % (request_body,))
    result = es.search(index=route.get('index'), doc_type=None, body=request_body)
    hits = result['hits']['hits']
    template = Template(route.get("format", "{{ __at_timestamp }} {{ message }}"))
    for hit in hits:
        doc = hit['_source']
        doc['__at_timestamp'] = doc.get('@timestamp')
        print template.render(doc)

@cli.command('list-indexes')
@click.pass_context
def list_indexes(ctx):
    es = Elasticsearch()
    indexes = es.indices.get('*')
    for index in sorted(indexes.keys()):
        print index
