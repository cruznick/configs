## Openbox autostart.sh
## ====================
## When you login to your CrunchBang Openbox session, this autostart script 
## will be executed to set-up your environment and launch any applications
## you want to run at startup.
##
## More information about this can be found at:
## http://openbox.org/wiki/Help:Autostart
##
## If you do something cool with your autostart script and you think others
## could benefit from your hack, please consider sharing it at:
## http://crunchbanglinux.org/forums/
##
## Have fun! :)

## Start session manager
lxsession &

## Enable power management
xfce4-power-manager &

## Start Thunar Daemon
thunar --daemon &

## Set desktop wallpaper
nitrogen --restore &

## Launch panel
tint2 &

## Enable Eyecandy - off by default, uncomment one of the commands below.
## Note: cairo-compmgr prefers a sleep delay, else it tends to produce
## odd shadows/quirks around tint2 & Conky.
#(sleep 10s && cb-compmgr --cairo-compmgr) &
#cb-compmgr --xcompmgr & 

## Launch network manager applet
(sleep 4s && nm-applet) &

## Detect and configure touchpad. See 'man synclient' for more info.
if egrep -iq 'touchpad' /proc/bus/input/devices; then
    synclient VertEdgeScroll=1 &
    synclient TapButton1=1 &
fi

## Start xscreensaver
xscreensaver -no-splash &

## Start Conky after a slight delay
(sleep 3s && conky -q -c ~/.conky/obox/conkyrc ) &

## Start volumeicon after a slight delay
(sleep 3s && volumeicon) &

## Nautilus gconf settings, minimises the impact of running Nautilus under
## a pure Openbox session. Safe to delete if you are never going to use Nautilus,
## or, uncomment if you plan on installing and using Nautilus.
gconftool-2 -s -t bool /apps/nautilus/preferences/show_desktop false &
gconftool-2 -s -t bool /desktop/gnome/background/draw_background false &
gconftool-2 -s -t bool /apps/nautilus/preferences/show_advanced_permissions true &



## keyboard
    setxkbmap  latam,us &
    (sleep 1s && fbxkb) &

## cb-fortune - have Statler say a little adage
(sleep 120s && cb-fortune) &

# Autostart the Dropbox deamon
(sleep 10s && ~/.dropbox-dist/dropboxd) &
sleep 1
parcellite &
mpd_infos.py &
guake &
xcom set &
 cp ~/.config/openbox/gtkobox ~/.gtkrc-2.0
