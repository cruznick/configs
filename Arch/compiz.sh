#!/bin/bash
# Set a background color
BG="#ffffff"
if which hsetroot >/dev/null 2>&1; then
    BG=hsetroot
else
    if which esetroot >/dev/null 2>&1; then
	BG=esetroot
    else
	if which xsetroot >/dev/null 2>&1; then
	    BG=xsetroot
	fi
    fi
fi
test -z $BG || $BG -solid "#202020"

# D-bus
if which dbus-launch >/dev/null 2>&1 && test -z "$DBUS_SESSION_BUS_ADDRESS"; then
    eval `dbus-launch --sh-syntax --exit-with-session`
fi

# Run XDG autostart things.  By default don't run anything desktop-specific
# See xdg-autostart --help more info
DESKTOP_ENV="COMPIZ"
if which /usr/bin/xdg-autostart >/dev/null 2>&1; then
  /usr/bin/xdg-autostart $DESKTOP_ENV
fi

export vblank_mode=0 

thunar --daemon &
python2 ~/bin/mpd_infos.py &
fusion-icon &
volwheel &
sleep 4
urxvtd -q -f -o &
sleep 1
#Disable Nautilus desktop.
gconftool-2 -s -t bool /apps/nautilus/preferences/show_desktop false &
# Do not let Nautilus set the background image.
gconftool-2 -s -t bool /desktop/gnome/background/draw_background false &
# Make Nautilus show the advanced permissions dialog
gconftool-2 -s -t bool /apps/nautilus/preferences/show_advanced_permissions true &
#covergloobus &
tilda &
parcellite  &
wicd-gtk &
avant-window-navigator
#tint2
