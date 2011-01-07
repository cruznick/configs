#!/bin/bash
cd /home/cruznick
#
eval `dbus-launch --sh-syntax --exit-with-session`
#
/usr/bin/X :0.0 -br -audit 0 -nolisten tcp vt7 &
#
export DISPLAY=:0.0
#
sleep 1
#
feh --bg-scale '/media/archivos/global/anime/Misa_Campo_by_blaffle.jpg'  &
cp ~/.config/compiz/gtkrccompiz ~/.gtkrc-2.0 &
compiz-manager decoration move resize > /tmp/compiz.log 2>&1 &

thunar --daemon &
python2 ~/.bin/mpd_infos.py &
fusion-icon &
volwheel&
sleep 2
parcellite &
blueman-applet &
sleep 1
xbindkeys &
xfce4-power-manager &
#Disable Nautilus desktop.
gconftool-2 -s -t bool /apps/nautilus/preferences/show_desktop false &
# Do not let Nautilus set the background image.
gconftool-2 -s -t bool /desktop/gnome/background/draw_background false &
# Make Nautilus show the advanced permissions dialog 
gconftool-2 -s -t bool /apps/nautilus/preferences/show_advanced_permissions true &
avant-window-navigator &
guake &
#lxpanel &
wicd-client
