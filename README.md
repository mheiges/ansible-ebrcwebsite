ebrcwebsite
=========

Provisions a WDK-based EuPathDB BRC website.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

The `settings_file` variable must reference a YAML file with website-specific settings.

See `doc/installsite_full.prop` for the full collection of required
website-specific settings. Many of the settings, such as SCM locations
and database configurations can be taken from the /dashboard API of an
existing site. If you leverage that then see `doc/installsite_min.prop`
for the minimum collection of required website-specific settings. You
can also construct your `settings_file` to fall somewhere between the
full and minimum collection. Say, for example, you want your website to
match dev.foodb.org except you want to change the database login to
`gusfring` you can add custom `login` keys.

    dashboard:
      hostname: dev.foodb.org
      auth:
        username: yaknow
        password: nott311ing
    wdk:
      modelconfig:
        userdb:
          login: gusfring
          password: s3cr3t
        appdb:
          login: gusfring
          password: s3cr3t
    httpd:
      vhost: sa.vm.foodb.org
      basic_auth_required: false
    website:
      owner: vagrant


Example Playbook
----------------

    - hosts: all
      become: no
      gather_facts: yes
      roles:
        - { role: ebrcwebsite }


    ansible-playbook --extra-vars "settings_file=$PWD/installsite.yml" playbook.yml

License
-------

BSD

Author Information
------------------

help@eupathdb.org
