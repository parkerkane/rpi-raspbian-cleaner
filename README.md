# rpi-raspbian-cleaner

Common tasks to clean up rasbian for headless usage.

### Usage

To uninstall default packages:

	$ fab clear
	
Do upgarde and do dist upgrade:
	
	$ fab upgrade
	
Update firmware:

	$ fab firmware
	
Set gpumem as low as possible (16MB):

	$ fab gpumem
	
Enable spi and i2c:

	$ fab spi
	
Remove getty from tty2-6:

	$ fab getty
	
Replace openssh with dropbear:

	$ fab dropbear
	
Make `/var/log`, `/var/run` and `/tmp` to use tmpfs to save SD card:

	$ fab tmpfs
	
Do all above:

	$ fab all
	
