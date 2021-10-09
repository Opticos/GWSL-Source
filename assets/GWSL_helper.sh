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
			sed -i.bak '/DISPLAY /d' ~/.config/fish/config.fish
			echo "set -gx DISPLAY :0.0 #GWSL" >> ~/.config/fish/config.fish
		elif [ $wsl_shell == "zsh" ]
		then
			# Configure Zsh
			sed -i.bak '/DISPLAY=/d' ~/.zshrc
			echo "export DISPLAY=:0.0  #GWSL" >> ~/.zshrc
		elif [ $wsl_shell == "bash" ]
		then
			# Configure Bash
			sed -i.bak '/DISPLAY=/d' ~/.profile
			echo "export DISPLAY=:0.0  #GWSL" >> ~/.profile
			sed -i.bak '/DISPLAY=/d' ~/.bashrc
			echo "export DISPLAY=:0.0  #GWSL" >> ~/.bashrc
		fi
	
	elif [ $wsl_version == "2" ]
	then
		echo Configuring Display for WSL 2 and $wsl_shell
		if [ $wsl_shell == "fish" ]
		then
			# Configure Fish
			sed -i.bak '/DISPLAY /d' ~/.config/fish/config.fish
			echo "set -gx DISPLAY (ip -4 route show default | cut -d' ' -f3):0.0 #GWSL" >> ~/.config/fish/config.fish
		elif [ $wsl_shell == "zsh" ]
		then
			# Configure Zsh
			sed -i.bak '/DISPLAY=/d' ~/.zshrc
			echo "export DISPLAY=\$(ip -4 route show default | cut -d' ' -f3):0.0 #GWSL" >> ~/.zshrc
		elif [ $wsl_shell == "bash" ]
		then
			# Configure Bash
			sed -i.bak '/DISPLAY=/d' ~/.profile
			echo "export DISPLAY=\$(ip -4 route show default | cut -d' ' -f3):0.0 #GWSL" >> ~/.profile
			sed -i.bak '/DISPLAY=/d' ~/.bashrc
			echo "export DISPLAY=\$(ip -4 route show default | cut -d' ' -f3):0.0 #GWSL" >> ~/.bashrc
		fi
	fi

elif [ "export-a" == "$i" ] #Bash Export audio = tcp:ip. Usage: tools export-a 1 shell
then
	wsl_version="$2"
	wsl_shell="$3"
	
	if [ $wsl_version == "1" ]
	then
		echo Configuring Audio for WSL 1 and $wsl_shell
		if [ $wsl_shell == "fish" ]
		then
			# Configure Fish
			sed -i.bak '/PULSE_SERVER /d' ~/.config/fish/config.fish
			echo "set -gx PULSE_SERVER tcp:localhost #GWSL" >> ~/.config/fish/config.fish
		elif [ $wsl_shell == "zsh" ]
		then
			# Configure Zsh
			sed -i.bak '/PULSE_SERVER=/d' ~/.zshrc
			echo "export PULSE_SERVER=tcp:localhost #GWSL" >> ~/.zshrc
		elif [ $wsl_shell == "bash" ]
		then
			# Configure Bash
			sed -i.bak '/PULSE_SERVER=/d' ~/.profile
			echo "export PULSE_SERVER=tcp:localhost #GWSL" >> ~/.profile
			sed -i.bak '/PULSE_SERVER=/d' ~/.bashrc
			echo "export PULSE_SERVER=tcp:localhost #GWSL" >> ~/.bashrc
		fi
	
	elif [ $wsl_version == "2" ]
	then
		echo Configuring Audio for WSL 2 and $wsl_shell
		if [ $wsl_shell == "fish" ]
		then
			# Configure Fish
			sed -i.bak '/PULSE_SERVER /d' ~/.config/fish/config.fish
			echo "set -gx PULSE_SERVER tcp:(ip -4 route show default | cut -d' ' -f3) #GWSL" >> ~/.config/fish/config.fish
		elif [ $wsl_shell == "zsh" ]
		then
			# Configure Zsh
			sed -i.bak '/PULSE_SERVER=/d' ~/.zshrc
			echo "export PULSE_SERVER=tcp:\$(ip -4 route show default | cut -d' ' -f3) #GWSL" >> ~/.zshrc
		elif [ $wsl_shell == "bash" ]
		then
			# Configure Bash
			sed -i.bak '/PULSE_SERVER=/d' ~/.profile
			echo "export PULSE_SERVER=tcp:\$(ip -4 route show default | cut -d' ' -f3) #GWSL" >> ~/.profile
			sed -i.bak '/PULSE_SERVER=/d' ~/.bashrc
			echo "export PULSE_SERVER=tcp:\$(ip -4 route show default | cut -d' ' -f3) #GWSL" >> ~/.bashrc
		fi
	fi

elif [ "export-v" == $i ] # set env variable in all wsl shells. Usage: tools export-v var val
then
    var_name="$2"
	var_value="$3"
	wsl_shell="$4"
	echo Exporting Variable $var_name for WSL with value $var_value on $wsl_shell
	
	if [ $wsl_shell == "fish" ]
	then
		# Configure Fish
		sed -i.bak '/set -gx '"$var_name"'/d' ~/.config/fish/config.fish
		echo 'set -gx '"$var_name"' '"$var_value"' #GWSL' >> ~/.config/fish/config.fish
		
	elif [ $wsl_shell == "zsh" ]
	then
		# Configure Zsh
		sed -i.bak '/'"$var_name"'=/d' ~/.zshrc
		echo 'export '"$var_name"'='"$var_value"' #GWSL' >> ~/.zshrc
		
	elif [ $wsl_shell == "bash" ]
	then
		# Configure Bash
		sed -i.bak '/'"$var_name"'=/d' ~/.profile
		echo 'export '"$var_name"'='"$var_value"' #GWSL' >> ~/.profile
		sed -i.bak '/'"$var_name"'=/d' ~/.bashrc
		echo 'export '"$var_name"'='"$var_value"' #GWSL' >> ~/.bashrc
	fi

elif [ "listappsold" == $i ] #return list of installed gui apps and commands
then
	all_apps=()
	apps=`find -L /usr/share/applications -name '*.desktop' -print0 |xargs -0 grep -i -l "Terminal=False"`
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
	
elif [ "listapps" == $i ] #return list of installed gui apps and commands
then
	all_apps=()
	apps=`find -L /usr/share/applications -name '*.desktop' -print0 |xargs -0 grep -i -l "Terminal=False"`
	for app in $apps
	do
		all_apps+=$app"\n"
		
	done
	echo -e $all_apps

elif [ "profile" == $i ] #cat of .profile
then
	wsl_shell="$2"
	
	
	if [ $wsl_shell == "fish" ]
	then
		cat ~/.config/fish/config.fish
	elif [ $wsl_shell == "zsh" ]
	then
		cat ~/.zshrc
	elif [ $wsl_shell == "bash" ]
	then
		cat ~/.profile
	fi

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
	
elif [ "cleanup" == $i ] #cleanup all modifications made by GWSL
then
	echo "cleaning .profile"
	sed -i.bak '/#GWSL/d' ~/.profile
	echo "cleaning .bashrc"
	sed -i.bak '/#GWSL/d' ~/.bashrc
	echo "cleaning .zshrc"
	sed -i.bak '/#GWSL/d' ~/.zshrc
	echo "cleaning .config/fish/config.fish"
	sed -i.bak '/#GWSL/d' ~/.config/fish/config.fish


else
   echo "Not recognized"
fi