$script = <<-SCRIPT
# echo "Preparing local node_modules folder…"
# mkdir -p /home/vagrant/app/sdk/vagrant_node_modules
# chown vagrant:vagrant /home/vagrant/app/sdk/vagrant_node_modules
echo "cd /vagrant" >> /home/vagrant/.profile
echo "cd /vagrant" >> /home/vagrant/.bashrc
echo "All good!!"
SCRIPT

Vagrant.configure("2") do |config|

    ######## March 23, 2020 - Support for express setup
    # Please read the instructions under network/setup/vexpress/README.md
    # March 24, 2020 - changed to 18.04
    
    # 1. Use this for "Standard setup"
    config.vm.box = "bento/ubuntu-20.04"

    # 2. Use this for "VirtualBox Express Setup"
    # config.vm.box = "acloudfan/hlfdev2.0-0"

 


    # Uncomment the lines below if you would like to protect the VM
    # config.ssh.username = 'vagrant'
    # config.ssh.password = 'vagrant'
    # config.ssh.insert_key = 'true'


    # Ports foward

	config.vm.network "forwarded_port", guest: 443, host: 443
	config.vm.network "forwarded_port", guest: 80, host: 80
	config.vm.network "forwarded_port", guest: 3030, host: 3030
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 8081, host: 8081
  config.vm.network "forwarded_port", guest: 8090, host: 8090
  config.vm.network "forwarded_port", guest: 8091, host: 8091
  config.vm.network "forwarded_port", guest: 4000, host: 4000
  config.vm.network "forwarded_port", guest: 8889, host: 8889
  config.vm.network "forwarded_port", guest: 8086, host: 8086
  config.vm.network "forwarded_port", guest: 8084, host: 8084
  config.vm.network "forwarded_port", guest: 8083, host: 8083
  config.vm.network "forwarded_port", guest: 8087, host: 8087
  config.vm.network "forwarded_port", guest: 9000, host: 9000
  config.vm.network "forwarded_port", guest: 9001, host: 9001
  config.vm.network "forwarded_port", guest: 8184, host: 8184
  config.vm.network "forwarded_port", guest: 8183, host: 8183
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 3306, host: 4306
  config.vm.network "forwarded_port", guest: 4840, host: 4840


    

    # For Orderer Container
    # config.vm.network "forwarded_port", guest: 7050, host: 7050

    # #Explorer
    # config.vm.network "forwarded_port", guest: 8080, host: 8080
    # #CouchDB
    # config.vm.network "forwarded_port", guest: 5984, host: 5984


    # # For Peer Container
    # config.vm.network "forwarded_port", guest: 7051, host: 7051
    # config.vm.network "forwarded_port", guest: 7052, host: 7052
    # config.vm.network "forwarded_port", guest: 8051, host: 8051
    # config.vm.network "forwarded_port", guest: 8052, host: 8052
    # config.vm.network "forwarded_port", guest: 9051, host: 9051
    # config.vm.network "forwarded_port", guest: 9052, host: 9052
    

    # This gets executed for both vm1 & vm2
    # config.vm.provision "shell", inline:  "echo 'All good'"
    config.vm.provision "shell", inline:  $script

    # config.vm.provision "shell", run: "always", inline: <<-SHELL
    #   mount --bind  /home/vagrant/app/sdk/node_modules /home/vagrant/app/sdk/vagrant_node_modules
    # SHELL
  
    # To use a diffrent Hypervisor create a section config.vm.provider
    # And comment out the following section
    # Configuration for Virtual Box
    config.vm.provider :virtualbox do |vb|
      # Change the memory here if needed - 3 Gb memory on Virtual Box VM
      vb.customize ["modifyvm", :id, "--memory", "3072", "--cpus", "1"]
      # Change this only if you need destop for Ubuntu - you will need more memory
      vb.gui = false
      # In case you have DNS issues
      # vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end

    # Configuration for Windows Hyperv
    config.vm.provider :hyperv do |hv|
      # Change the memory here if needed - 2 Gb memory on Virtual Box VM
      hv.customize ["modifyvm", :id, "--memory", "3072", "--cpus", "1"]
      # Change this only if you need destop for Ubuntu - you will need more memory
      hv.gui = false
      # In case you have DNS issues
      # vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end


  end