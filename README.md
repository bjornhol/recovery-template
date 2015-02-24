# recovery-template
Template for recovery with Fabric. [More details](http://blog.beatware.no/disaster-recovery-with-fabric.html) on my homepage.

Only tested with Python 2.7

Creates environment based on:

* Postgresql
* nginx and uWSGI
* Start uWSGI with Upstart
* Django application running with Virtualenv
* Application dependencies from pip and bower
* Application deployment tasks with gulp.js
* Copy files to server with Git
* Firewall with iptables
* Backup script scheduled with Cron
