;--------------------------------------------------------
; File Created by SDCC : free open source ISO C Compiler 
; Version 4.3.0 #14184 (MINGW64)
;--------------------------------------------------------
	.module hiscores
	.optsdcc -mz80
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _hiscores_overlay_entry
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _DATA
_standard_scores:
	.ds 480
_campaign_scores:
	.ds 480
_disk_image:
	.ds 2048
_slot_plain:
	.ds 1024
_is_campaign:
	.ds 1
_lmb_latch:
	.ds 1
_pressed_other:
	.ds 1
_pressed_exit:
	.ds 1
_active_slot:
	.ds 1
_disk_available:
	.ds 1
_active_generation:
	.ds 4
_animation_frame:
	.ds 2
_sprite_base_x:
	.ds 2
_sprite_base_y:
	.ds 2
_screen_dirty:
	.ds 1
_abi_call_barrier:
	.ds 1
_scale_px_table:
	.ds 1282
_scale_vertex_table:
	.ds 1282
_scale_tables_ready:
	.ds 1
;--------------------------------------------------------
; ram data
;--------------------------------------------------------
	.area _INITIALIZED
;--------------------------------------------------------
; absolute external ram data
;--------------------------------------------------------
	.area _DABS (ABS)
;--------------------------------------------------------
; global & static initialisations
;--------------------------------------------------------
	.area _HOME
	.area _GSINIT
	.area _GSFINAL
	.area _GSINIT
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area _HOME
	.area _HOME
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area _CODE
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:124: static void copy_bytes(uint8_t * dst, const uint8_t * src, uint16_t count)
;	---------------------------------
; Function copy_bytes
; ---------------------------------
_copy_bytes:
	push	ix
	ld	ix,#0
	add	ix,sp
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:126: while (count != 0) {
	ld	c, 4 (ix)
	ld	b, 5 (ix)
00101$:
	ld	a, b
	or	a, c
	jr	Z, 00104$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:127: *dst++ = *src++;
	ld	a, (de)
	inc	de
	ld	(hl), a
	inc	hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:128: --count;
	dec	bc
	jp	00101$
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:130: }
	pop	ix
	pop	hl
	pop	af
	jp	(hl)
_hs_bg:
	.dw #0x0400
	.db #0x00	; 0
	.dw #0x013f
	.dw #0x013f
	.dw #0x0000
	.dw #0x0000
	.dw #0x9184
	.db #0x01	; 1
	.dw #0x013f
	.dw #0x013f
	.dw #0x013f
	.dw #0x0000
	.dw #0x1f08
	.db #0x03	; 3
	.dw #0x0002
	.dw #0x013f
	.dw #0x027e
	.dw #0x0000
	.dw #0x2188
	.db #0x03	; 3
	.dw #0x013f
	.dw #0x00a1
	.dw #0x0000
	.dw #0x013f
	.dw #0xea28
	.db #0x03	; 3
	.dw #0x013f
	.dw #0x00a1
	.dw #0x013f
	.dw #0x013f
	.dw #0xb2c8
	.db #0x04	; 4
	.dw #0x0002
	.dw #0x00a1
	.dw #0x027e
	.dw #0x013f
_hs_title_standard:
	.dw #0xb40c
	.db #0x04	; 4
	.dw #0x013f
	.dw #0x0014
	.dw #0x0032
	.dw #0x001f
	.dw #0xccf8
	.db #0x04	; 4
	.dw #0x00dd
	.dw #0x0014
	.dw #0x0171
	.dw #0x001f
_hs_title_campaign:
	.dw #0xde3c
	.db #0x04	; 4
	.dw #0x013f
	.dw #0x0014
	.dw #0x0032
	.dw #0x001f
	.dw #0xf728
	.db #0x04	; 4
	.dw #0x00dd
	.dw #0x0014
	.dw #0x0171
	.dw #0x001f
_hs_button_campaign:
	.dw #0x086c
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0085
	.dw #0x0008
	.dw #0x013b
	.dw #0x1674
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0085
	.dw #0x0008
	.dw #0x013b
_hs_button_standard:
	.dw #0x247c
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0085
	.dw #0x0008
	.dw #0x013b
	.dw #0x3284
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0085
	.dw #0x0008
	.dw #0x013b
_hs_button_exit:
	.dw #0x408c
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0085
	.dw #0x025c
	.dw #0x013b
	.dw #0x4e94
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0085
	.dw #0x025c
	.dw #0x013b
_hs_monster_ids:
	.db #0x01	; 1
	.db #0x0c	; 12
	.db #0x15	; 21
	.db #0x27	; 39
	.db #0x1e	; 30
	.db #0x3a	; 58
	.db #0x30	; 48	'0'
	.db #0x0d	; 13
	.db #0x31	; 49	'1'
	.db #0x02	; 2
	.db #0x03	; 3
	.db #0x28	; 40
	.db #0x16	; 22
	.db #0x32	; 50	'2'
	.db #0x0e	; 14
	.db #0x18	; 24
	.db #0x1f	; 31
	.db #0x04	; 4
	.db #0x19	; 25
	.db #0x17	; 23
	.db #0x3b	; 59
	.db #0x05	; 5
	.db #0x0f	; 15
	.db #0x33	; 51	'3'
	.db #0x29	; 41
	.db #0x34	; 52	'4'
	.db #0x10	; 16
	.db #0x20	; 32
	.db #0x06	; 6
	.db #0x1a	; 26
	.db #0x2a	; 42
	.db #0x07	; 7
	.db #0x3f	; 63
	.db #0x1b	; 27
	.db #0x41	; 65	'A'
	.db #0x3d	; 61
	.db #0x35	; 53	'5'
	.db #0x42	; 66	'B'
	.db #0x3e	; 62
	.db #0x2b	; 43
	.db #0x21	; 33
	.db #0x08	; 8
	.db #0x12	; 18
	.db #0x2c	; 44
	.db #0x3c	; 60
	.db #0x37	; 55	'7'
	.db #0x11	; 17
	.db #0x22	; 34
	.db #0x09	; 9
	.db #0x13	; 19
	.db #0x36	; 54	'6'
	.db #0x2d	; 45
	.db #0x38	; 56	'8'
	.db #0x1c	; 28
	.db #0x23	; 35
	.db #0x0a	; 10
	.db #0x40	; 64
	.db #0x0b	; 11
	.db #0x14	; 20
	.db #0x2e	; 46
	.db #0x1d	; 29
	.db #0x39	; 57	'9'
	.db #0x24	; 36
	.db #0x25	; 37
	.db #0x2f	; 47
	.db #0x26	; 38
_hs_monsters:
	.dw #0x5c9c
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe6
	.dw #0x6000
	.db #0x05	; 5
	.dw #0x0026
	.dw #0x0019
	.dw #0xffe5
	.dw #0xffe7
	.dw #0x63b8
	.db #0x05	; 5
	.dw #0x0026
	.dw #0x0019
	.dw #0xffe5
	.dw #0xffe7
	.dw #0x6770
	.db #0x05	; 5
	.dw #0x0027
	.dw #0x0019
	.dw #0xffe5
	.dw #0xffe7
	.dw #0x6b40
	.db #0x05	; 5
	.dw #0x0027
	.dw #0x0019
	.dw #0xffe5
	.dw #0xffe7
	.dw #0x6f10
	.db #0x05	; 5
	.dw #0x0028
	.dw #0x0019
	.dw #0xffe5
	.dw #0xffe7
	.dw #0x72f8
	.db #0x05	; 5
	.dw #0x0024
	.dw #0x0017
	.dw #0xffe9
	.dw #0xffe7
	.dw #0x7634
	.db #0x05	; 5
	.dw #0x0020
	.dw #0x001a
	.dw #0xffe6
	.dw #0xffe8
	.dw #0x7974
	.db #0x05	; 5
	.dw #0x001c
	.dw #0x0014
	.dw #0xffed
	.dw #0xffe9
	.dw #0x7ba4
	.db #0x05	; 5
	.dw #0x001b
	.dw #0x0015
	.dw #0xffed
	.dw #0xffe9
	.dw #0x7ddc
	.db #0x05	; 5
	.dw #0x001a
	.dw #0x0016
	.dw #0xffed
	.dw #0xffe9
	.dw #0x8018
	.db #0x05	; 5
	.dw #0x0021
	.dw #0x0015
	.dw #0xffe8
	.dw #0xffe8
	.dw #0x82d0
	.db #0x05	; 5
	.dw #0x0024
	.dw #0x0018
	.dw #0xffe5
	.dw #0xffe8
	.dw #0x8630
	.db #0x05	; 5
	.dw #0x0024
	.dw #0x0018
	.dw #0xffe5
	.dw #0xffe8
	.dw #0x8990
	.db #0x05	; 5
	.dw #0x0023
	.dw #0x001c
	.dw #0xffe4
	.dw #0xffe6
	.dw #0x8d64
	.db #0x05	; 5
	.dw #0x0024
	.dw #0x0015
	.dw #0xffe3
	.dw #0xffe6
	.dw #0x9058
	.db #0x05	; 5
	.dw #0x0025
	.dw #0x0017
	.dw #0xffe2
	.dw #0xffe6
	.dw #0x93ac
	.db #0x05	; 5
	.dw #0x0025
	.dw #0x0018
	.dw #0xffe2
	.dw #0xffe6
	.dw #0x9724
	.db #0x05	; 5
	.dw #0x0025
	.dw #0x0017
	.dw #0xffe2
	.dw #0xffe6
	.dw #0x9a78
	.db #0x05	; 5
	.dw #0x0024
	.dw #0x0018
	.dw #0xffe2
	.dw #0xffe6
	.dw #0x9dd8
	.db #0x05	; 5
	.dw #0x0024
	.dw #0x0017
	.dw #0xffe2
	.dw #0xffe6
	.dw #0xa114
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x001a
	.dw #0xffe7
	.dw #0xffe8
	.dw #0xa43c
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x0016
	.dw #0xffea
	.dw #0xffe8
	.dw #0xa6e8
	.db #0x05	; 5
	.dw #0x0020
	.dw #0x0015
	.dw #0xffe8
	.dw #0xffe9
	.dw #0xa988
	.db #0x05	; 5
	.dw #0x0021
	.dw #0x0015
	.dw #0xffe8
	.dw #0xffe9
	.dw #0xac40
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x0015
	.dw #0xffea
	.dw #0xffe8
	.dw #0xaecc
	.db #0x05	; 5
	.dw #0x0021
	.dw #0x0015
	.dw #0xffea
	.dw #0xffe8
	.dw #0xb184
	.db #0x05	; 5
	.dw #0x0021
	.dw #0x0014
	.dw #0xffea
	.dw #0xffe8
	.dw #0xb418
	.db #0x05	; 5
	.dw #0x0028
	.dw #0x001c
	.dw #0xffe5
	.dw #0xffe6
	.dw #0xb878
	.db #0x05	; 5
	.dw #0x002c
	.dw #0x001b
	.dw #0xffe8
	.dw #0xffe4
	.dw #0xbd1c
	.db #0x05	; 5
	.dw #0x002c
	.dw #0x001a
	.dw #0xffe8
	.dw #0xffe4
	.dw #0xc194
	.db #0x05	; 5
	.dw #0x002c
	.dw #0x0018
	.dw #0xffe8
	.dw #0xffe4
	.dw #0xc5b4
	.db #0x05	; 5
	.dw #0x002b
	.dw #0x001a
	.dw #0xffe8
	.dw #0xffe5
	.dw #0xca14
	.db #0x05	; 5
	.dw #0x002a
	.dw #0x0019
	.dw #0xffe8
	.dw #0xffe6
	.dw #0xce30
	.db #0x05	; 5
	.dw #0x002a
	.dw #0x0019
	.dw #0xffe8
	.dw #0xffe6
	.dw #0xd24c
	.db #0x05	; 5
	.dw #0x0021
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe6
	.dw #0xd5e8
	.db #0x05	; 5
	.dw #0x0014
	.dw #0x0017
	.dw #0xfff5
	.dw #0xffe7
	.dw #0xd7b4
	.db #0x05	; 5
	.dw #0x001c
	.dw #0x0019
	.dw #0xffed
	.dw #0xffe7
	.dw #0xda70
	.db #0x05	; 5
	.dw #0x001c
	.dw #0x0018
	.dw #0xffed
	.dw #0xffe7
	.dw #0xdd10
	.db #0x05	; 5
	.dw #0x0014
	.dw #0x0017
	.dw #0xfff5
	.dw #0xffe7
	.dw #0xdedc
	.db #0x05	; 5
	.dw #0x0016
	.dw #0x0017
	.dw #0xfff6
	.dw #0xffe7
	.dw #0xe0d8
	.db #0x05	; 5
	.dw #0x0017
	.dw #0x0017
	.dw #0xfff6
	.dw #0xffe7
	.dw #0xe2ec
	.db #0x05	; 5
	.dw #0x0022
	.dw #0x0019
	.dw #0xffe7
	.dw #0xffe9
	.dw #0xe640
	.db #0x05	; 5
	.dw #0x001e
	.dw #0x0019
	.dw #0xffed
	.dw #0xffe6
	.dw #0xe930
	.db #0x05	; 5
	.dw #0x0026
	.dw #0x0017
	.dw #0xffe5
	.dw #0xffe5
	.dw #0xec9c
	.db #0x05	; 5
	.dw #0x0026
	.dw #0x0017
	.dw #0xffe5
	.dw #0xffe5
	.dw #0xf008
	.db #0x05	; 5
	.dw #0x001e
	.dw #0x0019
	.dw #0xffed
	.dw #0xffe6
	.dw #0xf2f8
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x0019
	.dw #0xffeb
	.dw #0xffe6
	.dw #0xf600
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x0019
	.dw #0xffeb
	.dw #0xffe6
	.dw #0xf908
	.db #0x05	; 5
	.dw #0x0020
	.dw #0x001b
	.dw #0xffe6
	.dw #0xffe7
	.dw #0xfc68
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x001a
	.dw #0xffef
	.dw #0xffe4
	.dw #0xff90
	.db #0x05	; 5
	.dw #0x001f
	.dw #0x001a
	.dw #0xffef
	.dw #0xffe4
	.dw #0x02b8
	.db #0x06	; 6
	.dw #0x0020
	.dw #0x001a
	.dw #0xffed
	.dw #0xffe4
	.dw #0x05f8
	.db #0x06	; 6
	.dw #0x002a
	.dw #0x001b
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x0a68
	.db #0x06	; 6
	.dw #0x002a
	.dw #0x001b
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x0ed8
	.db #0x06	; 6
	.dw #0x002a
	.dw #0x001b
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x1348
	.db #0x06	; 6
	.dw #0x0021
	.dw #0x001e
	.dw #0xffe5
	.dw #0xffe4
	.dw #0x1728
	.db #0x06	; 6
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x1ca8
	.db #0x06	; 6
	.dw #0x002d
	.dw #0x0023
	.dw #0xffdc
	.dw #0xffde
	.dw #0x22d0
	.db #0x06	; 6
	.dw #0x0031
	.dw #0x0022
	.dw #0xffd8
	.dw #0xffdd
	.dw #0x2954
	.db #0x06	; 6
	.dw #0x002f
	.dw #0x001f
	.dw #0xffdf
	.dw #0xffe2
	.dw #0x2f08
	.db #0x06	; 6
	.dw #0x0030
	.dw #0x0022
	.dw #0xffdb
	.dw #0xffdf
	.dw #0x3568
	.db #0x06	; 6
	.dw #0x002f
	.dw #0x0020
	.dw #0xffda
	.dw #0xffdf
	.dw #0x3b48
	.db #0x06	; 6
	.dw #0x001f
	.dw #0x001d
	.dw #0xffe6
	.dw #0xffe5
	.dw #0x3ecc
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe4
	.dw #0x4310
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe4
	.dw #0x4754
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe4
	.dw #0x4b98
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe4
	.dw #0x4fdc
	.db #0x06	; 6
	.dw #0x0028
	.dw #0x0015
	.dw #0xffe4
	.dw #0xffe7
	.dw #0x5324
	.db #0x06	; 6
	.dw #0x0028
	.dw #0x0013
	.dw #0xffe4
	.dw #0xffeb
	.dw #0x561c
	.db #0x06	; 6
	.dw #0x001f
	.dw #0x001f
	.dw #0xffe6
	.dw #0xffe3
	.dw #0x59e0
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe6
	.dw #0xffe3
	.dw #0x5e4c
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe6
	.dw #0xffe3
	.dw #0x62b8
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe6
	.dw #0xffe3
	.dw #0x6724
	.db #0x06	; 6
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe6
	.dw #0xffe3
	.dw #0x6b90
	.db #0x06	; 6
	.dw #0x0028
	.dw #0x0019
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x6f78
	.db #0x06	; 6
	.dw #0x0028
	.dw #0x001b
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x73b0
	.db #0x06	; 6
	.dw #0x0025
	.dw #0x0015
	.dw #0xffea
	.dw #0xffed
	.dw #0x76bc
	.db #0x06	; 6
	.dw #0x0020
	.dw #0x0011
	.dw #0xffea
	.dw #0xfff1
	.dw #0x78dc
	.db #0x06	; 6
	.dw #0x0021
	.dw #0x0011
	.dw #0xffe9
	.dw #0xfff1
	.dw #0x7b10
	.db #0x06	; 6
	.dw #0x0022
	.dw #0x0011
	.dw #0xffe8
	.dw #0xfff1
	.dw #0x7d54
	.db #0x06	; 6
	.dw #0x0020
	.dw #0x0010
	.dw #0xffea
	.dw #0xfff1
	.dw #0x7f54
	.db #0x06	; 6
	.dw #0x001d
	.dw #0x0010
	.dw #0xffed
	.dw #0xfff1
	.dw #0x8124
	.db #0x06	; 6
	.dw #0x001b
	.dw #0x0010
	.dw #0xffef
	.dw #0xfff1
	.dw #0x82d4
	.db #0x06	; 6
	.dw #0x001f
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe6
	.dw #0x8638
	.db #0x06	; 6
	.dw #0x0023
	.dw #0x0019
	.dw #0xffe9
	.dw #0xffe6
	.dw #0x89a4
	.db #0x06	; 6
	.dw #0x0029
	.dw #0x0018
	.dw #0xffe3
	.dw #0xffe5
	.dw #0x8d7c
	.db #0x06	; 6
	.dw #0x0029
	.dw #0x0018
	.dw #0xffe3
	.dw #0xffe5
	.dw #0x9154
	.db #0x06	; 6
	.dw #0x0021
	.dw #0x0019
	.dw #0xffe9
	.dw #0xffe6
	.dw #0x9490
	.db #0x06	; 6
	.dw #0x0021
	.dw #0x0019
	.dw #0xffe9
	.dw #0xffe6
	.dw #0x97cc
	.db #0x06	; 6
	.dw #0x0021
	.dw #0x0019
	.dw #0xffe9
	.dw #0xffe6
	.dw #0x9b08
	.db #0x06	; 6
	.dw #0x0022
	.dw #0x001e
	.dw #0xffe6
	.dw #0xffe4
	.dw #0x9f04
	.db #0x06	; 6
	.dw #0x002d
	.dw #0x0026
	.dw #0xffdf
	.dw #0xffd9
	.dw #0xa5b4
	.db #0x06	; 6
	.dw #0x002d
	.dw #0x0026
	.dw #0xffdd
	.dw #0xffdb
	.dw #0xac64
	.db #0x06	; 6
	.dw #0x0034
	.dw #0x0023
	.dw #0xffd9
	.dw #0xffdc
	.dw #0xb380
	.db #0x06	; 6
	.dw #0x0030
	.dw #0x0024
	.dw #0xffe0
	.dw #0xffdd
	.dw #0xba40
	.db #0x06	; 6
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdc
	.dw #0xffdc
	.dw #0xc1c4
	.db #0x06	; 6
	.dw #0x0034
	.dw #0x0023
	.dw #0xffdb
	.dw #0xffdc
	.dw #0xc8e0
	.db #0x06	; 6
	.dw #0x0020
	.dw #0x001b
	.dw #0xffe6
	.dw #0xffe7
	.dw #0xcc40
	.db #0x06	; 6
	.dw #0x001f
	.dw #0x001c
	.dw #0xffef
	.dw #0xffe2
	.dw #0xcfa4
	.db #0x06	; 6
	.dw #0x001f
	.dw #0x001c
	.dw #0xffef
	.dw #0xffe2
	.dw #0xd308
	.db #0x06	; 6
	.dw #0x0021
	.dw #0x001c
	.dw #0xffed
	.dw #0xffe2
	.dw #0xd6a4
	.db #0x06	; 6
	.dw #0x002a
	.dw #0x001d
	.dw #0xffe4
	.dw #0xffe1
	.dw #0xdb68
	.db #0x06	; 6
	.dw #0x002a
	.dw #0x001d
	.dw #0xffe4
	.dw #0xffe1
	.dw #0xe02c
	.db #0x06	; 6
	.dw #0x002a
	.dw #0x001d
	.dw #0xffe4
	.dw #0xffe1
	.dw #0xe4f0
	.db #0x06	; 6
	.dw #0x002e
	.dw #0x001e
	.dw #0xffdf
	.dw #0xffe4
	.dw #0xea54
	.db #0x06	; 6
	.dw #0x002e
	.dw #0x0019
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xeed4
	.db #0x06	; 6
	.dw #0x002e
	.dw #0x0019
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xf354
	.db #0x06	; 6
	.dw #0x002e
	.dw #0x0019
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xf7d4
	.db #0x06	; 6
	.dw #0x002d
	.dw #0x0019
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xfc3c
	.db #0x06	; 6
	.dw #0x002e
	.dw #0x0016
	.dw #0xffe0
	.dw #0xffe4
	.dw #0x0030
	.db #0x07	; 7
	.dw #0x002c
	.dw #0x0016
	.dw #0xffe2
	.dw #0xffe4
	.dw #0x03f8
	.db #0x07	; 7
	.dw #0x0025
	.dw #0x001d
	.dw #0xffe3
	.dw #0xffe5
	.dw #0x082c
	.db #0x07	; 7
	.dw #0x0025
	.dw #0x001c
	.dw #0xffe3
	.dw #0xffe5
	.dw #0x0c38
	.db #0x07	; 7
	.dw #0x0025
	.dw #0x001c
	.dw #0xffe3
	.dw #0xffe5
	.dw #0x1044
	.db #0x07	; 7
	.dw #0x0025
	.dw #0x001c
	.dw #0xffe3
	.dw #0xffe5
	.dw #0x1450
	.db #0x07	; 7
	.dw #0x0024
	.dw #0x001b
	.dw #0xffe4
	.dw #0xffe5
	.dw #0x181c
	.db #0x07	; 7
	.dw #0x0026
	.dw #0x001b
	.dw #0xffe2
	.dw #0xffe5
	.dw #0x1c20
	.db #0x07	; 7
	.dw #0x0026
	.dw #0x001b
	.dw #0xffe2
	.dw #0xffe5
	.dw #0x2024
	.db #0x07	; 7
	.dw #0x0025
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0x24c4
	.db #0x07	; 7
	.dw #0x002c
	.dw #0x001e
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x29ec
	.db #0x07	; 7
	.dw #0x002a
	.dw #0x001e
	.dw #0xffe3
	.dw #0xffe3
	.dw #0x2ed8
	.db #0x07	; 7
	.dw #0x002c
	.dw #0x001e
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x3400
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0x38f8
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x001d
	.dw #0xffe3
	.dw #0xffe1
	.dw #0x3da0
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x0020
	.dw #0xffe3
	.dw #0xffdf
	.dw #0x4280
	.db #0x07	; 7
	.dw #0x002c
	.dw #0x001f
	.dw #0xffdd
	.dw #0xffe3
	.dw #0x47d4
	.db #0x07	; 7
	.dw #0x0032
	.dw #0x0018
	.dw #0xffdd
	.dw #0xffe4
	.dw #0x4c84
	.db #0x07	; 7
	.dw #0x0032
	.dw #0x0018
	.dw #0xffdd
	.dw #0xffe4
	.dw #0x5134
	.db #0x07	; 7
	.dw #0x0032
	.dw #0x0015
	.dw #0xffdd
	.dw #0xffe3
	.dw #0x5550
	.db #0x07	; 7
	.dw #0x0032
	.dw #0x0018
	.dw #0xffdd
	.dw #0xffe4
	.dw #0x5a00
	.db #0x07	; 7
	.dw #0x0034
	.dw #0x0019
	.dw #0xffdb
	.dw #0xffe3
	.dw #0x5f14
	.db #0x07	; 7
	.dw #0x0035
	.dw #0x001e
	.dw #0xffda
	.dw #0xffe2
	.dw #0x654c
	.db #0x07	; 7
	.dw #0x001f
	.dw #0x0018
	.dw #0xffe6
	.dw #0xffea
	.dw #0x6834
	.db #0x07	; 7
	.dw #0x0023
	.dw #0x001b
	.dw #0xffe9
	.dw #0xffe4
	.dw #0x6be8
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x0019
	.dw #0xffe3
	.dw #0xffe4
	.dw #0x6fec
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x0019
	.dw #0xffe3
	.dw #0xffe4
	.dw #0x73f0
	.db #0x07	; 7
	.dw #0x0021
	.dw #0x001b
	.dw #0xffe9
	.dw #0xffe4
	.dw #0x776c
	.db #0x07	; 7
	.dw #0x0021
	.dw #0x001b
	.dw #0xffe9
	.dw #0xffe4
	.dw #0x7ae8
	.db #0x07	; 7
	.dw #0x0021
	.dw #0x001b
	.dw #0xffe9
	.dw #0xffe4
	.dw #0x7e64
	.db #0x07	; 7
	.dw #0x0030
	.dw #0x0023
	.dw #0xffe0
	.dw #0xffdf
	.dw #0x84f4
	.db #0x07	; 7
	.dw #0x002d
	.dw #0x0018
	.dw #0xffe3
	.dw #0xffe6
	.dw #0x892c
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x0018
	.dw #0xffe7
	.dw #0xffe6
	.dw #0x8d04
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x0017
	.dw #0xffe9
	.dw #0xffe6
	.dw #0x9088
	.db #0x07	; 7
	.dw #0x002e
	.dw #0x0017
	.dw #0xffe2
	.dw #0xffe6
	.dw #0x94ac
	.db #0x07	; 7
	.dw #0x0030
	.dw #0x0017
	.dw #0xffe0
	.dw #0xffe6
	.dw #0x98fc
	.db #0x07	; 7
	.dw #0x0030
	.dw #0x0015
	.dw #0xffe0
	.dw #0xffe7
	.dw #0x9cec
	.db #0x07	; 7
	.dw #0x0025
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xa18c
	.db #0x07	; 7
	.dw #0x002c
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe1
	.dw #0xa70c
	.db #0x07	; 7
	.dw #0x002a
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0xac24
	.db #0x07	; 7
	.dw #0x002c
	.dw #0x001f
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xb178
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x0020
	.dw #0xffe3
	.dw #0xffe1
	.dw #0xb698
	.db #0x07	; 7
	.dw #0x0029
	.dw #0x001d
	.dw #0xffe3
	.dw #0xffe1
	.dw #0xbb40
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x0020
	.dw #0xffe3
	.dw #0xffdf
	.dw #0xc020
	.db #0x07	; 7
	.dw #0x0020
	.dw #0x0014
	.dw #0xffea
	.dw #0xffee
	.dw #0xc2a0
	.db #0x07	; 7
	.dw #0x0028
	.dw #0x0015
	.dw #0xffe8
	.dw #0xffea
	.dw #0xc5e8
	.db #0x07	; 7
	.dw #0x0024
	.dw #0x0016
	.dw #0xffec
	.dw #0xffeb
	.dw #0xc900
	.db #0x07	; 7
	.dw #0x002a
	.dw #0x0013
	.dw #0xffe7
	.dw #0xffeb
	.dw #0xcc20
	.db #0x07	; 7
	.dw #0x002a
	.dw #0x0018
	.dw #0xffe7
	.dw #0xffe9
	.dw #0xd010
	.db #0x07	; 7
	.dw #0x0028
	.dw #0x0018
	.dw #0xffe7
	.dw #0xffe9
	.dw #0xd3d0
	.db #0x07	; 7
	.dw #0x0026
	.dw #0x0017
	.dw #0xffe8
	.dw #0xffe8
	.dw #0xd73c
	.db #0x07	; 7
	.dw #0x0024
	.dw #0x0020
	.dw #0xffe4
	.dw #0xffe2
	.dw #0xdbbc
	.db #0x07	; 7
	.dw #0x0028
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0xe094
	.db #0x07	; 7
	.dw #0x0024
	.dw #0x001f
	.dw #0xffe6
	.dw #0xffe2
	.dw #0xe4f0
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0xe9ac
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0xee68
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0xf324
	.db #0x07	; 7
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0xf7e0
	.db #0x07	; 7
	.dw #0x0026
	.dw #0x0022
	.dw #0xffe0
	.dw #0xffe0
	.dw #0xfcec
	.db #0x07	; 7
	.dw #0x0023
	.dw #0x0016
	.dw #0xffe3
	.dw #0xffe1
	.dw #0xfff0
	.db #0x07	; 7
	.dw #0x0026
	.dw #0x0017
	.dw #0xffe0
	.dw #0xffe0
	.dw #0x035c
	.db #0x08	; 8
	.dw #0x0027
	.dw #0x0016
	.dw #0xffdf
	.dw #0xffe1
	.dw #0x06b8
	.db #0x08	; 8
	.dw #0x0023
	.dw #0x0015
	.dw #0xffe3
	.dw #0xffe1
	.dw #0x0998
	.db #0x08	; 8
	.dw #0x0022
	.dw #0x0019
	.dw #0xffe3
	.dw #0xffe1
	.dw #0x0cec
	.db #0x08	; 8
	.dw #0x0022
	.dw #0x001a
	.dw #0xffe3
	.dw #0xffe1
	.dw #0x1060
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x0020
	.dw #0xffe4
	.dw #0xffe2
	.dw #0x14e0
	.db #0x08	; 8
	.dw #0x0028
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0x19b8
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x001f
	.dw #0xffe6
	.dw #0xffe2
	.dw #0x1e14
	.db #0x08	; 8
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0x22d0
	.db #0x08	; 8
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0x278c
	.db #0x08	; 8
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0x2c48
	.db #0x08	; 8
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0x3104
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe3
	.dw #0x3560
	.db #0x08	; 8
	.dw #0x0029
	.dw #0x001a
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x398c
	.db #0x08	; 8
	.dw #0x001d
	.dw #0x001c
	.dw #0xffed
	.dw #0xffe2
	.dw #0x3cb8
	.db #0x08	; 8
	.dw #0x001d
	.dw #0x001c
	.dw #0xffed
	.dw #0xffe2
	.dw #0x3fe4
	.db #0x08	; 8
	.dw #0x002a
	.dw #0x001a
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x4428
	.db #0x08	; 8
	.dw #0x002b
	.dw #0x0018
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x4830
	.db #0x08	; 8
	.dw #0x002d
	.dw #0x0018
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x4c68
	.db #0x08	; 8
	.dw #0x002d
	.dw #0x0021
	.dw #0xffdf
	.dw #0xffe1
	.dw #0x5238
	.db #0x08	; 8
	.dw #0x0031
	.dw #0x0021
	.dw #0xffde
	.dw #0xffe0
	.dw #0x588c
	.db #0x08	; 8
	.dw #0x0031
	.dw #0x0022
	.dw #0xffde
	.dw #0xffdf
	.dw #0x5f10
	.db #0x08	; 8
	.dw #0x0031
	.dw #0x0022
	.dw #0xffde
	.dw #0xffdf
	.dw #0x6594
	.db #0x08	; 8
	.dw #0x002e
	.dw #0x0021
	.dw #0xffe0
	.dw #0xffe0
	.dw #0x6b84
	.db #0x08	; 8
	.dw #0x0031
	.dw #0x0021
	.dw #0xffde
	.dw #0xffe0
	.dw #0x71d8
	.db #0x08	; 8
	.dw #0x002d
	.dw #0x0022
	.dw #0xffe0
	.dw #0xffe0
	.dw #0x77d4
	.db #0x08	; 8
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0x7c94
	.db #0x08	; 8
	.dw #0x0018
	.dw #0x001a
	.dw #0xfff2
	.dw #0xffe7
	.dw #0x7f04
	.db #0x08	; 8
	.dw #0x001d
	.dw #0x001a
	.dw #0xffed
	.dw #0xffe7
	.dw #0x81f8
	.db #0x08	; 8
	.dw #0x001e
	.dw #0x001a
	.dw #0xffec
	.dw #0xffe7
	.dw #0x8504
	.db #0x08	; 8
	.dw #0x0018
	.dw #0x0018
	.dw #0xfff4
	.dw #0xffe9
	.dw #0x8744
	.db #0x08	; 8
	.dw #0x0015
	.dw #0x0018
	.dw #0xfff7
	.dw #0xffe9
	.dw #0x893c
	.db #0x08	; 8
	.dw #0x0021
	.dw #0x0018
	.dw #0xffed
	.dw #0xffe9
	.dw #0x8c54
	.db #0x08	; 8
	.dw #0x0025
	.dw #0x001f
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x90d0
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x0018
	.dw #0xffe4
	.dw #0xffe4
	.dw #0x9430
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x0019
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x97b4
	.db #0x08	; 8
	.dw #0x0028
	.dw #0x001e
	.dw #0xffe0
	.dw #0xffe3
	.dw #0x9c64
	.db #0x08	; 8
	.dw #0x0028
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xa0ec
	.db #0x08	; 8
	.dw #0x0026
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xa53c
	.db #0x08	; 8
	.dw #0x0025
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xa970
	.db #0x08	; 8
	.dw #0x0026
	.dw #0x0022
	.dw #0xffe0
	.dw #0xffe0
	.dw #0xae7c
	.db #0x08	; 8
	.dw #0x0023
	.dw #0x0017
	.dw #0xffe3
	.dw #0xffe0
	.dw #0xb1a4
	.db #0x08	; 8
	.dw #0x0026
	.dw #0x0017
	.dw #0xffe0
	.dw #0xffe0
	.dw #0xb510
	.db #0x08	; 8
	.dw #0x0027
	.dw #0x0017
	.dw #0xffdf
	.dw #0xffe0
	.dw #0xb894
	.db #0x08	; 8
	.dw #0x0023
	.dw #0x0016
	.dw #0xffe3
	.dw #0xffe0
	.dw #0xbb98
	.db #0x08	; 8
	.dw #0x0022
	.dw #0x001a
	.dw #0xffe3
	.dw #0xffe0
	.dw #0xbf0c
	.db #0x08	; 8
	.dw #0x0022
	.dw #0x001b
	.dw #0xffe3
	.dw #0xffe0
	.dw #0xc2a4
	.db #0x08	; 8
	.dw #0x0026
	.dw #0x0021
	.dw #0xffe1
	.dw #0xffe1
	.dw #0xc78c
	.db #0x08	; 8
	.dw #0x0018
	.dw #0x001a
	.dw #0xfff2
	.dw #0xffe7
	.dw #0xc9fc
	.db #0x08	; 8
	.dw #0x001d
	.dw #0x001a
	.dw #0xffed
	.dw #0xffe7
	.dw #0xccf0
	.db #0x08	; 8
	.dw #0x001e
	.dw #0x001a
	.dw #0xffec
	.dw #0xffe7
	.dw #0xcffc
	.db #0x08	; 8
	.dw #0x0018
	.dw #0x0018
	.dw #0xfff4
	.dw #0xffe9
	.dw #0xd23c
	.db #0x08	; 8
	.dw #0x0015
	.dw #0x0018
	.dw #0xfff7
	.dw #0xffe9
	.dw #0xd434
	.db #0x08	; 8
	.dw #0x0021
	.dw #0x0018
	.dw #0xffed
	.dw #0xffe9
	.dw #0xd74c
	.db #0x08	; 8
	.dw #0x0016
	.dw #0x0022
	.dw #0xfff1
	.dw #0xffe0
	.dw #0xda38
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xda3c
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xda40
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xda44
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xda48
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xda4c
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xda50
	.db #0x08	; 8
	.dw #0x0025
	.dw #0x001f
	.dw #0xffe1
	.dw #0xffe3
	.dw #0xdecc
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x0018
	.dw #0xffe4
	.dw #0xffe4
	.dw #0xe22c
	.db #0x08	; 8
	.dw #0x0024
	.dw #0x0019
	.dw #0xffe4
	.dw #0xffe3
	.dw #0xe5b0
	.db #0x08	; 8
	.dw #0x0028
	.dw #0x001e
	.dw #0xffe0
	.dw #0xffe3
	.dw #0xea60
	.db #0x08	; 8
	.dw #0x0028
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xeee8
	.db #0x08	; 8
	.dw #0x0026
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xf338
	.db #0x08	; 8
	.dw #0x0025
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xf76c
	.db #0x08	; 8
	.dw #0x0016
	.dw #0x0022
	.dw #0xfff2
	.dw #0xffe0
	.dw #0xfa58
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xfa5c
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xfa60
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xfa64
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xfa68
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xfa6c
	.db #0x08	; 8
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0xfa70
	.db #0x08	; 8
	.dw #0x001a
	.dw #0x000e
	.dw #0xffe0
	.dw #0xfff3
	.dw #0xfbdc
	.db #0x08	; 8
	.dw #0x002b
	.dw #0x0023
	.dw #0xffdc
	.dw #0xffdf
	.dw #0x01c0
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0023
	.dw #0xffdc
	.dw #0xffdf
	.dw #0x07c4
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0024
	.dw #0xffdc
	.dw #0xffde
	.dw #0x0df4
	.db #0x09	; 9
	.dw #0x002a
	.dw #0x0024
	.dw #0xffe0
	.dw #0xffdf
	.dw #0x13dc
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0024
	.dw #0xffdc
	.dw #0xffde
	.dw #0x1a0c
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0024
	.dw #0xffdc
	.dw #0xffdf
	.dw #0x203c
	.db #0x09	; 9
	.dw #0x000e
	.dw #0x0020
	.dw #0xfff9
	.dw #0xffe1
	.dw #0x21fc
	.db #0x09	; 9
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0x2384
	.db #0x09	; 9
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0x250c
	.db #0x09	; 9
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0x2694
	.db #0x09	; 9
	.dw #0x000e
	.dw #0x001d
	.dw #0xfff9
	.dw #0xffe0
	.dw #0x282c
	.db #0x09	; 9
	.dw #0x000d
	.dw #0x001d
	.dw #0xfffa
	.dw #0xffe0
	.dw #0x29a8
	.db #0x09	; 9
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0x2b30
	.db #0x09	; 9
	.dw #0x0016
	.dw #0x0022
	.dw #0xfff1
	.dw #0xffe0
	.dw #0x2e1c
	.db #0x09	; 9
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x2e20
	.db #0x09	; 9
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x2e24
	.db #0x09	; 9
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x2e28
	.db #0x09	; 9
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x2e2c
	.db #0x09	; 9
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x2e30
	.db #0x09	; 9
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x2e34
	.db #0x09	; 9
	.dw #0x0025
	.dw #0x001d
	.dw #0xffe5
	.dw #0xffe5
	.dw #0x3268
	.db #0x09	; 9
	.dw #0x0029
	.dw #0x001e
	.dw #0xffe3
	.dw #0xffe3
	.dw #0x3738
	.db #0x09	; 9
	.dw #0x0029
	.dw #0x001e
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x3c08
	.db #0x09	; 9
	.dw #0x0028
	.dw #0x001e
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x40b8
	.db #0x09	; 9
	.dw #0x0029
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe2
	.dw #0x45b0
	.db #0x09	; 9
	.dw #0x002a
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe1
	.dw #0x4af0
	.db #0x09	; 9
	.dw #0x002a
	.dw #0x0020
	.dw #0xffe2
	.dw #0xffe1
	.dw #0x5030
	.db #0x09	; 9
	.dw #0x002f
	.dw #0x0022
	.dw #0xffdf
	.dw #0xffe0
	.dw #0x5670
	.db #0x09	; 9
	.dw #0x002e
	.dw #0x0022
	.dw #0xffe0
	.dw #0xffdf
	.dw #0x5c8c
	.db #0x09	; 9
	.dw #0x002f
	.dw #0x0022
	.dw #0xffdf
	.dw #0xffdf
	.dw #0x62cc
	.db #0x09	; 9
	.dw #0x002f
	.dw #0x0022
	.dw #0xffdf
	.dw #0xffdf
	.dw #0x690c
	.db #0x09	; 9
	.dw #0x0030
	.dw #0x0022
	.dw #0xffde
	.dw #0xffdf
	.dw #0x6f6c
	.db #0x09	; 9
	.dw #0x0031
	.dw #0x0022
	.dw #0xffdd
	.dw #0xffdf
	.dw #0x75f0
	.db #0x09	; 9
	.dw #0x002f
	.dw #0x0022
	.dw #0xffdf
	.dw #0xffdf
	.dw #0x7c30
	.db #0x09	; 9
	.dw #0x0027
	.dw #0x0022
	.dw #0xffdf
	.dw #0xffe0
	.dw #0x8160
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x86e0
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x8c60
	.db #0x09	; 9
	.dw #0x002d
	.dw #0x0020
	.dw #0xffdd
	.dw #0xffdf
	.dw #0x9200
	.db #0x09	; 9
	.dw #0x002d
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x97a0
	.db #0x09	; 9
	.dw #0x002d
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x9d40
	.db #0x09	; 9
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0xa2c0
	.db #0x09	; 9
	.dw #0x0037
	.dw #0x0022
	.dw #0xffdc
	.dw #0xffe0
	.dw #0xaa10
	.db #0x09	; 9
	.dw #0x002d
	.dw #0x001c
	.dw #0xffe2
	.dw #0xffe5
	.dw #0xaefc
	.db #0x09	; 9
	.dw #0x002e
	.dw #0x001d
	.dw #0xffe1
	.dw #0xffe4
	.dw #0xb434
	.db #0x09	; 9
	.dw #0x0030
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0xb9a4
	.db #0x09	; 9
	.dw #0x0029
	.dw #0x001a
	.dw #0xffe6
	.dw #0xffe6
	.dw #0xbdd0
	.db #0x09	; 9
	.dw #0x002a
	.dw #0x0019
	.dw #0xffe6
	.dw #0xffe7
	.dw #0xc1ec
	.db #0x09	; 9
	.dw #0x002a
	.dw #0x0018
	.dw #0xffe6
	.dw #0xffe7
	.dw #0xc5dc
	.db #0x09	; 9
	.dw #0x0021
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0xc9dc
	.db #0x09	; 9
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xce9c
	.db #0x09	; 9
	.dw #0x0025
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0xd318
	.db #0x09	; 9
	.dw #0x0027
	.dw #0x0020
	.dw #0xffe0
	.dw #0xffe2
	.dw #0xd7f8
	.db #0x09	; 9
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xdcb8
	.db #0x09	; 9
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xe178
	.db #0x09	; 9
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xe638
	.db #0x09	; 9
	.dw #0x002a
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xeb78
	.db #0x09	; 9
	.dw #0x0024
	.dw #0x0014
	.dw #0xffe0
	.dw #0xffe3
	.dw #0xee48
	.db #0x09	; 9
	.dw #0x0025
	.dw #0x0015
	.dw #0xffdf
	.dw #0xffe2
	.dw #0xf154
	.db #0x09	; 9
	.dw #0x0024
	.dw #0x0015
	.dw #0xffe0
	.dw #0xffe2
	.dw #0xf448
	.db #0x09	; 9
	.dw #0x001d
	.dw #0x0014
	.dw #0xffe7
	.dw #0xffe3
	.dw #0xf68c
	.db #0x09	; 9
	.dw #0x001d
	.dw #0x0014
	.dw #0xffe7
	.dw #0xffe3
	.dw #0xf8d0
	.db #0x09	; 9
	.dw #0x001d
	.dw #0x0014
	.dw #0xffe7
	.dw #0xffe3
	.dw #0xfb14
	.db #0x09	; 9
	.dw #0x000f
	.dw #0x0009
	.dw #0xffe8
	.dw #0xfff7
	.dw #0xfb9c
	.db #0x09	; 9
	.dw #0x0027
	.dw #0x001e
	.dw #0xffe4
	.dw #0xffe4
	.dw #0x0030
	.db #0x0a	; 10
	.dw #0x0029
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe3
	.dw #0x0528
	.db #0x0a	; 10
	.dw #0x0029
	.dw #0x001f
	.dw #0xffe4
	.dw #0xffe3
	.dw #0x0a20
	.db #0x0a	; 10
	.dw #0x0029
	.dw #0x0020
	.dw #0xffe2
	.dw #0xffe5
	.dw #0x0f40
	.db #0x0a	; 10
	.dw #0x002a
	.dw #0x0021
	.dw #0xffe2
	.dw #0xffe5
	.dw #0x14ac
	.db #0x0a	; 10
	.dw #0x0029
	.dw #0x0021
	.dw #0xffe2
	.dw #0xffe4
	.dw #0x19f8
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0021
	.dw #0xffe1
	.dw #0xffe1
	.dw #0x1ee0
	.db #0x0a	; 10
	.dw #0x0017
	.dw #0x001d
	.dw #0xfff2
	.dw #0xffe2
	.dw #0x217c
	.db #0x0a	; 10
	.dw #0x0019
	.dw #0x001d
	.dw #0xfff0
	.dw #0xffe2
	.dw #0x2454
	.db #0x0a	; 10
	.dw #0x001a
	.dw #0x001d
	.dw #0xffef
	.dw #0xffe2
	.dw #0x2748
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x001e
	.dw #0xffe2
	.dw #0xffe1
	.dw #0x2bdc
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x001e
	.dw #0xffe2
	.dw #0xffe1
	.dw #0x3070
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x001e
	.dw #0xffe2
	.dw #0xffe1
	.dw #0x3504
	.db #0x0a	; 10
	.dw #0x0024
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe3
	.dw #0x3960
	.db #0x0a	; 10
	.dw #0x0029
	.dw #0x001a
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x3d8c
	.db #0x0a	; 10
	.dw #0x001d
	.dw #0x001c
	.dw #0xffed
	.dw #0xffe2
	.dw #0x40b8
	.db #0x0a	; 10
	.dw #0x001d
	.dw #0x001c
	.dw #0xffed
	.dw #0xffe2
	.dw #0x43e4
	.db #0x0a	; 10
	.dw #0x002a
	.dw #0x001a
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x4828
	.db #0x0a	; 10
	.dw #0x002b
	.dw #0x0018
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x4c30
	.db #0x0a	; 10
	.dw #0x002d
	.dw #0x0018
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x5068
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0022
	.dw #0xffdf
	.dw #0xffe0
	.dw #0x5574
	.db #0x0a	; 10
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x5af4
	.db #0x0a	; 10
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x6074
	.db #0x0a	; 10
	.dw #0x002d
	.dw #0x0020
	.dw #0xffdd
	.dw #0xffdf
	.dw #0x6614
	.db #0x0a	; 10
	.dw #0x002d
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x6bb4
	.db #0x0a	; 10
	.dw #0x002d
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x7154
	.db #0x0a	; 10
	.dw #0x002c
	.dw #0x0020
	.dw #0xffde
	.dw #0xffdf
	.dw #0x76d4
	.db #0x0a	; 10
	.dw #0x0037
	.dw #0x0022
	.dw #0xffdc
	.dw #0xffe0
	.dw #0x7e24
	.db #0x0a	; 10
	.dw #0x002d
	.dw #0x001e
	.dw #0xffe2
	.dw #0xffe3
	.dw #0x836c
	.db #0x0a	; 10
	.dw #0x002e
	.dw #0x001e
	.dw #0xffe1
	.dw #0xffe3
	.dw #0x88d0
	.db #0x0a	; 10
	.dw #0x0030
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe4
	.dw #0x8e40
	.db #0x0a	; 10
	.dw #0x0029
	.dw #0x001c
	.dw #0xffe6
	.dw #0xffe4
	.dw #0x92bc
	.db #0x0a	; 10
	.dw #0x002a
	.dw #0x001b
	.dw #0xffe6
	.dw #0xffe5
	.dw #0x972c
	.db #0x0a	; 10
	.dw #0x002a
	.dw #0x0019
	.dw #0xffe6
	.dw #0xffe6
	.dw #0x9b48
	.db #0x0a	; 10
	.dw #0x0021
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0x9f48
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xa408
	.db #0x0a	; 10
	.dw #0x0025
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffe2
	.dw #0xa884
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x0020
	.dw #0xffe0
	.dw #0xffe2
	.dw #0xad64
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xb224
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xb6e4
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xbba4
	.db #0x0a	; 10
	.dw #0x000e
	.dw #0x0020
	.dw #0xfff9
	.dw #0xffe1
	.dw #0xbd64
	.db #0x0a	; 10
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0xbeec
	.db #0x0a	; 10
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0xc074
	.db #0x0a	; 10
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0xc1fc
	.db #0x0a	; 10
	.dw #0x000e
	.dw #0x001d
	.dw #0xfff9
	.dw #0xffe0
	.dw #0xc394
	.db #0x0a	; 10
	.dw #0x000d
	.dw #0x001d
	.dw #0xfffa
	.dw #0xffe0
	.dw #0xc510
	.db #0x0a	; 10
	.dw #0x000e
	.dw #0x001c
	.dw #0xfff9
	.dw #0xffe1
	.dw #0xc698
	.db #0x0a	; 10
	.dw #0x002a
	.dw #0x0020
	.dw #0xffe1
	.dw #0xffe2
	.dw #0xcbd8
	.db #0x0a	; 10
	.dw #0x0024
	.dw #0x0014
	.dw #0xffe0
	.dw #0xffe3
	.dw #0xcea8
	.db #0x0a	; 10
	.dw #0x0025
	.dw #0x0015
	.dw #0xffdf
	.dw #0xffe2
	.dw #0xd1b4
	.db #0x0a	; 10
	.dw #0x0024
	.dw #0x0015
	.dw #0xffe0
	.dw #0xffe2
	.dw #0xd4a8
	.db #0x0a	; 10
	.dw #0x001d
	.dw #0x0014
	.dw #0xffe7
	.dw #0xffe3
	.dw #0xd6ec
	.db #0x0a	; 10
	.dw #0x001d
	.dw #0x0014
	.dw #0xffe7
	.dw #0xffe3
	.dw #0xd930
	.db #0x0a	; 10
	.dw #0x001d
	.dw #0x0014
	.dw #0xffe7
	.dw #0xffe3
	.dw #0xdb74
	.db #0x0a	; 10
	.dw #0x0026
	.dw #0x0023
	.dw #0xffe1
	.dw #0xffdf
	.dw #0xe0a8
	.db #0x0a	; 10
	.dw #0x0017
	.dw #0x001f
	.dw #0xfff2
	.dw #0xffe0
	.dw #0xe374
	.db #0x0a	; 10
	.dw #0x0019
	.dw #0x001f
	.dw #0xfff0
	.dw #0xffe0
	.dw #0xe67c
	.db #0x0a	; 10
	.dw #0x001a
	.dw #0x001f
	.dw #0xffef
	.dw #0xffe0
	.dw #0xe9a4
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe0
	.dw #0xee60
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe0
	.dw #0xf31c
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x001f
	.dw #0xffe2
	.dw #0xffe0
	.dw #0xf7d8
	.db #0x0a	; 10
	.dw #0x0027
	.dw #0x0016
	.dw #0xffe4
	.dw #0xffec
	.dw #0xfb34
	.db #0x0a	; 10
	.dw #0x002c
	.dw #0x0022
	.dw #0xffe3
	.dw #0xffde
	.dw #0x010c
	.db #0x0b	; 11
	.dw #0x002c
	.dw #0x0022
	.dw #0xffe3
	.dw #0xffde
	.dw #0x06e4
	.db #0x0b	; 11
	.dw #0x002c
	.dw #0x0022
	.dw #0xffe3
	.dw #0xffde
	.dw #0x0cbc
	.db #0x0b	; 11
	.dw #0x0030
	.dw #0x001f
	.dw #0xffe3
	.dw #0xffdf
	.dw #0x128c
	.db #0x0b	; 11
	.dw #0x0033
	.dw #0x001e
	.dw #0xffe3
	.dw #0xffe2
	.dw #0x1888
	.db #0x0b	; 11
	.dw #0x002f
	.dw #0x001b
	.dw #0xffe8
	.dw #0xffe4
	.dw #0x1d80
	.db #0x0b	; 11
	.dw #0x002f
	.dw #0x001e
	.dw #0xffdd
	.dw #0xffe4
	.dw #0x2304
	.db #0x0b	; 11
	.dw #0x0031
	.dw #0x0024
	.dw #0xffde
	.dw #0xffde
	.dw #0x29e8
	.db #0x0b	; 11
	.dw #0x0032
	.dw #0x0024
	.dw #0xffde
	.dw #0xffde
	.dw #0x30f0
	.db #0x0b	; 11
	.dw #0x0031
	.dw #0x0024
	.dw #0xffde
	.dw #0xffde
	.dw #0x37d4
	.db #0x0b	; 11
	.dw #0x0034
	.dw #0x0024
	.dw #0xffdc
	.dw #0xffde
	.dw #0x3f24
	.db #0x0b	; 11
	.dw #0x0037
	.dw #0x0025
	.dw #0xffda
	.dw #0xffdd
	.dw #0x4718
	.db #0x0b	; 11
	.dw #0x0039
	.dw #0x0025
	.dw #0xffdb
	.dw #0xffdd
	.dw #0x4f58
	.db #0x0b	; 11
	.dw #0x0030
	.dw #0x0021
	.dw #0xffdf
	.dw #0xffe1
	.dw #0x5588
	.db #0x0b	; 11
	.dw #0x0029
	.dw #0x001f
	.dw #0xffde
	.dw #0xffe1
	.dw #0x5a80
	.db #0x0b	; 11
	.dw #0x0028
	.dw #0x001f
	.dw #0xffde
	.dw #0xffe1
	.dw #0x5f58
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x001f
	.dw #0xffde
	.dw #0xffe1
	.dw #0x6414
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe2
	.dw #0x6880
	.db #0x0b	; 11
	.dw #0x0014
	.dw #0x001d
	.dw #0xfff4
	.dw #0xffe2
	.dw #0x6ac4
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe2
	.dw #0x6f30
	.db #0x0b	; 11
	.dw #0x0018
	.dw #0x0023
	.dw #0xfff2
	.dw #0xffdf
	.dw #0x7278
	.db #0x0b	; 11
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x727c
	.db #0x0b	; 11
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x7280
	.db #0x0b	; 11
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x7284
	.db #0x0b	; 11
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x7288
	.db #0x0b	; 11
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x728c
	.db #0x0b	; 11
	.dw #0x0001
	.dw #0x0001
	.dw #0x0000
	.dw #0x0000
	.dw #0x7290
	.db #0x0b	; 11
	.dw #0x0030
	.dw #0x0021
	.dw #0xffdf
	.dw #0xffe1
	.dw #0x78c0
	.db #0x0b	; 11
	.dw #0x0029
	.dw #0x001f
	.dw #0xffde
	.dw #0xffe1
	.dw #0x7db8
	.db #0x0b	; 11
	.dw #0x0028
	.dw #0x001f
	.dw #0xffde
	.dw #0xffe1
	.dw #0x8290
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x001f
	.dw #0xffde
	.dw #0xffe1
	.dw #0x874c
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe2
	.dw #0x8bb8
	.db #0x0b	; 11
	.dw #0x0014
	.dw #0x001d
	.dw #0xfff4
	.dw #0xffe2
	.dw #0x8dfc
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x001d
	.dw #0xffe0
	.dw #0xffe2
	.dw #0x9268
	.db #0x0b	; 11
	.dw #0x0027
	.dw #0x0020
	.dw #0xffdf
	.dw #0xffe2
	.dw #0x9748
	.db #0x0b	; 11
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe0
	.dw #0xffdf
	.dw #0x9c08
	.db #0x0b	; 11
	.dw #0x0028
	.dw #0x0023
	.dw #0xffde
	.dw #0xffde
	.dw #0xa180
	.db #0x0b	; 11
	.dw #0x0029
	.dw #0x0023
	.dw #0xffdd
	.dw #0xffde
	.dw #0xa71c
	.db #0x0b	; 11
	.dw #0x0026
	.dw #0x0020
	.dw #0xffe0
	.dw #0xffdf
	.dw #0xabdc
	.db #0x0b	; 11
	.dw #0x0029
	.dw #0x0023
	.dw #0xffde
	.dw #0xffde
	.dw #0xb178
	.db #0x0b	; 11
	.dw #0x002a
	.dw #0x0023
	.dw #0xffde
	.dw #0xffde
	.dw #0xb738
	.db #0x0b	; 11
	.dw #0x002d
	.dw #0x0027
	.dw #0xffdb
	.dw #0xffdb
	.dw #0xbe14
	.db #0x0b	; 11
	.dw #0x002a
	.dw #0x001d
	.dw #0xffde
	.dw #0xffdb
	.dw #0xc2d8
	.db #0x0b	; 11
	.dw #0x002e
	.dw #0x001d
	.dw #0xffda
	.dw #0xffdb
	.dw #0xc810
	.db #0x0b	; 11
	.dw #0x002e
	.dw #0x001d
	.dw #0xffda
	.dw #0xffdb
	.dw #0xcd48
	.db #0x0b	; 11
	.dw #0x002a
	.dw #0x001f
	.dw #0xffde
	.dw #0xffdb
	.dw #0xd260
	.db #0x0b	; 11
	.dw #0x002a
	.dw #0x001f
	.dw #0xffde
	.dw #0xffdb
	.dw #0xd778
	.db #0x0b	; 11
	.dw #0x002a
	.dw #0x001d
	.dw #0xffde
	.dw #0xffdb
	.dw #0xdc3c
	.db #0x0b	; 11
	.dw #0x0031
	.dw #0x0019
	.dw #0xffe0
	.dw #0xffe9
	.dw #0xe108
	.db #0x0b	; 11
	.dw #0x003c
	.dw #0x0024
	.dw #0xffd5
	.dw #0xffde
	.dw #0xe978
	.db #0x0b	; 11
	.dw #0x003b
	.dw #0x0023
	.dw #0xffd7
	.dw #0xffdf
	.dw #0xf18c
	.db #0x0b	; 11
	.dw #0x0036
	.dw #0x001f
	.dw #0xffdc
	.dw #0xffe2
	.dw #0xf818
	.db #0x0b	; 11
	.dw #0x0039
	.dw #0x0023
	.dw #0xffd8
	.dw #0xffdf
	.dw #0xffe4
	.db #0x0b	; 11
	.dw #0x0035
	.dw #0x0021
	.dw #0xffdc
	.dw #0xffe1
	.dw #0x06bc
	.db #0x0c	; 12
	.dw #0x0035
	.dw #0x0020
	.dw #0xffdc
	.dw #0xffe2
	.dw #0x0d5c
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0026
	.dw #0xffdb
	.dw #0xffdc
	.dw #0x1514
	.db #0x0c	; 12
	.dw #0x0032
	.dw #0x0025
	.dw #0xffde
	.dw #0xffdc
	.dw #0x1c50
	.db #0x0c	; 12
	.dw #0x0032
	.dw #0x0025
	.dw #0xffde
	.dw #0xffdc
	.dw #0x238c
	.db #0x0c	; 12
	.dw #0x0032
	.dw #0x0025
	.dw #0xffde
	.dw #0xffdc
	.dw #0x2ac8
	.db #0x0c	; 12
	.dw #0x0030
	.dw #0x0026
	.dw #0xffe0
	.dw #0xffdc
	.dw #0x31e8
	.db #0x0c	; 12
	.dw #0x0032
	.dw #0x0026
	.dw #0xffde
	.dw #0xffdc
	.dw #0x3954
	.db #0x0c	; 12
	.dw #0x0031
	.dw #0x0025
	.dw #0xffe0
	.dw #0xffdc
	.dw #0x406c
	.db #0x0c	; 12
	.dw #0x0035
	.dw #0x0025
	.dw #0xffdc
	.dw #0xffdd
	.dw #0x4818
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x4f9c
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x5720
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x5ea4
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x6628
	.db #0x0c	; 12
	.dw #0x0033
	.dw #0x0026
	.dw #0xffde
	.dw #0xffdb
	.dw #0x6dbc
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x7540
	.db #0x0c	; 12
	.dw #0x0035
	.dw #0x0025
	.dw #0xffdc
	.dw #0xffdd
	.dw #0x7cec
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x8470
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x8bf4
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x9378
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0x9afc
	.db #0x0c	; 12
	.dw #0x0033
	.dw #0x0026
	.dw #0xffde
	.dw #0xffdb
	.dw #0xa290
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0xaa14
	.db #0x0c	; 12
	.dw #0x002d
	.dw #0x0027
	.dw #0xffdb
	.dw #0xffdb
	.dw #0xb0f0
	.db #0x0c	; 12
	.dw #0x002a
	.dw #0x001d
	.dw #0xffde
	.dw #0xffdb
	.dw #0xb5b4
	.db #0x0c	; 12
	.dw #0x002e
	.dw #0x001d
	.dw #0xffda
	.dw #0xffdb
	.dw #0xbaec
	.db #0x0c	; 12
	.dw #0x002e
	.dw #0x001d
	.dw #0xffda
	.dw #0xffdb
	.dw #0xc024
	.db #0x0c	; 12
	.dw #0x002a
	.dw #0x001f
	.dw #0xffde
	.dw #0xffdb
	.dw #0xc53c
	.db #0x0c	; 12
	.dw #0x002a
	.dw #0x001f
	.dw #0xffde
	.dw #0xffdb
	.dw #0xca54
	.db #0x0c	; 12
	.dw #0x002a
	.dw #0x001d
	.dw #0xffde
	.dw #0xffdb
	.dw #0xcf18
	.db #0x0c	; 12
	.dw #0x0035
	.dw #0x0025
	.dw #0xffdc
	.dw #0xffdd
	.dw #0xd6c4
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0xde48
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0xe5cc
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0xed50
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
	.dw #0xf4d4
	.db #0x0c	; 12
	.dw #0x0033
	.dw #0x0026
	.dw #0xffde
	.dw #0xffdb
	.dw #0xfc68
	.db #0x0c	; 12
	.dw #0x0034
	.dw #0x0025
	.dw #0xffdd
	.dw #0xffdc
_hs_glyphs:
	.dw #0x0000
	.db #0x00	; 0
	.dw #0x0000
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x01	; 1
	.db #0x04	; 4
	.db #0x00	;  0
	.dw #0x03ec
	.db #0x0d	; 13
	.dw #0x0450
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0e	; 14
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x04b4
	.db #0x0d	; 13
	.dw #0x052c
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x0f	; 15
	.db #0x07	; 7
	.db #0x00	;  0
	.dw #0x05a4
	.db #0x0d	; 13
	.dw #0x064c
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x06f4
	.db #0x0d	; 13
	.dw #0x07a0
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x11	; 17
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x084c
	.db #0x0d	; 13
	.dw #0x092c
	.db #0x0d	; 13
	.db #0x10	; 16
	.db #0x0e	; 14
	.db #0x0f	; 15
	.db #0x00	;  0
	.dw #0x0a0c
	.db #0x0d	; 13
	.dw #0x0ab4
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x0b5c
	.db #0x0d	; 13
	.dw #0x0ba8
	.db #0x0d	; 13
	.db #0x05	; 5
	.db #0x0f	; 15
	.db #0x04	; 4
	.db #0x00	;  0
	.dw #0x0bf4
	.db #0x0d	; 13
	.dw #0x0c74
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x12	; 18
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x0cf4
	.db #0x0d	; 13
	.dw #0x0d74
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x12	; 18
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x0df4
	.db #0x0d	; 13
	.dw #0x0e8c
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x0f24
	.db #0x0d	; 13
	.dw #0x0fb4
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x1044
	.db #0x0d	; 13
	.dw #0x1074
	.db #0x0d	; 13
	.db #0x06	; 6
	.db #0x08	; 8
	.db #0x05	; 5
	.db #0x00	;  0
	.dw #0x10a4
	.db #0x0d	; 13
	.dw #0x10e4
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x09	; 9
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x1124
	.db #0x0d	; 13
	.dw #0x1148
	.db #0x0d	; 13
	.db #0x06	; 6
	.db #0x06	; 6
	.db #0x05	; 5
	.db #0x00	;  0
	.dw #0x116c
	.db #0x0d	; 13
	.dw #0x11f4
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x11	; 17
	.db #0x07	; 7
	.db #0x00	;  0
	.dw #0x127c
	.db #0x0d	; 13
	.dw #0x1308
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x1394
	.db #0x0d	; 13
	.dw #0x1420
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x14ac
	.db #0x0d	; 13
	.dw #0x1538
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x15c4
	.db #0x0d	; 13
	.dw #0x1650
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x16dc
	.db #0x0d	; 13
	.dw #0x1768
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x17f4
	.db #0x0d	; 13
	.dw #0x1880
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x190c
	.db #0x0d	; 13
	.dw #0x1998
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x1a24
	.db #0x0d	; 13
	.dw #0x1ab0
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x1b3c
	.db #0x0d	; 13
	.dw #0x1bc8
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x1c54
	.db #0x0d	; 13
	.dw #0x1ce0
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x1d6c
	.db #0x0d	; 13
	.dw #0x1dc0
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0c	; 12
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x1e14
	.db #0x0d	; 13
	.dw #0x1e78
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0e	; 14
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x1edc
	.db #0x0d	; 13
	.dw #0x1f6c
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x1ffc
	.db #0x0d	; 13
	.dw #0x2074
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0a	; 10
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x20ec
	.db #0x0d	; 13
	.dw #0x217c
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x220c
	.db #0x0d	; 13
	.dw #0x228c
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0e	; 14
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x230c
	.db #0x0d	; 13
	.dw #0x23fc
	.db #0x0d	; 13
	.db #0x0f	; 15
	.db #0x10	; 16
	.db #0x0e	; 14
	.db #0x00	;  0
	.dw #0x24ec
	.db #0x0d	; 13
	.dw #0x2594
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x263c
	.db #0x0d	; 13
	.dw #0x26c8
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x2754
	.db #0x0d	; 13
	.dw #0x27f0
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x288c
	.db #0x0d	; 13
	.dw #0x2934
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x29dc
	.db #0x0d	; 13
	.dw #0x2a68
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x2af4
	.db #0x0d	; 13
	.dw #0x2b80
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x2c0c
	.db #0x0d	; 13
	.dw #0x2ca8
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x2d44
	.db #0x0d	; 13
	.dw #0x2de0
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x2e7c
	.db #0x0d	; 13
	.dw #0x2ee0
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0e	; 14
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x2f44
	.db #0x0d	; 13
	.dw #0x2fb4
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x0e	; 14
	.db #0x07	; 7
	.db #0x00	;  0
	.dw #0x3024
	.db #0x0d	; 13
	.dw #0x30c0
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x315c
	.db #0x0d	; 13
	.dw #0x31dc
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0e	; 14
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x325c
	.db #0x0d	; 13
	.dw #0x3314
	.db #0x0d	; 13
	.db #0x0d	; 13
	.db #0x0e	; 14
	.db #0x0c	; 12
	.db #0x00	;  0
	.dw #0x33cc
	.db #0x0d	; 13
	.dw #0x3468
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x3504
	.db #0x0d	; 13
	.dw #0x35ac
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x3654
	.db #0x0d	; 13
	.dw #0x36e0
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x376c
	.db #0x0d	; 13
	.dw #0x3838
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x11	; 17
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x3904
	.db #0x0d	; 13
	.dw #0x39a0
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x3a3c
	.db #0x0d	; 13
	.dw #0x3ac8
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x3b54
	.db #0x0d	; 13
	.dw #0x3bf0
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x3c8c
	.db #0x0d	; 13
	.dw #0x3d28
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x3dc4
	.db #0x0d	; 13
	.dw #0x3e6c
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x3f14
	.db #0x0d	; 13
	.dw #0x3fe8
	.db #0x0d	; 13
	.db #0x0f	; 15
	.db #0x0e	; 14
	.db #0x0e	; 14
	.db #0x00	;  0
	.dw #0x40bc
	.db #0x0d	; 13
	.dw #0x4158
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x0e	; 14
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x41f4
	.db #0x0d	; 13
	.dw #0x429c
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x4344
	.db #0x0d	; 13
	.dw #0x43d0
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0e	; 14
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x445c
	.db #0x0d	; 13
	.dw #0x44dc
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x12	; 18
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x455c
	.db #0x0d	; 13
	.dw #0x45e4
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x11	; 17
	.db #0x07	; 7
	.db #0x00	;  0
	.dw #0x466c
	.db #0x0d	; 13
	.dw #0x46ec
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x12	; 18
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x476c
	.db #0x0d	; 13
	.dw #0x4814
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0e	; 14
	.db #0x0b	; 11
	.db #0x00	;  0
	.dw #0x48bc
	.db #0x0d	; 13
	.dw #0x4900
	.db #0x0d	; 13
	.db #0x0b	; 11
	.db #0x06	; 6
	.db #0x0a	; 10
	.db #0x00	;  0
	.dw #0x4944
	.db #0x0d	; 13
	.dw #0x49e4
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x10	; 16
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x4a84
	.db #0x0d	; 13
	.dw #0x4af0
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x4b5c
	.db #0x0d	; 13
	.dw #0x4bf4
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x4c8c
	.db #0x0d	; 13
	.dw #0x4cf8
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x4d64
	.db #0x0d	; 13
	.dw #0x4dfc
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x4e94
	.db #0x0d	; 13
	.dw #0x4f00
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x4f6c
	.db #0x0d	; 13
	.dw #0x4fd8
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0f	; 15
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x5044
	.db #0x0d	; 13
	.dw #0x50dc
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x5174
	.db #0x0d	; 13
	.dw #0x520c
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x52a4
	.db #0x0d	; 13
	.dw #0x52ec
	.db #0x0d	; 13
	.db #0x05	; 5
	.db #0x0e	; 14
	.db #0x04	; 4
	.db #0x00	;  0
	.dw #0x5334
	.db #0x0d	; 13
	.dw #0x53ac
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x11	; 17
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x5424
	.db #0x0d	; 13
	.dw #0x54bc
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x5554
	.db #0x0d	; 13
	.dw #0x55a0
	.db #0x0d	; 13
	.db #0x05	; 5
	.db #0x0f	; 15
	.db #0x04	; 4
	.db #0x00	;  0
	.dw #0x55ec
	.db #0x0d	; 13
	.dw #0x5694
	.db #0x0d	; 13
	.db #0x0e	; 14
	.db #0x0c	; 12
	.db #0x0d	; 13
	.db #0x00	;  0
	.dw #0x573c
	.db #0x0d	; 13
	.dw #0x57b4
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0c	; 12
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x582c
	.db #0x0d	; 13
	.dw #0x58a4
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0c	; 12
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x591c
	.db #0x0d	; 13
	.dw #0x59b4
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x5a4c
	.db #0x0d	; 13
	.dw #0x5ae4
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0f	; 15
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x5b7c
	.db #0x0d	; 13
	.dw #0x5bd0
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0c	; 12
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x5c24
	.db #0x0d	; 13
	.dw #0x5c84
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x0c	; 12
	.db #0x07	; 7
	.db #0x00	;  0
	.dw #0x5ce4
	.db #0x0d	; 13
	.dw #0x5d48
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x0e	; 14
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x5dac
	.db #0x0d	; 13
	.dw #0x5e24
	.db #0x0d	; 13
	.db #0x0a	; 10
	.db #0x0c	; 12
	.db #0x09	; 9
	.db #0x00	;  0
	.dw #0x5e9c
	.db #0x0d	; 13
	.dw #0x5f08
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x5f74
	.db #0x0d	; 13
	.dw #0x6010
	.db #0x0d	; 13
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0c	; 12
	.db #0x00	;  0
	.dw #0x60ac
	.db #0x0d	; 13
	.dw #0x6118
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0c	; 12
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x6184
	.db #0x0d	; 13
	.dw #0x620c
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x0f	; 15
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x6294
	.db #0x0d	; 13
	.dw #0x62f4
	.db #0x0d	; 13
	.db #0x08	; 8
	.db #0x0c	; 12
	.db #0x07	; 7
	.db #0x00	;  0
	.dw #0x6354
	.db #0x0d	; 13
	.dw #0x63f8
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x12	; 18
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x649c
	.db #0x0d	; 13
	.dw #0x651c
	.db #0x0d	; 13
	.db #0x07	; 7
	.db #0x12	; 18
	.db #0x06	; 6
	.db #0x00	;  0
	.dw #0x659c
	.db #0x0d	; 13
	.dw #0x6640
	.db #0x0d	; 13
	.db #0x09	; 9
	.db #0x12	; 18
	.db #0x08	; 8
	.db #0x00	;  0
	.dw #0x66e4
	.db #0x0d	; 13
	.dw #0x6768
	.db #0x0d	; 13
	.db #0x0c	; 12
	.db #0x0b	; 11
	.db #0x0b	; 11
	.db #0x00	;  0
_monster_animation_sequence:
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x02	; 2
	.db #0x03	; 3
	.db #0x04	; 4
	.db #0x05	; 5
	.db #0x04	; 4
	.db #0x03	; 3
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x00	; 0
	.db #0x01	; 1
	.db #0x02	; 2
	.db #0x01	; 1
	.db #0x00	; 0
_default_standard:
	.ascii "Lord Kilburn"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Beltway"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0046
	.dw #0x0096
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Tsabu"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Deathgate"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0050
	.dw #0x008c
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Sir Galant"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Enroth"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x005a
	.dw #0x0082
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Thundax"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Lost Continent"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0064
	.dw #0x0078
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Lord Haart"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Mountain King"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0078
	.dw #0x006e
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Ariel"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Pandemonium"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x008c
	.dw #0x0064
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Rebecca"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Terra Firma"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x00a0
	.dw #0x005a
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Sandro"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "The Clearing"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x00b4
	.dw #0x0050
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Crodo"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Vikings!"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x00c8
	.dw #0x0046
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Barock"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Wastelands"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x00f0
	.dw #0x003c
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
_default_campaign:
	.ascii "Antoine"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Roland"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0258
	.dw #0x0258
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Astra"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Archibald"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x028a
	.dw #0x028a
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Agar"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Roland"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x02bc
	.dw #0x02bc
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Vatawna"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Archibald"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x02ee
	.dw #0x02ee
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Vesper"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Roland"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0320
	.dw #0x0320
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Ambrose"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Archibald"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0352
	.dw #0x0352
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Troyan"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Roland"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0384
	.dw #0x0384
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Jojosh"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Archibald"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x03e8
	.dw #0x03e8
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Wrathmont"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Roland"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x07d0
	.dw #0x07d0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.ascii "Maximus"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.ascii "Archibald"
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.db 0x00
	.dw #0x0bb8
	.dw #0x0bb8
	.byte #0x00, #0x00, #0x00, #0x00	; 0
	.byte #0x00, #0x00, #0x00, #0x00	; 0
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:132: static void zero_bytes(uint8_t * dst, uint16_t count)
;	---------------------------------
; Function zero_bytes
; ---------------------------------
_zero_bytes:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:134: while (count != 0) {
00101$:
	ld	a, d
	or	a, e
	ret	Z
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:135: *dst++ = 0;
	ld	(hl), #0x00
	inc	hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:136: --count;
	dec	de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:138: }
	jp	00101$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:140: static uint16_t read16(const uint8_t * p)
;	---------------------------------
; Function read16
; ---------------------------------
_read16:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:142: return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
	ld	e, (hl)
	inc	hl
	ld	d, #0x00
	ld	l, (hl)
;	spillPairReg hl
;	spillPairReg hl
;	spillPairReg hl
	xor	a, a
	or	a, e
	ld	e, a
	ld	a, l
	or	a, d
	ld	d, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:143: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:145: static uint32_t read32(const uint8_t * p)
;	---------------------------------
; Function read32
; ---------------------------------
_read32:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-8
	add	iy, sp
	ld	sp, iy
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:147: return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
	ld	a, (de)
	ld	-4 (ix), a
	xor	a, a
	ld	-3 (ix), a
	ld	-2 (ix), a
	ld	-1 (ix), a
	ld	l, e
;	spillPairReg hl
;	spillPairReg hl
	ld	h, d
;	spillPairReg hl
;	spillPairReg hl
	inc	hl
	ld	c, (hl)
	ld	b, #0x00
	ld	hl, #0x0000
	ld	h, l
;	spillPairReg hl
;	spillPairReg hl
	ld	l, b
;	spillPairReg hl
;	spillPairReg hl
	ld	b, c
	ld	c, #0x00
	ld	a, -4 (ix)
	or	a, c
	ld	-8 (ix), a
	ld	a, -3 (ix)
	or	a, b
	ld	-7 (ix), a
	ld	a, -2 (ix)
	or	a, l
	ld	-6 (ix), a
	ld	a, -1 (ix)
	or	a, h
	ld	-5 (ix), a
	ld	l, e
;	spillPairReg hl
;	spillPairReg hl
	ld	h, d
;	spillPairReg hl
;	spillPairReg hl
	inc	hl
	inc	hl
	ld	l, (hl)
;	spillPairReg hl
	ld	h, #0x00
;	spillPairReg hl
;	spillPairReg hl
	ld	bc, #0x0000
	ld	a, -8 (ix)
	or	a, c
	ld	-4 (ix), a
	ld	a, -7 (ix)
	or	a, b
	ld	-3 (ix), a
	ld	a, -6 (ix)
	or	a, l
	ld	-2 (ix), a
	ld	a, -5 (ix)
	or	a, h
	ld	-1 (ix), a
	ld	hl, #3
	add	hl, de
	ld	h, (hl)
;	spillPairReg hl
;	spillPairReg hl
	ld	bc, #0x0000
	ld	l, #0x00
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -4 (ix)
	or	a, c
	ld	e, a
	ld	a, -3 (ix)
	or	a, b
	ld	d, a
	ld	a, -2 (ix)
	or	a, l
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -1 (ix)
	or	a, h
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:148: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:150: static void write16(uint8_t * p, uint16_t v)
;	---------------------------------
; Function write16
; ---------------------------------
_write16:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:152: p[0] = (uint8_t)v;
	ld	(hl), e
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:153: p[1] = (uint8_t)(v >> 8);
	inc	hl
	ld	(hl), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:154: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:156: static void write32(uint8_t * p, uint32_t v)
;	---------------------------------
; Function write32
; ---------------------------------
_write32:
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:158: p[0] = (uint8_t)v;
	ld	iy, #2
	add	iy, sp
	ld	a, 0 (iy)
	ld	(de), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:159: p[1] = (uint8_t)(v >> 8);
	ld	c, e
	ld	b, d
	inc	bc
	ld	a, 1 (iy)
	ld	(bc), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:160: p[2] = (uint8_t)(v >> 16);
	ld	c, e
	ld	b, d
	inc	bc
	inc	bc
	ld	a, 2 (iy)
	ld	(bc), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:161: p[3] = (uint8_t)(v >> 24);
	inc	de
	inc	de
	inc	de
	ld	a, 3 (iy)
	ld	(de), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:162: }
	pop	hl
	pop	af
	pop	af
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:164: static uint32_t crc32_update(uint32_t crc, uint8_t value)
;	---------------------------------
; Function crc32_update
; ---------------------------------
_crc32_update:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:167: crc ^= value;
	ld	a, 4 (ix)
	push	iy
	ex	(sp), hl
	ld	h, #0x00
;	spillPairReg hl
;	spillPairReg hl
	ex	(sp), hl
	pop	iy
	ld	bc, #0x0000
	xor	a, e
	ld	e, a
	push	iy
	ld	a, -5 (ix)
	pop	iy
	xor	a, d
	ld	d, a
	ld	a, c
	xor	a, l
	ld	c, a
	ld	a, b
	xor	a, h
	ld	b, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:168: for (i = 0; i < 8; ++i) {
	ld	l, #0x00
;	spillPairReg hl
;	spillPairReg hl
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:170: crc = (crc >> 1) ^ 0xEDB88320UL;
	inc	sp
	inc	sp
	push	de
	ld	-2 (ix), c
	ld	-1 (ix), b
	srl	-1 (ix)
	rr	-2 (ix)
	rr	-3 (ix)
	rr	-4 (ix)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:169: if ((crc & 1) != 0) {
	bit	0, e
	jr	Z, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:170: crc = (crc >> 1) ^ 0xEDB88320UL;
	ld	a, -4 (ix)
	xor	a, #0x20
	ld	e, a
	ld	a, -3 (ix)
	xor	a, #0x83
	ld	d, a
	ld	a, -2 (ix)
	xor	a, #0xb8
	ld	c, a
	ld	a, -1 (ix)
	xor	a, #0xed
	ld	b, a
	jp	00106$
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:173: crc >>= 1;
	pop	de
	push	de
	ld	c, -2 (ix)
	ld	b, -1 (ix)
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:168: for (i = 0; i < 8; ++i) {
	inc	l
	ld	a, l
	sub	a, #0x08
	jr	C, 00105$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:176: return crc;
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	h, b
;	spillPairReg hl
;	spillPairReg hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:177: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:179: static uint32_t crc32_block(const uint8_t * data, uint16_t size)
;	---------------------------------
; Function crc32_block
; ---------------------------------
_crc32_block:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	ld	c, l
	ld	b, h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:181: uint32_t crc = 0xFFFFFFFFUL;
	ld	-4 (ix), #0xff
	ld	-3 (ix), #0xff
	ld	-2 (ix), #0xff
	ld	-1 (ix), #0xff
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:182: while (size != 0) {
00101$:
	ld	a, d
	or	a, e
	jr	Z, 00103$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:183: crc = crc32_update(crc, *data++);
	ld	a, (bc)
	inc	bc
	push	bc
	push	de
	push	af
	inc	sp
	ld	e, -4 (ix)
	ld	d, -3 (ix)
	ld	l, -2 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -1 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_crc32_update
	inc	sp
	push	de
	pop	iy
	pop	de
	pop	bc
	inc	sp
	inc	sp
	push	iy
	ld	-2 (ix), l
	ld	-1 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:184: --size;
	dec	de
	jp	00101$
00103$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:186: return crc ^ 0xFFFFFFFFUL;
	ld	a, -4 (ix)
	cpl
	ld	e, a
	ld	a, -3 (ix)
	cpl
	ld	d, a
	ld	a, -2 (ix)
	cpl
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -1 (ix)
	cpl
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:187: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:189: static uint32_t keyed_tag(const uint8_t * data, uint16_t size, uint32_t generation, uint8_t slot_id)
;	---------------------------------
; Function keyed_tag
; ---------------------------------
_keyed_tag:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-8
	add	iy, sp
	ld	sp, iy
	ld	c, l
	ld	b, h
	ld	-4 (ix), e
	ld	-3 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:192: uint32_t tag = 0xA5C35A7DUL ^ generation ^ ((uint32_t)slot_id * 0x45D9F3BUL);
	ld	a, 4 (ix)
	xor	a, #0x7d
	ld	-8 (ix), a
	ld	a, 5 (ix)
	xor	a, #0x5a
	ld	-7 (ix), a
	ld	a, 6 (ix)
	xor	a, #0xc3
	ld	-6 (ix), a
	ld	a, 7 (ix)
	xor	a, #0xa5
	ld	-5 (ix), a
	ld	e, 8 (ix)
	ld	d, #0x00
	ld	hl, #0x0000
	push	bc
	push	hl
	push	de
	ld	de, #0x9f3b
	ld	hl, #0x045d
	call	__mullong
	pop	af
	pop	af
	pop	bc
	ld	a, -8 (ix)
	xor	a, e
	ld	-8 (ix), a
	ld	a, -7 (ix)
	xor	a, d
	ld	-7 (ix), a
	ld	a, -6 (ix)
	xor	a, l
	ld	-6 (ix), a
	ld	a, -5 (ix)
	xor	a, h
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:193: while (size != 0) {
	ld	-2 (ix), c
	ld	-1 (ix), b
	ld	c, -4 (ix)
	ld	b, -3 (ix)
00101$:
	ld	a, b
	or	a, c
	jp	Z, 00103$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:194: tag = (tag << 5) | (tag >> 27);
	pop	hl
	push	hl
	ld	e, -6 (ix)
	ld	d, -5 (ix)
	ld	a, #0x05
00117$:
	add	hl, hl
	rl	e
	rl	d
	dec	a
	jr	NZ,00117$
	ld	a, #0x1b
00119$:
	srl	-5 (ix)
	rr	-6 (ix)
	rr	-7 (ix)
	rr	-8 (ix)
	dec	a
	jr	NZ, 00119$
	ld	a, l
	or	a, -8 (ix)
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, h
	or	a, -7 (ix)
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, e
	or	a, -6 (ix)
	ld	e, a
	ld	a, d
	or	a, -5 (ix)
	ld	d, a
	ex	(sp), hl
	ld	-6 (ix), e
	ld	-5 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:195: tag ^= ((uint32_t)(*data++) + 0x9E3779B9UL);
	ld	l, -2 (ix)
	ld	h, -1 (ix)
	ld	l, (hl)
;	spillPairReg hl
	inc	-2 (ix)
	jr	NZ, 00121$
	inc	-1 (ix)
00121$:
	ld	h, #0x00
;	spillPairReg hl
;	spillPairReg hl
	ld	de, #0x0000
	push	de
	ld	de, #0x79b9
	add	hl, de
	pop	de
	ld	a, e
	adc	a, #0x37
	ld	e, a
	ld	a, d
	adc	a, #0x9e
	ld	d, a
	ld	a, -8 (ix)
	xor	a, l
	ld	-8 (ix), a
	ld	a, -7 (ix)
	xor	a, h
	ld	-7 (ix), a
	ld	a, -6 (ix)
	xor	a, e
	ld	-6 (ix), a
	ld	a, -5 (ix)
	xor	a, d
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:196: --size;
	dec	bc
	jp	00101$
00103$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:198: return tag;
	pop	de
	push	de
	ld	l, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -5 (ix)
;	spillPairReg hl
;	spillPairReg hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:199: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:201: static uint8_t ror8(uint8_t v, uint8_t rot)
;	---------------------------------
; Function ror8
; ---------------------------------
_ror8:
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:203: rot &= 7;
	ld	a, l
	and	a, #0x07
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:204: if (rot == 0) {
	ld	e, a
	or	a, a
	jr	NZ, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:205: return v;
	ld	a, c
	ret
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:207: return (uint8_t)((v >> rot) | (v << (8 - rot)));
	ld	a, e
	push	af
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	pop	af
	inc	a
	jp	00111$
00110$:
	srl	l
00111$:
	dec	a
	jr	NZ, 00110$
	ld	a, #0x08
	sub	a, e
	ld	b, a
	ld	a, c
	inc	b
	jp	00113$
00112$:
	add	a, a
00113$:
	djnz	00112$
	or	a, l
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:208: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:210: static uint8_t rol8(uint8_t v, uint8_t rot)
;	---------------------------------
; Function rol8
; ---------------------------------
_rol8:
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:212: rot &= 7;
	ld	a, l
	and	a, #0x07
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:213: if (rot == 0) {
	ld	e, a
	or	a, a
	jr	NZ, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:214: return v;
	ld	a, c
	ret
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:216: return (uint8_t)((v << rot) | (v >> (8 - rot)));
	ld	a, e
	push	af
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	pop	af
	inc	a
	jp	00111$
00110$:
	sla	l
00111$:
	dec	a
	jr	NZ,00110$
	ld	a, #0x08
	sub	a, e
	ld	b, a
	inc	b
	jp	00113$
00112$:
	srl	c
00113$:
	djnz	00112$
	ld	a, l
	or	a, c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:217: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:219: static void decode_slot(const uint8_t * encoded, uint8_t * plain, uint8_t slot_id)
;	---------------------------------
; Function decode_slot
; ---------------------------------
_decode_slot:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-14
	add	iy, sp
	ld	sp, iy
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	-6 (ix), e
	ld	-5 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:223: uint32_t seed = HS_XOR_KEY ^ ((uint32_t)slot_id * 0x45D9F3BUL);
	ld	c, 4 (ix)
	ld	b, #0x00
	ld	de, #0x0000
	push	de
	push	bc
	ld	de, #0x9f3b
	ld	hl, #0x045d
	call	__mullong
	pop	af
	pop	af
	ld	a, e
	xor	a, #0x53
	ld	-14 (ix), a
	ld	a, d
	xor	a, #0x4a
	ld	-13 (ix), a
	ld	a, l
	xor	a, #0x32
	ld	-12 (ix), a
	ld	a, h
	xor	a, #0x48
	ld	-11 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:224: for (i = 0; i < HS_SLOT_SIZE; ++i) {
	xor	a, a
	ld	-2 (ix), a
	ld	-1 (ix), a
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:226: seed = seed * 1664525UL + 1013904223UL;
	ld	l, -12 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -11 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	l, -14 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -13 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x660d
	ld	hl, #0x0019
	call	__mullong
	pop	af
	pop	af
	ld	-10 (ix), e
	ld	-9 (ix), d
	ld	-8 (ix), l
	ld	-7 (ix), h
	ld	a, -10 (ix)
	add	a, #0x5f
	ld	-14 (ix), a
	ld	a, -9 (ix)
	adc	a, #0xf3
	ld	-13 (ix), a
	ld	a, -8 (ix)
	adc	a, #0x6e
	ld	-12 (ix), a
	ld	a, -7 (ix)
	adc	a, #0x3c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:227: mask = (uint8_t)((seed >> 24) ^ ((uint16_t)i * 37) ^ (i >> 3));
	ld	-11 (ix), a
	ld	e, a
	ld	c, -2 (ix)
	ld	a, c
	add	a, a
	add	a, a
	add	a, a
	add	a, c
	add	a, a
	add	a, a
	add	a, c
	xor	a, e
	ld	b, a
	ld	e, -2 (ix)
	ld	d, -1 (ix)
	srl	d
	rr	e
	srl	d
	rr	e
	srl	d
	rr	e
	ld	a, b
	xor	a, e
	ld	b, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:228: plain[i] = ror8(encoded[i], (uint8_t)(i + slot_id)) ^ mask;
	ld	a, -6 (ix)
	add	a, -2 (ix)
	ld	e, a
	ld	a, -5 (ix)
	adc	a, -1 (ix)
	ld	d, a
	ld	a, c
	add	a, 4 (ix)
	ld	c, a
	ld	a, -4 (ix)
	add	a, -2 (ix)
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -3 (ix)
	adc	a, -1 (ix)
	ld	h, a
	ld	h, (hl)
;	spillPairReg hl
	push	bc
	push	de
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	a, h
	call	_ror8
	pop	de
	pop	bc
	xor	a, b
	ld	(de), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:224: for (i = 0; i < HS_SLOT_SIZE; ++i) {
	inc	-2 (ix)
	jr	NZ, 00112$
	inc	-1 (ix)
00112$:
	ld	c, -2 (ix)
	ld	b, -1 (ix)
	ld	a, b
	sub	a, #0x04
	jp	C, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:230: }
	ld	sp, ix
	pop	ix
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:232: static void encode_slot(const uint8_t * plain, uint8_t * encoded, uint8_t slot_id)
;	---------------------------------
; Function encode_slot
; ---------------------------------
_encode_slot:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-14
	add	iy, sp
	ld	sp, iy
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	-6 (ix), e
	ld	-5 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:235: uint32_t seed = HS_XOR_KEY ^ ((uint32_t)slot_id * 0x45D9F3BUL);
	ld	c, 4 (ix)
	ld	b, #0x00
	ld	de, #0x0000
	push	de
	push	bc
	ld	de, #0x9f3b
	ld	hl, #0x045d
	call	__mullong
	pop	af
	pop	af
	ld	a, e
	xor	a, #0x53
	ld	-14 (ix), a
	ld	a, d
	xor	a, #0x4a
	ld	-13 (ix), a
	ld	a, l
	xor	a, #0x32
	ld	-12 (ix), a
	ld	a, h
	xor	a, #0x48
	ld	-11 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:236: for (i = 0; i < HS_SLOT_SIZE; ++i) {
	xor	a, a
	ld	-2 (ix), a
	ld	-1 (ix), a
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:238: seed = seed * 1664525UL + 1013904223UL;
	ld	l, -12 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -11 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	l, -14 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -13 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x660d
	ld	hl, #0x0019
	call	__mullong
	pop	af
	pop	af
	ld	-10 (ix), e
	ld	-9 (ix), d
	ld	-8 (ix), l
	ld	-7 (ix), h
	ld	a, -10 (ix)
	add	a, #0x5f
	ld	-14 (ix), a
	ld	a, -9 (ix)
	adc	a, #0xf3
	ld	-13 (ix), a
	ld	a, -8 (ix)
	adc	a, #0x6e
	ld	-12 (ix), a
	ld	a, -7 (ix)
	adc	a, #0x3c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:239: mask = (uint8_t)((seed >> 24) ^ ((uint16_t)i * 37) ^ (i >> 3));
	ld	-11 (ix), a
	ld	e, a
	ld	c, -2 (ix)
	ld	a, c
	add	a, a
	add	a, a
	add	a, a
	add	a, c
	add	a, a
	add	a, a
	add	a, c
	xor	a, e
	ld	b, a
	ld	e, -2 (ix)
	ld	d, -1 (ix)
	srl	d
	rr	e
	srl	d
	rr	e
	srl	d
	rr	e
	ld	a, b
	xor	a, e
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:240: encoded[i] = rol8(plain[i] ^ mask, (uint8_t)(i + slot_id));
	ld	a, -6 (ix)
	add	a, -2 (ix)
	ld	e, a
	ld	a, -5 (ix)
	adc	a, -1 (ix)
	ld	d, a
	ld	a, c
	add	a, 4 (ix)
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -4 (ix)
	add	a, -2 (ix)
	ld	c, a
	ld	a, -3 (ix)
	adc	a, -1 (ix)
	ld	b, a
	ld	a, (bc)
	xor	a, h
	ld	c, a
	push	de
	ld	a, c
	call	_rol8
	pop	de
	ld	(de), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:236: for (i = 0; i < HS_SLOT_SIZE; ++i) {
	inc	-2 (ix)
	jr	NZ, 00112$
	inc	-1 (ix)
00112$:
	ld	c, -2 (ix)
	ld	b, -1 (ix)
	ld	a, b
	sub	a, #0x04
	jp	C, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:242: }
	ld	sp, ix
	pop	ix
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:244: static void copy_entry_from_disk(HsEntry * dst, const uint8_t * src)
;	---------------------------------
; Function copy_entry_from_disk
; ---------------------------------
_copy_entry_from_disk:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	push	af
	ld	c, l
	ld	b, h
	ld	-2 (ix), e
	ld	-1 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:247: copy_bytes((uint8_t *)dst->player, src, 16);
	push	bc
	ld	hl, #0x0010
	push	hl
	ld	e, -2 (ix)
	ld	d, -1 (ix)
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	h, b
;	spillPairReg hl
;	spillPairReg hl
	call	_copy_bytes
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:248: copy_bytes((uint8_t *)dst->scenario, src + 16, 20);
	ld	a, -2 (ix)
	add	a, #0x10
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	ld	hl, #0x0010
	add	hl, bc
	push	bc
	ld	bc, #0x0014
	push	bc
	call	_copy_bytes
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:249: dst->player[15] = 0;
	ld	hl, #0x000f
	add	hl, bc
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:250: dst->scenario[19] = 0;
	ld	hl, #0x0010
	add	hl, bc
	ld	de, #0x0013
	add	hl, de
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:251: dst->days = read16(src + 36);
	ld	hl, #0x0024
	add	hl, bc
	ld	a, -2 (ix)
	add	a, #0x24
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	push	hl
	push	bc
	ex	de, hl
	call	_read16
	pop	bc
	pop	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:252: dst->rating = read16(src + 38);
	ld	hl, #0x0026
	add	hl, bc
	ld	a, -2 (ix)
	add	a, #0x26
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	push	hl
	push	bc
	ex	de, hl
	call	_read16
	pop	bc
	pop	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:253: dst->completion_time = read32(src + 40);
	ld	hl, #0x0028
	add	hl, bc
	ex	de, hl
	ld	a, -2 (ix)
	add	a, #0x28
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	push	bc
	push	de
	call	_read32
	ld	-6 (ix), e
	ld	-5 (ix), d
	ld	-4 (ix), l
	ld	-3 (ix), h
	pop	de
	ld	hl, #2
	add	hl, sp
	ld	bc, #0x0004
	ldir
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:254: dst->map_seed = read32(src + 44);
	ld	hl, #0x002c
	add	hl, bc
	ld	a, -2 (ix)
	add	a, #0x2c
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	ex	de, hl
	push	de
	call	_read32
	ld	c, l
	ld	b, h
	pop	hl
	ld	(hl), e
	inc	hl
	ld	(hl), d
	inc	hl
	ld	(hl), c
	inc	hl
	ld	(hl), b
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:255: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:257: static void copy_entry_to_disk(uint8_t * dst, const HsEntry * src)
;	---------------------------------
; Function copy_entry_to_disk
; ---------------------------------
_copy_entry_to_disk:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	ld	c, l
	ld	b, h
	inc	sp
	inc	sp
	push	de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:259: copy_bytes(dst, (const uint8_t *)src->player, 16);
	push	bc
	ld	hl, #0x0010
	push	hl
	ld	e, -2 (ix)
	ld	d, -1 (ix)
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	h, b
;	spillPairReg hl
;	spillPairReg hl
	call	_copy_bytes
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:260: copy_bytes(dst + 16, (const uint8_t *)src->scenario, 20);
	ld	a, -2 (ix)
	add	a, #0x10
	ld	e, a
	ld	a, -1 (ix)
	adc	a, #0x00
	ld	d, a
	ld	hl, #0x0010
	add	hl, bc
	push	bc
	ld	bc, #0x0014
	push	bc
	call	_copy_bytes
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:261: write16(dst + 36, src->days);
	pop	de
	push	de
	ld	hl, #36
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	hl, #0x0024
	add	hl, bc
	push	bc
	call	_write16
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:262: write16(dst + 38, src->rating);
	pop	de
	push	de
	ld	hl, #38
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	hl, #0x0026
	add	hl, bc
	push	bc
	call	_write16
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:263: write32(dst + 40, src->completion_time);
	pop	de
	push	de
	ld	hl, #40
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	inc	hl
	inc	hl
	ld	a, (hl)
	dec	hl
	ld	l, (hl)
;	spillPairReg hl
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	iy, #0x0028
	add	iy, bc
	push	bc
	push	hl
	push	de
	push	iy
	pop	hl
	call	_write32
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:264: write32(dst + 44, src->map_seed);
	pop	de
	push	de
	ld	hl, #44
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	inc	hl
	inc	hl
	ld	a, (hl)
	dec	hl
	ld	l, (hl)
;	spillPairReg hl
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, c
	add	a, #0x2c
	ld	c, a
	jr	NC, 00103$
	inc	b
00103$:
	push	hl
	push	de
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	h, b
;	spillPairReg hl
;	spillPairReg hl
	call	_write32
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:265: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:267: static void load_defaults(void)
;	---------------------------------
; Function load_defaults
; ---------------------------------
_load_defaults:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:269: copy_bytes((uint8_t *)standard_scores, (const uint8_t *)default_standard, sizeof(default_standard));
	ld	hl, #0x01e0
	push	hl
	ld	de, #_default_standard
	ld	hl, #_standard_scores
	call	_copy_bytes
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:270: copy_bytes((uint8_t *)campaign_scores, (const uint8_t *)default_campaign, sizeof(default_campaign));
	ld	hl, #0x01e0
	push	hl
	ld	de, #_default_campaign
	ld	hl, #_campaign_scores
	call	_copy_bytes
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:271: active_slot = 0;
	ld	hl, #_active_slot
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:272: active_generation = 0;
	xor	a, a
	ld	(_active_generation+0), a
	ld	(_active_generation+1), a
	ld	(_active_generation+2), a
	ld	(_active_generation+3), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:273: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:275: static uint8_t parse_plain_slot(uint8_t slot_id, uint32_t * generation_out)
;	---------------------------------
; Function parse_plain_slot
; ---------------------------------
_parse_plain_slot:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-18
	add	hl, sp
	ld	sp, hl
	ld	-2 (ix), a
	ld	-4 (ix), e
	ld	-3 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:282: uint8_t * payload = slot_plain + HS_HEADER_SIZE;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:287: if (slot_plain[0] != 'H' || slot_plain[1] != '2' || slot_plain[2] != 'H' || slot_plain[3] != 'S') {
	ld	a, (#_slot_plain + 0)
	sub	a, #0x48
	jr	NZ, 00101$
	ld	a, (#_slot_plain + 1)
	sub	a, #0x32
	jr	NZ, 00101$
	ld	a, (#_slot_plain + 2)
	sub	a, #0x48
	jr	NZ, 00101$
	ld	a, (#_slot_plain + 3)
	sub	a, #0x53
	jr	Z, 00102$
00101$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:288: return 0;
	xor	a, a
	jp	00123$
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:290: if (slot_plain[4] != HS_VERSION || slot_plain[5] != slot_id || slot_plain[6] != HS_ENTRY_SIZE) {
	ld	a, (#_slot_plain + 4)
	dec	a
	jr	NZ, 00106$
	ld	hl, #_slot_plain + 5
	ld	a,-2 (ix)
	sub	a,(hl)
	jr	NZ, 00106$
	ld	a, (#_slot_plain + 6)
	sub	a, #0x30
	jr	Z, 00107$
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:291: return 0;
	xor	a, a
	jp	00123$
00107$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:293: if (slot_plain[7] != HS_ENTRY_COUNT || slot_plain[8] != HS_ENTRY_COUNT) {
	ld	a, (#_slot_plain + 7)
	sub	a, #0x0a
	jr	NZ, 00110$
	ld	a, (#_slot_plain + 8)
	sub	a, #0x0a
	jr	Z, 00111$
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:294: return 0;
	xor	a, a
	jp	00123$
00111$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:297: generation = read32(slot_plain + 12);
	ld	hl, #(_slot_plain + 12)
	call	_read32
	ld	-10 (ix), e
	ld	-9 (ix), d
	ld	-8 (ix), l
	ld	-7 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:298: crc = read32(slot_plain + 16);
	ld	hl, #(_slot_plain + 16)
	call	_read32
	ld	c, l
	ld	b, h
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:299: tag = read32(slot_plain + 20);
	push	hl
	push	bc
	ld	hl, #(_slot_plain + 20)
	call	_read32
	push	hl
	pop	iy
	pop	bc
	pop	hl
	inc	sp
	inc	sp
	push	de
	push	iy
	ex	(sp), hl
	ld	-16 (ix), l
	ex	(sp), hl
	ex	(sp), hl
	ld	-15 (ix), h
	ex	(sp), hl
	pop	iy
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:300: if (crc32_block(payload, HS_SLOT_SIZE - HS_HEADER_SIZE) != crc) {
	push	hl
	push	bc
	ld	de, #0x03c0
	ld	hl, #(_slot_plain + 64)
	call	_crc32_block
	ld	-14 (ix), e
	ld	-13 (ix), d
	ld	-12 (ix), l
	ld	-11 (ix), h
	pop	bc
	pop	hl
	ld	e, -14 (ix)
	ld	d, -13 (ix)
	cp	a, a
	sbc	hl, de
	jr	NZ, 00202$
	ld	l, -12 (ix)
	ld	h, -11 (ix)
	cp	a, a
	sbc	hl, bc
	jr	Z, 00114$
00202$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:301: return 0;
	xor	a, a
	jp	00123$
00114$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:303: if (keyed_tag(payload, HS_SLOT_SIZE - HS_HEADER_SIZE, generation, slot_id) != tag) {
	ld	a, -2 (ix)
	push	af
	inc	sp
	ld	l, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	l, -10 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -9 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x03c0
	ld	hl, #(_slot_plain + 64)
	call	_keyed_tag
	pop	af
	pop	af
	inc	sp
	ex	de, hl
	pop	bc
	push	bc
	cp	a, a
	sbc	hl, bc
	jr	NZ, 00203$
	pop	bc
	pop	hl
	push	hl
	push	bc
	cp	a, a
	sbc	hl, de
	jr	Z, 00133$
00203$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:304: return 0;
	xor	a, a
	jp	00123$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:307: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
00133$:
	ld	-1 (ix), #0x00
00119$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:308: copy_entry_from_disk(&standard_scores[i], payload + (uint16_t)i * HS_ENTRY_SIZE);
	ld	a, -1 (ix)
	ld	-6 (ix), a
	ld	-5 (ix), #0x00
	ld	c, a
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	-6 (ix), l
	ld	-5 (ix), h
	ld	a, #<((_slot_plain + 64))
	add	a, -6 (ix)
	ld	e, a
	ld	a, #>((_slot_plain + 64))
	adc	a, -5 (ix)
	ld	d, a
	ld	c, -1 (ix)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	bc, #_standard_scores
	add	hl, bc
	call	_copy_entry_from_disk
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:307: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x0a
	jr	C, 00119$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:310: payload += (uint16_t)HS_ENTRY_COUNT * HS_ENTRY_SIZE;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:311: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	ld	c, #0x00
00121$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:312: copy_entry_from_disk(&campaign_scores[i], payload + (uint16_t)i * HS_ENTRY_SIZE);
	ld	e, c
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ex	de, hl
	ld	hl, #(_slot_plain + 544)
	add	hl, de
	ex	de, hl
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	push	de
	ld	de, #_campaign_scores
	add	hl, de
	pop	de
	push	bc
	call	_copy_entry_from_disk
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:311: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	c
	ld	a, c
	sub	a, #0x0a
	jr	C, 00121$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:315: *generation_out = generation;
	ld	e, -4 (ix)
	ld	d, -3 (ix)
	ld	hl, #8
	add	hl, sp
	ld	bc, #0x0004
	ldir
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:316: return 1;
	ld	a, #0x01
00123$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:317: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:319: static void load_from_disk(void)
;	---------------------------------
; Function load_from_disk
; ---------------------------------
_load_from_disk:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-8
	add	hl, sp
	ld	sp, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:321: uint32_t gen0 = 0;
	xor	a, a
	ld	-8 (ix), a
	ld	-7 (ix), a
	ld	-6 (ix), a
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:322: uint32_t gen1 = 0;
	xor	a, a
	ld	-4 (ix), a
	ld	-3 (ix), a
	ld	-2 (ix), a
	ld	-1 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:326: disk_available = 0;
	ld	hl, #_disk_available
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:327: MEM16(HMM2_HsAbiPtr) = (uint16_t)disk_image;
	ld	hl, #_disk_image
	ld	(0xb16d), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:328: ABI_CALL(HMM2_HscAbi_ReadHgs);
	call	0xb0b9
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:329: if (MEM8(HMM2_HsAbiStatus) == 0) {
	ld	a, (#0xb16b)
	or	a, a
	jr	NZ, 00105$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:330: load_defaults();
	call	_load_defaults
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:331: return;
	jp	00114$
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:333: disk_available = 1;
	ld	hl, #_disk_available
	ld	(hl), #0x01
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:335: decode_slot(disk_image, slot_plain, 0);
	xor	a, a
	push	af
	inc	sp
	ld	de, #_slot_plain
	ld	hl, #_disk_image
	call	_decode_slot
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:336: ok0 = parse_plain_slot(0, &gen0);
	ld	hl, #0
	add	hl, sp
	ex	de, hl
	xor	a, a
	call	_parse_plain_slot
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:337: decode_slot(disk_image + HS_SLOT_SIZE, slot_plain, 1);
	push	bc
	ld	a, #0x01
	push	af
	inc	sp
	ld	de, #_slot_plain
	ld	hl, #(_disk_image + 1024)
	call	_decode_slot
	ld	hl, #6
	add	hl, sp
	ex	de, hl
	ld	a, #0x01
	call	_parse_plain_slot
	pop	bc
	ld	b, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:340: if (ok0 == 0 && ok1 == 0) {
	ld	a, c
	or	a,a
	jr	NZ, 00107$
	or	a,b
	jr	NZ, 00107$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:341: load_defaults();
	call	_load_defaults
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:342: return;
	jp	00114$
00107$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:344: if (ok0 != 0 && (ok1 == 0 || gen0 >= gen1)) {
	ld	a, c
	or	a, a
	jr	Z, 00110$
	ld	a, b
	or	a, a
	jr	Z, 00109$
	ld	a, -8 (ix)
	sub	a, -4 (ix)
	ld	a, -7 (ix)
	sbc	a, -3 (ix)
	ld	a, -6 (ix)
	sbc	a, -2 (ix)
	ld	a, -5 (ix)
	sbc	a, -1 (ix)
	jr	C, 00110$
00109$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:345: decode_slot(disk_image, slot_plain, 0);
	xor	a, a
	push	af
	inc	sp
	ld	de, #_slot_plain
	ld	hl, #_disk_image
	call	_decode_slot
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:346: parse_plain_slot(0, &gen0);
	ld	hl, #0
	add	hl, sp
	ex	de, hl
	xor	a, a
	call	_parse_plain_slot
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:347: active_slot = 0;
	ld	hl, #_active_slot
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:348: active_generation = gen0;
	ld	de, #_active_generation
	ld	hl, #0
	add	hl, sp
	ld	bc, #4
	ldir
	jp	00114$
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:351: decode_slot(disk_image + HS_SLOT_SIZE, slot_plain, 1);
	ld	a, #0x01
	push	af
	inc	sp
	ld	de, #_slot_plain
	ld	hl, #(_disk_image + 1024)
	call	_decode_slot
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:352: parse_plain_slot(1, &gen1);
	ld	hl, #4
	add	hl, sp
	ex	de, hl
	ld	a, #0x01
	call	_parse_plain_slot
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:353: active_slot = 1;
	ld	hl, #_active_slot
	ld	(hl), #0x01
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:354: active_generation = gen1;
	ld	de, #_active_generation
	ld	hl, #4
	add	hl, sp
	ld	bc, #4
	ldir
00114$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:356: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:358: static uint8_t save_to_disk(void)
;	---------------------------------
; Function save_to_disk
; ---------------------------------
_save_to_disk:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-10
	add	hl, sp
	ld	sp, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:369: if (disk_available == 0) {
	ld	a, (_disk_available+0)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:370: return 0;
	or	a,a
	jp	Z,00114$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:373: next_slot = active_slot ^ 1;
	ld	a, (_active_slot+0)
	xor	a, #0x01
	ld	-10 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:374: generation = active_generation + 1;
	ld	a, (_active_generation+0)
	add	a, #0x01
	ld	-9 (ix), a
	ld	a, (_active_generation+1)
	adc	a, #0x00
	ld	-8 (ix), a
	ld	a, (_active_generation+2)
	adc	a, #0x00
	ld	-7 (ix), a
	ld	a, (_active_generation+3)
	adc	a, #0x00
	ld	-6 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:375: zero_bytes(slot_plain, HS_SLOT_SIZE);
	ld	de, #0x0400
	ld	hl, #_slot_plain
	call	_zero_bytes
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:376: slot_plain[0] = 'H';
	ld	hl, #_slot_plain
	ld	(hl), #0x48
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:377: slot_plain[1] = '2';
	ld	hl, #(_slot_plain + 1)
	ld	(hl), #0x32
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:378: slot_plain[2] = 'H';
	ld	hl, #(_slot_plain + 2)
	ld	(hl), #0x48
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:379: slot_plain[3] = 'S';
	ld	hl, #(_slot_plain + 3)
	ld	(hl), #0x53
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:380: slot_plain[4] = HS_VERSION;
	ld	hl, #(_slot_plain + 4)
	ld	(hl), #0x01
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:381: slot_plain[5] = next_slot;
	ld	hl, #(_slot_plain + 5)
	ld	a, -10 (ix)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:382: slot_plain[6] = HS_ENTRY_SIZE;
	ld	hl, #(_slot_plain + 6)
	ld	(hl), #0x30
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:383: slot_plain[7] = HS_ENTRY_COUNT;
	ld	hl, #(_slot_plain + 7)
	ld	(hl), #0x0a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:384: slot_plain[8] = HS_ENTRY_COUNT;
	ld	hl, #(_slot_plain + 8)
	ld	(hl), #0x0a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:385: write32(slot_plain + 12, generation);
	ld	l, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	l, -9 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	hl, #(_slot_plain + 12)
	call	_write32
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:387: payload = slot_plain + HS_HEADER_SIZE;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:388: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	ld	-1 (ix), #0x00
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:389: copy_entry_to_disk(payload + (uint16_t)i * HS_ENTRY_SIZE, &standard_scores[i]);
	ld	c, -1 (ix)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	-5 (ix), l
	ld	-4 (ix), h
	ld	a, #<(_standard_scores)
	add	a, -5 (ix)
	ld	-3 (ix), a
	ld	a, #>(_standard_scores)
	adc	a, -4 (ix)
	ld	-2 (ix), a
	ld	e, -3 (ix)
	ld	d, -2 (ix)
	ld	c, -1 (ix)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	bc, #(_slot_plain + 64)
	add	hl, bc
	call	_copy_entry_to_disk
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:388: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x0a
	jr	C, 00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:391: payload += (uint16_t)HS_ENTRY_COUNT * HS_ENTRY_SIZE;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:392: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	ld	c, #0x00
00112$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:393: copy_entry_to_disk(payload + (uint16_t)i * HS_ENTRY_SIZE, &campaign_scores[i]);
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ex	de, hl
	ld	iy, #_campaign_scores
	add	iy, de
	ld	e, c
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	de, #(_slot_plain + 544)
	add	hl, de
	push	bc
	push	iy
	pop	de
	call	_copy_entry_to_disk
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:392: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	c
	ld	a, c
	sub	a, #0x0a
	jr	C, 00112$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:395: payload = slot_plain + HS_HEADER_SIZE;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:396: write32(slot_plain + 16, crc32_block(payload, HS_SLOT_SIZE - HS_HEADER_SIZE));
	ld	de, #0x03c0
	ld	hl, #(_slot_plain + 64)
	call	_crc32_block
	push	hl
	push	de
	ld	hl, #(_slot_plain + 16)
	call	_write32
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:397: write32(slot_plain + 20, keyed_tag(payload, HS_SLOT_SIZE - HS_HEADER_SIZE, generation, next_slot));
	ld	a, -10 (ix)
	push	af
	inc	sp
	ld	l, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	l, -9 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x03c0
	ld	hl, #(_slot_plain + 64)
	call	_keyed_tag
	pop	af
	pop	af
	inc	sp
	push	hl
	push	de
	ld	hl, #(_slot_plain + 20)
	call	_write32
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:399: encode_slot(slot_plain, slot_plain, next_slot);
	ld	a, -10 (ix)
	push	af
	inc	sp
	ld	de, #_slot_plain
	ld	hl, #_slot_plain
	call	_encode_slot
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:400: MEM16(HMM2_HsAbiPtr) = (uint16_t)slot_plain;
	ld	hl, #_slot_plain
	ld	(0xb16d), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:401: MEM8(HMM2_HsAbiSlot) = next_slot;
	ld	hl, #0xb16c
	ld	a, -10 (ix)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:402: ABI_CALL(HMM2_HscAbi_WriteHgsSlot);
	call	0xb10e
	ld	iy, #_abi_call_barrier
	inc	0 (iy)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:403: if (MEM8(HMM2_HsAbiStatus) == 0) {
	ld	a, (#0xb16b)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:404: return 0;
	or	a,a
	jr	Z, 00114$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:406: active_slot = next_slot;
	ld	a, -10 (ix)
	ld	(_active_slot+0), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:407: active_generation = generation;
	ld	de, #_active_generation
	ld	hl, #1
	add	hl, sp
	ld	bc, #4
	ldir
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:408: return 1;
	ld	a, #0x01
00114$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:409: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:411: static uint8_t same_completion(const HsEntry * a, const HsEntry * b)
;	---------------------------------
; Function same_completion
; ---------------------------------
_same_completion:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	push	af
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:414: if (a->days != b->days || a->rating != b->rating || a->map_seed != b->map_seed) {
	ld	-2 (ix), l
	ld	-1 (ix), h
	ld	bc,#36
	add	hl,bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	de
	pop	iy
	ld	l, 36 (iy)
;	spillPairReg hl
	ld	h, 37 (iy)
;	spillPairReg hl
	cp	a, a
	sbc	hl, bc
	jr	NZ, 00101$
	ld	c, -2 (ix)
	ld	b, -1 (ix)
	ld	hl, #38
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	push	de
	pop	iy
	ld	l, 38 (iy)
;	spillPairReg hl
	ld	h, 39 (iy)
;	spillPairReg hl
	cp	a, a
	sbc	hl, bc
	jr	NZ, 00101$
	ld	l, -2 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -1 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ex	de, hl
	push	hl
	ld	hl, #2
	add	hl, sp
	ex	de, hl
	ld	bc, #0x002c
	add	hl, bc
	ld	bc, #0x0004
	ldir
	pop	de
	push	de
	pop	iy
	ld	l, 44 (iy)
;	spillPairReg hl
	ld	h, 45 (iy)
;	spillPairReg hl
	ld	c, 46 (iy)
	ld	b, 47 (iy)
	ld	a, l
	sub	a, -6 (ix)
	jr	NZ, 00141$
	ld	a, h
	sub	a, -5 (ix)
	jr	NZ, 00141$
	ld	l, -4 (ix)
	ld	h, -3 (ix)
	cp	a, a
	sbc	hl, bc
	jr	Z, 00115$
00141$:
00101$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:415: return 0;
	xor	a, a
	jp	00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:417: for (i = 0; i < 20; ++i) {
00115$:
	ld	iy, #0x0010
	ld	c, -2 (ix)
	ld	b, -1 (ix)
	add	iy, bc
	ld	hl, #0x0010
	add	hl, de
	ex	de, hl
	ld	c, #0x00
00108$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:418: if (a->scenario[i] != b->scenario[i]) {
	push	iy
	pop	hl
	ld	b, #0x00
	add	hl, bc
	ld	a, c
	add	a, e
	ld	-4 (ix), a
	ld	a, #0x00
	adc	a, d
	ld	-3 (ix), a
	ld	a, (hl)
	ld	l, -4 (ix)
	ld	h, -3 (ix)
	ld	b, (hl)
	sub	a, b
	jr	Z, 00109$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:419: return 0;
	xor	a, a
	jp	00110$
00109$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:417: for (i = 0; i < 20; ++i) {
	inc	c
	ld	a, c
	sub	a, #0x14
	jr	C, 00108$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:422: return 1;
	ld	a, #0x01
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:423: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:425: static uint8_t better_score(const HsEntry * a, const HsEntry * b, uint8_t campaign)
;	---------------------------------
; Function better_score
; ---------------------------------
_better_score:
	push	ix
	ld	ix,#0
	add	ix,sp
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:428: return a->rating < b->rating;
	ld	bc, #0x0026
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	hl, #38
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:427: if (campaign != 0) {
	ld	a, 4 (ix)
	or	a, a
	jr	Z, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:428: return a->rating < b->rating;
	ld	a, c
	sub	a, e
	ld	a, b
	sbc	a, d
	ld	a, #0x00
	rla
	jp	00103$
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:430: return a->rating > b->rating;
	ld	a, e
	sub	a, c
	ld	a, d
	sbc	a, b
	ld	a, #0x00
	rla
00103$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:431: }
	pop	ix
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:433: static int8_t register_score(HsEntry * table, const HsEntry * entry, uint8_t campaign)
;	---------------------------------
; Function register_score
; ---------------------------------
_register_score:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-57
	add	iy, sp
	ld	sp, iy
	ld	-3 (ix), l
	ld	-2 (ix), h
	ld	-5 (ix), e
	ld	-4 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:444: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	ld	-9 (ix), #0x00
	ld	-1 (ix), #0x00
00113$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:445: if (same_completion(&table[i], entry) != 0) {
	ld	c, -1 (ix)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	a, l
	add	a, -3 (ix)
	ld	-8 (ix), a
	ld	a, h
	adc	a, -2 (ix)
	ld	-7 (ix), a
	ld	e, -5 (ix)
	ld	d, -4 (ix)
	ld	l, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_same_completion
	ld	-6 (ix), a
	or	a, a
	jr	Z, 00114$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:446: copy_bytes((uint8_t *)&table[i], (const uint8_t *)entry, sizeof(HsEntry));
	ld	e, -5 (ix)
	ld	d, -4 (ix)
	ld	l, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	bc, #0x0030
	push	bc
	call	_copy_bytes
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:447: save_to_disk();
	call	_save_to_disk
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:448: return (int8_t)i;
	ld	a, -9 (ix)
	jp	00121$
00114$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:444: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	ld	-9 (ix), a
	ld	a, -1 (ix)
	sub	a, #0x0a
	jr	C, 00113$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:452: if (better_score(entry, &table[HS_ENTRY_COUNT - 1], campaign) == 0) {
	ld	a, -3 (ix)
	add	a, #0xb0
	ld	-7 (ix), a
	ld	a, -2 (ix)
	adc	a, #0x01
	ld	-6 (ix), a
	ld	a, 4 (ix)
	push	af
	inc	sp
	ld	e, -7 (ix)
	ld	d, -6 (ix)
	ld	l, -5 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -4 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_better_score
	or	a, a
	jr	NZ, 00105$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:453: return -1;
	ld	a, #0xff
	jp	00121$
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:456: copy_bytes((uint8_t *)&table[HS_ENTRY_COUNT - 1], (const uint8_t *)entry, sizeof(HsEntry));
	ld	e, -5 (ix)
	ld	d, -4 (ix)
	ld	l, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	bc, #0x0030
	push	bc
	call	_copy_bytes
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:457: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	ld	c, #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:458: for (j = 0; j + 1 < HS_ENTRY_COUNT; ++j) {
00128$:
	ld	b, #0x00
00115$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:459: if (better_score(&table[j + 1], &table[j], campaign) != 0) {
	ld	e, b
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	a, l
	add	a, -3 (ix)
	ld	-9 (ix), a
	ld	a, h
	adc	a, -2 (ix)
	ld	-8 (ix), a
	ld	e, b
	ld	d, #0x00
	inc	de
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	a, -3 (ix)
	add	a, l
	ld	-7 (ix), a
	ld	a, -2 (ix)
	adc	a, h
	ld	-6 (ix), a
	push	bc
	ld	a, 4 (ix)
	push	af
	inc	sp
	ld	e, -9 (ix)
	ld	d, -8 (ix)
	ld	l, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_better_score
	pop	bc
	or	a, a
	jr	Z, 00116$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:461: copy_bytes((uint8_t *)&tmp, (const uint8_t *)&table[j], sizeof(HsEntry));
	ld	e, -9 (ix)
	ld	d, -8 (ix)
	push	bc
	ld	hl, #0x0030
	push	hl
	ld	hl, #4
	add	hl, sp
	call	_copy_bytes
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:462: copy_bytes((uint8_t *)&table[j], (const uint8_t *)&table[j + 1], sizeof(HsEntry));
	ld	e, -7 (ix)
	ld	d, -6 (ix)
	ld	l, -9 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	bc
	ld	bc, #0x0030
	push	bc
	call	_copy_bytes
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:463: copy_bytes((uint8_t *)&table[j + 1], (const uint8_t *)&tmp, sizeof(HsEntry));
	ld	l, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	bc
	ld	de, #0x0030
	ex	de, hl
	push	hl
	ld	hl, #4
	add	hl, sp
	ex	de, hl
	call	_copy_bytes
	pop	bc
00116$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:458: for (j = 0; j + 1 < HS_ENTRY_COUNT; ++j) {
	inc	b
	ld	e, b
	ld	d, #0x00
	inc	de
	ld	a, e
	sub	a, #0x0a
	ld	a, d
	rla
	ccf
	rra
	sbc	a, #0x80
	jp	C, 00115$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:457: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	c
	ld	a, c
	sub	a, #0x0a
	jp	C, 00128$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:468: save_to_disk();
	call	_save_to_disk
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:469: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	ld	bc, #0x0
00119$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:470: if (same_completion(&table[i], entry) != 0) {
	ld	e, b
	ld	d, #0x00
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	e, -3 (ix)
	ld	d, -2 (ix)
	add	hl, de
	push	bc
	ld	e, -5 (ix)
	ld	d, -4 (ix)
	call	_same_completion
	pop	bc
	or	a, a
	jr	Z, 00120$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:471: return (int8_t)i;
	ld	a, c
	jp	00121$
00120$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:469: for (i = 0; i < HS_ENTRY_COUNT; ++i) {
	inc	b
	ld	c, b
	ld	a, b
	sub	a, #0x0a
	jr	C, 00119$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:474: return -1;
	ld	a, #0xff
00121$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:475: }
	ld	sp, ix
	pop	ix
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:477: static void init_scale_tables(void)
;	---------------------------------
; Function init_scale_tables
; ---------------------------------
_init_scale_tables:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-6
	add	hl, sp
	ld	sp, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:480: uint16_t px_value = 0;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:481: uint16_t vertex_base = 0;
	ld	bc, #0x0000
	ld	d, b
	ld	e, c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:483: uint8_t px_remainder = 4;
	ld	-4 (ix), #0x04
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:484: uint8_t vertex_extra_remainder = 2;
	ld	-3 (ix), #0x02
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:486: if (scale_tables_ready != 0) {
	ld	a, (_scale_tables_ready+0)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:487: return;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:490: for (i = 0; i <= HS_SCALE_TABLE_MAX; ++i) {
	or	a,a
	jp	NZ,00112$
	ld	-2 (ix), a
	ld	-1 (ix), a
	ld	iy, #0x0000
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:491: scale_px_table[i] = px_value;
	inc	sp
	inc	sp
	push	iy
	sla	-6 (ix)
	rl	-5 (ix)
	ld	a, -6 (ix)
	add	a, #<(_scale_px_table)
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -5 (ix)
	adc	a, #>(_scale_px_table)
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	(hl), c
	inc	hl
	ld	(hl), b
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:492: scale_vertex_table[i] = (uint16_t)(vertex_base + vertex_extra);
	ld	a, -6 (ix)
	add	a, #<(_scale_vertex_table)
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -5 (ix)
	adc	a, #>(_scale_vertex_table)
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -2 (ix)
	add	a, e
	ld	-6 (ix), a
	ld	a, -1 (ix)
	adc	a, d
	ld	-5 (ix), a
	ld	a, -6 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -5 (ix)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:494: px_remainder = (uint8_t)(px_remainder + 8U);
	ld	a, -4 (ix)
	add	a, #0x08
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:495: if (px_remainder >= 5U) {
	ld	-4 (ix), a
	sub	a, #0x05
	jr	C, 00104$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:496: px_remainder = (uint8_t)(px_remainder - 5U);
	ld	a, -4 (ix)
	add	a, #0xfb
	ld	-4 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:497: ++px_value;
	inc	bc
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:499: if (px_remainder >= 5U) {
	ld	a, -4 (ix)
	sub	a, #0x05
	jr	C, 00106$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:500: px_remainder = (uint8_t)(px_remainder - 5U);
	ld	a, -4 (ix)
	add	a, #0xfb
	ld	-4 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:501: ++px_value;
	inc	bc
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:504: vertex_base = (uint16_t)(vertex_base + 25U);
	ld	hl, #0x0019
	add	hl, de
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:505: vertex_extra_remainder = (uint8_t)(vertex_extra_remainder + 3U);
	inc	-3 (ix)
	inc	-3 (ix)
	inc	-3 (ix)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:506: if (vertex_extra_remainder >= 5U) {
	ld	a, -3 (ix)
	sub	a, #0x05
	jr	C, 00111$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:507: vertex_extra_remainder = (uint8_t)(vertex_extra_remainder - 5U);
	ld	a, -3 (ix)
	add	a, #0xfb
	ld	-3 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:508: ++vertex_extra;
	inc	-2 (ix)
	jr	NZ, 00146$
	inc	-1 (ix)
00146$:
00111$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:490: for (i = 0; i <= HS_SCALE_TABLE_MAX; ++i) {
	inc	iy
	push	iy
	pop	hl
	ld	a, #0x80
	cp	a, l
	ld	a, #0x02
	sbc	a, h
	jp	NC, 00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:512: scale_tables_ready = 1;
	ld	hl, #_scale_tables_ready
	ld	(hl), #0x01
00112$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:513: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:515: static void set_palette(uint16_t lo, uint8_t hi)
;	---------------------------------
; Function set_palette
; ---------------------------------
_set_palette:
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:517: MEM16(HMM2_HsAbiAddrLo) = lo;
	ld	(0xb16f), de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:518: MEM8(HMM2_HsAbiAddrHi) = hi;
	ld	hl, #0xb171
	ld	iy, #2
	add	iy, sp
	ld	a, 0 (iy)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:519: ABI_CALL(HMM2_HscAbi_SetPalette);
	call	0xaf0d
	ld	iy, #_abi_call_barrier
	inc	0 (iy)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:520: }
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:522: static void set_game_mode(uint8_t mode)
;	---------------------------------
; Function set_game_mode
; ---------------------------------
_set_game_mode:
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:524: MEM8(HMM2_HsAbiMode) = mode;
	ld	hl, #0xb184
	ld	(hl), c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:525: ABI_CALL(HMM2_HscAbi_SetGameMode);
	call	0xb0a8
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:526: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:528: static void emit_sprite_current(const HsSprite * sprite)
;	---------------------------------
; Function emit_sprite_current
; ---------------------------------
_emit_sprite_current:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-8
	add	iy, sp
	ld	sp, iy
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:531: int16_t x = sprite_base_x + sprite->x;
	ld	c, e
	ld	b, d
	ld	hl, #7
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	a, (_sprite_base_x+0)
	add	a, c
	ld	c, a
	ld	a, (_sprite_base_x+1)
	adc	a, b
	ld	b, a
	inc	sp
	inc	sp
	push	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:532: int16_t y = sprite_base_y + sprite->y;
	ld	c, e
	ld	b, d
	ld	hl, #9
	add	hl, bc
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	iy, (_sprite_base_y)
	add	iy, bc
	push	iy
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:533: uint16_t w = sprite->w;
	push	de
	pop	iy
	ld	a, 3 (iy)
	ld	-6 (ix), a
	ld	a, 4 (iy)
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:534: uint16_t h = sprite->h;
	push	de
	pop	iy
	ld	a, 5 (iy)
	ld	-4 (ix), a
	ld	a, 6 (iy)
	ld	-3 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:537: MEM16(HMM2_HsAbiAddrLo) = sprite->lo;
	ld	a, (de)
	ld	-2 (ix), a
	inc	de
	ld	a, (de)
	ld	-1 (ix), a
	dec	de
	ld	hl, #0xb16f
	ld	a, -2 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -1 (ix)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:538: MEM8(HMM2_HsAbiAddrHi) = sprite->hi;
	inc	de
	inc	de
	ld	a, (de)
	ld	l, #0x71
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:539: MEM16(HMM2_HsAbiW) = w;
	ld	l, #0x72
	ld	a, -6 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -5 (ix)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:540: MEM16(HMM2_HsAbiH) = h;
	ld	l, #0x74
	ld	a, -4 (ix)
	ld	(hl), a
	inc	hl
	ld	a, -3 (ix)
	ld	(hl), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:542: scale_index = w;
	ld	e, -6 (ix)
	ld	d, -5 (ix)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:543: if (scale_index > HS_SCALE_TABLE_MAX) {
	ld	l, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -5 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	a, #0x80
	cp	a, l
	ld	a, #0x02
	sbc	a, h
	jr	NC, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:544: scale_index = HS_SCALE_TABLE_MAX;
	ld	de, #0x0280
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:546: MEM16(HMM2_HsAbiSizeW) = scale_px_table[scale_index];
	ex	de, hl
	add	hl, hl
	ld	de, #_scale_px_table
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	(0xb176), de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:548: scale_index = h;
	ld	e, -4 (ix)
	ld	d, -3 (ix)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:549: if (scale_index > HS_SCALE_TABLE_MAX) {
	ld	l, -4 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -3 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	a, #0x80
	cp	a, l
	ld	a, #0x02
	sbc	a, h
	jr	NC, 00104$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:550: scale_index = HS_SCALE_TABLE_MAX;
	ld	de, #0x0280
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:552: MEM16(HMM2_HsAbiSizeH) = scale_px_table[scale_index];
	ex	de, hl
	add	hl, hl
	ld	de, #_scale_px_table
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	(0xb178), de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:554: if (x <= 0) {
	pop	de
	push	de
	xor	a, a
	cp	a, e
	sbc	a, d
	jp	PO, 00150$
	xor	a, #0x80
00150$:
	jp	M, 00108$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:555: MEM16(HMM2_HsAbiVX) = 0;
	ld	hl, #0x0000
	ld	(0xb17a), hl
	jp	00109$
00108$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:558: scale_index = (uint16_t)x;
	pop	de
	push	de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:559: if (scale_index > HS_SCALE_TABLE_MAX) {
	ld	l, e
;	spillPairReg hl
;	spillPairReg hl
	ld	h, d
;	spillPairReg hl
;	spillPairReg hl
	ld	a, #0x80
	cp	a, l
	ld	a, #0x02
	sbc	a, h
	jr	NC, 00106$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:560: scale_index = HS_SCALE_TABLE_MAX;
	ld	de, #0x0280
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:562: MEM16(HMM2_HsAbiVX) = scale_vertex_table[scale_index];
	ex	de, hl
	add	hl, hl
	ld	de, #_scale_vertex_table
	add	hl, de
	ld	e, (hl)
	inc	hl
	ld	d, (hl)
	ld	(0xb17a), de
00109$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:565: if (y <= 0) {
	ld	e, c
	ld	d, b
	xor	a, a
	cp	a, e
	sbc	a, d
	jp	PO, 00151$
	xor	a, #0x80
00151$:
	jp	M, 00113$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:566: MEM16(HMM2_HsAbiVY) = 0;
	ld	hl, #0x0000
	ld	(0xb17c), hl
	jp	00115$
00113$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:569: scale_index = (uint16_t)y;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:570: if (scale_index > HS_SCALE_TABLE_MAX) {
	ld	e, c
	ld	d, b
	ld	a, #0x80
	cp	a, e
	ld	a, #0x02
	sbc	a, d
	jr	NC, 00111$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:571: scale_index = HS_SCALE_TABLE_MAX;
	ld	bc, #0x0280
00111$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:573: MEM16(HMM2_HsAbiVY) = scale_vertex_table[scale_index];
	ld	de, #_scale_vertex_table+0
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, de
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	ld	(0xb17c), bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:575: ABI_CALL(HMM2_HscAbi_EmitSprite);
00115$:
	call	0xaf2c
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:576: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:584: static void emit_sprite_array(const HsSprite * sprites, uint8_t count)
;	---------------------------------
; Function emit_sprite_array
; ---------------------------------
_emit_sprite_array:
	push	ix
	ld	ix,#0
	add	ix,sp
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:587: for (i = 0; i < count; ++i) {
	ld	c, #0x00
00106$:
	ld	a, c
	sub	a, 4 (ix)
	jr	NC, 00108$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:588: emit_sprite_at(&sprites[i], 0, 0);
	ld	hl, #0x0000
	ld	(_sprite_base_x), hl
	ld	(_sprite_base_y), hl
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, de
	push	bc
	push	de
	call	_emit_sprite_current
	pop	de
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:587: for (i = 0; i < count; ++i) {
	inc	c
	jp	00106$
00108$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:590: }
	pop	ix
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:592: static uint16_t text_width(const char * text, uint16_t max_chars)
;	---------------------------------
; Function text_width
; ---------------------------------
_text_width:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	ld	-2 (ix), l
	ld	-1 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:594: uint16_t width = 0;
	ld	hl, #0x0000
	ex	(sp), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:595: while (*text != 0 && max_chars != 0) {
00105$:
	ld	l, -2 (ix)
	ld	h, -1 (ix)
	ld	c, (hl)
	ld	a, c
	or	a, a
	jr	Z, 00107$
	ld	a, d
	or	a, e
	jr	Z, 00107$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:596: uint8_t ch = (uint8_t)*text++;
	inc	-2 (ix)
	jr	NZ, 00131$
	inc	-1 (ix)
00131$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:597: if (ch < 32 || ch > 126) {
	ld	a, c
	sub	a, #0x20
	jr	C, 00101$
	ld	a, #0x7e
	sub	a, c
	jr	NC, 00102$
00101$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:598: ch = '?';
	ld	c, #0x3f
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:600: width += hs_glyphs[ch - 32].adv;
	ld	a, c
	ld	c, #0x00
	add	a, #0xe0
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, c
	adc	a, #0xff
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	c, l
	ld	b, h
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	ld	bc, #_hs_glyphs
	add	hl, bc
	ld	bc, #0x0008
	add	hl, bc
	ld	c, (hl)
	ld	b, #0x00
	pop	hl
	push	hl
	add	hl, bc
	ex	(sp), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:601: --max_chars;
	dec	de
	jp	00105$
00107$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:603: return width;
	pop	de
	push	de
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:604: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:606: static void draw_text_fit(const char * text, int16_t x, int16_t y, uint16_t max_width, uint8_t yellow)
;	---------------------------------
; Function draw_text_fit
; ---------------------------------
_draw_text_fit:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-25
	add	iy, sp
	ld	sp, iy
	ld	-4 (ix), l
	ld	-3 (ix), h
	ld	-6 (ix), e
	ld	-5 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:609: uint16_t used = 0;
	xor	a, a
	ld	-14 (ix), a
	ld	-13 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:611: while (*text != 0 && chars_left != 0) {
	ld	a, 4 (ix)
	ld	-12 (ix), a
	ld	a, 5 (ix)
	ld	-11 (ix), a
	ld	-2 (ix), #0x28
	ld	-1 (ix), #0
00112$:
	ld	l, -4 (ix)
	ld	h, -3 (ix)
	ld	c, (hl)
	ld	a, c
	or	a, a
	jp	Z, 00115$
	ld	a, -1 (ix)
	or	a, -2 (ix)
	jp	Z, 00115$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:614: uint8_t ch = (uint8_t)*text++;
	inc	-4 (ix)
	jr	NZ, 00162$
	inc	-3 (ix)
00162$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:615: if (ch < 32 || ch > 126) {
	ld	a, c
	sub	a, #0x20
	jr	C, 00101$
	ld	a, #0x7e
	sub	a, c
	jr	NC, 00102$
00101$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:616: ch = '?';
	ld	c, #0x3f
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:618: glyph = &hs_glyphs[ch - 32];
	ld	e, c
	ld	d, #0x00
	ld	a, e
	add	a, #0xe0
	ld	e, a
	ld	a, d
	adc	a, #0xff
	ld	d, a
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, de
	add	hl, hl
	ld	de, #_hs_glyphs
	add	hl, de
	ex	de, hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:619: if (used + glyph->adv > max_width) {
	ld	hl, #0x0008
	add	hl, de
	ld	-10 (ix), l
	ld	-9 (ix), h
	ld	l, (hl)
;	spillPairReg hl
	ld	h, #0x00
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -14 (ix)
	ld	-8 (ix), a
	ld	a, -13 (ix)
	ld	-7 (ix), a
	ld	a, -8 (ix)
	add	a, l
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, -7 (ix)
	adc	a, h
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, 6 (ix)
	sub	a, l
	ld	a, 7 (ix)
	sbc	a, h
	jp	C, 00115$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:622: if (ch != ' ') {
	ld	a, c
	sub	a, #0x20
	jp	Z,00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:623: glyph_sprite.lo = yellow ? glyph->yellow_lo : glyph->white_lo;
	ld	a, 8 (ix)
	or	a, a
	jr	Z, 00117$
	ld	l, e
;	spillPairReg hl
;	spillPairReg hl
	ld	h, d
;	spillPairReg hl
;	spillPairReg hl
	inc	hl
	inc	hl
	inc	hl
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
	jp	00118$
00117$:
	ld	l, e
	ld	h, d
	ld	c, (hl)
	inc	hl
	ld	b, (hl)
00118$:
	inc	sp
	inc	sp
	push	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:624: glyph_sprite.hi = yellow ? glyph->yellow_hi : glyph->white_hi;
	ld	a, 8 (ix)
	or	a, a
	jr	Z, 00119$
	ld	c, e
	ld	b, d
	ld	hl, #5
	add	hl, bc
	ld	a, (hl)
	jp	00120$
00119$:
	ld	c, e
	ld	b, d
	inc	bc
	inc	bc
	ld	a, (bc)
00120$:
	ld	-23 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:625: glyph_sprite.w = glyph->w;
	ld	c, e
	ld	b, d
	ld	hl, #6
	add	hl, bc
	ld	c, (hl)
	ld	b, #0x00
	ld	-22 (ix), c
	ld	-21 (ix), b
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:626: glyph_sprite.h = glyph->h;
	ld	c, e
	ld	b, d
	ld	hl, #7
	add	hl, bc
	ld	c, (hl)
	ld	b, #0x00
	ld	-20 (ix), c
	ld	-19 (ix), b
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:627: glyph_sprite.x = (int16_t)used;
	ld	c, -14 (ix)
	ld	b, -13 (ix)
	ld	-18 (ix), c
	ld	-17 (ix), b
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:628: glyph_sprite.y = glyph->y;
	ld	hl, #9
	add	hl, de
	ld	a, (hl)
	ld	c, a
	rlca
	sbc	a, a
	ld	b, a
	ld	-16 (ix), c
	ld	-15 (ix), b
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:629: emit_sprite_at(&glyph_sprite, x, y);
	ld	l, -6 (ix)
	ld	h, -5 (ix)
	ld	(_sprite_base_x), hl
	ld	l, -12 (ix)
	ld	h, -11 (ix)
	ld	(_sprite_base_y), hl
	ld	hl, #0
	add	hl, sp
	call	_emit_sprite_current
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:631: used += glyph->adv;
	ld	l, -10 (ix)
	ld	h, -9 (ix)
	ld	c, (hl)
	ld	b, #0x00
	ld	l, -8 (ix)
	ld	h, -7 (ix)
	add	hl, bc
	ld	-14 (ix), l
	ld	-13 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:632: --chars_left;
	ld	l, -2 (ix)
	ld	h, -1 (ix)
	dec	hl
	ld	-2 (ix), l
	ld	-1 (ix), h
	jp	00112$
00115$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:634: }
	ld	sp, ix
	pop	ix
	pop	hl
	pop	af
	pop	af
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:636: static void u16_to_text(uint16_t value, char * out)
;	---------------------------------
; Function u16_to_text
; ---------------------------------
_u16_to_text:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
	push	af
	ld	c, l
	ld	b, h
	ld	-2 (ix), e
	ld	-1 (ix), d
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:640: uint8_t started = 0;
	ld	e, #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:642: if (value == 0) {
	ld	a, b
	or	a, c
	jr	NZ, 00118$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:643: out[0] = '0';
	ld	l, -2 (ix)
	ld	h, -1 (ix)
	ld	(hl), #0x30
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:644: out[1] = 0;
	ld	c, -2 (ix)
	ld	b, -1 (ix)
	inc	bc
	xor	a, a
	ld	(bc), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:645: return;
	jp	00112$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:648: for (i = 0; i < 4; ++i) {
00118$:
	ld	a, -2 (ix)
	ld	-4 (ix), a
	ld	a, -1 (ix)
	ld	-3 (ix), a
	ld	-2 (ix), #0x00
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:650: uint16_t divisor = divisors[i];
	ld	l, -2 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, #0x00
;	spillPairReg hl
;	spillPairReg hl
	add	hl, hl
	push	de
	ld	de, #_u16_to_text_divisors_65536_144
	add	hl, de
	pop	de
	ld	a, (hl)
	ld	-6 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:651: while (value >= divisor) {
	ld	-1 (ix), #0x00
00103$:
	ld	a, c
	sub	a, -6 (ix)
	ld	a, b
	sbc	a, -5 (ix)
	jr	C, 00120$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:652: value = (uint16_t)(value - divisor);
	ld	a, c
	sub	a, -6 (ix)
	ld	c, a
	ld	a, b
	sbc	a, -5 (ix)
	ld	b, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:653: ++digit;
	inc	-1 (ix)
	jp	00103$
00120$:
	ld	a, -1 (ix)
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:655: if (digit != 0 || started != 0) {
	ld	a, -1 (ix)
	or	a,a
	jr	NZ, 00106$
	or	a,e
	jr	Z, 00111$
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:656: *out++ = (char)('0' + digit);
	ld	a, -5 (ix)
	add	a, #0x30
	pop	de
	pop	hl
	push	hl
	push	de
	ld	(hl), a
	inc	-4 (ix)
	jr	NZ, 00146$
	inc	-3 (ix)
00146$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:657: started = 1;
	ld	e, #0x01
00111$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:648: for (i = 0; i < 4; ++i) {
	inc	-2 (ix)
	ld	a, -2 (ix)
	sub	a, #0x04
	jr	C, 00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:661: *out++ = (char)('0' + (uint8_t)value);
	ld	a, c
	add	a, #0x30
	pop	bc
	pop	hl
	push	hl
	push	bc
	ld	(hl), a
	ld	c, -4 (ix)
	ld	b, -3 (ix)
	inc	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:662: *out = 0;
	xor	a, a
	ld	(bc), a
00112$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:663: }
	ld	sp, ix
	pop	ix
	ret
_u16_to_text_divisors_65536_144:
	.dw #0x2710
	.dw #0x03e8
	.dw #0x0064
	.dw #0x000a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:665: static uint8_t mod15_u8(uint8_t value)
;	---------------------------------
; Function mod15_u8
; ---------------------------------
_mod15_u8:
	ld	b, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:667: value = (uint8_t)((value >> 4) + (value & 0x0F));
	ld	c, b
	srl	c
	srl	c
	srl	c
	srl	c
	ld	a, b
	and	a, #0x0f
	add	a, c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:668: if (value >= 15U) {
	cp	a, #0x0f
	jr	C, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:669: value = (uint8_t)(value - 15U);
	add	a, #0xf1
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:671: if (value >= 15U) {
	cp	a, #0x0f
	ret	C
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:672: value = (uint8_t)(value - 15U);
	add	a, #0xf1
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:674: return value;
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:675: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:677: static uint8_t monster_by_rating(uint16_t rating)
;	---------------------------------
; Function monster_by_rating
; ---------------------------------
_monster_by_rating:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-7
	add	iy, sp
	ld	sp, iy
	ld	-3 (ix), l
	ld	-2 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:680: uint16_t threshold = 0;
	ld	hl, #0x0000
	ex	(sp), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:681: uint8_t step = 0;
	ld	-5 (ix), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:683: for (i = 0; i < HS_MONSTER_RANKING_COUNT; ++i) {
	ld	-1 (ix), #0x00
00115$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:684: uint8_t monster = hs_monster_ids[i];
	ld	a, -1 (ix)
	add	a, #<(_hs_monster_ids)
	ld	c, a
	ld	a, #0x00
	adc	a, #>(_hs_monster_ids)
	ld	b, a
	ld	a, (bc)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:685: if (monster == 1) {
	ld	-4 (ix), a
	dec	a
	jr	NZ, 00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:686: step = 3;
	ld	-5 (ix), #0x03
	jp	00111$
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:688: else if (monster == 12) {
	ld	a, -4 (ix)
	sub	a, #0x0c
	jr	NZ, 00107$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:689: step = 4;
	ld	-5 (ix), #0x04
	jp	00111$
00107$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:691: else if (monster == 27) {
	ld	a, -4 (ix)
	sub	a, #0x1b
	jr	NZ, 00104$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:692: step = 3;
	ld	-5 (ix), #0x03
	jp	00111$
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:694: else if (monster == 38) {
	ld	a, -4 (ix)
	sub	a, #0x26
	jr	NZ, 00111$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:695: step = 1;
	ld	-5 (ix), #0x01
00111$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:697: threshold += step;
	ld	c, -5 (ix)
	ld	b, #0x00
	pop	hl
	push	hl
	add	hl, bc
	ex	(sp), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:698: if (rating <= threshold) {
	ld	a, -7 (ix)
	sub	a, -3 (ix)
	ld	a, -6 (ix)
	sbc	a, -2 (ix)
	jr	C, 00116$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:699: return monster;
	ld	a, -4 (ix)
	jp	00117$
00116$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:683: for (i = 0; i < HS_MONSTER_RANKING_COUNT; ++i) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x42
	jr	C, 00115$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:702: return hs_monster_ids[HS_MONSTER_RANKING_COUNT - 1];
	ld	a, (#_hs_monster_ids + 65)
00117$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:703: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:705: static uint8_t monster_by_day(uint16_t days)
;	---------------------------------
; Function monster_by_day
; ---------------------------------
_monster_by_day:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-7
	add	iy, sp
	ld	sp, iy
	ld	-4 (ix), l
	ld	-3 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:708: uint16_t threshold = 0;
	xor	a, a
	ld	-2 (ix), a
	ld	-1 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:709: uint16_t step = 0;
	ld	hl, #0x0000
	ex	(sp), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:711: for (i = HS_MONSTER_RANKING_COUNT - 1; i >= 0; --i) {
	ld	c, #0x41
00118$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:712: uint8_t monster = hs_monster_ids[(uint8_t)i];
	ld	e, c
	ld	hl, #_hs_monster_ids
	ld	d, #0x00
	add	hl, de
	ld	a, (hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:713: if (monster == 38) {
	ld	-5 (ix), a
	sub	a, #0x26
	jr	NZ, 00113$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:714: step = 300;
	ld	hl, #0x012c
	ex	(sp), hl
	jp	00114$
00113$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:716: else if (monster == 47) {
	ld	a, -5 (ix)
	sub	a, #0x2f
	jr	NZ, 00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:717: step = 20;
	ld	hl, #0x0014
	ex	(sp), hl
	jp	00114$
00110$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:719: else if (monster == 26) {
	ld	a, -5 (ix)
	sub	a, #0x1a
	jr	NZ, 00107$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:720: step = 100;
	ld	hl, #0x0064
	ex	(sp), hl
	jp	00114$
00107$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:722: else if (monster == 23) {
	ld	a, -5 (ix)
	sub	a, #0x17
	jr	NZ, 00104$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:723: step = 200;
	ld	hl, #0x00c8
	ex	(sp), hl
	jp	00114$
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:725: else if (monster == 1) {
	ld	a, -5 (ix)
	dec	a
	jr	NZ, 00114$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:726: step = 1;
	ld	hl, #0x0001
	ex	(sp), hl
00114$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:728: threshold += step;
	ld	a, -2 (ix)
	add	a, -7 (ix)
	ld	-2 (ix), a
	ld	a, -1 (ix)
	adc	a, -6 (ix)
	ld	-1 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:729: if (days <= threshold) {
	ld	a, -2 (ix)
	sub	a, -4 (ix)
	ld	a, -1 (ix)
	sbc	a, -3 (ix)
	jr	C, 00119$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:730: return monster;
	ld	a, -5 (ix)
	jp	00120$
00119$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:711: for (i = HS_MONSTER_RANKING_COUNT - 1; i >= 0; --i) {
	dec	c
	bit	7, c
	jr	Z, 00118$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:733: return 1;
	ld	a, #0x01
00120$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:734: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:736: static uint8_t monster_rank_index(uint8_t monster_id)
;	---------------------------------
; Function monster_rank_index
; ---------------------------------
_monster_rank_index:
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:739: for (i = 0; i < HS_MONSTER_RANKING_COUNT; ++i) {
	ld	b, #0x00
	ld	e, b
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:740: if (hs_monster_ids[i] == monster_id) {
	ld	hl, #_hs_monster_ids
	ld	d, #0x00
	add	hl, de
	ld	a, (hl)
	sub	a, c
	jr	NZ, 00105$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:741: return i;
	ld	a, b
	ret
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:739: for (i = 0; i < HS_MONSTER_RANKING_COUNT; ++i) {
	inc	e
	ld	a,e
	ld	b,a
	sub	a, #0x42
	jr	C, 00104$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:744: return 0;
	xor	a, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:745: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:747: static void render_rows(const HsEntry * table, uint8_t campaign)
;	---------------------------------
; Function render_rows
; ---------------------------------
_render_rows:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	iy, #-24
	add	iy, sp
	ld	sp, iy
	ld	-3 (ix), l
	ld	-2 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:752: for (row = 0; row < HS_ENTRY_COUNT; ++row) {
	ld	-1 (ix), #0x00
00108$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:753: int16_t y = ROW_Y + (int16_t)row * ROW_STEP;
	ld	a, -1 (ix)
	ld	-5 (ix), a
	ld	-4 (ix), #0x00
	ld	c, a
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	-16 (ix), l
	ld	-15 (ix), h
	ld	a, -16 (ix)
	add	a, #0x48
	ld	-5 (ix), a
	ld	a, -15 (ix)
	adc	a, #0x00
	ld	-4 (ix), a
	ld	a, -5 (ix)
	ld	-14 (ix), a
	ld	a, -4 (ix)
	ld	-13 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:755: uint8_t monster_id = campaign ? monster_by_day(table[row].rating) : monster_by_rating(table[row].rating);
	ld	c, -1 (ix)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, hl
	ld	-5 (ix), l
	ld	-4 (ix), h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:757: uint8_t phase = monster_animation_sequence[mod15_u8((uint8_t)(y + table[row].days + animation_frame))];
	ld	a, -3 (ix)
	add	a, -5 (ix)
	ld	-12 (ix), a
	ld	a, -2 (ix)
	adc	a, -4 (ix)
	ld	-11 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:755: uint8_t monster_id = campaign ? monster_by_day(table[row].rating) : monster_by_rating(table[row].rating);
	ld	a, -12 (ix)
	add	a, #0x26
	ld	-10 (ix), a
	ld	a, -11 (ix)
	adc	a, #0x00
	ld	-9 (ix), a
	ld	l, -10 (ix)
	ld	h, -9 (ix)
	ld	a, (hl)
	ld	-5 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-4 (ix), a
	ld	a, 4 (ix)
	or	a, a
	jr	Z, 00112$
	ld	l, -5 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -4 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_monster_by_day
	jp	00113$
00112$:
	ld	l, -5 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -4 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_monster_by_rating
00113$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:756: uint8_t rank = monster_rank_index(monster_id);
	call	_monster_rank_index
	ld	-5 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:757: uint8_t phase = monster_animation_sequence[mod15_u8((uint8_t)(y + table[row].days + animation_frame))];
	ld	a, -14 (ix)
	ld	-6 (ix), a
	ld	a, -12 (ix)
	add	a, #0x24
	ld	-8 (ix), a
	ld	a, -11 (ix)
	adc	a, #0x00
	ld	-7 (ix), a
	ld	l, -8 (ix)
	ld	h, -7 (ix)
	ld	a, (hl)
	ld	-4 (ix), a
	add	a, -6 (ix)
	ld	-6 (ix), a
	ld	a, (_animation_frame+0)
	ld	-4 (ix), a
	add	a, -6 (ix)
	ld	-4 (ix), a
	call	_mod15_u8
	ld	c, a
	ld	hl, #_monster_animation_sequence
	ld	b, #0x00
	add	hl, bc
	ld	a, (hl)
	ld	-4 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:759: draw_text_fit(table[row].player, COL_PLAYER, y, COL_SCENARIO - COL_PLAYER - 4, yellow);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0x0098
	push	hl
	ld	l, -14 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -13 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x0058
	ld	l, -12 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -11 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_draw_text_fit
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:760: draw_text_fit(table[row].scenario, COL_SCENARIO, y, COL_DAYS - COL_SCENARIO - 4, yellow);
	ld	a, -12 (ix)
	add	a, #0x10
	ld	-24 (ix), a
	ld	a, -11 (ix)
	adc	a, #0x00
	ld	-23 (ix), a
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0x009b
	push	hl
	ld	l, -14 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -13 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x00f4
	ld	l, -24 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -23 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_draw_text_fit
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:761: u16_to_text(table[row].days, num);
	ld	l, -8 (ix)
	ld	h, -7 (ix)
	ld	a, (hl)
	ld	-12 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-11 (ix), a
	ld	hl, #2
	add	hl, sp
	ex	de, hl
	ld	l, -12 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -11 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_u16_to_text
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:762: draw_text_fit(num, COL_DAYS, y, COL_RATING - COL_DAYS - 4, yellow);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0x004d
	push	hl
	ld	l, -14 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -13 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x0193
	ld	hl, #7
	add	hl, sp
	call	_draw_text_fit
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:763: u16_to_text(table[row].rating, num);
	ld	l, -10 (ix)
	ld	h, -9 (ix)
	ld	a, (hl)
	ld	-7 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-6 (ix), a
	ld	hl, #2
	add	hl, sp
	ex	de, hl
	ld	l, -7 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -6 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_u16_to_text
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:764: draw_text_fit(num, COL_RATING, y, COL_MONSTER_X - COL_RATING - 4, yellow);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0x0042
	push	hl
	ld	l, -14 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -13 (ix)
;	spillPairReg hl
;	spillPairReg hl
	push	hl
	ld	de, #0x01e4
	ld	hl, #7
	add	hl, sp
	call	_draw_text_fit
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:766: emit_sprite_at(&hs_monsters[rank][0], COL_MONSTER_X, COL_MONSTER_Y + (int16_t)row * ROW_STEP);
	ld	hl, #0x022a
	ld	(_sprite_base_x), hl
	ld	a, -16 (ix)
	add	a, #0x5b
	ld	-7 (ix), a
	ld	a, -15 (ix)
	adc	a, #0x00
	ld	-6 (ix), a
	ld	l, -7 (ix)
	ld	h, -6 (ix)
	ld	(_sprite_base_y), hl
	ld	c, -5 (ix)
	ld	b, #0x00
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, hl
	add	hl, bc
	ld	-9 (ix), l
	ld	-8 (ix), h
	ld	a, -9 (ix)
	add	a, #<(_hs_monsters)
	ld	-11 (ix), a
	ld	a, -8 (ix)
	adc	a, #>(_hs_monsters)
	ld	-10 (ix), a
	ld	a, -11 (ix)
	ld	-9 (ix), a
	ld	a, -10 (ix)
	ld	-8 (ix), a
	ld	l, -9 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -8 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_emit_sprite_current
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:767: emit_sprite_at(&hs_monsters[rank][1 + phase], COL_MONSTER_X, COL_MONSTER_Y + (int16_t)row * ROW_STEP);
	ld	hl, #0x022a
	ld	(_sprite_base_x), hl
	ld	l, -7 (ix)
	ld	h, -6 (ix)
	ld	(_sprite_base_y), hl
	ld	a, -4 (ix)
	inc	a
	ld	c, a
	add	a, a
	add	a, c
	add	a, a
	add	a, a
	sub	a, c
	add	a, -11 (ix)
	ld	-5 (ix), a
	ld	a, #0x00
	adc	a, -10 (ix)
	ld	-4 (ix), a
	ld	l, -5 (ix)
;	spillPairReg hl
;	spillPairReg hl
	ld	h, -4 (ix)
;	spillPairReg hl
;	spillPairReg hl
	call	_emit_sprite_current
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:752: for (row = 0; row < HS_ENTRY_COUNT; ++row) {
	inc	-1 (ix)
	ld	a, -1 (ix)
	sub	a, #0x0a
	jp	C, 00108$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:769: }
	ld	sp, ix
	pop	ix
	pop	hl
	inc	sp
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:771: static void render_screen(void)
;	---------------------------------
; Function render_screen
; ---------------------------------
_render_screen:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:774: ABI_CALL(HMM2_HscAbi_RenderBegin);
	call	0xaea2
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:775: set_palette(HS_OPAQUE_PAL_LO, HS_OPAQUE_PAL_HI);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0x0200
	call	_set_palette
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:776: emit_sprite_array(hs_bg, HS_BG_COUNT);
	ld	a, #0x06
	push	af
	inc	sp
	ld	hl, #_hs_bg
	call	_emit_sprite_array
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:777: set_palette(HS_TRANSPARENT_PAL_LO, HS_TRANSPARENT_PAL_HI);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #0x0000
	call	_set_palette
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:779: if (is_campaign != 0) {
	ld	a, (_is_campaign+0)
	or	a, a
	jr	Z, 00105$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:780: emit_sprite_array(hs_title_campaign, HS_TITLE_CAMPAIGN_COUNT);
	ld	a, #0x02
	push	af
	inc	sp
	ld	hl, #_hs_title_campaign
	call	_emit_sprite_array
	jp	00106$
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:783: emit_sprite_array(hs_title_standard, HS_TITLE_STANDARD_COUNT);
	ld	a, #0x02
	push	af
	inc	sp
	ld	hl, #_hs_title_standard
	call	_emit_sprite_array
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:786: render_rows(is_campaign ? campaign_scores : standard_scores, is_campaign);
	ld	a, (_is_campaign+0)
	or	a, a
	jr	Z, 00124$
	ld	de, #_campaign_scores+0
	jp	00125$
00124$:
	ld	de, #_standard_scores+0
00125$:
	ld	a, (_is_campaign+0)
	push	af
	inc	sp
	ex	de, hl
	call	_render_rows
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:788: if (is_campaign != 0) {
	ld	a, (_is_campaign+0)
	or	a, a
	jr	Z, 00110$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:789: emit_sprite_at(&hs_button_campaign[pressed_other ? 1 : 0], 0, 0);
	ld	hl, #0x0000
	ld	(_sprite_base_x), hl
	ld	(_sprite_base_y), hl
	ld	bc, #_hs_button_campaign+0
	ld	a, (_pressed_other+0)
	or	a, a
	jr	Z, 00126$
	ld	de, #0x0001
	jp	00127$
00126$:
	ld	de, #0x0000
00127$:
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, bc
	call	_emit_sprite_current
	jp	00116$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:792: emit_sprite_at(&hs_button_standard[pressed_other ? 1 : 0], 0, 0);
00110$:
	ld	hl, #0x0000
	ld	(_sprite_base_x), hl
	ld	(_sprite_base_y), hl
	ld	bc, #_hs_button_standard+0
	ld	a, (_pressed_other+0)
	or	a, a
	jr	Z, 00128$
	ld	de, #0x0001
	jp	00129$
00128$:
	ld	de, #0x0000
00129$:
	ld	l, e
	ld	h, d
	add	hl, hl
	add	hl, hl
	add	hl, de
	add	hl, hl
	add	hl, de
	add	hl, bc
	call	_emit_sprite_current
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:794: emit_sprite_at(&hs_button_exit[pressed_exit ? 1 : 0], 0, 0);
00116$:
	ld	hl, #0x0000
	ld	(_sprite_base_x), hl
	ld	(_sprite_base_y), hl
	ld	a, (_pressed_exit+0)
	or	a, a
	jr	Z, 00130$
	ld	bc, #0x0001
	jp	00131$
00130$:
	ld	bc, #0x0000
00131$:
	ld	l, c
	ld	h, b
	add	hl, hl
	add	hl, hl
	add	hl, bc
	add	hl, hl
	add	hl, bc
	ld	de, #_hs_button_exit
	add	hl, de
	call	_emit_sprite_current
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:795: ABI_CALL(HMM2_HscAbi_RenderEnd);
	call	0xaec2
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:796: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:798: static void render_or_wait(void)
;	---------------------------------
; Function render_or_wait
; ---------------------------------
_render_or_wait:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:806: ++animation_frame;
	ld	hl, (_animation_frame)
	inc	hl
	ld	(_animation_frame), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:807: render_screen();
	call	_render_screen
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:808: screen_dirty = 0;
	ld	hl, #_screen_dirty
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:809: }
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:811: static uint8_t in_rect(uint16_t x, uint16_t y, uint16_t rx, uint16_t ry, uint16_t rw, uint16_t rh)
;	---------------------------------
; Function in_rect
; ---------------------------------
_in_rect:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	c, l
	ld	b, h
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:813: if (x < rx || y < ry) {
	ld	a, c
	sub	a, 4 (ix)
	ld	a, b
	sbc	a, 5 (ix)
	jr	C, 00101$
	ld	a, e
	sub	a, 6 (ix)
	ld	a, d
	sbc	a, 7 (ix)
	jr	NC, 00102$
00101$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:814: return 0;
	xor	a, a
	jp	00107$
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:816: if (x >= rx + rw || y >= ry + rh) {
	ld	a, 4 (ix)
	add	a, 8 (ix)
	ld	l, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, 5 (ix)
	adc	a, 9 (ix)
	ld	h, a
;	spillPairReg hl
;	spillPairReg hl
	ld	a, c
	sub	a, l
	ld	a, b
	sbc	a, h
	jr	NC, 00104$
	ld	a, 6 (ix)
	add	a, 10 (ix)
	ld	c, a
	ld	a, 7 (ix)
	adc	a, 11 (ix)
	ld	b, a
	ld	a, e
	sub	a, c
	ld	a, d
	sbc	a, b
	jr	C, 00105$
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:817: return 0;
	xor	a, a
	jp	00107$
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:819: return 1;
	ld	a, #0x01
00107$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:820: }
	pop	ix
	pop	hl
	ld	iy, #8
	add	iy, sp
	ld	sp, iy
	jp	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:822: static void update_screen(void)
;	---------------------------------
; Function update_screen
; ---------------------------------
_update_screen:
	push	ix
	ld	ix,#0
	add	ix,sp
	push	af
	push	af
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:831: ABI_CALL(HMM2_HscAbi_PollInput);
	call	0xb061
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:832: x = MEM16(HMM2_HsAbiInputX);
	ld	bc, (#0xb17e)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:833: y = MEM16(HMM2_HsAbiInputY);
	ld	hl, #0xb180
	ld	a, (hl)
	ld	-4 (ix), a
	inc	hl
	ld	a, (hl)
	ld	-3 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:834: lmb = MEM8(HMM2_HsAbiInputLmb);
	ld	hl, #0xb182
	ld	a, (hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:836: new_pressed_other = lmb && in_rect(x, y, BUTTON_OTHER_X, BUTTON_Y, BUTTON_W, BUTTON_H);
	ld	-2 (ix), a
	or	a, a
	jr	Z, 00125$
	push	bc
	ld	hl, #0x0088
	push	hl
	ld	l, #0x1c
	push	hl
	ld	hl, #0x013b
	push	hl
	ld	hl, #0x0008
	push	hl
	ld	e, -4 (ix)
	ld	d, -3 (ix)
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	h, b
;	spillPairReg hl
;	spillPairReg hl
	call	_in_rect
	pop	bc
	or	a, a
	jr	NZ, 00126$
00125$:
	xor	a, a
	jp	00127$
00126$:
	ld	a, #0x01
00127$:
	ld	-1 (ix), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:837: new_pressed_exit = lmb && in_rect(x, y, BUTTON_EXIT_X, BUTTON_Y, BUTTON_W, BUTTON_H);
	ld	a, -2 (ix)
	or	a, a
	jr	Z, 00128$
	ld	hl, #0x0088
	push	hl
	ld	l, #0x1c
	push	hl
	ld	hl, #0x013b
	push	hl
	ld	hl, #0x025c
	push	hl
	ld	e, -4 (ix)
	ld	d, -3 (ix)
	ld	l, c
;	spillPairReg hl
;	spillPairReg hl
	ld	h, b
;	spillPairReg hl
;	spillPairReg hl
	call	_in_rect
	or	a, a
	jr	NZ, 00129$
00128$:
	ld	c, #0x00
	jp	00130$
00129$:
	ld	c, #0x01
00130$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:838: if (new_pressed_other != pressed_other || new_pressed_exit != pressed_exit) {
	ld	a, (_pressed_other+0)
	sub	a, -1 (ix)
	jr	NZ, 00104$
	ld	a, (_pressed_exit+0)
	sub	a, c
	jr	Z, 00105$
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:839: screen_dirty = 1;
	ld	a, #0x01
	ld	(#_screen_dirty), a
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:841: pressed_other = new_pressed_other;
	ld	a, -1 (ix)
	ld	(_pressed_other+0), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:842: pressed_exit = new_pressed_exit;
	ld	a, c
	ld	(#_pressed_exit), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:844: if (MEM8(HMM2_HsAbiInputEsc) != 0) {
	ld	a, (#0xb183)
	or	a, a
	jr	Z, 00111$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:845: ABI_CALL(HMM2_HscAbi_GoMenu);
	call	0xb092
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:846: return;
	jp	00123$
00111$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:849: if (lmb == 0) {
	ld	a, -2 (ix)
	or	a, a
	jr	NZ, 00113$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:850: lmb_latch = 0;
	ld	hl, #_lmb_latch
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:851: return;
	jp	00123$
00113$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:853: if (lmb_latch != 0) {
	ld	a, (_lmb_latch+0)
	or	a, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:854: return;
	jr	NZ, 00123$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:856: lmb_latch = 1;
	ld	a, #0x01
	ld	(#_lmb_latch), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:858: if (pressed_exit != 0) {
	ld	a, (_pressed_exit+0)
	or	a, a
	jr	Z, 00120$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:859: ABI_CALL(HMM2_HscAbi_GoMenu);
	call	0xb092
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:860: return;
	jp	00123$
00120$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:862: if (pressed_other != 0) {
	ld	a, (_pressed_other+0)
	or	a, a
	jr	Z, 00123$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:863: is_campaign ^= 1;
	ld	a, (_is_campaign+0)
	xor	a, #0x01
	ld	(_is_campaign+0), a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:864: set_game_mode(is_campaign ? GAME_MODE_HISCORES_CAMPAIGN : GAME_MODE_HISCORES_STANDARD);
	ld	a, (_is_campaign+0)
	or	a, a
	jr	Z, 00131$
	ld	bc, #0x0005
	jp	00132$
00131$:
	ld	bc, #0x0004
00132$:
	ld	a, c
	call	_set_game_mode
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:865: screen_dirty = 1;
	ld	hl, #_screen_dirty
	ld	(hl), #0x01
00123$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:867: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:869: static void enter_screen(uint8_t campaign)
;	---------------------------------
; Function enter_screen
; ---------------------------------
_enter_screen:
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:872: init_scale_tables();
	push	bc
	call	_init_scale_tables
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:873: is_campaign = campaign;
	ld	hl, #_is_campaign
	ld	(hl), c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:874: lmb_latch = 1;
	ld	hl, #_lmb_latch
	ld	(hl), #0x01
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:875: pressed_other = 0;
	ld	hl, #_pressed_other
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:876: pressed_exit = 0;
	ld	hl, #_pressed_exit
	ld	(hl), #0x00
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:877: animation_frame = 0;
	ld	hl, #0x0000
	ld	(_animation_frame), hl
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:878: screen_dirty = 1;
	ld	hl, #_screen_dirty
	ld	(hl), #0x01
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:879: load_from_disk();
	call	_load_from_disk
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:880: set_game_mode(is_campaign ? GAME_MODE_HISCORES_CAMPAIGN : GAME_MODE_HISCORES_STANDARD);
	ld	a, (_is_campaign+0)
	or	a, a
	jr	Z, 00103$
	ld	bc, #0x0005
	jp	00104$
00103$:
	ld	bc, #0x0004
00104$:
	ld	a, c
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:881: }
	jp	_set_game_mode
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:883: static void register_from_abi(uint8_t campaign)
;	---------------------------------
; Function register_from_abi
; ---------------------------------
_register_from_abi:
	push	ix
	ld	ix,#0
	add	ix,sp
	ld	hl, #-48
	add	hl, sp
	ld	sp, hl
	ld	c, a
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:887: const uint8_t * src = (const uint8_t *)MEM16(HMM2_HsAbiPtr);
	ld	de, (#0xb16d)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:888: copy_entry_from_disk(&entry, src);
	push	bc
	ld	hl, #2
	add	hl, sp
	call	_copy_entry_from_disk
	pop	bc
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:889: if (campaign != 0) {
	ld	a, c
	or	a, a
	jr	Z, 00102$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:890: register_score(campaign_scores, &entry, 1);
	ld	a, #0x01
	push	af
	inc	sp
	ld	hl, #1
	add	hl, sp
	ex	de, hl
	ld	hl, #_campaign_scores
	call	_register_score
	jp	00103$
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:893: register_score(standard_scores, &entry, 0);
	xor	a, a
	push	af
	inc	sp
	ld	hl, #1
	add	hl, sp
	ex	de, hl
	ld	hl, #_standard_scores
	call	_register_score
00103$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:895: screen_dirty = 1;
	ld	hl, #_screen_dirty
	ld	(hl), #0x01
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:896: }
	ld	sp, ix
	pop	ix
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:898: void hiscores_overlay_entry(void)
;	---------------------------------
; Function hiscores_overlay_entry
; ---------------------------------
_hiscores_overlay_entry::
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:901: switch (MEM8(HMM2_HsAbiCmd)) {
	ld	hl, #0xb16a
	ld	c, (hl)
	ld	a, #0x05
	sub	a, c
	ret	C
	ld	b, #0x00
	ld	hl, #00116$
	add	hl, bc
	add	hl, bc
	add	hl, bc
	jp	(hl)
00116$:
	jp	00101$
	jp	00102$
	jp	00103$
	jp	00104$
	jp	00105$
	jp	00106$
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:902: case HS_CMD_ENTER_STANDARD:
00101$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:903: enter_screen(0);
	xor	a, a
	call	_enter_screen
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:904: ++abi_call_barrier;
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:905: break;
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:906: case HS_CMD_ENTER_CAMPAIGN:
00102$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:907: enter_screen(1);
	ld	a, #0x01
	call	_enter_screen
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:908: ++abi_call_barrier;
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:909: break;
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:910: case HS_CMD_UPDATE:
00103$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:911: update_screen();
	call	_update_screen
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:912: ++abi_call_barrier;
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:913: break;
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:914: case HS_CMD_RENDER:
00104$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:915: render_or_wait();
	call	_render_or_wait
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:916: ++abi_call_barrier;
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:917: break;
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:918: case HS_CMD_REGISTER_STANDARD:
00105$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:919: register_from_abi(0);
	xor	a, a
	call	_register_from_abi
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:920: ++abi_call_barrier;
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:921: break;
	ret
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:922: case HS_CMD_REGISTER_CAMPAIGN:
00106$:
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:923: register_from_abi(1);
	ld	a, #0x01
	call	_register_from_abi
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:924: ++abi_call_barrier;
	ld	hl, #_abi_call_barrier
	inc	(hl)
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:928: }
;C:\Users\Администратор\Desktop\HMM2\Source\C\hiscores.c:929: }
	ret
	.area _CODE
	.area _INITIALIZER
	.area _CABS (ABS)
