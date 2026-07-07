; Сгенерировано Source/Tools/viewport_pack.py

RUNTIME_DL_BUFFER       EQU CMD_ADDRESS_PTR
RUNTIME_VIEW_W          EQU 15
RUNTIME_VIEW_H          EQU 15
RUNTIME_TILE_COUNT      EQU RUNTIME_VIEW_W * RUNTIME_VIEW_H

RuntimeDL_Header:
                FT_CLEAR_COLOR_RGB 0, 0, 0
                FT_CLEAR 1, 1, 1
                FT_SCISSOR_XY GAME_VIEW_SCREEN_X, GAME_VIEW_SCREEN_Y
                FT_SCISSOR_SIZE GAME_VIEW_SCREEN_W, GAME_VIEW_SCREEN_H
RuntimeDL_TranslateX:
RuntimeDL_TranslateX_Low:
                DEFW 0
RuntimeDL_TranslateX_High:
                DEFW #2B00
RuntimeDL_TranslateY:
RuntimeDL_TranslateY_Low:
                DEFW 0
RuntimeDL_TranslateY_High:
                DEFW #2C00
                FT_BITMAP_HANDLE 0
RuntimeDL_Handle0_PaletteSource:
                FT_PALETTE_SOURCE #000000
RuntimeDL_Handle0_BitmapSource:
                FT_BITMAP_SOURCE #004000
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_REPEAT, FT_REPEAT, 52, 52
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160
                FT_BITMAP_HANDLE 1
RuntimeDL_Handle1_PaletteSource:
                FT_PALETTE_SOURCE #000000
RuntimeDL_Handle1_BitmapSource:
                FT_BITMAP_SOURCE #024000
                FT_BITMAP_LAYOUT FT_PALETTED4444, 32, 32
                FT_BITMAP_SIZE FT_NEAREST, FT_REPEAT, FT_REPEAT, 52, 52
                FT_BITMAP_TRANSFORM_A 160
                FT_BITMAP_TRANSFORM_E 160

                FT_BEGIN FT_BITMAPS
RuntimeDL_Header_SIZE EQU $ - RuntimeDL_Header

RuntimeDL_UpdateTerrainSources:
                LD   A, (CompositeDrawBank)
                OR   A
                JR   Z, .bank0
.bank1:
                LD   HL, #C400
                LD   (RuntimeDL_Handle0_PaletteSource), HL
                LD   A, #03
                LD   (RuntimeDL_Handle0_PaletteSource + 2), A
                LD   HL, #0400
                LD   (RuntimeDL_Handle0_BitmapSource), HL
                LD   A, #04
                LD   (RuntimeDL_Handle0_BitmapSource + 2), A
                LD   HL, #C400
                LD   (RuntimeDL_Handle1_PaletteSource), HL
                LD   A, #03
                LD   (RuntimeDL_Handle1_PaletteSource + 2), A
                LD   HL, #0400
                LD   (RuntimeDL_Handle1_BitmapSource), HL
                LD   A, #06
                LD   (RuntimeDL_Handle1_BitmapSource + 2), A
                RET
.bank0:
                LD   HL, #0000
                LD   (RuntimeDL_Handle0_PaletteSource), HL
                LD   A, #00
                LD   (RuntimeDL_Handle0_PaletteSource + 2), A
                LD   HL, #4000
                LD   (RuntimeDL_Handle0_BitmapSource), HL
                LD   A, #00
                LD   (RuntimeDL_Handle0_BitmapSource + 2), A
                LD   HL, #0000
                LD   (RuntimeDL_Handle1_PaletteSource), HL
                LD   A, #00
                LD   (RuntimeDL_Handle1_PaletteSource + 2), A
                LD   HL, #4000
                LD   (RuntimeDL_Handle1_BitmapSource), HL
                LD   A, #02
                LD   (RuntimeDL_Handle1_BitmapSource + 2), A
                RET

RuntimeDL_RightBand:
                FT_END
RuntimeDL_TranslateXRight:
RuntimeDL_TranslateXRight_Low:
                DEFW 12288
RuntimeDL_TranslateXRight_High:
                DEFW #2B00
                FT_BEGIN FT_BITMAPS
RuntimeDL_RightBand_SIZE EQU $ - RuntimeDL_RightBand

RuntimeDL_Tail:
                FT_END
                FT_DISPLAY
RuntimeDL_Tail_SIZE EQU $ - RuntimeDL_Tail

RuntimeDL_ObjectTranslate:
RuntimeDL_ObjectTranslateX_Low:
                DEFW 0
RuntimeDL_ObjectTranslateX_High:
                DEFW #2B00
RuntimeDL_ObjectTranslateY_Low:
                DEFW 0
RuntimeDL_ObjectTranslateY_High:
                DEFW #2C00
RuntimeDL_ObjectTranslate_SIZE EQU $ - RuntimeDL_ObjectTranslate
MAP_TERRAIN_CELL_STRIDE EQU 37
RUNTIME_LEFT_VIEW_W EQU 15
RUNTIME_RIGHT_VIEW_W EQU RUNTIME_VIEW_W - RUNTIME_LEFT_VIEW_W
RUNTIME_LEFT_SCREEN_X16 EQU 12288
RUNTIME_TILE_DL_BYTES EQU 12
MAP_TERRAIN_CELL_ENTRY_SIZE EQU 6
RUNTIME_LEFT_DL_BYTES EQU 2700
RUNTIME_RIGHT_DL_BYTES EQU 0
RUNTIME_BASE_DL_SIZE EQU RuntimeDL_Header_SIZE + RUNTIME_LEFT_DL_BYTES + RuntimeDL_RightBand_SIZE + RUNTIME_RIGHT_DL_BYTES + RuntimeDL_Tail_SIZE
RUNTIME_OBJECT_DL_SIZE EQU RUNTIME_BASE_DL_SIZE + RuntimeDL_ObjectTranslate_SIZE + OBJECT_VIEW_DL_SIZE - 4
COMPOSITE_UPLOAD_PAGE_BASE EQU #C4
COMPOSITE_UPLOAD_CELL_PAGE EQU #C4
COMPOSITE_UPLOAD_STRIDE EQU 37
COMPOSITE_UPLOAD_HEIGHT EQU 37
COMPOSITE_UPLOAD_ENTRY_SIZE EQU 8214
COMPOSITE_TILE_BYTES EQU 1024
COMPOSITE_BG_PALETTE_SIZE EQU 512
COMPOSITE_BG_TILE_BASE EQU #004000
COMPOSITE_BG_PALETTED4444 EQU 1
COMPOSITE_CACHE_BANKS EQU 2
COMPOSITE_CACHE_BANK_SIZE EQU 246784
COMPOSITE_CACHE_BANK1_RAMG EQU #03C400
MAP_TERRAIN_CELLS_PAGE EQU #8F
MAP_TERRAIN_CELLS_ADDR EQU #0000
OBJECT_VIEW_STRIDE EQU 23
OBJECT_VIEW_ENTRY_SIZE EQU 7
WATER_CYCLE_INDEX EQU 231
WATER_CYCLE_COUNT EQU 7
WATER_CYCLE_BANK0_RAMG EQU #0001CE
WATER_CYCLE_BANK1_RAMG EQU #03C5CE
WaterCycleOriginal:
                DEFW #F27D, #F16C, #F04B, #F03A, #F05B, #F03A, #F04B

ObjectViewDL_Table:
                DEFB #01
                DEFW #0000
                DEFW 128
                DEFW 232
                DEFB #01
                DEFW #0168
                DEFW 160
                DEFW 296
                DEFB #01
                DEFW #0330
                DEFW 180
                DEFW 340
                DEFB #01
                DEFW #0538
                DEFW 184
                DEFW 384
                DEFB #01
                DEFW #0770
                DEFW 200
                DEFW 416
                DEFB #01
                DEFW #09D8
                DEFW 228
                DEFW 420
                DEFB #01
                DEFW #0C60
                DEFW 252
                DEFW 452
                DEFB #01
                DEFW #0F20
                DEFW 252
                DEFW 484
                DEFB #01
                DEFW #1200
                DEFW 252
                DEFW 532
                DEFB #01
                DEFW #1510
                DEFW 268
                DEFW 596
                DEFB #01
                DEFW #1870
                DEFW 260
                DEFW 640
                DEFB #01
                DEFW #1BF4
                DEFW 252
                DEFW 700
                DEFB #01
                DEFW #1FAC
                DEFW 264
                DEFW 728
                DEFB #01
                DEFW #238C
                DEFW 268
                DEFW 712
                DEFB #01
                DEFW #2760
                DEFW 284
                DEFW 728
                DEFB #01
                DEFW #2B54
                DEFW 296
                DEFW 744
                DEFB #01
                DEFW #2F64
                DEFW 280
                DEFW 744
                DEFB #01
                DEFW #3364
                DEFW 268
                DEFW 748
                DEFB #01
                DEFW #375C
                DEFW 268
                DEFW 716
                DEFB #01
                DEFW #3B34
                DEFW 264
                DEFW 668
                DEFB #02
                DEFW #0000
                DEFW 228
                DEFW 636
                DEFB #02
                DEFW #0360
                DEFW 192
                DEFW 604
                DEFB #02
                DEFW #067C
                DEFW 192
                DEFW 572
                DEFB #02
                DEFW #0978
                DEFW 128
                DEFW 232
                DEFB #02
                DEFW #0AE0
                DEFW 160
                DEFW 296
                DEFB #02
                DEFW #0CA8
                DEFW 180
                DEFW 340
                DEFB #02
                DEFW #0EB0
                DEFW 184
                DEFW 384
                DEFB #02
                DEFW #10E8
                DEFW 200
                DEFW 416
                DEFB #02
                DEFW #1350
                DEFW 228
                DEFW 420
                DEFB #02
                DEFW #15D8
                DEFW 252
                DEFW 452
                DEFB #02
                DEFW #1898
                DEFW 252
                DEFW 484
                DEFB #02
                DEFW #1B78
                DEFW 252
                DEFW 532
                DEFB #02
                DEFW #1E88
                DEFW 268
                DEFW 596
                DEFB #02
                DEFW #21E8
                DEFW 260
                DEFW 640
                DEFB #02
                DEFW #256C
                DEFW 252
                DEFW 700
                DEFB #02
                DEFW #2924
                DEFW 264
                DEFW 744
                DEFB #02
                DEFW #2D14
                DEFW 268
                DEFW 744
                DEFB #02
                DEFW #3108
                DEFW 284
                DEFW 760
                DEFB #02
                DEFW #351C
                DEFW 296
                DEFW 776
                DEFB #02
                DEFW #394C
                DEFW 280
                DEFW 776
                DEFB #03
                DEFW #0000
                DEFW 268
                DEFW 780
                DEFB #03
                DEFW #0418
                DEFW 268
                DEFW 748
                DEFB #03
                DEFW #0810
                DEFW 264
                DEFW 700
                DEFB #03
                DEFW #0BD4
                DEFW 228
                DEFW 668
                DEFB #03
                DEFW #0F54
                DEFW 192
                DEFW 636
                DEFB #03
                DEFW #1290
                DEFW 192
                DEFW 604
                DEFB #03
                DEFW #15AC
                DEFW 128
                DEFW 260
                DEFB #03
                DEFW #1730
                DEFW 160
                DEFW 324
                DEFB #03
                DEFW #1914
                DEFW 180
                DEFW 368
                DEFB #03
                DEFW #1B38
                DEFW 184
                DEFW 412
                DEFB #03
                DEFW #1D8C
                DEFW 200
                DEFW 444
                DEFB #03
                DEFW #2010
                DEFW 228
                DEFW 448
                DEFB #03
                DEFW #22B4
                DEFW 252
                DEFW 480
                DEFB #03
                DEFW #2590
                DEFW 252
                DEFW 500
                DEFB #03
                DEFW #2880
                DEFW 252
                DEFW 532
                DEFB #03
                DEFW #2B90
                DEFW 268
                DEFW 596
                DEFB #03
                DEFW #2EF0
                DEFW 260
                DEFW 640
                DEFB #03
                DEFW #3274
                DEFW 252
                DEFW 700
                DEFB #03
                DEFW #362C
                DEFW 264
                DEFW 744
                DEFB #03
                DEFW #3A1C
                DEFW 268
                DEFW 744
                DEFB #04
                DEFW #0000
                DEFW 284
                DEFW 760
                DEFB #04
                DEFW #0414
                DEFW 296
                DEFW 776
                DEFB #04
                DEFW #0844
                DEFW 280
                DEFW 776
                DEFB #04
                DEFW #0C64
                DEFW 268
                DEFW 780
                DEFB #04
                DEFW #107C
                DEFW 268
                DEFW 748
                DEFB #04
                DEFW #1474
                DEFW 264
                DEFW 700
                DEFB #04
                DEFW #1838
                DEFW 228
                DEFW 668
                DEFB #04
                DEFW #1BB8
                DEFW 192
                DEFW 636
                DEFB #04
                DEFW #1EF4
                DEFW 192
                DEFW 604
                DEFB #04
                DEFW #2210
                DEFW 128
                DEFW 308
                DEFB #04
                DEFW #23C4
                DEFW 160
                DEFW 372
                DEFB #04
                DEFW #25D8
                DEFW 180
                DEFW 416
                DEFB #04
                DEFW #282C
                DEFW 184
                DEFW 460
                DEFB #04
                DEFW #2AB0
                DEFW 200
                DEFW 492
                DEFB #04
                DEFW #2D64
                DEFW 228
                DEFW 480
                DEFB #04
                DEFW #3028
                DEFW 252
                DEFW 512
                DEFB #04
                DEFW #3324
                DEFW 252
                DEFW 532
                DEFB #04
                DEFW #3634
                DEFW 252
                DEFW 564
                DEFB #04
                DEFW #3964
                DEFW 268
                DEFW 644
                DEFB #07
                DEFW #0000
                DEFW 260
                DEFW 672
                DEFB #07
                DEFW #03A4
                DEFW 256
                DEFW 716
                DEFB #07
                DEFW #0770
                DEFW 268
                DEFW 760
                DEFB #07
                DEFW #0B74
                DEFW 276
                DEFW 760
                DEFB #07
                DEFW #0F80
                DEFW 280
                DEFW 776
                DEFB #07
                DEFW #13A0
                DEFW 280
                DEFW 776
                DEFB #07
                DEFW #17C0
                DEFW 264
                DEFW 776
                DEFB #07
                DEFW #1BD0
                DEFW 252
                DEFW 764
                DEFB #07
                DEFW #1FC8
                DEFW 252
                DEFW 716
                DEFB #07
                DEFW #2390
                DEFW 248
                DEFW 668
                DEFB #07
                DEFW #2724
                DEFW 212
                DEFW 636
                DEFB #07
                DEFW #2A74
                DEFW 188
                DEFW 604
                DEFB #07
                DEFW #2D8C
                DEFW 188
                DEFW 572
                DEFB #07
                DEFW #3084
                DEFW 128
                DEFW 308
                DEFB #07
                DEFW #3238
                DEFW 160
                DEFW 372
                DEFB #07
                DEFW #344C
                DEFW 180
                DEFW 416
                DEFB #07
                DEFW #36A0
                DEFW 184
                DEFW 460
                DEFB #07
                DEFW #3924
                DEFW 200
                DEFW 508
                DEFB #07
                DEFW #3BE8
                DEFW 228
                DEFW 512
                DEFB #08
                DEFW #0000
                DEFW 252
                DEFW 560
                DEFB #08
                DEFW #032C
                DEFW 252
                DEFW 596
                DEFB #08
                DEFW #067C
                DEFW 252
                DEFW 628
                DEFB #08
                DEFW #09EC
                DEFW 268
                DEFW 708
                DEFB #08
                DEFW #0DBC
                DEFW 260
                DEFW 752
                DEFB #08
                DEFW #11B0
                DEFW 256
                DEFW 812
                DEFB #08
                DEFW #15DC
                DEFW 268
                DEFW 856
                DEFB #08
                DEFW #1A40
                DEFW 276
                DEFW 856
                DEFB #08
                DEFW #1EAC
                DEFW 280
                DEFW 872
                DEFB #08
                DEFW #232C
                DEFW 280
                DEFW 872
                DEFB #08
                DEFW #27AC
                DEFW 264
                DEFW 872
                DEFB #08
                DEFW #2C1C
                DEFW 252
                DEFW 860
                DEFB #08
                DEFW #3074
                DEFW 252
                DEFW 812
                DEFB #08
                DEFW #349C
                DEFW 248
                DEFW 748
                DEFB #08
                DEFW #3880
                DEFW 212
                DEFW 700
                DEFB #08
                DEFW #3C10
                DEFW 188
                DEFW 652
                DEFB #09
                DEFW #0000
                DEFW 188
                DEFW 604
                DEFB #09
                DEFW #0318
                DEFW 160
                DEFW 356
                DEFB #09
                DEFW #051C
                DEFW 192
                DEFW 436
                DEFB #09
                DEFW #0790
                DEFW 212
                DEFW 480
                DEFB #09
                DEFW #0A44
                DEFW 216
                DEFW 508
                DEFB #09
                DEFW #0D18
                DEFW 232
                DEFW 540
                DEFB #09
                DEFW #101C
                DEFW 260
                DEFW 560
                DEFB #09
                DEFW #1350
                DEFW 284
                DEFW 608
                DEFB #09
                DEFW #16CC
                DEFW 284
                DEFW 644
                DEFB #09
                DEFW #1A6C
                DEFW 284
                DEFW 692
                DEFB #09
                DEFW #1E3C
                DEFW 300
                DEFW 788
                DEFB #09
                DEFW #227C
                DEFW 292
                DEFW 816
                DEFB #09
                DEFW #26D0
                DEFW 272
                DEFW 876
                DEFB #09
                DEFW #2B4C
                DEFW 268
                DEFW 920
                DEFB #09
                DEFW #2FF0
                DEFW 276
                DEFW 920
                DEFB #09
                DEFW #349C
                DEFW 280
                DEFW 948
                DEFB #09
                DEFW #3968
                DEFW 280
                DEFW 932
                DEFB #0A
                DEFW #0000
                DEFW 264
                DEFW 916
                DEFB #0A
                DEFW #049C
                DEFW 252
                DEFW 904
                DEFB #0A
                DEFW #0920
                DEFW 252
                DEFW 856
                DEFB #0A
                DEFW #0D74
                DEFW 248
                DEFW 792
                DEFB #0A
                DEFW #1184
                DEFW 212
                DEFW 744
                DEFB #0A
                DEFW #1540
                DEFW 188
                DEFW 696
                DEFB #0A
                DEFW #18B4
                DEFW 188
                DEFW 648
                DEFB #0A
                DEFW #1BF8
                DEFW 176
                DEFW 404
                DEFB #0A
                DEFW #1E3C
                DEFW 208
                DEFW 484
                DEFB #0A
                DEFW #20F0
                DEFW 212
                DEFW 512
                DEFB #0A
                DEFW #23C4
                DEFW 216
                DEFW 540
                DEFB #0A
                DEFW #26B8
                DEFW 232
                DEFW 588
                DEFB #0A
                DEFW #29EC
                DEFW 260
                DEFW 636
                DEFB #0A
                DEFW #2D6C
                DEFW 284
                DEFW 684
                DEFB #0A
                DEFW #3134
                DEFW 284
                DEFW 720
                DEFB #0A
                DEFW #3520
                DEFW 284
                DEFW 752
                DEFB #0A
                DEFW #392C
                DEFW 300
                DEFW 828
                DEFB #0B
                DEFW #0000
                DEFW 292
                DEFW 844
                DEFB #0B
                DEFW #0470
                DEFW 272
                DEFW 888
                DEFB #0B
                DEFW #08F8
                DEFW 268
                DEFW 928
                DEFB #0B
                DEFW #0DA4
                DEFW 276
                DEFW 944
                DEFB #0B
                DEFW #1268
                DEFW 280
                DEFW 988
                DEFB #0B
                DEFW #175C
                DEFW 280
                DEFW 972
                DEFB #0B
                DEFW #1C40
                DEFW 264
                DEFW 956
                DEFB #0B
                DEFW #2104
                DEFW 252
                DEFW 960
                DEFB #0B
                DEFW #25C0
                DEFW 252
                DEFW 912
                DEFB #0B
                DEFW #2A4C
                DEFW 248
                DEFW 852
                DEFB #0B
                DEFW #2E98
                DEFW 212
                DEFW 792
                DEFB #0B
                DEFW #3284
                DEFW 188
                DEFW 744
                DEFB #0B
                DEFW #3628
                DEFW 188
                DEFW 696
                DEFB #0B
                DEFW #399C
                DEFW 228
                DEFW 416
                DEFB #0B
                DEFW #3C20
                DEFW 260
                DEFW 480
                DEFB #0C
                DEFW #0000
                DEFW 264
                DEFW 508
                DEFB #0C
                DEFW #0304
                DEFW 268
                DEFW 536
                DEFB #0C
                DEFW #0628
                DEFW 260
                DEFW 584
                DEFB #0C
                DEFW #0974
                DEFW 264
                DEFW 632
                DEFB #0C
                DEFW #0CF4
                DEFW 272
                DEFW 680
                DEFB #0C
                DEFW #10AC
                DEFW 272
                DEFW 732
                DEFB #0C
                DEFW #1498
                DEFW 272
                DEFW 768
                DEFB #0C
                DEFW #18A8
                DEFW 288
                DEFW 860
                DEFB #0C
                DEFW #1D24
                DEFW 268
                DEFW 860
                DEFB #0C
                DEFW #218C
                DEFW 236
                DEFW 888
                DEFB #0C
                DEFW #25F0
                DEFW 232
                DEFW 912
                DEFB #0C
                DEFW #2A68
                DEFW 240
                DEFW 924
                DEFB #0C
                DEFW #2EF4
                DEFW 244
                DEFW 972
                DEFB #0C
                DEFW #33B4
                DEFW 240
                DEFW 972
                DEFB #0C
                DEFW #3870
                DEFW 224
                DEFW 972
                DEFB #0D
                DEFW #0000
                DEFW 212
                DEFW 976
                DEFB #0D
                DEFW #04A4
                DEFW 212
                DEFW 928
                DEFB #0D
                DEFW #0918
                DEFW 212
                DEFW 868
                DEFB #0D
                DEFW #0D50
                DEFW 196
                DEFW 808
                DEFB #0D
                DEFW #113C
                DEFW 188
                DEFW 760
                DEFB #0D
                DEFW #14F0
                DEFW 188
                DEFW 696
                DEFB #0D
                DEFW #1864
                DEFW 240
                DEFW 480
                DEFB #0D
                DEFW #1B34
                DEFW 292
                DEFW 544
                DEFB #0D
                DEFW #1E78
                DEFW 296
                DEFW 572
                DEFB #0D
                DEFW #21DC
                DEFW 300
                DEFW 600
                DEFB #0D
                DEFW #2560
                DEFW 284
                DEFW 664
                DEFB #0D
                DEFW #2914
                DEFW 272
                DEFW 728
                DEFB #0D
                DEFW #2CFC
                DEFW 280
                DEFW 776
                DEFB #0D
                DEFW #311C
                DEFW 280
                DEFW 828
                DEFB #0D
                DEFW #3570
                DEFW 280
                DEFW 848
                DEFB #0D
                DEFW #39D8
                DEFW 284
                DEFW 908
                DEFB #0E
                DEFW #0000
                DEFW 268
                DEFW 908
                DEFB #0E
                DEFW #0498
                DEFW 248
                DEFW 904
                DEFB #0E
                DEFW #0918
                DEFW 272
                DEFW 912
                DEFB #0E
                DEFW #0DB8
                DEFW 308
                DEFW 940
                DEFB #0E
                DEFW #1298
                DEFW 312
                DEFW 1004
                DEFB #0E
                DEFW #17BC
                DEFW 304
                DEFW 1004
                DEFB #0E
                DEFW #1CD8
                DEFW 284
                DEFW 1004
                DEFB #0E
                DEFW #21E0
                DEFW 272
                DEFW 1008
                DEFB #0E
                DEFW #26E0
                DEFW 272
                DEFW 960
                DEFB #0E
                DEFW #2BB0
                DEFW 272
                DEFW 884
                DEFB #0E
                DEFW #3034
                DEFW 256
                DEFW 808
                DEFB #0E
                DEFW #345C
                DEFW 248
                DEFW 760
                DEFB #0E
                DEFW #384C
                DEFW 248
                DEFW 696
                DEFB #0E
                DEFW #3BFC
                DEFW 240
                DEFW 496
                DEFB #0F
                DEFW #0000
                DEFW 292
                DEFW 560
                DEFB #0F
                DEFW #0354
                DEFW 296
                DEFW 588
                DEFB #0F
                DEFW #06C8
                DEFW 300
                DEFW 632
                DEFB #0F
                DEFW #0A6C
                DEFW 284
                DEFW 712
                DEFB #0F
                DEFW #0E50
                DEFW 276
                DEFW 776
                DEFB #0F
                DEFW #126C
                DEFW 284
                DEFW 840
                DEFB #0F
                DEFW #16D0
                DEFW 284
                DEFW 892
                DEFB #0F
                DEFW #1B68
                DEFW 284
                DEFW 912
                DEFB #0F
                DEFW #2014
                DEFW 288
                DEFW 956
                DEFB #0F
                DEFW #24F0
                DEFW 272
                DEFW 956
                DEFB #0F
                DEFW #29BC
                DEFW 252
                DEFW 952
                DEFB #0F
                DEFW #2E70
                DEFW 260
                DEFW 960
                DEFB #0F
                DEFW #3334
                DEFW 308
                DEFW 988
                DEFB #0F
                DEFW #3844
                DEFW 312
                DEFW 1020
                DEFB #15
                DEFW #0000
                DEFW 304
                DEFW 1004
                DEFB #15
                DEFW #051C
                DEFW 284
                DEFW 988
                DEFB #15
                DEFW #0A14
                DEFW 272
                DEFW 992
                DEFB #15
                DEFW #0F04
                DEFW 272
                DEFW 924
                DEFB #15
                DEFW #13B0
                DEFW 272
                DEFW 836
                DEFB #15
                DEFW #1804
                DEFW 252
                DEFW 760
                DEFB #15
                DEFW #1BF8
                DEFW 244
                DEFW 696
                DEFB #15
                DEFW #1FA4
                DEFW 244
                DEFW 632
                DEFB #15
                DEFW #2310
                DEFW 240
                DEFW 496
                DEFB #15
                DEFW #25F0
                DEFW 276
                DEFW 544
                DEFB #15
                DEFW #2924
                DEFW 260
                DEFW 588
                DEFB #15
                DEFW #2C74
                DEFW 260
                DEFW 628
                DEFB #15
                DEFW #2FEC
                DEFW 244
                DEFW 712
                DEFB #15
                DEFW #33A8
                DEFW 236
                DEFW 776
                DEFB #15
                DEFW #379C
                DEFW 244
                DEFW 824
                DEFB #16
                DEFW #0000
                DEFW 244
                DEFW 856
                DEFB #16
                DEFW #044C
                DEFW 244
                DEFW 876
                DEFB #16
                DEFW #08AC
                DEFW 248
                DEFW 920
                DEFB #16
                DEFW #0D3C
                DEFW 232
                DEFW 920
                DEFB #16
                DEFW #11BC
                DEFW 212
                DEFW 916
                DEFB #16
                DEFW #1624
                DEFW 192
                DEFW 924
                DEFB #16
                DEFW #1A80
                DEFW 224
                DEFW 952
                DEFB #16
                DEFW #1F18
                DEFW 240
                DEFW 1000
                DEFB #16
                DEFW #23F0
                DEFW 232
                DEFW 1000
                DEFB #16
                DEFW #28C0
                DEFW 216
                DEFW 1000
                DEFB #16
                DEFW #2D80
                DEFW 224
                DEFW 988
                DEFB #16
                DEFW #323C
                DEFW 240
                DEFW 920
                DEFB #16
                DEFW #36C4
                DEFW 240
                DEFW 832
                DEFB #16
                DEFW #3AF4
                DEFW 220
                DEFW 760
                DEFB #17
                DEFW #0000
                DEFW 212
                DEFW 712
                DEFB #17
                DEFW #039C
                DEFW 212
                DEFW 648
                DEFB #17
                DEFW #06F8
                DEFW 208
                DEFW 560
                DEFB #17
                DEFW #09F8
                DEFW 228
                DEFW 608
                DEFB #17
                DEFW #0D3C
                DEFW 212
                DEFW 652
                DEFB #17
                DEFW #109C
                DEFW 212
                DEFW 676
                DEFB #17
                DEFW #1414
                DEFW 196
                DEFW 744
                DEFB #17
                DEFW #17C0
                DEFW 188
                DEFW 804
                DEFB #17
                DEFW #1BA0
                DEFW 196
                DEFW 856
                DEFB #17
                DEFW #1FBC
                DEFW 196
                DEFW 872
                DEFB #17
                DEFW #23E8
                DEFW 196
                DEFW 892
                DEFB #17
                DEFW #2828
                DEFW 200
                DEFW 920
                DEFB #17
                DEFW #2C88
                DEFW 184
                DEFW 904
                DEFB #17
                DEFW #30C8
                DEFW 164
                DEFW 900
                DEFB #17
                DEFW #34F0
                DEFW 160
                DEFW 908
                DEFB #17
                DEFW #391C
                DEFW 192
                DEFW 936
                DEFB #18
                DEFW #0000
                DEFW 208
                DEFW 968
                DEFB #18
                DEFW #0498
                DEFW 200
                DEFW 952
                DEFB #18
                DEFW #0918
                DEFW 200
                DEFW 940
                DEFB #18
                DEFW #0D8C
                DEFW 220
                DEFW 908
                DEFB #18
                DEFW #11F4
                DEFW 220
                DEFW 856
                DEFB #18
                DEFW #1628
                DEFW 204
                DEFW 768
                DEFB #18
                DEFW #19F4
                DEFW 184
                DEFW 696
                DEFB #18
                DEFW #1D64
                DEFW 176
                DEFW 632
                DEFB #18
                DEFW #208C
                DEFW 176
                DEFW 568
                DEFB #18
                DEFW #2374
                DEFW 216
                DEFW 548
                DEFB #18
                DEFW #2670
                DEFW 236
                DEFW 580
                DEFB #18
                DEFW #29A0
                DEFW 236
                DEFW 612
                DEFB #18
                DEFW #2CF0
                DEFW 256
                DEFW 624
                DEFB #18
                DEFW #3060
                DEFW 244
                DEFW 692
                DEFB #18
                DEFW #3408
                DEFW 232
                DEFW 748
                DEFB #18
                DEFW #37DC
                DEFW 240
                DEFW 808
                DEFB #19
                DEFW #0000
                DEFW 240
                DEFW 808
                DEFB #19
                DEFW #0418
                DEFW 240
                DEFW 796
                DEFB #19
                DEFW #0824
                DEFW 244
                DEFW 808
                DEFB #19
                DEFW #0C40
                DEFW 228
                DEFW 780
                DEFB #19
                DEFW #1030
                DEFW 208
                DEFW 764
                DEFB #19
                DEFW #13FC
                DEFW 200
                DEFW 756
                DEFB #19
                DEFW #17B8
                DEFW 232
                DEFW 784
                DEFB #19
                DEFW #1BB0
                DEFW 248
                DEFW 816
                DEFB #19
                DEFW #1FD8
                DEFW 240
                DEFW 800
                DEFB #19
                DEFW #23E8
                DEFW 240
                DEFW 784
                DEFB #19
                DEFW #27E8
                DEFW 256
                DEFW 752
                DEFB #19
                DEFW #2BD8
                DEFW 236
                DEFW 716
                DEFB #19
                DEFW #2F90
                DEFW 204
                DEFW 628
                DEFB #19
                DEFW #32D0
                DEFW 184
                DEFW 560
                DEFB #19
                DEFW #35B8
                DEFW 176
                DEFW 496
                DEFB #19
                DEFW #3858
                DEFW 176
                DEFW 448
                DEFB #19
                DEFW #3AC8
                DEFW 244
                DEFW 548
                DEFB #1A
                DEFW #0000
                DEFW 264
                DEFW 580
                DEFB #1A
                DEFW #034C
                DEFW 276
                DEFW 612
                DEFB #1A
                DEFW #06C4
                DEFW 312
                DEFW 624
                DEFB #1A
                DEFW #0A6C
                DEFW 312
                DEFW 676
                DEFB #1A
                DEFW #0E48
                DEFW 296
                DEFW 748
                DEFB #1A
                DEFW #125C
                DEFW 300
                DEFW 824
                DEFB #1A
                DEFW #16C0
                DEFW 300
                DEFW 808
                DEFB #1A
                DEFW #1B14
                DEFW 300
                DEFW 764
                DEFB #1A
                DEFW #1F3C
                DEFW 304
                DEFW 776
                DEFB #1A
                DEFW #2374
                DEFW 288
                DEFW 748
                DEFB #1A
                DEFW #2780
                DEFW 252
                DEFW 732
                DEFB #1A
                DEFW #2B58
                DEFW 228
                DEFW 728
                DEFB #1A
                DEFW #2F14
                DEFW 260
                DEFW 772
                DEFB #1A
                DEFW #331C
                DEFW 276
                DEFW 804
                DEFB #1A
                DEFW #3754
                DEFW 268
                DEFW 788
                DEFB #1A
                DEFW #3B74
                DEFW 268
                DEFW 772
                DEFB #1B
                DEFW #0000
                DEFW 284
                DEFW 740
                DEFB #1B
                DEFW #0400
                DEFW 252
                DEFW 704
                DEFB #1B
                DEFW #07BC
                DEFW 204
                DEFW 632
                DEFB #1B
                DEFW #0B00
                DEFW 184
                DEFW 544
                DEFB #1B
                DEFW #0DD8
                DEFW 176
                DEFW 468
                DEFB #1B
                DEFW #105C
                DEFW 176
                DEFW 420
                DEFB #1B
                DEFW #12B0
                DEFW 236
                DEFW 564
                DEFB #1B
                DEFW #15D0
                DEFW 256
                DEFW 596
                DEFB #1B
                DEFW #1924
                DEFW 268
                DEFW 628
                DEFB #1B
                DEFW #1CA4
                DEFW 316
                DEFW 640
                DEFB #1B
                DEFW #2060
                DEFW 328
                DEFW 692
                DEFB #1B
                DEFW #245C
                DEFW 324
                DEFW 764
                DEFB #1B
                DEFW #289C
                DEFW 340
                DEFW 824
                DEFB #1B
                DEFW #2D28
                DEFW 340
                DEFW 808
                DEFB #1B
                DEFW #31A4
                DEFW 340
                DEFW 748
                DEFB #1B
                DEFW #35E4
                DEFW 344
                DEFW 728
                DEFB #1B
                DEFW #3A14
                DEFW 332
                DEFW 700
                DEFB #1C
                DEFW #0000
                DEFW 300
                DEFW 652
                DEFB #1C
                DEFW #03B8
                DEFW 276
                DEFW 632
                DEFB #1C
                DEFW #0744
                DEFW 308
                DEFW 676
                DEFB #1C
                DEFW #0B1C
                DEFW 324
                DEFW 708
                DEFB #1C
                DEFW #0F24
                DEFW 304
                DEFW 692
                DEFB #1C
                DEFW #1308
                DEFW 288
                DEFW 676
                DEFB #1C
                DEFW #16CC
                DEFW 300
                DEFW 644
                DEFB #1C
                DEFW #1A7C
                DEFW 256
                DEFW 608
                DEFB #1C
                DEFW #1DDC
                DEFW 208
                DEFW 536
                DEFB #1C
                DEFW #20C4
                DEFW 188
                DEFW 448
                DEFB #1C
                DEFW #2340
                DEFW 168
                DEFW 372
                DEFB #1C
                DEFW #255C
                DEFW 168
                DEFW 324
                DEFB #1C
                DEFW #2748
                DEFW 204
                DEFW 548
                DEFB #1C
                DEFW #2A38
                DEFW 236
                DEFW 564
                DEFB #1C
                DEFW #2D58
                DEFW 248
                DEFW 596
                DEFB #1C
                DEFW #30A4
                DEFW 296
                DEFW 608
                DEFB #1C
                DEFW #342C
                DEFW 308
                DEFW 660
                DEFB #1C
                DEFW #37F4
                DEFW 292
                DEFW 732
                DEFB #1D
                DEFW #0000
                DEFW 308
                DEFW 792
                DEFB #1D
                DEFW #044C
                DEFW 308
                DEFW 776
                DEFB #1D
                DEFW #0888
                DEFW 308
                DEFW 716
                DEFB #1D
                DEFW #0C88
                DEFW 312
                DEFW 696
                DEFB #1D
                DEFW #1078
                DEFW 316
                DEFW 668
                DEFB #1D
                DEFW #1450
                DEFW 300
                DEFW 620
                DEFB #1D
                DEFW #17E8
                DEFW 292
                DEFW 600
                DEFB #1D
                DEFW #1B64
                DEFW 324
                DEFW 628
                DEFB #1D
                DEFW #1F1C
                DEFW 340
                DEFW 676
                DEFB #1D
                DEFW #2314
                DEFW 320
                DEFW 676
                DEFB #1D
                DEFW #26F8
                DEFW 288
                DEFW 676
                DEFB #1D
                DEFW #2ABC
                DEFW 284
                DEFW 644
                DEFB #1D
                DEFW #2E5C
                DEFW 240
                DEFW 608
                DEFB #1D
                DEFW #31AC
                DEFW 192
                DEFW 536
                DEFB #1D
                DEFW #3484
                DEFW 172
                DEFW 448
                DEFB #1D
                DEFW #36F0
                DEFW 152
                DEFW 372
                DEFB #1D
                DEFW #38FC
                DEFW 152
                DEFW 324
                DEFB #1D
                DEFW #3AD8
                DEFW 204
                DEFW 548
                DEFB #1E
                DEFW #0000
                DEFW 236
                DEFW 580
                DEFB #1E
                DEFW #0330
                DEFW 248
                DEFW 628
                DEFB #1E
                DEFW #069C
                DEFW 296
                DEFW 640
                DEFB #1E
                DEFW #0A44
                DEFW 308
                DEFW 692
                DEFB #1E
                DEFW #0E2C
                DEFW 292
                DEFW 764
                DEFB #1E
                DEFW #124C
                DEFW 308
                DEFW 824
                DEFB #1E
                DEFW #16B8
                DEFW 308
                DEFW 808
                DEFB #1E
                DEFW #1B14
                DEFW 308
                DEFW 748
                DEFB #1E
                DEFW #1F34
                DEFW 312
                DEFW 728
                DEFB #1E
                DEFW #2344
                DEFW 316
                DEFW 700
                DEFB #1E
                DEFW #273C
                DEFW 300
                DEFW 652
                DEFB #1E
                DEFW #2AF4
                DEFW 292
                DEFW 616
                DEFB #1E
                DEFW #2E80
                DEFW 324
                DEFW 628
                DEFB #1E
                DEFW #3238
                DEFW 356
                DEFW 676
                DEFB #1E
                DEFW #3640
                DEFW 352
                DEFW 676
                DEFB #1E
                DEFW #3A44
                DEFW 320
                DEFW 660
                DEFB #1F
                DEFW #0000
                DEFW 316
                DEFW 612
                DEFB #1F
                DEFW #03A0
                DEFW 272
                DEFW 576
                DEFB #1F
                DEFW #06F0
                DEFW 224
                DEFW 504
                DEFB #1F
                DEFW #09C8
                DEFW 204
                DEFW 416
                DEFB #1F
                DEFW #0C34
                DEFW 184
                DEFW 340
                DEFB #1F
                DEFW #0E40
                DEFW 184
                DEFW 292
                DEFB #1F
                DEFW #101C
                DEFW 204
                DEFW 520
                DEFB #1F
                DEFW #12F0
                DEFW 236
                DEFW 552
                DEFB #1F
                DEFW #1604
                DEFW 248
                DEFW 600
                DEFB #1F
                DEFW #1954
                DEFW 296
                DEFW 612
                DEFB #1F
                DEFW #1CE0
                DEFW 308
                DEFW 664
                DEFB #1F
                DEFW #20AC
                DEFW 292
                DEFW 736
                DEFB #1F
                DEFW #24B0
                DEFW 308
                DEFW 796
                DEFB #1F
                DEFW #2900
                DEFW 308
                DEFW 792
                DEFB #1F
                DEFW #2D4C
                DEFW 308
                DEFW 748
                DEFB #1F
                DEFW #316C
                DEFW 312
                DEFW 728
                DEFB #1F
                DEFW #357C
                DEFW 316
                DEFW 700
                DEFB #1F
                DEFW #3974
                DEFW 300
                DEFW 652
                DEFB #96
                DEFW #0000
                DEFW 292
                DEFW 616
                DEFB #96
                DEFW #038C
                DEFW 324
                DEFW 628
                DEFB #96
                DEFW #0744
                DEFW 356
                DEFW 676
                DEFB #96
                DEFW #0B4C
                DEFW 352
                DEFW 676
                DEFB #96
                DEFW #0F50
                DEFW 320
                DEFW 660
                DEFB #96
                DEFW #1324
                DEFW 316
                DEFW 612
                DEFB #96
                DEFW #16C4
                DEFW 272
                DEFW 576
                DEFB #96
                DEFW #1A14
                DEFW 224
                DEFW 504
                DEFB #96
                DEFW #1CEC
                DEFW 204
                DEFW 416
                DEFB #96
                DEFW #1F58
                DEFW 184
                DEFW 340
                DEFB #96
                DEFW #2164
                DEFW 184
                DEFW 292
                DEFB #96
                DEFW #2340
                DEFW 236
                DEFW 472
                DEFB #96
                DEFW #2604
                DEFW 256
                DEFW 504
                DEFB #96
                DEFW #28FC
                DEFW 268
                DEFW 568
                DEFB #96
                DEFW #2C40
                DEFW 316
                DEFW 596
                DEFB #96
                DEFW #2FD0
                DEFW 332
                DEFW 648
                DEFB #96
                DEFW #33A4
                DEFW 328
                DEFW 736
                DEFB #96
                DEFW #37CC
                DEFW 344
                DEFW 796
                DEFB #97
                DEFW #0000
                DEFW 344
                DEFW 792
                DEFB #97
                DEFW #0470
                DEFW 344
                DEFW 748
                DEFB #97
                DEFW #08B4
                DEFW 348
                DEFW 712
                DEFB #97
                DEFW #0CD8
                DEFW 352
                DEFW 700
                DEFB #97
                DEFW #10F4
                DEFW 332
                DEFW 668
                DEFB #97
                DEFW #14DC
                DEFW 324
                DEFW 632
                DEFB #97
                DEFW #1898
                DEFW 344
                DEFW 644
                DEFB #97
                DEFW #1C74
                DEFW 344
                DEFW 692
                DEFB #97
                DEFW #2080
                DEFW 324
                DEFW 692
                DEFB #97
                DEFW #2478
                DEFW 292
                DEFW 676
                DEFB #97
                DEFW #2840
                DEFW 288
                DEFW 612
                DEFB #97
                DEFW #2BC4
                DEFW 244
                DEFW 560
                DEFB #97
                DEFW #2EE8
                DEFW 192
                DEFW 488
                DEFB #97
                DEFW #3190
                DEFW 172
                DEFW 400
                DEFB #97
                DEFW #33CC
                DEFW 152
                DEFW 324
                DEFB #97
                DEFW #35A8
                DEFW 152
                DEFW 276
                DEFB #97
                DEFW #3754
                DEFW 236
                DEFW 472
                DEFB #97
                DEFW #3A18
                DEFW 256
                DEFW 520
                DEFB #98
                DEFW #0000
                DEFW 268
                DEFW 584
                DEFB #98
                DEFW #0354
                DEFW 316
                DEFW 612
                DEFB #98
                DEFW #06F4
                DEFW 332
                DEFW 648
                DEFB #98
                DEFW #0AC8
                DEFW 328
                DEFW 720
                DEFB #98
                DEFW #0EE0
                DEFW 344
                DEFW 764
                DEFB #98
                DEFW #1334
                DEFW 344
                DEFW 744
                DEFB #98
                DEFW #1774
                DEFW 344
                DEFW 700
                DEFB #98
                DEFW #1B88
                DEFW 348
                DEFW 664
                DEFB #98
                DEFW #1F7C
                DEFW 352
                DEFW 636
                DEFB #98
                DEFW #2358
                DEFW 332
                DEFW 588
                DEFB #98
                DEFW #26F0
                DEFW 324
                DEFW 552
                DEFB #98
                DEFW #2A5C
                DEFW 344
                DEFW 564
                DEFB #98
                DEFW #2DE8
                DEFW 344
                DEFW 612
                DEFB #98
                DEFW #31A4
                DEFW 324
                DEFW 612
                DEFB #98
                DEFW #354C
                DEFW 292
                DEFW 580
                DEFB #98
                DEFW #38B4
                DEFW 288
                DEFW 516
                DEFB #98
                DEFW #3BD8
                DEFW 244
                DEFW 464
                DEFB #99
                DEFW #0000
                DEFW 192
                DEFW 408
                DEFB #99
                DEFW #0258
                DEFW 172
                DEFW 336
                DEFB #99
                DEFW #0454
                DEFW 152
                DEFW 276
                DEFB #99
                DEFW #0600
                DEFW 152
                DEFW 244
                DEFB #99
                DEFW #078C
                DEFW 204
                DEFW 408
                DEFB #99
                DEFW #09F0
                DEFW 224
                DEFW 440
                DEFB #99
                DEFW #0C88
                DEFW 236
                DEFW 504
                DEFB #99
                DEFW #0F6C
                DEFW 284
                DEFW 548
                DEFB #99
                DEFW #12AC
                DEFW 300
                DEFW 600
                DEFB #99
                DEFW #1630
                DEFW 308
                DEFW 672
                DEFB #99
                DEFW #1A04
                DEFW 336
                DEFW 716
                DEFB #99
                DEFW #1E20
                DEFW 336
                DEFW 696
                DEFB #99
                DEFW #2228
                DEFW 336
                DEFW 636
                DEFB #99
                DEFW #25F4
                DEFW 340
                DEFW 588
                DEFB #99
                DEFW #2994
                DEFW 344
                DEFW 572
                DEFB #99
                DEFW #2D28
                DEFW 328
                DEFW 524
                DEFB #99
                DEFW #307C
                DEFW 324
                DEFW 488
                DEFB #99
                DEFW #33A8
                DEFW 344
                DEFW 500
                DEFB #99
                DEFW #36F4
                DEFW 344
                DEFW 536
                DEFB #99
                DEFW #3A64
                DEFW 324
                DEFW 552
                DEFB #9A
                DEFW #0000
                DEFW 292
                DEFW 536
                DEFB #9A
                DEFW #033C
                DEFW 288
                DEFW 472
                DEFB #9A
                DEFW #0634
                DEFW 244
                DEFW 420
                DEFB #9A
                DEFW #08CC
                DEFW 192
                DEFW 364
                DEFB #9A
                DEFW #0AF8
                DEFW 172
                DEFW 292
                DEFB #9A
                DEFW #0CC8
                DEFW 152
                DEFW 232
                DEFB #9A
                DEFW #0E48
                DEFW 152
                DEFW 200
                DEFB #9A
                DEFW #0FA8
                DEFW 200
                DEFW 328
                DEFB #9A
                DEFW #11B8
                DEFW 220
                DEFW 360
                DEFB #9A
                DEFW #13FC
                DEFW 236
                DEFW 424
                DEFB #9A
                DEFW #1690
                DEFW 284
                DEFW 452
                DEFB #9A
                DEFW #1970
                DEFW 300
                DEFW 488
                DEFB #9A
                DEFW #1C84
                DEFW 308
                DEFW 548
                DEFB #9A
                DEFW #1FDC
                DEFW 336
                DEFW 592
                DEFB #9A
                DEFW #237C
                DEFW 336
                DEFW 572
                DEFB #9A
                DEFW #2708
                DEFW 336
                DEFW 528
                DEFB #9A
                DEFW #2A68
                DEFW 340
                DEFW 496
                DEFB #9A
                DEFW #2DAC
                DEFW 344
                DEFW 496
                DEFB #9A
                DEFW #30F4
                DEFW 328
                DEFW 464
                DEFB #9A
                DEFW #340C
                DEFW 324
                DEFW 432
                DEFB #9A
                DEFW #3700
                DEFW 344
                DEFW 432
                DEFB #9A
                DEFW #3A08
                DEFW 344
                DEFW 448
                DEFB #9B
                DEFW #0000
                DEFW 324
                DEFW 464
                DEFB #9B
                DEFW #0314
                DEFW 292
                DEFW 448
                DEFB #9B
                DEFW #05F8
                DEFW 288
                DEFW 384
                DEFB #9B
                DEFW #0898
                DEFW 244
                DEFW 348
                DEFB #9B
                DEFW #0AE8
                DEFW 192
                DEFW 304
                DEFB #9B
                DEFW #0CD8
                DEFW 172
                DEFW 244
                DEFB #9B
                DEFW #0E78
                DEFW 152
                DEFW 184
                DEFB #9B
                DEFW #0FC8
                DEFW 152
                DEFW 152
                DEFB #9B
                DEFW #10F8
                DEFW 160
                DEFW 300
                DEFB #9B
                DEFW #12C4
                DEFW 180
                DEFW 332
                DEFB #9B
                DEFW #14C4
                DEFW 196
                DEFW 380
                DEFB #9B
                DEFW #1704
                DEFW 244
                DEFW 408
                DEFB #9B
                DEFW #1990
                DEFW 280
                DEFW 444
                DEFB #9B
                DEFW #1C64
                DEFW 304
                DEFW 504
                DEFB #9B
                DEFW #1F8C
                DEFW 332
                DEFW 548
                DEFB #9B
                DEFW #22FC
                DEFW 332
                DEFW 512
                DEFB #9B
                DEFW #2648
                DEFW 332
                DEFW 464
                DEFB #9B
                DEFW #2964
                DEFW 336
                DEFW 416
                DEFB #9B
                DEFW #2C54
                DEFW 340
                DEFW 416
                DEFB #9B
                DEFW #2F48
                DEFW 324
                DEFW 384
                DEFB #9B
                DEFW #320C
                DEFW 308
                DEFW 368
                DEFB #9B
                DEFW #34B0
                DEFW 328
                DEFW 368
                DEFB #9B
                DEFW #3768
                DEFW 328
                DEFW 384
                DEFB #9B
                DEFW #3A30
                DEFW 324
                DEFW 400
                DEFB #9B
                DEFW #3D04
                DEFW 292
                DEFW 384
                DEFB #9C
                DEFW #0000
                DEFW 288
                DEFW 336
                DEFB #9C
                DEFW #0270
                DEFW 244
                DEFW 300
                DEFB #9C
                DEFW #0490
                DEFW 192
                DEFW 256
                DEFB #9C
                DEFW #0650
                DEFW 172
                DEFW 196
                DEFB #9C
                DEFW #07C0
                DEFW 152
                DEFW 136
                DEFB #9C
                DEFW #08E0
                DEFW 152
                DEFW 120

PICKUP_COUNT            EQU 20
PickupAmounts:          DEFW 7, 4, 7, 4, 4, 4, 700


CompositeBank_SelectNext:
                LD   A, (CompositeDrawBank)
                XOR  1
                LD   (CompositeDrawBank), A
                OR   A
                JR   Z, .bank0
                LD   HL, #C400
                LD   (CompositeUploadOffsetLow), HL
                LD   A, #03
                LD   (CompositeUploadOffsetHigh), A
                RET
.bank0:        LD   HL, #0000
                LD   (CompositeUploadOffsetLow), HL
                XOR  A
                LD   (CompositeUploadOffsetHigh), A
                RET

CompositeUpload_AddBankOffset:
                PUSH HL
                LD   L, E
                LD   H, D
                LD   BC, (CompositeUploadOffsetLow)
                ADD  HL, BC
                EX   DE, HL
                LD   B, A
                LD   A, (CompositeUploadOffsetHigh)
                ADC  A, B
                POP  HL
                RET

CompositeTiles_UploadForScroll:
                CALL CompositeBank_SelectNext
                JP   CompositeTiles_UploadFull
                LD   A, (RuntimeLastOriginX)
                CP   #FF
                JP   Z, CompositeTiles_UploadFull
                LD   A, (ViewportOriginY)
                LD   B, A
                LD   A, (RuntimeLastOriginY)
                CP   B
                JR   NZ, CompositeUpload_CheckY
                LD   A, (ViewportOriginX)
                LD   B, A
                LD   A, (RuntimeLastOriginX)
                CP   B
                RET  Z
                INC  A
                CP   B
                JP   Z, CompositeTiles_UploadRight
                LD   A, (ViewportOriginX)
                INC  A
                LD   B, A
                LD   A, (RuntimeLastOriginX)
                CP   B
                JP   Z, CompositeTiles_UploadLeft
                JP   CompositeTiles_UploadFull
CompositeUpload_CheckY:
                LD   A, (ViewportOriginX)
                LD   B, A
                LD   A, (RuntimeLastOriginX)
                CP   B
                JP   NZ, CompositeTiles_UploadFull
                LD   A, (ViewportOriginY)
                LD   B, A
                LD   A, (RuntimeLastOriginY)
                INC  A
                CP   B
                JP   Z, CompositeTiles_UploadDown
                LD   A, (ViewportOriginY)
                INC  A
                LD   B, A
                LD   A, (RuntimeLastOriginY)
                CP   B
                JP   Z, CompositeTiles_UploadUp
                JP   CompositeTiles_UploadFull

CompositeTiles_UploadFull:
                CALL CompositeUpload_UploadPalette
                LD   A, (ViewportOriginX)
                LD   (CompositeUpload_StartX), A
                LD   A, (ViewportOriginY)
                LD   (CompositeUpload_StartY), A
                LD   A, 15
                LD   (CompositeUpload_RectW), A
                LD   A, 15
                LD   (CompositeUpload_RectH), A
                CALL CompositeUpload_ClampRect
                JP   CompositeUpload_Rect

CompositeTiles_UploadRight:
                LD   A, (ViewportOriginX)
                ADD  A, 14
                CP   36
                JR   C, .store_x
                LD   A, 35
.store_x:      LD   (CompositeUpload_StartX), A
                LD   A, (ViewportOriginY)
                LD   (CompositeUpload_StartY), A
                LD   A, 1
                LD   (CompositeUpload_RectW), A
                LD   A, 15
                LD   (CompositeUpload_RectH), A
                CALL CompositeUpload_ClampRect
                JP   CompositeUpload_Rect

CompositeTiles_UploadLeft:
                LD   A, (ViewportOriginX)
                LD   (CompositeUpload_StartX), A
                LD   A, (ViewportOriginY)
                LD   (CompositeUpload_StartY), A
                LD   A, 1
                LD   (CompositeUpload_RectW), A
                LD   A, 15
                LD   (CompositeUpload_RectH), A
                CALL CompositeUpload_ClampRect
                JP   CompositeUpload_Rect

CompositeTiles_UploadDown:
                LD   A, (ViewportOriginX)
                LD   (CompositeUpload_StartX), A
                LD   A, (ViewportOriginY)
                ADD  A, 14
                CP   36
                JR   C, .store_y
                LD   A, 35
.store_y:      LD   (CompositeUpload_StartY), A
                LD   A, 15
                LD   (CompositeUpload_RectW), A
                LD   A, 1
                LD   (CompositeUpload_RectH), A
                CALL CompositeUpload_ClampRect
                JP   CompositeUpload_Rect

CompositeTiles_UploadUp:
                LD   A, (ViewportOriginX)
                LD   (CompositeUpload_StartX), A
                LD   A, (ViewportOriginY)
                LD   (CompositeUpload_StartY), A
                LD   A, 15
                LD   (CompositeUpload_RectW), A
                LD   A, 1
                LD   (CompositeUpload_RectH), A
                CALL CompositeUpload_ClampRect
                JP   CompositeUpload_Rect

CompositeUpload_ClampRect:
                LD   A, (CompositeUpload_StartX)
                LD   B, A
                LD   A, 37
                SUB  B
                LD   B, A
                LD   A, (CompositeUpload_RectW)
                CP   B
                JR   C, .height
                JR   Z, .height
                LD   A, B
                LD   (CompositeUpload_RectW), A
.height:       LD   A, (CompositeUpload_StartY)
                LD   B, A
                LD   A, 37
                SUB  B
                LD   B, A
                LD   A, (CompositeUpload_RectH)
                CP   B
                RET  C
                RET  Z
                LD   A, B
                LD   (CompositeUpload_RectH), A
                RET

CompositeUpload_UploadPalette:
                LD   A, #20
                LD   (Render_DmaSourcePage), A
                LD   HL, #C000
                LD   A, #00
                LD   DE, #0000
                CALL CompositeUpload_AddBankOffset
                LD   BC, 512
                CALL Render_WriteMem_DMA
                RET

CompositeUpload_Rect:
                GetPage3
                LD   (CompositeUpload_RestorePage), A
                SetPage3 #C4
                CALL CompositeUploadCellPtr
CompositeUpload_RowLoop:
                LD   A, (CompositeUpload_RectW)
                LD   (CompositeUpload_ColCount), A
CompositeUpload_ColLoop:
                CALL CompositeUpload_Cell
                LD   BC, 6
                ADD  IX, BC
                LD   HL, CompositeUpload_ColCount
                DEC  (HL)
                JR   NZ, CompositeUpload_ColLoop
                LD   BC, (COMPOSITE_UPLOAD_STRIDE - 1) * 6
                LD   A, (CompositeUpload_RectW)
CompositeUpload_RowSkipLoop:
                DEC  A
                JR   Z, CompositeUpload_RowSkipDone
                LD   DE, -6
                ADD  IX, DE
                JR   CompositeUpload_RowSkipLoop
CompositeUpload_RowSkipDone:
                ADD  IX, BC
                LD   HL, CompositeUpload_RectH
                DEC  (HL)
                JR   NZ, CompositeUpload_RowLoop
CompositeUpload_RestorePage EQU $+1
                LD   A, #00
                SetPage3_A
                RET

CompositeUpload_Cell:
                LD   A, (IX + 0)
                LD   (Render_DmaSourcePage), A
                LD   L, (IX + 1)
                LD   H, (IX + 2)
                LD   DE, #C000
                ADD  HL, DE
                LD   A, (IX + 3)
                LD   E, (IX + 4)
                LD   D, (IX + 5)
                CALL CompositeUpload_AddBankOffset
                LD   BC, 1024
                CALL Render_WriteMem_DMA
                RET

CompositeUploadCellPtr:
                LD   HL, 0
                LD   A, (CompositeUpload_StartY)
                LD   B, A
                LD   DE, 222
                OR   A
                JR   Z, .x
.yloop:         ADD  HL, DE
                DJNZ .yloop
.x:             LD   A, (CompositeUpload_StartX)
                LD   E, A
                LD   D, 0
                ADD  HL, DE
                ADD  HL, DE
                ADD  HL, DE
                ADD  HL, DE
                ADD  HL, DE
                ADD  HL, DE
                LD   DE, #C000
                ADD  HL, DE
                PUSH HL
                POP  IX
                RET

CompositeUpload_StartX:
                DEFB 0
CompositeUpload_StartY:
                DEFB 0
CompositeUpload_RectW:
                DEFB 0
CompositeUpload_RectH:
                DEFB 0
CompositeUpload_ColCount:
                DEFB 0
CompositeDrawBank:
                DEFB 0
CompositeUploadOffsetLow:
                DEFW 0
CompositeUploadOffsetHigh:
                DEFB 0
