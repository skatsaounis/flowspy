Firewall on Demand
==================

Description
-----------

Firewall on Demand applies, via Netconf, flow rules to a network device.
These rules are then propagated via e-bgp to peering routers. Each user
is authenticated against shibboleth. Authorization is performed via a
combination of a Shibboleth attribute and the peer network address range
that the user originates from. FoD is meant to operate over this
architecture:

    +-----------+          +------------+        +------------+
    |   FoD     | NETCONF  | flowspec   | ebgp   |   router   |
    | web app   +----------> device     +-------->            |
    +-----------+          +------+-----+        +------------+
                                  | ebgp
                                  |
                           +------v-----+
                           |   router   |
                           |            |
                           +------------+

NETCONF is chosen as the mgmt protocol to apply rules to a single
flowspec capable device. Rules are then propagated via igbp to all
flowspec capable routers. Of course FoD could apply rules directly (via
NETCONF always) to a router and then ibgp would do the rest. In GRNET’s
case the flowspec capable device is an EX4200.

> **attention**
>
> Make sure your FoD server has ssh access to your flowspec device.

> **attention**
>
> Installation instructions assume a clean Debian Wheezy with Django 1.4

Contact
-------

You can find more about FoD or raise your issues at [GRNET FoD
repository][].

You can contact us directly at staurosk{at}noc[dot]grnet(.)gr

Repositories
------------

  [GRNET FoD repository]: https://code.grnet.gr/projects/flowspy
  [Github FoD repository]: https://github.com/grnet/flowspy

Installation
============

Debian Wheezy (x64) - Django 1.4.x
----------------------------------

This guide assumes that installation is carried out in /srv/flowspy
directory. If other directory is to be used, please change the
corresponding configuration files. It is also assumed that the root user
will perform every action.

### Upgrading from v\<1.1.x

> **note**
>
> If PEER\_\*\_TABLE tables are set to FALSE in settings.py, you need to
> perform the south migrations per application:
>
>     ./manage.py migrate longerusername
>     ./manage.py migrate flowspec
>     ./manage.py migrate accounts

If upgrading from flowspy version \<1.1.x pay attention to settings.py
changes. Also, do not forget to run if PEER\_\*\_TABLE tables are set to
TRUE in settings.py:

    ./manage.py migrate

to catch-up with latest database changes.

### Upgrading from v\<1.0.x

If upgrading from flowspy version \<1.0.x pay attention to settings.py
changes. Also, do not forget to run:

    ./manage.py migrate

to catch-up with latest database changes.

### Required system packages

Update and install the required packages:

    apt-get update
    apt-get upgrade
    apt-get install mysql-server apache2 memcached libapache2-mod-proxy-html gunicorn beanstalkd python-django python-django-south python-django-tinymce tinymce python-mysqldb python-yaml python-memcache python-django-registration python-ipaddr python-lxml mysql-client git python-django-celery python-paramiko python-gevent vim

Also, django rest framework package is required. In debian Wheezy it is
not available, but one can install it via pip.

> **note**
>
> Set username and password for mysql if used

> **note**
>
> If you wish to deploy an outgoing mail server, now it is time to do
> it. Otherwise you could set FoD to send out mails via a third party
> account

### Create a database

If you are using mysql, you should create a database:

    mysql -u root -p -e 'create database fod'

### Required application packages

Get the required packages and their dependencies and install them:

    apt-get install libxml2-dev libxslt-dev gcc python-dev

-   ncclient: NETCONF python client:

        cd ~
        git clone https://github.com/leopoul/ncclient.git
        cd ncclient
        python setup.py install

-   nxpy: Python Objects from/to XML proxy:

        cd ~
        git clone https://code.grnet.gr/git/nxpy
        cd nxpy
        python setup.py install

-   flowspy: core application. Installation is done at /srv/flowspy:

        cd /srv
        git clone https://code.grnet.gr/git/flowspy
        cd flowspy

Application configuration
=========================

Copy settings.py.dist to settings.py:

    cd flowspy
    cp settings.py.dist settings.py

Edit settings.py file and set the following according to your
configuration:

    ADMINS: set your admin name and email (assuming that your server can send notifications)
    DATABASES (to point to your local database). You could use views instead of tables for models: peer, peercontacts, peernetworks. For this to work we suggest MySQL with MyISAM db engine
    SECRET_KEY : Make this unique, and don't share it with anybody
    STATIC_ROOT: /srv/flowspy/static (or your installation directory)
    STATIC_URL (static media directory) . If you have followed the above this should be: /srv/flowspy/static
    TEMPLATE_DIRS : If you have followed the above this should be: /srv/flowspy/templates
    CACHE_BACKEND:  Enable Memcached for production or leave to DummyCache for development environments
    Alternatively you could go for redis with the corresponding Django client lib.
    NETCONF_DEVICE (tested with Juniper EX4200 but any BGP enabled Juniper should work). This is the flowspec capable device
    NETCONF_USER (enable ssh and netconf on device)
    NETCONF_PASS
    If beanstalk is selected the following should be left intact.
    BROKER_HOST (beanstalk host)
    BROKER_PORT (beanstalk port)
    SERVER_EMAIL
    EMAIL_SUBJECT_PREFIX
    If beanstalk is selected the following should be left intact.
    BROKER_URL (beanstalk url)
    SHIB_AUTH_ENTITLEMENT (if you go for Shibboleth authentication)
    NOTIFY_ADMIN_MAILS (bcc mail addresses)
    PROTECTED_SUBNETS (subnets for which source or destination address will prevent rule creation and notify the NOTIFY_ADMIN_MAILS)
    The whois client is meant to be used in case you have inserted peers with their ASes in the peers table and wish to get network info for each one in an automated manner.
    PRIMARY_WHOIS
    ALTERNATE_WHOIS
    If you wish to deploy FoD with Shibboleth change the following attributes according to your setup:
    SHIB_AUTH_ENTITLEMENT = 'urn:mace'
    SHIB_ADMIN_DOMAIN = 'example.com'
    SHIB_LOGOUT_URL = 'https://example.com/Shibboleth.sso/Logout'
    SHIB_USERNAME = ['HTTP_EPPN']
    SHIB_MAIL = ['mail', 'HTTP_MAIL', 'HTTP_SHIB_INETORGPERSON_MAIL']
    SHIB_FIRSTNAME = ['HTTP_SHIB_INETORGPERSON_GIVENNAME']
    SHIB_LASTNAME = ['HTTP_SHIB_PERSON_SURNAME']
    SHIB_ENTITLEMENT = ['HTTP_SHIB_EP_ENTITLEMENT']

If you have not installed an outgoing mail server you can always use
your own account (either corporate or gmail, hotmail ,etc) by adding the
following lines in settings.py:

    EMAIL_USE_TLS = True #(or False)
    EMAIL_HOST = 'smtp.example.com'
    EMAIL_HOST_USER = 'username'
    EMAIL_HOST_PASSWORD = 'yourpassword'
    EMAIL_PORT = 587 #(outgoing)

It is strongly advised that you do not change the following to False
values unless, you want to integrate FoD with you CRM or members
database. This implies that you are able/have the rights to create
database views between the two databases:

    PEER_MANAGED_TABLE = True
    PEER_RANGE_MANAGED_TABLE = True
    PEER_TECHC_MANAGED_TABLE = True

By doing that the corresponding tables as defined in peers/models will
not be created. As noted above, you have to create the views that the
tables will rely on.

> **note**
>
> Soon we will release a version with django-registration as a means to
> add users and Shibboleth will become an alternative

Let’s move on with some copies and dir creations:

    mkdir /var/log/fod
    chown www-data.www-data /var/log/fod
    cp urls.py.dist urls.py
    cd ..

> **note**
>
> LOG\_FILE\_LOCATION in settings.py is set to **/var/log/fod**. Adjust
> the chown command above to your selected dir.

System configuration
====================

Apache operates as a gunicorn Proxy with WSGI and Shibboleth modules
enabled. Depending on the setup the apache configuration may vary:

    a2enmod rewrite
    a2enmod proxy
    a2enmod ssl
    a2enmod proxy_http

If shibboleth is to be used:

    apt-get install libapache2-mod-shib2
    a2enmod shib2

Now it is time to configure beanstalk, gunicorn, celery and apache.

beanstalkd
----------

Enable beanstalk by editting /etc/default/beanstalkd:

    vim /etc/default/beanstalkd

Uncomment the line **START=yes** to enable beanstalk

Start beanstalkd:

    service beanstalkd start

gunicorn.d
----------

Create and edit /etc/gunicorn.d/fod:

    vim /etc/gunicorn.d/fod

FoD is served via gunicorn and is then proxied by Apache. If the above
directory conventions have been followed so far, then your configuration
should be:

    CONFIG = {
          'mode': 'django',
          'working_dir': '/srv/flowspy',
          'args': (
               '--bind=127.0.0.1:8081',
               '--workers=1',
               '--worker-class=egg:gunicorn#gevent',
               '--timeout=30',
               '--debug',
               '--log-level=debug',
               '--log-file=/var/log/gunicorn/fod.log',
          ),
    }

celeryd
=======

Celery is used over beanstalkd to apply firewall rules in a serial
manner so that locks are avoided on the flowspec capable device. In our
setup celery runs via django. That is why the python-django-celery
package was installed.

Create the celeryd daemon at /etc/init.d/celeryd **if it does not
already exist**:

    vim /etc/init.d/celeryd

The configuration should be:

    #!/bin/sh -e
    # ============================================
    #  celeryd - Starts the Celery worker daemon.
    # ============================================
    #
    # :Usage: /etc/init.d/celeryd {start|stop|force-reload|restart|try-restart|status}
    # :Configuration file: /etc/default/celeryd
    #
    # See http://docs.celeryq.org/en/latest/cookbook/daemonizing.html#init-script-celeryd


    ### BEGIN INIT INFO
    # Provides:              celeryd
    # Required-Start:     $network $local_fs $remote_fs
    # Required-Stop:       $network $local_fs $remote_fs
    # Default-Start:       2 3 4 5
    # Default-Stop:        0 1 6
    # Short-Description: celery task worker daemon
    # Description:          Starts the Celery worker daemon for a single project.
    ### END INIT INFO

    #set -e

    DEFAULT_PID_FILE="/var/run/celery/%n.pid"
    DEFAULT_LOG_FILE="/var/log/celery/%n.log"
    DEFAULT_LOG_LEVEL="INFO"
    DEFAULT_NODES="celery"
    DEFAULT_CELERYD="-m celery.bin.celeryd_detach"
    ENABLED="false"

    [ -r "$CELERY_DEFAULTS" ] && . "$CELERY_DEFAULTS"

    [ -r /etc/default/celeryd ] && . /etc/default/celeryd

    if [ "$ENABLED" != "true" ]; then
          echo "celery daemon disabled - see /etc/default/celeryd."
          exit 0
    fi


    CELERYD_PID_FILE=${CELERYD_PID_FILE:-${CELERYD_PIDFILE:-$DEFAULT_PID_FILE}}
    CELERYD_LOG_FILE=${CELERYD_LOG_FILE:-${CELERYD_LOGFILE:-$DEFAULT_LOG_FILE}}
    CELERYD_LOG_LEVEL=${CELERYD_LOG_LEVEL:-${CELERYD_LOGLEVEL:-$DEFAULT_LOG_LEVEL}}
    CELERYD_MULTI=${CELERYD_MULTI:-"celeryd-multi"}
    CELERYD=${CELERYD:-$DEFAULT_CELERYD}
    CELERYCTL=${CELERYCTL:="celeryctl"}
    CELERYD_NODES=${CELERYD_NODES:-$DEFAULT_NODES}

    export CELERY_LOADER

    if [ -n "$2" ]; then
          CELERYD_OPTS="$CELERYD_OPTS $2"
    fi

    CELERYD_LOG_DIR=`dirname $CELERYD_LOG_FILE`
    CELERYD_PID_DIR=`dirname $CELERYD_PID_FILE`
    if [ ! -d "$CELERYD_LOG_DIR" ]; then
          mkdir -p $CELERYD_LOG_DIR
    fi
    if [ ! -d "$CELERYD_PID_DIR" ]; then
          mkdir -p $CELERYD_PID_DIR
    fi

    # Extra start-stop-daemon options, like user/group.
    if [ -n "$CELERYD_USER" ]; then
          DAEMON_OPTS="$DAEMON_OPTS --uid=$CELERYD_USER"
          chown "$CELERYD_USER" $CELERYD_LOG_DIR $CELERYD_PID_DIR
    fi
    if [ -n "$CELERYD_GROUP" ]; then
          DAEMON_OPTS="$DAEMON_OPTS --gid=$CELERYD_GROUP"
          chgrp "$CELERYD_GROUP" $CELERYD_LOG_DIR $CELERYD_PID_DIR
    fi

    if [ -n "$CELERYD_CHDIR" ]; then
          DAEMON_OPTS="$DAEMON_OPTS --workdir=\"$CELERYD_CHDIR\""
    fi


    check_dev_null() {
          if [ ! -c /dev/null ]; then
               echo "/dev/null is not a character device!"
               exit 1
          fi
    }


    export PATH="${PATH:+$PATH:}/usr/sbin:/sbin"


    stop_workers () {
          $CELERYD_MULTI stop $CELERYD_NODES --pidfile="$CELERYD_PID_FILE"
    }


    start_workers () {
          $CELERYD_MULTI start $CELERYD_NODES $DAEMON_OPTS           \
                                        --pidfile="$CELERYD_PID_FILE"        \
                                        --logfile="$CELERYD_LOG_FILE"        \
                                        --loglevel="$CELERYD_LOG_LEVEL"     \
                                        --cmd="$CELERYD"                           \
                                        $CELERYD_OPTS
    }


    restart_workers () {
          $CELERYD_MULTI restart $CELERYD_NODES $DAEMON_OPTS        \
                                           --pidfile="$CELERYD_PID_FILE"     \
                                           --logfile="$CELERYD_LOG_FILE"     \
                                           --loglevel="$CELERYD_LOG_LEVEL"  \
                                           --cmd="$CELERYD"                        \
                                           $CELERYD_OPTS
    }



    case "$1" in
          start)
               check_dev_null
               start_workers
          ;;

          stop)
               check_dev_null
               stop_workers
          ;;

          reload|force-reload)
               echo "Use restart"
          ;;

          status)
               $CELERYCTL status $CELERYCTL_OPTS
          ;;

          restart)
               check_dev_null
               restart_workers
          ;;

          try-restart)
               check_dev_null
               restart_workers
          ;;

          *)
               echo "Usage: /etc/init.d/celeryd {start|stop|restart|try-restart|kill}"
               exit 1
          ;;
    esac

    exit 0

celeryd configuration
=====================

celeryd requires a /etc/default/celeryd file to be in place. Thus we are
going to create this file (/etc/default/celeryd):

    vim /etc/default/celeryd

Again if the directory conventions have been followed the file is (pay
attention to the CELERYD\_USER, CELERYD\_GROUP and change accordingly) :

    # Default: false
    ENABLED="true"

    # Name of nodes to start, here we have a single node
    CELERYD_NODES="w1"
    # or we could have three nodes:
    #CELERYD_NODES="w1 w2 w3"

    # Where to chdir at start.
    CELERYD_CHDIR="/srv/flowspy"
    # How to call "manage.py celeryd_multi"
    CELERYD_MULTI="python $CELERYD_CHDIR/manage.py celeryd_multi"

    # How to call "manage.py celeryctl"
    CELERYCTL="python $CELERYD_CHDIR/manage.py celeryctl"

    # Extra arguments to celeryd
    #CELERYD_OPTS="--time-limit=300 --concurrency=8"
    CELERYD_OPTS="-E -B --schedule=/var/run/celery/celerybeat-schedule --concurrency=1 --soft-time-limit=180 --time-limit=1800"
    # Name of the celery config module.
    CELERY_CONFIG_MODULE="celeryconfig"

    # %n will be replaced with the nodename.
    CELERYD_LOG_FILE="/var/log/celery/fod_%n.log"
    CELERYD_PID_FILE="/var/run/celery/%n.pid"

    CELERYD_USER="root"
    CELERYD_GROUP="root"

    # Name of the projects settings module.
    export DJANGO_SETTINGS_MODULE="flowspy.settings"

Apache
======

Apache proxies gunicorn. Things are more flexible here as you may follow
your own configuration and conventions. Create and edit
/etc/apache2/sites-available/fod. You should set \<server\_name\> and
\<admin\_mail\> along with your certificates. If under testing
environment, you can use the provided snakeoil certs. If you do not
intent to use Shibboleth delete or comment the corresponding
configuration parts inside **Shibboleth configuration** :

    vim /etc/apache2/sites-available/fod

Again if the directory conventions have been followed the file should
be:

    <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        ServerName  fod.example.com
        DocumentRoot /var/www

        ErrorLog ${APACHE_LOG_DIR}/fod_error.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel debug

        CustomLog ${APACHE_LOG_DIR}/fod_access.log combined

        Alias /static       /srv/flowspy/static
          RewriteEngine On
          RewriteCond %{HTTPS} off
          RewriteRule ^/(.*) https://fod.example.com/$1 [L,R]
    </VirtualHost>

    <VirtualHost *:443>
        ServerName    fod.example.com
        ServerAdmin     webmaster@localhost
        ServerSignature        On

        SSLEngine on
        SSLCertificateFile    /etc/ssl/certs/fod.example.com.crt
        SSLCertificateChainFile /etc/ssl/certs/example-chain.pem
        SSLCertificateKeyFile    /etc/ssl/private/fod.example.com.key

        AddDefaultCharset UTF-8
        IndexOptions        +Charset=UTF-8

        ShibConfig       /etc/shibboleth/shibboleth2.xml
        Alias          /shibboleth-sp /usr/share/shibboleth


        <Location /login>
             AuthType shibboleth
             ShibRequireSession On
             ShibUseHeaders On
             ShibRequestSetting entityID https://idp.example.com/idp/shibboleth
             require valid-user
        </Location>

        # Shibboleth debugging CGI script
        ScriptAlias /shibboleth/test /usr/lib/cgi-bin/shibtest.cgi
        <Location /shibboleth/test>
             AuthType shibboleth
             ShibRequireSession On
             ShibUseHeaders On
             require valid-user
        </Location>

        <Location /Shibboleth.sso>
             SetHandler shib
        </Location>

        # Shibboleth SP configuration

        #SetEnv                       proxy-sendchunked

              <Proxy *>
               Order allow,deny
               Allow from all
               </Proxy>

               SSLProxyEngine           off
               ProxyErrorOverride     off
          ProxyTimeout     28800
             ProxyPass        /static !
             ProxyPass          /shibboleth !
             ProxyPass        /Shibboleth.sso !

               ProxyPass           / http://localhost:8081/ retry=0
               ProxyPassReverse / http://localhost:8081/

          Alias /static          /srv/flowspy/static

        LogLevel warn

Now, enable your site. You might want to disable the default site if fod
is the only site you host on your server:

    a2dissite default
    a2ensite fod

You are not far away from deploying FoD. When asked for a super user,
create one:

    cd /srv/flowspy
    python manage.py syncdb
    python manage.py migrate longerusername
    python manage.py migrate flowspec
    python manage.py migrate djcelery
    python manage.py migrate accounts
    python manage.py migrate

If you have not changed the values of the PEER\_\*\_TABLE variables to
False and thus you are going for a default installation (that is
PEER\_\*\_TABLE variables are set to True) , then run:

    python manage.py migrate peers

If however you have set the PEER\_\*\_TABLE variables to False and by
accident you have ran the command above, then you have to cleanup you
database manually by dropping the peer\* tables plus the techc\_email
table. For MySQL the command is:

    DROP TABLE `peer`, `peer_networks`, `peer_range`, `peer_techc_emails`, techc_email;

Restart, gunicorn and apache:

    service gunicorn restart && service apache2 restart

Propagate the flatpages
=======================

Inside the initial\_data/fixtures\_manual.xml file we have placed 4
flatpages (2 for Greek, 2 for English) with Information and Terms of
Service about the service. To import the flatpages, run from root
folder:

    python manage.py loaddata initial_data/fixtures_manual.xml

Testing the platform
====================

Log in to the admin interface via [https:\\/\\/][]\<hostname\>/admin. Go
to Peer ranges and add a new range (part of/or a complete subnet), eg.
10.20.0.0/19 Go to Peers and add a new peer, eg. id: 1, name: Test, AS:
16503, tag: TEST and move the network you have created from Avalable to
Chosen. From the admin front, go to User, and edit your user. From the
bottom of the page, select the TEST peer and save. Last but not least,
modify as required the existing (example.com) Site instance (admin
home-\>Sites). You are done. As you are logged-in via the admin, there
is no need to go through Shibboleth at this time. Go to
<hostname\> and create a new rule. Your rule should be
applied on the flowspec capable device after aprox. 10 seconds. If no
Shibboleth authentication is available, a
<hostname\> altlogin is provided.

Branding
========

Via the admin interface you can modify flatpages to suit your needs

Footer
------

Under the templates folder (templates), you can alter the footer.html
file to include your own footer messages, badges, etc.

Welcome Page
------------

Under the templates folder (templates), you can alter the welcome page -
welcome.html with your own images, carousel, videos, etc.

Usage
======

Web interface
-------------------------
FoD comes with a web interface, in which one can edit and apply new routes.

Rest Api
--------------

There is a rest api available in /api/v1/. One can set new rules or see the applied ones by using it.

