pkgconfigdir = $(datadir)/pkgconfig
pkgconfig_DATA = xbitmaps.pc

MAINTAINERCLEANFILES = ChangeLog INSTALL

bitmapdir = $(includedir)/X11/bitmaps

dist_bitmap_DATA =	\
	1x1		\
	2x2		\
	black		\
	black6		\
	boxes		\
	box6		\
	calculator	\
	cntr_ptr	\
	cntr_ptrmsk	\
	cross_weave	\
	dimple1		\
	dimple3		\
	dot		\
	dropbar7	\
	dropbar8	\
	escherknot	\
	flagdown	\
	flagup		\
	flipped_gray	\
	gray		\
	gray1		\
	gray3		\
	grid16		\
	grid2		\
	grid4		\
	grid8		\
	hlines2		\
	hlines3		\
	icon		\
	keyboard16	\
	left_ptr	\
	left_ptrmsk	\
	letters		\
	light_gray	\
	mailempty	\
	mailemptymsk	\
	mailfull	\
	mailfullmsk	\
	mensetmanus	\
	menu10		\
	menu12		\
	menu16		\
	menu6		\
	menu8		\
	noletters	\
	opendot		\
	opendotMask	\
	plaid		\
	right_ptr	\
	right_ptrmsk	\
	root_weave	\
	scales		\
	sipb		\
	star		\
	starMask	\
	stipple		\
	target		\
	terminal	\
	tie_fighter	\
	vlines2		\
	vlines3		\
	weird_size	\
	wide_weave	\
	wingdogs	\
	woman		\
	xfd_icon	\
	xlogo11		\
	xlogo16		\
	xlogo32		\
	xlogo64		\
	xsnow


.PHONY: ChangeLog INSTALL

INSTALL:
	$(INSTALL_CMD)

ChangeLog:
	$(CHANGELOG_CMD)

dist-hook: ChangeLog INSTALL
