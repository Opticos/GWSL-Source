#!/bin/bash
# GWSL Helper Script v4

cd ~


i="$1"

#BASH EXPORTS
if [ "export-d" == "$i" ] #Bash Export Display = ip. Usage: tools export-d 1
then
	wsl_version="$2"
	wsl_shell="$3"
	
	if [ $wsl_version == "1" ]
	then
		echo Configuring Display for WSL 1 and $wsl_shell
		if [ $wsl_shell == "fish" ]
		then
			# Configure Fish
			sed -i.bak '/DISPLAY=/d' ~/.config/fish/config.fish
			echo "export DISPLAY=:0.0" >> ~/.config/fish/config.fish
		elif [ $wsl_shell == "zsh" ]
		then
			# Configure Zsh
			sed -i.bak '/DISPLAY=/d' ~/.zshrc
			echo "export DISPLAY=:0.0" >> ~/.zshrc
		elif [ $wsl_shell == "bash" ]
		then
			# Configure Bash
			sed -i.bak '/DISPLAY=/d' ~/.profile
			echo "export DISPLAY=:0.0" >> ~/.profile
			sed -i.bak '/DISPLAY=/d' ~/.bashrc
			echo "export DISPLAY=:0.0" >> ~/.bashrc
	
	elif [ $wsl_version == "2" ]
	then
		echo Configuring Display for WSL 2 and $wsl_shell
		if [ $wsl_shell == "fish" ]
		then
			# Configure Fish
			sed -i.bak '/DISPLAY /d' ~/.config/fish/config.fish
			echo "set -gx DISPLAY (cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.config/fish/config.fish
		elif [ $wsl_shell == "zsh" ]
		then
			# Configure Zsh
			sed -i.bak '/DISPLAY=/d' ~/.zshrc
			echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.zshrc
			elif [ $wsl_shell == "bash" ]
		then
			# Configure Bash
			sed -i.bak '/DISPLAY=/d' ~/.profile
			echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.profile
			sed -i.bak '/DISPLAY=/d' ~/.bashrc
			echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.bashrc
	fi

elif [ "export-v" == $i ] # set env variable in all wsl shells. Usage: tools export-v var val
then
    var_name="$2"
	var_value="$3"
	echo Exporting Variable $var_name for WSL with value $var_value
	# Configure Fish
	sed -i.bak '/set -gx '"$var_name"'/d' ~/.config/fish/config.fish
	echo 'set -gx '"$var_name"' '"$var_value" >> ~/.config/fish/config.fish
	# Configure Zsh
	sed -i.bak '/'"$var_name"'=/d' ~/.zshrc
	echo 'export '"$var_name"'='"$var_value" >> ~/.zshrc
	# Configure Bash
	sed -i.bak '/'"$var_name"'=/d' ~/.profile
	echo 'export '"$var_name"'='"$var_value" >> ~/.profile
	sed -i.bak '/'"$var_name"'=/d' ~/.bashrc
	echo 'export '"$var_name"'='"$var_value" >> ~/.bashrc
	

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
		all_apps+=`cat $app | sed -En '/^Name=/p'`
		all_apps+=":cmd:"
		all_apps+=`cat $app | sed -En '/^Exec=/p'`
		all_apps+=":ico:"
		all_apps+=`cat $app | sed -En '/Icon=/p'`
		all_apps+="/:/"
	done
	echo -e $all_apps

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

else
   echo "Not recognized"
fi
