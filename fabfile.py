from fabric.api import *
from fabric.colors import *

env.user = 'sites'

repo_home = '/opt/repo'
repo = '/opt/repo/template.git'
www_home = '/opt/www'
www = '/opt/www/template/app'
config = '/opt/www/template/config'


def upgrade():
    sudo('apt-get update')
    sudo('apt-get -y upgrade')
    sudo('apt-get -y dist-upgrade')
    sudo('apt-get -y autoremove')


def db_install():
    sudo('apt-get -y install libpq-dev python-dev')
    sudo('apt-get -y install postgresql postgresql-contrib')


def db_create():
    db_user = 'app'
    db_pass = 'pw'
    db_name = 'appdb'

    sudo('createdb %s' % (db_name), user='postgres')
    sudo('psql -c "CREATE USER %s WITH PASSWORD \'%s\'"' % (db_user, db_pass), user='postgres')
    sudo('psql -c "GRANT ALL PRIVILEGES ON DATABASE %s TO %s"' % (db_name, db_user), user='postgres')


def env_install():
    sudo('apt-get -y install python-virtualenv')
    sudo('apt-get -y install git')
    sudo('curl -sL https://deb.nodesource.com/setup | sudo bash -')
    sudo('apt-get -y install nodejs')
    sudo('npm install -g gulp')
    sudo('npm install -g bower')


def env_create():
    sudo('rm -rf %s' % www)
    sudo('rm -rf %s' % repo)
    sudo('mkdir -p %s' % www)
    sudo('mkdir -p %s' % repo)

    with cd(www_home):
        sudo('chown sites.sites template -R')

    with cd(repo_home):
        sudo('chown sites.sites template.git')

    with cd(www):
        run('virtualenv venv')

    with cd(repo):
        run('git init --bare')

    with cd(repo + '/hooks'):
        run('touch post-receive')
        run('chmod +x post-receive')
        run('echo "#!/bin/sh" >> post-receive')
        run('echo "git --work-tree=%s --git-dir=%s checkout -f" >> post-receive' % (www, repo))


def web_install():
    with prefix('source %s/bin/activate' % (www + '/venv')):
        run('pip install uwsgi')

    sudo('apt-get -y install nginx')


def web_config():
    sudo('rm -rf %s' % config)
    sudo('mkdir -p %s' % config, user=env.user)

    put('uwsgi/template.ini', config)
    put('crt/*', config)
    put('upstart/template.conf', '/etc/init/', use_sudo=True)

    with cd('/var/log'):
        sudo('touch template.log')
        sudo('chown sites.sites template.log')

    with cd('/etc/init'):
        sudo('chown root.root template.conf')
    
    put('nginx/template.no', '/etc/nginx/sites-available/', use_sudo=True)
    
    with cd('/etc/nginx/sites-enabled'):
        sudo('rm -f template.no')
        sudo('ln -s ../sites-available/template.no template.no')


def web_start():
    sudo('service nginx restart')


def firewall_setup():
    sudo('iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 22 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 80 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 443 -j ACCEPT')
    sudo('iptables -I INPUT 1 -i lo -j ACCEPT')
    sudo('iptables -P INPUT DROP')   


def backup_setup():
    sudo('apt-get -y install s3cmd')

    put('cron/backup-db', config)
    with cd(config):
        run('chmod +x backup-db')

    run('(crontab -l 2>/dev/null; echo "0 20 * * * %s/backup-db") | crontab -' % config) 


def msg():
    print('Login and save firewall: ' + red('sudo apt-get install iptables-persistent'))
    print('Initialize s3cmd: ' + red('cd ~ & s3cmd --configure'))
    print('Add remote repo to project: ' + green('git remote add <name> ssh://%s@%s%s' % (env.user, env.host_string, repo)))
    print('To push: ' + green('git push <name> master'))

def fullrestore():
    upgrade()
    db_install()
    db_create()
    env_install()
    env_create()
    web_install()
    web_config()
    web_start()
    firewall_setup()
    backup_setup()

    msg() # Instruction for deployment and further manual steps needed
