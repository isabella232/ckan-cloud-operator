import click
import yaml

from ckan_cloud_operator import logs

from ckan_cloud_operator.providers.ckan.db import migration as db_migration_manager
from ckan_cloud_operator.providers.ckan import manager
from .storage import cli as ckan_storage_cli


@click.group()
def ckan():
    """Manage CKAN Instances"""
    pass


ckan.add_command(ckan_storage_cli.storage)


@ckan.command()
@click.option('--interactive', is_flag=True)
def initialize(interactive):
    manager.initialize(interactive=interactive)
    logs.exit_great_success()


@ckan.command()
@click.argument('OLD_SITE_ID')
@click.argument('NEW_INSTANCE_ID', required=False)
@click.argument('ROUTER_NAME', required=False)
@click.option('--skip-gitlab', is_flag=True)
@click.option('--force', is_flag=True)
@click.option('--rerun', is_flag=True)
@click.option('--recreate-dbs', is_flag=True)
@click.option('--recreate', is_flag=True)
@click.option('--recreate-instance', is_flag=True)
@click.option('--skip-routes', is_flag=True)
@click.option('--skip-solr', is_flag=True)
@click.option('--skip-deployment', is_flag=True)
@click.option('--no-db-proxy', is_flag=True)
def migrate_deis_instance(old_site_id, new_instance_id, router_name, skip_gitlab, force, rerun, recreate_dbs, recreate,
                          recreate_instance, skip_routes, skip_solr, skip_deployment, no_db_proxy):
    """Run a full end-to-end migration of an instasnce"""
    manager.migrate_deis_instance(old_site_id, new_instance_id, router_name, skip_gitlab, force, rerun, recreate_dbs,
                                  recreate, recreate_instance, skip_routes, skip_solr, skip_deployment, no_db_proxy)
    logs.exit_great_success()


@ckan.command()
@click.argument('OLD_SITE_ID')
@click.option('--db-name')
@click.option('--datastore-name')
@click.option('--force', is_flag=True)
@click.option('--rerun', is_flag=True)
@click.option('--recreate-dbs', is_flag=True)
@click.option('--dbs-suffix')
@click.option('--skip-create-dbs', is_flag=True)
@click.option('--skip-datastore-import', is_flag=True)
def migrate_deis_dbs(old_site_id, db_name, datastore_name, force, rerun, recreate_dbs, dbs_suffix, skip_create_dbs,
                     skip_datastore_import):
    migration_generator = db_migration_manager.migrate_deis_dbs(
        old_site_id, db_name, datastore_name, force=force, rerun=rerun, recreate_dbs=recreate_dbs, dbs_suffix=dbs_suffix,
        skip_create_dbs=skip_create_dbs, skip_datastore_import=skip_datastore_import
    )
    for event in migration_generator:
        db_migration_manager.print_event_exit_on_complete(
            event,
            f'{old_site_id} -> {db_name}, {datastore_name}'
        )


@ckan.command()
@click.option('--db-name')
def migrate_list(db_name):
    for item in db_migration_manager.get()['items']:
        data = dict(item.get('spec', {}), **{'resource-name': item.get('metadata', {}).get('name')})
        if data.get('db-name') == db_name or not db_name:
            print(yaml.dump([data], default_flow_style=False))


@ckan.command()
@click.argument('MIGRATION_NAME', nargs=-1)
@click.option('--delete-dbs', is_flag=True)
def migrate_delete(migration_name, delete_dbs):
    for name in migration_name:
        db_migration_manager.delete(name, delete_dbs)
    logs.exit_great_success()


@ckan.command()
def get_all_dbs_users():
    dbs, users = manager.get_all_dbs_users()
    print(yaml.dump({
        'dbs': [' | '.join(map(str, db)) for db in dbs],
        'users': [' | '.join(map(str, user)) for user in users]
    }, default_flow_style=False))


@ckan.command()
@click.argument('INSTANCE_ID')
def post_create_checks(instance_id):
    manager.post_create_checks(instance_id)
    logs.exit_great_success()


@ckan.command()
@click.argument('INSTANCE_ID')
def admin_credentials(instance_id):
    logs.print_yaml_dump(manager.ckan_admin_credentials(instance_id))


@ckan.command()
@click.argument('OLD_SITE_ID')
def db_migration_import_urls(old_site_id):
    logs.print_yaml_dump(db_migration_manager.get_db_import_urls(old_site_id))