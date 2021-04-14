1.3.3
First Stable Release

1.3.4
First Broken Build
Added process management stability (No more disappearing windows)
Fixed DPI fpr dashboard and tray menu
Decreased service cpu usage from 20% to 0.2%
Added catch for older versions of windows

1.3.5
Attempted Build Fix (FAILED)
First version with Traditional Installer Support

1.3.6
Fixed Broken Build
Added option to change Dashboard position
Changed method of finding Host IP
ADD NOTE ON SITE TO SAY FIXED

1.3.7 #CURRENT RELEASE. OPTIONS WITH TODO GO INTO 1.3.8
DONE PulseAudio Bundle (NEED POC)
DONE Add catch to make sure WSL is v2 on 1909. Somehow get rid of support for previous builds. (RESEARCH BUILD NUMBERS)
DONE check to see if bash is existing with which to fix problems with other shells
TODO Add localization with gettext and poedit. Get Volunteers.
TODO Update DOCS accordingly.
TODO If gwsl closed before service can start, keep service a little longer and try to finish starting service in background
TODO Remove "." to specify profile and use -l to start a login shell (it is an L)
NEEDS WORK Add logging for output of linux commands
DONE Add settings.json option to pass flags to vcxsrv
DONE Make GWSL move with new taskbar positions too...
DONE Make shell button also use windows terminal. Put in settings
TODO Get people to port GWSL_helper.sh into more shells
DONE Add -startup flag for starting at windows login
DONE HI-DPI
DONE TEST WITH JETBRAINS IDEs
MAYBE A BUG Help with shortcuts not working because of local encoding
DONE Add Notiication Saying display exported
TODO (FAILED ATTEMPT) Add xserver text to logo on the store because title cannot be changed

1.3.8 OR FUTURE
*  DONE AND TEST update vcxsrv to latest 64
*  DONE DPI in store version and remove duplicate vcxsrv. POC Done. TEST AND RELEASE
*  TODO sound POC COMPLETED
*  DONE port number in ssh box
*  TODO more shell compatability (Goes with consolidation of run commands)
*  TODO maybe: Remove "." to specify profile and use -l to start a login shell (it is an L)
*  TODO If gwsl closed before service can start, keep service a little longer and try to finish starting service in background
*  TODO localize it maybe
*  TODO WRITE MANUALS
*  DONE reduce cpu spikes with check service calls Check PR from @sanzoghenzo for reference
*  DONE faster app loading with @sanzoghenzo's method. Test all distros. Wait. !!!!!I think this might break WSL1 compatability. Maybe slower is better at this stage
*  TODO debug GWSL error #31 github
*  TODO GET PASSWORD OUT OF LOGS (add donotlog arg to pass to run when consolidated)
*  TODO Make sure new profile system works with shortcut menu. THIS WILL ALSO FIX #31
*  TODO again! consolidate run commands
*  DONE TRY TO USE WSL tools from @sanzoghenzo and help debug his code. 
*  DONE SSH keys for authentication
*  Add button in distro settings to add libgl indirect to profile etc.
*  DONE Add button saying type to jump down the list.
*  Add "ubuntu" to store tags
*  Add "xserver" to store icon
