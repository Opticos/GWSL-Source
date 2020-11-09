#!/bin/bash
# GWSL Helper Script v3

cd ~



for i in "$*"
do
    if [ "export2" == $i ] #Export Display = ip 
	then
		echo "exporting DISPLAY for WSL2"
		sed -i.bak '/DISPLAY=/d' ~/.profile
		echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.profile

		
		sed -i.bak '/DISPLAY=/d' ~/.bashrc
		echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.bashrc
	
	
	elif [ "export1" == $i ] #Export Display = 0 
	then
		echo "exporting DISPLAY for WSL1"
		sed -i.bak '/DISPLAY=/d' ~/.profile
		echo "export DISPLAY=:0" >> ~/.profile
		
		sed -i.bak '/DISPLAY=/d' ~/.bashrc
		echo "export DISPLAY=:0" >> ~/.bashrc
		
	elif [ "qt1" == $i ] #QT scale 1
	then
		echo "exporting qt=1"
		sed -i.bak '/QT_SCALE_FACTOR=/d' ~/.profile
		echo "export QT_SCALE_FACTOR=1" >> ~/.profile
		
		sed -i.bak '/QT_SCALE_FACTOR=/d' ~/.bashrc
		echo "export QT_SCALE_FACTOR=1" >> ~/.bashrc
		
	elif [ "qt2" == $i ] #QT scale 2
	then
		echo "exporting qt=2"
		sed -i.bak '/QT_SCALE_FACTOR=/d' ~/.profile
		echo "export QT_SCALE_FACTOR=2" >> ~/.profile
		
		sed -i.bak '/QT_SCALE_FACTOR=/d' ~/.bashrc
		echo "export QT_SCALE_FACTOR=2" >> ~/.bashrc
		
	elif [ "gtk1" == $i ] #GTK scale 1
	then
		echo "exporting gtk=1"
		sed -i.bak '/GDK_SCALE=/d' ~/.profile
		echo "export GDK_SCALE=1" >> ~/.profile
		
		sed -i.bak '/GDK_SCALE=/d' ~/.bashrc
		echo "export GDK_SCALE=1" >> ~/.bashrc
		
	elif [ "gtk2" == $i ] #GTK scale 2
	then
		echo "exporting gtk=2"
		sed -i.bak '/GDK_SCALE=/d' ~/.profile
		echo "export GDK_SCALE=2" >> ~/.profile
		
		sed -i.bak '/GDK_SCALE=/d' ~/.bashrc
		echo "export GDK_SCALE=2" >> ~/.bashrc
	
	elif [ "listapps" == $i ] #return list of installed gui apps and commands
	then
		all_apps=()
		apps=`find /usr/share/applications -name '*.desktop' -print0 |xargs -0 grep -i -l "Terminal=False"`
		for app in $apps
		do
			all_apps+=`cat $app | sed -En '/Name=/p'`
			all_apps+=":cmd:"
			all_apps+=`cat $app | sed -En '/^Exec=/p'`
			all_apps+=":ico:"
			all_apps+=`cat $app | sed -En '/Icon=/p'`
			all_apps+="/:/"
		done
		echo $all_apps
		
	elif [ "profile" == $i ] #cat of .profile
	then
		cat ~/.profile
		
	elif [ "listthemes" == $i ] #return list of installed themes in usr themes and home themes
	then
		all_themes=()
		themes=`find /usr/share/themes  -maxdepth 1 -type d`
		for theme in $themes
		do
			type=`ls $theme`
			if [[ $type == *"gtk-"* ]]
			then
				all_themes+=$theme
				all_themes+=":theme:"
			fi
		done
		
		themes=`find ~/.themes  -maxdepth 1 -type d` || echo ""
		for theme in $themes
		do
			type=`ls $theme`
			if [[ $type == *"gtk-"* ]]
			then
				all_themes+=$theme
				all_themes+=":theme:"
			fi
		done
		
		
		echo $all_themes
		
	elif [ "dbus" == $i ] #inject start dbus into profile
	then
		echo "injecting dbus into .profile"
		sed -i.bak '//etc/init.d/dbus start/d' ~/.profile
		echo "sudo /etc/init.d/dbus start" >> ~/.profile
		
		sed -i.bak '//etc/init.d/dbus start/d' ~/.bashrc
		echo "sudo /etc/init.d/dbus start" >> ~/.bashrc
	
		
	fi
done