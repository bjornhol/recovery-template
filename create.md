Create environment
-----------
1. Create Ubuntu VPS
2. adduser sites
3. adduser sites sudo
4. Add authorized_keys for sites
5. fab -H <ip> fullrestore
6. Watch for remote git repo output
7. Watch for iptables instructions
8. Watch for sshd config instructions
9. Reboot and continue

Deploy site
-----------
1. git remote add <reponame> <url>
2. fab -H <ip> deploy:<reponame>
3. fab -H <ip> restore_database:<fixture> (optional)