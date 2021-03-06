from fabric.api import *
from fabric.contrib.files import upload_template, exists

env.user = 'pi'
env.password = 'raspberry'

packages = """
dbus-x11 desktop-base desktop-file-utils dillo gdb gdbserver gconf-service gconf2 gconf2-common gnome-icon-theme gnome-themes-standard gpicview
gtk2-engines:armhf  hicolor-icon-theme  
gcc g++ g++-4.6  gcc-4.6  gcc-4.4-base gcc-4.5-base gcc-4.6-base  libc6-dev libtagcoll2-dev  libwibble-dev  libxapian-dev
libfm-gtk-bin libfm-gtk1 libgtk2.0-0:armhf libgtk2.0-bin libgtk2.0-common netsurf-gtk
penguinspuzzle omxplayer netsurf-common  mupdf menu-xdg  lxde-icon-theme  lxmenu-data  luajit 
samba-common scratch smartsim squeak-plugins-scratch  squeak-vm  usbmuxd 
xserver-common xserver-xorg xserver-xorg-core xserver-xorg-input-all xserver-xorg-input-evdev xserver-xorg-input-synaptics xserver-xorg-video-fbdev
xdg-utils xauth x11-xkb-utils x11-utils x11-common

nfs-common libnfsidmap2 python3 lua5.1
alsa-base alsa-utils libasound2

libx11-6:armhf libx11-data libx11-xcb1:armhf libxau6:armhf libxcb-render0:armhf libxcb-shape0:armhf libxcb-shm0:armhf libxcb-xfixes0:armhf
libxcb1:armhf libxcursor1:armhf libxdmcp6:armhf libxfixes3:armhf libxkbcommon0:armhf libxrender1:armhf

raspberrypi-artwork
dphys-swapfile

consolekit desktop-base* desktop-file-utils* gnome-icon-theme* gnome-themes-standard* hicolor-icon-theme* leafpad* lxde* 
lxde-core* midori* xserver-common* xserver-xorg* xserver-xorg-core* xserver-xorg-input-all* xserver-xorg-input-evdev* xserver-xorg-input-synaptics* xserver-xorg-video-fbdev*
""".replace("\n", " ").replace('\r', '').split()


def clear():

	tmp = packages[:]

	while len(tmp):
		sudo("apt-get -y purge %s" % ' '.join(tmp[:40]), warn_only=True)
		tmp=tmp[40:]

	sudo("apt-get -y autoremove")

	sudo("dpkg -l |  awk ' /^rc/ {print $2}' | xargs apt-get -y remove --purge")

	sudo("rm -rf Desktop python_games")

	orphan()

def orphan():
	if not exists('/usr/bin/deborphan'):
		sudo("apt-get -y install deborphan")

	sudo("apt-get -y autoremove")

	while True:

		packages = run('deborphan --guess-all').replace('\n', ' ').replace('\r', ' ').strip()

		if packages == '':
			break

		sudo("apt-get -y purge %s" % packages)
		sudo("apt-get -y autoremove")

	sudo("dpkg -l |  awk ' /^rc/ {print $2}' | xargs apt-get -y remove --purge")

def upgrade():
	sudo("apt-get -y update && apt-get -y dist-upgrade && apt-get -y autoremove && apt-get -y autoclean")

def firmware():
	sudo("wget http://goo.gl/1BOfJ -O /usr/bin/rpi-update && chmod +x /usr/bin/rpi-update")
	sudo('mount -o remount,rw /boot')
	sudo("rpi-update")

def nosnd():
	mods = "snd_soc_wm8804 snd_soc_bcm2708_i2s snd_bcm2835 snd_soc_core snd snd_pcm snd_seq snd_timer snd_seq_device snd_page_alloc"

	sudo('echo -n > /etc/modprobe.d/snd-blacklist.conf')

	for x in mods.split():
		sudo('echo "blacklist %s" >> /etc/modprobe.d/snd-blacklist.conf' % x)

	sudo("sed -i 's/snd-bcm2835/#snd-bcm2835/g' /etc/modules")

def gpumem():
	sudo('mount -o remount,rw /boot')
	sudo("echo gpu_mem=16 >> /boot/config.txt")

def spi():
	if exists("/etc/modprobe.d/raspi-blacklist.conf"):
		sudo("rm /etc/modprobe.d/raspi-blacklist.conf", warn_only=True)

def getty():
	sudo("sed -i '/[2-6]:23:respawn:\/sbin\/getty 38400 tty[2-6]/s%^%#%g' /etc/inittab")

def dropbear():
	sudo("apt-get -y install dropbear openssh-client")
	sudo("sed -i 's/NO_START=1/NO_START=0/g' /etc/default/dropbear")
	sudo("sed -i 's/DROPBEAR_EXTRA_ARGS=/DROPBEAR_EXTRA_ARGS=-m /g' /etc/default/dropbear")
	sudo("/etc/init.d/ssh stop && /etc/init.d/dropbear start && apt-get -y purge openssh-server", warn_only=True)

def boot():
	sudo("reboot")

def tmpfs():
	sudo('echo "tmpfs /var/log tmpfs nodev,nosuid,size=50M 0 0" >> /etc/fstab')
	sudo('echo "tmpfs /var/run tmpfs nodev,nosuid,size=1M 0 0" >> /etc/fstab')
	sudo('echo "tmpfs /tmp tmpfs nodev,nosuid,size=100M 0 0" >> /etc/fstab')

def all():
	clear()
	orphan
	upgrade()
	nosnd()
	spi()
	getty()
	dropbear()
	gpumem()
	firmware()
	tmpfs()
	boot()