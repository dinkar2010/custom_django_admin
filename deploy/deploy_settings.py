from fabric.api import env

#
# Deployment environments
#
production_servers = ['movincart.co.']
staging_server = ['movincart.staging.com']

env.user = 'ubuntu'
env.key_filename = '~/.ssh/us_west_app.pem'
env.forward_agent = True
env.code_dir = '~/movincart'
