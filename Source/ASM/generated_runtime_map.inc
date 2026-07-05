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
                DEFW 220
                DEFB #01
                DEFW #015C
                DEFW 160
                DEFW 272
                DEFB #01
                DEFW #030C
                DEFW 180
                DEFW 316
                DEFB #01
                DEFW #04FC
                DEFW 184
                DEFW 360
                DEFB #01
                DEFW #071C
                DEFW 200
                DEFW 396
                DEFB #01
                DEFW #0970
                DEFW 228
                DEFW 384
                DEFB #01
                DEFW #0BD4
                DEFW 252
                DEFW 404
                DEFB #01
                DEFW #0E64
                DEFW 252
                DEFW 424
                DEFB #01
                DEFW #1108
                DEFW 252
                DEFW 472
                DEFB #01
                DEFW #13DC
                DEFW 268
                DEFW 536
                DEFB #01
                DEFW #1700
                DEFW 260
                DEFW 580
                DEFB #01
                DEFW #1A48
                DEFW 252
                DEFW 632
                DEFB #01
                DEFW #1DBC
                DEFW 264
                DEFW 672
                DEFB #01
                DEFW #2164
                DEFW 268
                DEFW 668
                DEFB #01
                DEFW #250C
                DEFW 284
                DEFW 660
                DEFB #01
                DEFW #28BC
                DEFW 296
                DEFW 664
                DEFB #01
                DEFW #2C7C
                DEFW 280
                DEFW 656
                DEFB #01
                DEFW #3024
                DEFW 268
                DEFW 680
                DEFB #01
                DEFW #33D8
                DEFW 268
                DEFW 660
                DEFB #01
                DEFW #3778
                DEFW 264
                DEFW 624
                DEFB #01
                DEFW #3AF0
                DEFW 228
                DEFW 604
                DEFB #02
                DEFW #0000
                DEFW 192
                DEFW 584
                DEFB #02
                DEFW #0308
                DEFW 192
                DEFW 564
                DEFB #02
                DEFW #05FC
                DEFW 128
                DEFW 220
                DEFB #02
                DEFW #0758
                DEFW 160
                DEFW 272
                DEFB #02
                DEFW #0908
                DEFW 180
                DEFW 316
                DEFB #02
                DEFW #0AF8
                DEFW 184
                DEFW 360
                DEFB #02
                DEFW #0D18
                DEFW 200
                DEFW 396
                DEFB #02
                DEFW #0F6C
                DEFW 228
                DEFW 384
                DEFB #02
                DEFW #11D0
                DEFW 252
                DEFW 404
                DEFB #02
                DEFW #1460
                DEFW 252
                DEFW 424
                DEFB #02
                DEFW #1704
                DEFW 252
                DEFW 472
                DEFB #02
                DEFW #19D8
                DEFW 268
                DEFW 536
                DEFB #02
                DEFW #1CFC
                DEFW 260
                DEFW 580
                DEFB #02
                DEFW #2044
                DEFW 252
                DEFW 632
                DEFB #02
                DEFW #23B8
                DEFW 264
                DEFW 676
                DEFB #02
                DEFW #2764
                DEFW 268
                DEFW 688
                DEFB #02
                DEFW #2B20
                DEFW 284
                DEFW 692
                DEFB #02
                DEFW #2EF0
                DEFW 296
                DEFW 696
                DEFB #02
                DEFW #32D0
                DEFW 280
                DEFW 688
                DEFB #02
                DEFW #3698
                DEFW 268
                DEFW 712
                DEFB #02
                DEFW #3A6C
                DEFW 268
                DEFW 692
                DEFB #03
                DEFW #0000
                DEFW 264
                DEFW 656
                DEFB #03
                DEFW #0398
                DEFW 228
                DEFW 636
                DEFB #03
                DEFW #06F8
                DEFW 192
                DEFW 616
                DEFB #03
                DEFW #0A20
                DEFW 192
                DEFW 596
                DEFB #03
                DEFW #0D34
                DEFW 128
                DEFW 248
                DEFB #03
                DEFW #0EAC
                DEFW 160
                DEFW 300
                DEFB #03
                DEFW #1078
                DEFW 180
                DEFW 344
                DEFB #03
                DEFW #1284
                DEFW 184
                DEFW 392
                DEFB #03
                DEFW #14C4
                DEFW 200
                DEFW 424
                DEFB #03
                DEFW #1734
                DEFW 228
                DEFW 412
                DEFB #03
                DEFW #19B4
                DEFW 252
                DEFW 432
                DEFB #03
                DEFW #1C60
                DEFW 252
                DEFW 440
                DEFB #03
                DEFW #1F14
                DEFW 252
                DEFW 472
                DEFB #03
                DEFW #21E8
                DEFW 268
                DEFW 536
                DEFB #03
                DEFW #250C
                DEFW 260
                DEFW 580
                DEFB #03
                DEFW #2854
                DEFW 252
                DEFW 632
                DEFB #03
                DEFW #2BC8
                DEFW 264
                DEFW 676
                DEFB #03
                DEFW #2F74
                DEFW 268
                DEFW 688
                DEFB #03
                DEFW #3330
                DEFW 284
                DEFW 692
                DEFB #03
                DEFW #3700
                DEFW 296
                DEFW 696
                DEFB #03
                DEFW #3AE0
                DEFW 280
                DEFW 688
                DEFB #04
                DEFW #0000
                DEFW 268
                DEFW 712
                DEFB #04
                DEFW #03D4
                DEFW 268
                DEFW 692
                DEFB #04
                DEFW #0794
                DEFW 264
                DEFW 656
                DEFB #04
                DEFW #0B2C
                DEFW 228
                DEFW 636
                DEFB #04
                DEFW #0E8C
                DEFW 192
                DEFW 616
                DEFB #04
                DEFW #11B4
                DEFW 192
                DEFW 596
                DEFB #04
                DEFW #14C8
                DEFW 128
                DEFW 296
                DEFB #04
                DEFW #1670
                DEFW 160
                DEFW 348
                DEFB #04
                DEFW #186C
                DEFW 180
                DEFW 392
                DEFB #04
                DEFW #1AA8
                DEFW 184
                DEFW 440
                DEFB #04
                DEFW #1D18
                DEFW 200
                DEFW 472
                DEFB #04
                DEFW #1FB8
                DEFW 228
                DEFW 444
                DEFB #04
                DEFW #2258
                DEFW 252
                DEFW 464
                DEFB #04
                DEFW #2524
                DEFW 252
                DEFW 472
                DEFB #04
                DEFW #27F8
                DEFW 252
                DEFW 504
                DEFB #04
                DEFW #2AEC
                DEFW 268
                DEFW 580
                DEFB #04
                DEFW #2E3C
                DEFW 260
                DEFW 608
                DEFB #04
                DEFW #31A0
                DEFW 256
                DEFW 644
                DEFB #04
                DEFW #3524
                DEFW 268
                DEFW 688
                DEFB #04
                DEFW #38E0
                DEFW 276
                DEFW 700
                DEFB #07
                DEFW #0000
                DEFW 280
                DEFW 704
                DEFB #07
                DEFW #03D8
                DEFW 280
                DEFW 692
                DEFB #07
                DEFW #07A4
                DEFW 264
                DEFW 684
                DEFB #07
                DEFW #0B58
                DEFW 252
                DEFW 692
                DEFB #07
                DEFW #0F08
                DEFW 252
                DEFW 656
                DEFB #07
                DEFW #1294
                DEFW 248
                DEFW 620
                DEFB #07
                DEFW #15F8
                DEFW 212
                DEFW 600
                DEFB #07
                DEFW #1924
                DEFW 188
                DEFW 580
                DEFB #07
                DEFW #1C24
                DEFW 188
                DEFW 560
                DEFB #07
                DEFW #1F10
                DEFW 128
                DEFW 296
                DEFB #07
                DEFW #20B8
                DEFW 160
                DEFW 348
                DEFB #07
                DEFW #22B4
                DEFW 180
                DEFW 392
                DEFB #07
                DEFW #24F0
                DEFW 184
                DEFW 440
                DEFB #07
                DEFW #2760
                DEFW 200
                DEFW 488
                DEFB #07
                DEFW #2A10
                DEFW 228
                DEFW 476
                DEFB #07
                DEFW #2CD0
                DEFW 252
                DEFW 512
                DEFB #07
                DEFW #2FCC
                DEFW 252
                DEFW 536
                DEFB #07
                DEFW #32E0
                DEFW 252
                DEFW 568
                DEFB #07
                DEFW #3614
                DEFW 268
                DEFW 644
                DEFB #07
                DEFW #39A4
                DEFW 260
                DEFW 684
                DEFB #08
                DEFW #0000
                DEFW 256
                DEFW 736
                DEFB #08
                DEFW #03E0
                DEFW 268
                DEFW 784
                DEFB #08
                DEFW #07FC
                DEFW 276
                DEFW 796
                DEFB #08
                DEFW #0C2C
                DEFW 280
                DEFW 800
                DEFB #08
                DEFW #1064
                DEFW 280
                DEFW 788
                DEFB #08
                DEFW #1490
                DEFW 264
                DEFW 780
                DEFB #08
                DEFW #18A4
                DEFW 252
                DEFW 788
                DEFB #08
                DEFW #1CB4
                DEFW 252
                DEFW 752
                DEFB #08
                DEFW #20A0
                DEFW 248
                DEFW 700
                DEFB #08
                DEFW #2454
                DEFW 212
                DEFW 664
                DEFB #08
                DEFW #27C0
                DEFW 188
                DEFW 628
                DEFB #08
                DEFW #2AF0
                DEFW 188
                DEFW 592
                DEFB #08
                DEFW #2DFC
                DEFW 160
                DEFW 308
                DEFB #08
                DEFW #2FD0
                DEFW 192
                DEFW 364
                DEFB #08
                DEFW #31FC
                DEFW 212
                DEFW 408
                DEFB #08
                DEFW #3468
                DEFW 216
                DEFW 452
                DEFB #08
                DEFW #3704
                DEFW 232
                DEFW 496
                DEFB #08
                DEFW #39DC
                DEFW 260
                DEFW 500
                DEFB #09
                DEFW #0000
                DEFW 284
                DEFW 536
                DEFB #09
                DEFW #0334
                DEFW 284
                DEFW 560
                DEFB #09
                DEFW #0680
                DEFW 284
                DEFW 608
                DEFB #09
                DEFW #09FC
                DEFW 300
                DEFW 700
                DEFB #09
                DEFW #0DE4
                DEFW 292
                DEFW 724
                DEFB #09
                DEFW #11DC
                DEFW 272
                DEFW 776
                DEFB #09
                DEFW #15F4
                DEFW 268
                DEFW 824
                DEFB #09
                DEFW #1A38
                DEFW 276
                DEFW 836
                DEFB #09
                DEFW #1E90
                DEFW 280
                DEFW 852
                DEFB #09
                DEFW #22FC
                DEFW 280
                DEFW 836
                DEFB #09
                DEFW #2758
                DEFW 264
                DEFW 824
                DEFB #09
                DEFW #2B98
                DEFW 252
                DEFW 832
                DEFB #09
                DEFW #2FD4
                DEFW 252
                DEFW 796
                DEFB #09
                DEFW #33EC
                DEFW 248
                DEFW 744
                DEFB #09
                DEFW #37CC
                DEFW 212
                DEFW 708
                DEFB #09
                DEFW #3B64
                DEFW 188
                DEFW 672
                DEFB #0A
                DEFW #0000
                DEFW 188
                DEFW 636
                DEFB #0A
                DEFW #0338
                DEFW 176
                DEFW 356
                DEFB #0A
                DEFW #054C
                DEFW 208
                DEFW 412
                DEFB #0A
                DEFW #07B8
                DEFW 212
                DEFW 440
                DEFB #0A
                DEFW #0A44
                DEFW 216
                DEFW 484
                DEFB #0A
                DEFW #0D00
                DEFW 232
                DEFW 532
                DEFB #0A
                DEFW #0FFC
                DEFW 260
                DEFW 568
                DEFB #0A
                DEFW #1338
                DEFW 284
                DEFW 616
                DEFB #0A
                DEFW #16BC
                DEFW 284
                DEFW 660
                DEFB #0A
                DEFW #1A6C
                DEFW 284
                DEFW 704
                DEFB #0A
                DEFW #1E48
                DEFW 300
                DEFW 780
                DEFB #0A
                DEFW #2280
                DEFW 292
                DEFW 792
                DEFB #0A
                DEFW #26BC
                DEFW 272
                DEFW 828
                DEFB #0A
                DEFW #2B08
                DEFW 268
                DEFW 860
                DEFB #0A
                DEFW #2F70
                DEFW 276
                DEFW 876
                DEFB #0A
                DEFW #33F0
                DEFW 280
                DEFW 896
                DEFB #0A
                DEFW #3888
                DEFW 280
                DEFW 880
                DEFB #0B
                DEFW #0000
                DEFW 264
                DEFW 868
                DEFB #0B
                DEFW #046C
                DEFW 252
                DEFW 880
                DEFB #0B
                DEFW #08D8
                DEFW 252
                DEFW 832
                DEFB #0B
                DEFW #0D14
                DEFW 248
                DEFW 772
                DEFB #0B
                DEFW #1110
                DEFW 212
                DEFW 720
                DEFB #0B
                DEFW #14B4
                DEFW 188
                DEFW 684
                DEFB #0B
                DEFW #181C
                DEFW 188
                DEFW 648
                DEFB #0B
                DEFW #1B60
                DEFW 228
                DEFW 368
                DEFB #0B
                DEFW #1DB4
                DEFW 260
                DEFW 408
                DEFB #0B
                DEFW #2050
                DEFW 264
                DEFW 424
                DEFB #0B
                DEFW #2300
                DEFW 268
                DEFW 468
                DEFB #0B
                DEFW #25E0
                DEFW 260
                DEFW 516
                DEFB #0B
                DEFW #28E8
                DEFW 264
                DEFW 564
                DEFB #0B
                DEFW #2C24
                DEFW 272
                DEFW 612
                DEFB #0B
                DEFW #2F98
                DEFW 272
                DEFW 660
                DEFB #0B
                DEFW #333C
                DEFW 272
                DEFW 696
                DEFB #0B
                DEFW #3704
                DEFW 288
                DEFW 776
                DEFB #0B
                DEFW #3B2C
                DEFW 268
                DEFW 772
                DEFB #0C
                DEFW #0000
                DEFW 236
                DEFW 792
                DEFB #0C
                DEFW #0404
                DEFW 232
                DEFW 808
                DEFB #0C
                DEFW #0814
                DEFW 240
                DEFW 824
                DEFB #0C
                DEFW #0C3C
                DEFW 244
                DEFW 856
                DEFB #0C
                DEFW #1088
                DEFW 240
                DEFW 856
                DEFB #0C
                DEFW #14D0
                DEFW 224
                DEFW 860
                DEFB #0C
                DEFW #190C
                DEFW 212
                DEFW 860
                DEFB #0C
                DEFW #1D3C
                DEFW 212
                DEFW 812
                DEFB #0C
                DEFW #213C
                DEFW 212
                DEFW 752
                DEFB #0C
                DEFW #2500
                DEFW 196
                DEFW 700
                DEFB #0C
                DEFW #2880
                DEFW 188
                DEFW 664
                DEFB #0C
                DEFW #2BD4
                DEFW 188
                DEFW 624
                DEFB #0C
                DEFW #2F00
                DEFW 240
                DEFW 424
                DEFB #0C
                DEFW #3198
                DEFW 292
                DEFW 464
                DEFB #0C
                DEFW #348C
                DEFW 296
                DEFW 480
                DEFB #0C
                DEFW #3794
                DEFW 300
                DEFW 524
                DEFB #0C
                DEFW #3ACC
                DEFW 284
                DEFW 588
                DEFB #0D
                DEFW #0000
                DEFW 272
                DEFW 652
                DEFB #0D
                DEFW #039C
                DEFW 280
                DEFW 700
                DEFB #0D
                DEFW #0770
                DEFW 280
                DEFW 748
                DEFB #0D
                DEFW #0B74
                DEFW 280
                DEFW 768
                DEFB #0D
                DEFW #0F8C
                DEFW 284
                DEFW 820
                DEFB #0D
                DEFW #13DC
                DEFW 268
                DEFW 816
                DEFB #0D
                DEFW #1818
                DEFW 248
                DEFW 808
                DEFB #0D
                DEFW #1C38
                DEFW 272
                DEFW 820
                DEFB #0D
                DEFW #207C
                DEFW 308
                DEFW 852
                DEFB #0D
                DEFW #2504
                DEFW 312
                DEFW 888
                DEFB #0D
                DEFW #29B4
                DEFW 304
                DEFW 888
                DEFB #0D
                DEFW #2E5C
                DEFW 284
                DEFW 892
                DEFB #0D
                DEFW #32F4
                DEFW 272
                DEFW 892
                DEFB #0D
                DEFW #3780
                DEFW 272
                DEFW 844
                DEFB #0D
                DEFW #3BDC
                DEFW 272
                DEFW 768
                DEFB #0E
                DEFW #0000
                DEFW 256
                DEFW 700
                DEFB #0E
                DEFW #03BC
                DEFW 248
                DEFW 664
                DEFB #0E
                DEFW #074C
                DEFW 248
                DEFW 624
                DEFB #0E
                DEFW #0AB4
                DEFW 240
                DEFW 440
                DEFB #0E
                DEFW #0D5C
                DEFW 292
                DEFW 480
                DEFB #0E
                DEFW #1060
                DEFW 296
                DEFW 496
                DEFB #0E
                DEFW #1378
                DEFW 300
                DEFW 556
                DEFB #0E
                DEFW #16D0
                DEFW 284
                DEFW 632
                DEFB #0E
                DEFW #1A64
                DEFW 276
                DEFW 700
                DEFB #0E
                DEFW #1E34
                DEFW 284
                DEFW 764
                DEFB #0E
                DEFW #224C
                DEFW 284
                DEFW 812
                DEFB #0E
                DEFW #2694
                DEFW 284
                DEFW 832
                DEFB #0E
                DEFW #2AF0
                DEFW 288
                DEFW 868
                DEFB #0E
                DEFW #2F74
                DEFW 272
                DEFW 852
                DEFB #0E
                DEFW #33D8
                DEFW 252
                DEFW 832
                DEFB #0E
                DEFW #3814
                DEFW 260
                DEFW 844
                DEFB #0F
                DEFW #0000
                DEFW 308
                DEFW 876
                DEFB #0F
                DEFW #04A0
                DEFW 312
                DEFW 892
                DEFB #0F
                DEFW #0954
                DEFW 304
                DEFW 888
                DEFB #0F
                DEFW #0DFC
                DEFW 284
                DEFW 888
                DEFB #0F
                DEFW #1290
                DEFW 272
                DEFW 888
                DEFB #0F
                DEFW #1718
                DEFW 272
                DEFW 836
                DEFB #0F
                DEFW #1B6C
                DEFW 272
                DEFW 756
                DEFB #0F
                DEFW #1F70
                DEFW 252
                DEFW 688
                DEFB #0F
                DEFW #231C
                DEFW 244
                DEFW 636
                DEFB #0F
                DEFW #268C
                DEFW 244
                DEFW 596
                DEFB #0F
                DEFW #29D4
                DEFW 240
                DEFW 440
                DEFB #0F
                DEFW #2C7C
                DEFW 276
                DEFW 464
                DEFB #0F
                DEFW #2F60
                DEFW 260
                DEFW 496
                DEFB #0F
                DEFW #3254
                DEFW 260
                DEFW 556
                DEFB #0F
                DEFW #3584
                DEFW 244
                DEFW 612
                DEFB #0F
                DEFW #38DC
                DEFW 236
                DEFW 652
                DEFB #0F
                DEFW #3C54
                DEFW 244
                DEFW 696
                DEFB #15
                DEFW #0000
                DEFW 244
                DEFW 732
                DEFB #15
                DEFW #03D0
                DEFW 244
                DEFW 752
                DEFB #15
                DEFW #07B4
                DEFW 248
                DEFW 776
                DEFB #15
                DEFW #0BB4
                DEFW 232
                DEFW 760
                DEFB #15
                DEFW #0F94
                DEFW 212
                DEFW 740
                DEFB #15
                DEFW #134C
                DEFW 192
                DEFW 752
                DEFB #15
                DEFW #16FC
                DEFW 224
                DEFW 784
                DEFB #15
                DEFW #1AEC
                DEFW 240
                DEFW 816
                DEFB #15
                DEFW #1F0C
                DEFW 232
                DEFW 840
                DEFB #15
                DEFW #233C
                DEFW 216
                DEFW 868
                DEFB #15
                DEFW #2778
                DEFW 224
                DEFW 864
                DEFB #15
                DEFW #2BB8
                DEFW 240
                DEFW 812
                DEFB #15
                DEFW #2FD4
                DEFW 240
                DEFW 732
                DEFB #15
                DEFW #33A0
                DEFW 220
                DEFW 664
                DEFB #15
                DEFW #3714
                DEFW 212
                DEFW 628
                DEFB #15
                DEFW #3A5C
                DEFW 212
                DEFW 600
                DEFB #16
                DEFW #0000
                DEFW 208
                DEFW 480
                DEFB #16
                DEFW #02B0
                DEFW 228
                DEFW 504
                DEFB #16
                DEFW #058C
                DEFW 212
                DEFW 536
                DEFB #16
                DEFW #0878
                DEFW 212
                DEFW 580
                DEFB #16
                DEFW #0B90
                DEFW 196
                DEFW 620
                DEFB #16
                DEFW #0EC0
                DEFW 188
                DEFW 660
                DEFB #16
                DEFW #1210
                DEFW 196
                DEFW 696
                DEFB #16
                DEFW #158C
                DEFW 196
                DEFW 724
                DEFB #16
                DEFW #1924
                DEFW 196
                DEFW 744
                DEFB #16
                DEFW #1CD0
                DEFW 200
                DEFW 764
                DEFB #16
                DEFW #2094
                DEFW 184
                DEFW 732
                DEFB #16
                DEFW #2428
                DEFW 164
                DEFW 712
                DEFB #16
                DEFW #2794
                DEFW 160
                DEFW 724
                DEFB #16
                DEFW #2B08
                DEFW 192
                DEFW 756
                DEFB #16
                DEFW #2EBC
                DEFW 208
                DEFW 772
                DEFB #16
                DEFW #3290
                DEFW 200
                DEFW 780
                DEFB #16
                DEFW #3664
                DEFW 200
                DEFW 792
                DEFB #16
                DEFW #3A44
                DEFW 220
                DEFW 772
                DEFB #17
                DEFW #0000
                DEFW 220
                DEFW 736
                DEFB #17
                DEFW #03BC
                DEFW 204
                DEFW 656
                DEFB #17
                DEFW #0718
                DEFW 184
                DEFW 588
                DEFB #17
                DEFW #0A1C
                DEFW 176
                DEFW 548
                DEFB #17
                DEFW #0CF0
                DEFW 176
                DEFW 520
                DEFB #17
                DEFW #0FA8
                DEFW 216
                DEFW 468
                DEFB #17
                DEFW #1254
                DEFW 236
                DEFW 476
                DEFB #17
                DEFW #151C
                DEFW 236
                DEFW 496
                DEFB #17
                DEFW #17F8
                DEFW 256
                DEFW 524
                DEFB #17
                DEFW #1B04
                DEFW 244
                DEFW 564
                DEFB #17
                DEFW #1E2C
                DEFW 232
                DEFW 604
                DEFB #17
                DEFW #2170
                DEFW 240
                DEFW 636
                DEFB #17
                DEFW #24DC
                DEFW 240
                DEFW 660
                DEFB #17
                DEFW #2860
                DEFW 240
                DEFW 672
                DEFB #17
                DEFW #2BF0
                DEFW 244
                DEFW 688
                DEFB #17
                DEFW #2F94
                DEFW 228
                DEFW 644
                DEFB #17
                DEFW #32FC
                DEFW 208
                DEFW 612
                DEFB #17
                DEFW #3630
                DEFW 200
                DEFW 608
                DEFB #17
                DEFW #3958
                DEFW 232
                DEFW 640
                DEFB #18
                DEFW #0000
                DEFW 248
                DEFW 656
                DEFB #18
                DEFW #0388
                DEFW 240
                DEFW 664
                DEFB #18
                DEFW #0710
                DEFW 240
                DEFW 672
                DEFB #18
                DEFW #0AA0
                DEFW 256
                DEFW 652
                DEFB #18
                DEFW #0E2C
                DEFW 236
                DEFW 632
                DEFB #18
                DEFW #1190
                DEFW 204
                DEFW 552
                DEFB #18
                DEFW #1484
                DEFW 184
                DEFW 476
                DEFB #18
                DEFW #1718
                DEFW 176
                DEFW 424
                DEFB #18
                DEFW #1970
                DEFW 176
                DEFW 400
                DEFB #18
                DEFW #1BB0
                DEFW 244
                DEFW 492
                DEFB #18
                DEFW #1E90
                DEFW 264
                DEFW 500
                DEFB #18
                DEFW #218C
                DEFW 276
                DEFW 520
                DEFB #18
                DEFW #24A8
                DEFW 312
                DEFW 536
                DEFB #18
                DEFW #27F8
                DEFW 312
                DEFW 548
                DEFB #18
                DEFW #2B54
                DEFW 296
                DEFW 604
                DEFB #18
                DEFW #2ED8
                DEFW 300
                DEFW 652
                DEFB #18
                DEFW #3290
                DEFW 300
                DEFW 672
                DEFB #18
                DEFW #365C
                DEFW 300
                DEFW 664
                DEFB #18
                DEFW #3A20
                DEFW 304
                DEFW 680
                DEFB #19
                DEFW #0000
                DEFW 288
                DEFW 636
                DEFB #19
                DEFW #039C
                DEFW 252
                DEFW 604
                DEFB #19
                DEFW #06F4
                DEFW 228
                DEFW 592
                DEFB #19
                DEFW #0A28
                DEFW 260
                DEFW 628
                DEFB #19
                DEFW #0DA0
                DEFW 276
                DEFW 644
                DEFB #19
                DEFW #1138
                DEFW 268
                DEFW 652
                DEFB #19
                DEFW #14D0
                DEFW 268
                DEFW 660
                DEFB #19
                DEFW #1870
                DEFW 284
                DEFW 640
                DEFB #19
                DEFW #1C0C
                DEFW 252
                DEFW 620
                DEFB #19
                DEFW #1F74
                DEFW 204
                DEFW 556
                DEFB #19
                DEFW #226C
                DEFW 184
                DEFW 460
                DEFB #19
                DEFW #24F0
                DEFW 176
                DEFW 396
                DEFB #19
                DEFW #272C
                DEFW 176
                DEFW 372
                DEFB #19
                DEFW #2950
                DEFW 236
                DEFW 508
                DEFB #19
                DEFW #2C38
                DEFW 256
                DEFW 516
                DEFB #19
                DEFW #2F3C
                DEFW 268
                DEFW 524
                DEFB #19
                DEFW #3254
                DEFW 316
                DEFW 540
                DEFB #19
                DEFW #35AC
                DEFW 328
                DEFW 552
                DEFB #19
                DEFW #391C
                DEFW 324
                DEFW 608
                DEFB #1A
                DEFW #0000
                DEFW 340
                DEFW 652
                DEFB #1A
                DEFW #03E0
                DEFW 340
                DEFW 672
                DEFB #1A
                DEFW #07D4
                DEFW 340
                DEFW 648
                DEFB #1A
                DEFW #0BB0
                DEFW 344
                DEFW 636
                DEFB #1A
                DEFW #0F84
                DEFW 332
                DEFW 592
                DEFB #1A
                DEFW #1320
                DEFW 300
                DEFW 532
                DEFB #1A
                DEFW #1660
                DEFW 276
                DEFW 504
                DEFB #1A
                DEFW #196C
                DEFW 308
                DEFW 540
                DEFB #1A
                DEFW #1CBC
                DEFW 324
                DEFW 556
                DEFB #1A
                DEFW #202C
                DEFW 304
                DEFW 564
                DEFB #1A
                DEFW #2390
                DEFW 288
                DEFW 572
                DEFB #1A
                DEFW #26EC
                DEFW 300
                DEFW 552
                DEFB #1A
                DEFW #2A40
                DEFW 256
                DEFW 532
                DEFB #1A
                DEFW #2D54
                DEFW 208
                DEFW 468
                DEFB #1A
                DEFW #2FF8
                DEFW 188
                DEFW 372
                DEFB #1A
                DEFW #3228
                DEFW 168
                DEFW 308
                DEFB #1A
                DEFW #3404
                DEFW 168
                DEFW 284
                DEFB #1A
                DEFW #35C8
                DEFW 204
                DEFW 504
                DEFB #1A
                DEFW #388C
                DEFW 236
                DEFW 508
                DEFB #1A
                DEFW #3B74
                DEFW 248
                DEFW 516
                DEFB #1B
                DEFW #0000
                DEFW 296
                DEFW 532
                DEFB #1B
                DEFW #033C
                DEFW 308
                DEFW 544
                DEFB #1B
                DEFW #0690
                DEFW 292
                DEFW 600
                DEFB #1B
                DEFW #0A0C
                DEFW 308
                DEFW 644
                DEFB #1B
                DEFW #0DC4
                DEFW 308
                DEFW 664
                DEFB #1B
                DEFW #1190
                DEFW 308
                DEFW 640
                DEFB #1B
                DEFW #1544
                DEFW 312
                DEFW 628
                DEFB #1B
                DEFW #18F0
                DEFW 316
                DEFW 584
                DEFB #1B
                DEFW #1C74
                DEFW 300
                DEFW 524
                DEFB #1B
                DEFW #1FAC
                DEFW 292
                DEFW 496
                DEFB #1B
                DEFW #22C0
                DEFW 324
                DEFW 516
                DEFB #1B
                DEFW #2608
                DEFW 340
                DEFW 548
                DEFB #1B
                DEFW #2980
                DEFW 320
                DEFW 560
                DEFB #1B
                DEFW #2CF0
                DEFW 288
                DEFW 572
                DEFB #1B
                DEFW #304C
                DEFW 284
                DEFW 552
                DEFB #1B
                DEFW #3390
                DEFW 240
                DEFW 532
                DEFB #1B
                DEFW #3694
                DEFW 192
                DEFW 468
                DEFB #1B
                DEFW #3928
                DEFW 172
                DEFW 372
                DEFB #1B
                DEFW #3B48
                DEFW 152
                DEFW 308
                DEFB #1B
                DEFW #3D14
                DEFW 152
                DEFW 284
                DEFB #1C
                DEFW #0000
                DEFW 204
                DEFW 504
                DEFB #1C
                DEFW #02C4
                DEFW 236
                DEFW 524
                DEFB #1C
                DEFW #05BC
                DEFW 248
                DEFW 548
                DEFB #1C
                DEFW #08D8
                DEFW 296
                DEFW 564
                DEFB #1C
                DEFW #0C34
                DEFW 308
                DEFW 576
                DEFB #1C
                DEFW #0FA8
                DEFW 292
                DEFW 632
                DEFB #1C
                DEFW #1344
                DEFW 308
                DEFW 676
                DEFB #1C
                DEFW #171C
                DEFW 308
                DEFW 696
                DEFB #1C
                DEFW #1B08
                DEFW 308
                DEFW 672
                DEFB #1C
                DEFW #1EDC
                DEFW 312
                DEFW 660
                DEFB #1C
                DEFW #22A8
                DEFW 316
                DEFW 616
                DEFB #1C
                DEFW #264C
                DEFW 300
                DEFW 556
                DEFB #1C
                DEFW #29A4
                DEFW 292
                DEFW 512
                DEFB #1C
                DEFW #2CC8
                DEFW 324
                DEFW 516
                DEFB #1C
                DEFW #3010
                DEFW 356
                DEFW 552
                DEFB #1C
                DEFW #339C
                DEFW 352
                DEFW 564
                DEFB #1C
                DEFW #3730
                DEFW 320
                DEFW 560
                DEFB #1C
                DEFW #3AA0
                DEFW 316
                DEFW 524
                DEFB #1D
                DEFW #0000
                DEFW 272
                DEFW 504
                DEFB #1D
                DEFW #0308
                DEFW 224
                DEFW 440
                DEFB #1D
                DEFW #05A0
                DEFW 204
                DEFW 344
                DEFB #1D
                DEFW #07C4
                DEFW 184
                DEFW 280
                DEFB #1D
                DEFW #0994
                DEFW 184
                DEFW 256
                DEFB #1D
                DEFW #0B4C
                DEFW 204
                DEFW 476
                DEFB #1D
                DEFW #0DF4
                DEFW 236
                DEFW 496
                DEFB #1D
                DEFW #10D0
                DEFW 248
                DEFW 520
                DEFB #1D
                DEFW #13D0
                DEFW 296
                DEFW 536
                DEFB #1D
                DEFW #1710
                DEFW 308
                DEFW 560
                DEFB #1D
                DEFW #1A74
                DEFW 292
                DEFW 624
                DEFB #1D
                DEFW #1E08
                DEFW 308
                DEFW 668
                DEFB #1D
                DEFW #21D8
                DEFW 308
                DEFW 692
                DEFB #1D
                DEFW #25C0
                DEFW 308
                DEFW 672
                DEFB #1D
                DEFW #2994
                DEFW 312
                DEFW 660
                DEFB #1D
                DEFW #2D60
                DEFW 316
                DEFW 616
                DEFB #1D
                DEFW #3104
                DEFW 300
                DEFW 556
                DEFB #1D
                DEFW #345C
                DEFW 292
                DEFW 512
                DEFB #1D
                DEFW #3780
                DEFW 324
                DEFW 516
                DEFB #1D
                DEFW #3AC8
                DEFW 356
                DEFW 552
                DEFB #1E
                DEFW #0000
                DEFW 352
                DEFW 564
                DEFB #1E
                DEFW #0394
                DEFW 320
                DEFW 560
                DEFB #1E
                DEFW #0704
                DEFW 316
                DEFW 524
                DEFB #1E
                DEFW #0A4C
                DEFW 272
                DEFW 504
                DEFB #1E
                DEFW #0D54
                DEFW 224
                DEFW 440
                DEFB #1E
                DEFW #0FEC
                DEFW 204
                DEFW 344
                DEFB #1E
                DEFW #1210
                DEFW 184
                DEFW 280
                DEFB #1E
                DEFW #13E0
                DEFW 184
                DEFW 256
                DEFB #1E
                DEFW #1598
                DEFW 236
                DEFW 428
                DEFB #1E
                DEFW #1830
                DEFW 256
                DEFW 448
                DEFB #1E
                DEFW #1AF0
                DEFW 268
                DEFW 488
                DEFB #1E
                DEFW #1DE4
                DEFW 316
                DEFW 508
                DEFB #1E
                DEFW #211C
                DEFW 332
                DEFW 532
                DEFB #1E
                DEFW #247C
                DEFW 328
                DEFW 600
                DEFB #1E
                DEFW #281C
                DEFW 344
                DEFW 644
                DEFB #1E
                DEFW #2BF8
                DEFW 344
                DEFW 668
                DEFB #1E
                DEFW #2FEC
                DEFW 344
                DEFW 648
                DEFB #1E
                DEFW #33CC
                DEFW 348
                DEFW 624
                DEFB #1E
                DEFW #3798
                DEFW 352
                DEFW 596
                DEFB #1E
                DEFW #3B4C
                DEFW 332
                DEFW 552
                DEFB #1F
                DEFW #0000
                DEFW 324
                DEFW 508
                DEFB #1F
                DEFW #0340
                DEFW 344
                DEFW 512
                DEFB #1F
                DEFW #0698
                DEFW 344
                DEFW 548
                DEFB #1F
                DEFW #0A14
                DEFW 324
                DEFW 560
                DEFB #1F
                DEFW #0D88
                DEFW 292
                DEFW 556
                DEFB #1F
                DEFW #10D8
                DEFW 288
                DEFW 516
                DEFB #1F
                DEFW #13FC
                DEFW 244
                DEFW 492
                DEFB #1F
                DEFW #16DC
                DEFW 192
                DEFW 428
                DEFB #1F
                DEFW #1948
                DEFW 172
                DEFW 332
                DEFB #1F
                DEFW #1B40
                DEFW 152
                DEFW 268
                DEFB #1F
                DEFW #1CE4
                DEFW 152
                DEFW 244
                DEFB #1F
                DEFW #1E70
                DEFW 236
                DEFW 428
                DEFB #1F
                DEFW #2108
                DEFW 256
                DEFW 452
                DEFB #1F
                DEFW #23CC
                DEFW 268
                DEFW 492
                DEFB #1F
                DEFW #26C4
                DEFW 316
                DEFW 512
                DEFB #1F
                DEFW #2A00
                DEFW 332
                DEFW 520
                DEFB #1F
                DEFW #2D54
                DEFW 328
                DEFW 572
                DEFB #1F
                DEFW #30D8
                DEFW 344
                DEFW 600
                DEFB #1F
                DEFW #3488
                DEFW 344
                DEFW 608
                DEFB #1F
                DEFW #3840
                DEFW 344
                DEFW 588
                DEFB #1F
                DEFW #3BE4
                DEFW 348
                DEFW 564
                DEFB #96
                DEFW #0000
                DEFW 352
                DEFW 532
                DEFB #96
                DEFW #0374
                DEFW 332
                DEFW 484
                DEFB #96
                DEFW #06A4
                DEFW 324
                DEFW 440
                DEFB #96
                DEFW #09A0
                DEFW 344
                DEFW 444
                DEFB #96
                DEFW #0CB4
                DEFW 344
                DEFW 480
                DEFB #96
                DEFW #0FEC
                DEFW 324
                DEFW 492
                DEFB #96
                DEFW #131C
                DEFW 292
                DEFW 484
                DEFB #96
                DEFW #1624
                DEFW 288
                DEFW 444
                DEFB #96
                DEFW #1900
                DEFW 244
                DEFW 420
                DEFB #96
                DEFW #1B98
                DEFW 192
                DEFW 372
                DEFB #96
                DEFW #1DCC
                DEFW 172
                DEFW 292
                DEFB #96
                DEFW #1F9C
                DEFW 152
                DEFW 244
                DEFB #96
                DEFW #2128
                DEFW 152
                DEFW 224
                DEFB #96
                DEFW #22A0
                DEFW 204
                DEFW 376
                DEFB #96
                DEFW #24E4
                DEFW 224
                DEFW 396
                DEFB #96
                DEFW #2750
                DEFW 236
                DEFW 436
                DEFB #96
                DEFW #29F0
                DEFW 284
                DEFW 460
                DEFB #96
                DEFW #2CD8
                DEFW 300
                DEFW 484
                DEFB #96
                DEFW #2FE8
                DEFW 308
                DEFW 548
                DEFB #96
                DEFW #3340
                DEFW 336
                DEFW 576
                DEFB #96
                DEFW #36D0
                DEFW 336
                DEFW 584
                DEFB #96
                DEFW #3A68
                DEFW 336
                DEFW 548
                DEFB #97
                DEFW #0000
                DEFW 340
                DEFW 520
                DEFB #97
                DEFW #035C
                DEFW 344
                DEFW 504
                DEFB #97
                DEFW #06AC
                DEFW 328
                DEFW 456
                DEFB #97
                DEFW #09BC
                DEFW 324
                DEFW 412
                DEFB #97
                DEFW #0C9C
                DEFW 344
                DEFW 416
                DEFB #97
                DEFW #0F94
                DEFW 344
                DEFW 436
                DEFB #97
                DEFW #12A0
                DEFW 324
                DEFW 452
                DEFB #97
                DEFW #15A8
                DEFW 292
                DEFW 448
                DEFB #97
                DEFW #188C
                DEFW 288
                DEFW 408
                DEFB #97
                DEFW #1B44
                DEFW 244
                DEFW 384
                DEFB #97
                DEFW #1DB8
                DEFW 192
                DEFW 336
                DEFB #97
                DEFW #1FC8
                DEFW 172
                DEFW 256
                DEFB #97
                DEFW #2174
                DEFW 152
                DEFW 196
                DEFB #97
                DEFW #22D0
                DEFW 152
                DEFW 176
                DEFB #97
                DEFW #2418
                DEFW 200
                DEFW 296
                DEFB #97
                DEFW #2608
                DEFW 220
                DEFW 316
                DEFB #97
                DEFW #2820
                DEFW 236
                DEFW 356
                DEFB #97
                DEFW #2A70
                DEFW 284
                DEFW 364
                DEFB #97
                DEFW #2CF8
                DEFW 300
                DEFW 372
                DEFB #97
                DEFW #2F98
                DEFW 308
                DEFW 424
                DEFB #97
                DEFW #3274
                DEFW 336
                DEFW 452
                DEFB #97
                DEFW #3588
                DEFW 336
                DEFW 460
                DEFB #97
                DEFW #38A4
                DEFW 336
                DEFW 436
                DEFB #97
                DEFW #3BA8
                DEFW 340
                DEFW 428
                DEFB #98
                DEFW #0000
                DEFW 344
                DEFW 428
                DEFB #98
                DEFW #0304
                DEFW 328
                DEFW 396
                DEFB #98
                DEFW #05D8
                DEFW 324
                DEFW 364
                DEFB #98
                DEFW #0888
                DEFW 344
                DEFW 364
                DEFB #98
                DEFW #0B4C
                DEFW 344
                DEFW 380
                DEFB #98
                DEFW #0E20
                DEFW 324
                DEFW 396
                DEFB #98
                DEFW #10F0
                DEFW 292
                DEFW 392
                DEFB #98
                DEFW #139C
                DEFW 288
                DEFW 352
                DEFB #98
                DEFW #161C
                DEFW 244
                DEFW 344
                DEFB #98
                DEFW #1868
                DEFW 192
                DEFW 308
                DEFB #98
                DEFW #1A5C
                DEFW 172
                DEFW 244
                DEFB #98
                DEFW #1BFC
                DEFW 152
                DEFW 184
                DEFB #98
                DEFW #1D4C
                DEFW 152
                DEFW 152
                DEFB #98
                DEFW #1E7C
                DEFW 160
                DEFW 268
                DEFB #98
                DEFW #2028
                DEFW 180
                DEFW 288
                DEFB #98
                DEFW #21FC
                DEFW 196
                DEFW 312
                DEFB #98
                DEFW #23F8
                DEFW 244
                DEFW 320
                DEFB #98
                DEFW #262C
                DEFW 280
                DEFW 328
                DEFB #98
                DEFW #288C
                DEFW 304
                DEFW 380
                DEFB #98
                DEFW #2B38
                DEFW 332
                DEFW 408
                DEFB #98
                DEFW #2E1C
                DEFW 332
                DEFW 400
                DEFB #98
                DEFW #30F8
                DEFW 332
                DEFW 376
                DEFB #98
                DEFW #33BC
                DEFW 336
                DEFW 348
                DEFB #98
                DEFW #3668
                DEFW 340
                DEFW 348
                DEFB #98
                DEFW #3918
                DEFW 324
                DEFW 316
                DEFB #98
                DEFW #3B98
                DEFW 308
                DEFW 300
                DEFB #99
                DEFW #0000
                DEFW 328
                DEFW 300
                DEFB #99
                DEFW #0274
                DEFW 328
                DEFW 316
                DEFB #99
                DEFW #04F8
                DEFW 324
                DEFW 332
                DEFB #99
                DEFW #0788
                DEFW 292
                DEFW 328
                DEFB #99
                DEFW #09F4
                DEFW 288
                DEFW 304
                DEFB #99
                DEFW #0C44
                DEFW 244
                DEFW 296
                DEFB #99
                DEFW #0E60
                DEFW 192
                DEFW 260
                DEFB #99
                DEFW #1024
                DEFW 172
                DEFW 196
                DEFB #99
                DEFW #1194
                DEFW 152
                DEFW 136
                DEFB #99
                DEFW #12B4
                DEFW 152
                DEFW 120

PICKUP_COUNT            EQU 20
PickupList:
                DEFB 19, 6, 3
                DEFB 20, 6, 3
                DEFB 23, 7, 0
                DEFB 17, 9, 1
                DEFB 27, 9, 0
                DEFB 12, 10, 1
                DEFB 33, 10, 5
                DEFB 10, 13, 3
                DEFB 19, 13, 2
                DEFB 10, 14, 3
                DEFB 11, 19, 4
                DEFB 4, 21, 6
                DEFB 15, 22, 2
                DEFB 24, 22, 4
                DEFB 27, 22, 6
                DEFB 20, 23, 4
                DEFB 17, 26, 5
                DEFB 18, 26, 5
                DEFB 15, 29, 0
                DEFB 14, 32, 0
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
