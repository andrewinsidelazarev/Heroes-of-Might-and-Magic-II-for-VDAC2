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
                DEFW 248
                DEFW 404
                DEFB #01
                DEFW #0E60
                DEFW 248
                DEFW 424
                DEFB #01
                DEFW #1100
                DEFW 248
                DEFW 472
                DEFB #01
                DEFW #13D0
                DEFW 264
                DEFW 536
                DEFB #01
                DEFW #16F0
                DEFW 256
                DEFW 580
                DEFB #01
                DEFW #1A34
                DEFW 248
                DEFW 632
                DEFB #01
                DEFW #1DA4
                DEFW 268
                DEFW 672
                DEFB #01
                DEFW #2150
                DEFW 280
                DEFW 668
                DEFB #01
                DEFW #2504
                DEFW 296
                DEFW 660
                DEFB #01
                DEFW #28C0
                DEFW 308
                DEFW 664
                DEFB #01
                DEFW #2C8C
                DEFW 292
                DEFW 656
                DEFB #01
                DEFW #3040
                DEFW 280
                DEFW 680
                DEFB #01
                DEFW #3400
                DEFW 280
                DEFW 660
                DEFB #01
                DEFW #37AC
                DEFW 276
                DEFW 624
                DEFB #01
                DEFW #3B30
                DEFW 240
                DEFW 604
                DEFB #02
                DEFW #0000
                DEFW 200
                DEFW 584
                DEFB #02
                DEFW #0310
                DEFW 200
                DEFW 564
                DEFB #02
                DEFW #060C
                DEFW 128
                DEFW 220
                DEFB #02
                DEFW #0768
                DEFW 160
                DEFW 272
                DEFB #02
                DEFW #0918
                DEFW 180
                DEFW 316
                DEFB #02
                DEFW #0B08
                DEFW 184
                DEFW 360
                DEFB #02
                DEFW #0D28
                DEFW 200
                DEFW 396
                DEFB #02
                DEFW #0F7C
                DEFW 228
                DEFW 384
                DEFB #02
                DEFW #11E0
                DEFW 248
                DEFW 404
                DEFB #02
                DEFW #146C
                DEFW 248
                DEFW 424
                DEFB #02
                DEFW #170C
                DEFW 248
                DEFW 472
                DEFB #02
                DEFW #19DC
                DEFW 264
                DEFW 536
                DEFB #02
                DEFW #1CFC
                DEFW 256
                DEFW 580
                DEFB #02
                DEFW #2040
                DEFW 248
                DEFW 632
                DEFB #02
                DEFW #23B0
                DEFW 268
                DEFW 676
                DEFB #02
                DEFW #2760
                DEFW 280
                DEFW 688
                DEFB #02
                DEFW #2B28
                DEFW 296
                DEFW 692
                DEFB #02
                DEFW #2F04
                DEFW 308
                DEFW 696
                DEFB #02
                DEFW #32F0
                DEFW 292
                DEFW 688
                DEFB #02
                DEFW #36C4
                DEFW 280
                DEFW 712
                DEFB #02
                DEFW #3AA4
                DEFW 280
                DEFW 692
                DEFB #03
                DEFW #0000
                DEFW 276
                DEFW 656
                DEFB #03
                DEFW #03A4
                DEFW 240
                DEFW 636
                DEFB #03
                DEFW #0710
                DEFW 200
                DEFW 616
                DEFB #03
                DEFW #0A40
                DEFW 200
                DEFW 596
                DEFB #03
                DEFW #0D5C
                DEFW 128
                DEFW 248
                DEFB #03
                DEFW #0ED4
                DEFW 160
                DEFW 300
                DEFB #03
                DEFW #10A0
                DEFW 180
                DEFW 344
                DEFB #03
                DEFW #12AC
                DEFW 184
                DEFW 392
                DEFB #03
                DEFW #14EC
                DEFW 200
                DEFW 424
                DEFB #03
                DEFW #175C
                DEFW 228
                DEFW 412
                DEFB #03
                DEFW #19DC
                DEFW 248
                DEFW 432
                DEFB #03
                DEFW #1C84
                DEFW 248
                DEFW 440
                DEFB #03
                DEFW #1F34
                DEFW 248
                DEFW 472
                DEFB #03
                DEFW #2204
                DEFW 264
                DEFW 536
                DEFB #03
                DEFW #2524
                DEFW 256
                DEFW 580
                DEFB #03
                DEFW #2868
                DEFW 248
                DEFW 632
                DEFB #03
                DEFW #2BD8
                DEFW 268
                DEFW 676
                DEFB #03
                DEFW #2F88
                DEFW 280
                DEFW 688
                DEFB #03
                DEFW #3350
                DEFW 296
                DEFW 692
                DEFB #03
                DEFW #372C
                DEFW 308
                DEFW 696
                DEFB #03
                DEFW #3B18
                DEFW 292
                DEFW 688
                DEFB #04
                DEFW #0000
                DEFW 280
                DEFW 712
                DEFB #04
                DEFW #03E0
                DEFW 280
                DEFW 692
                DEFB #04
                DEFW #07AC
                DEFW 276
                DEFW 656
                DEFB #04
                DEFW #0B50
                DEFW 240
                DEFW 636
                DEFB #04
                DEFW #0EBC
                DEFW 200
                DEFW 616
                DEFB #04
                DEFW #11EC
                DEFW 200
                DEFW 596
                DEFB #04
                DEFW #1508
                DEFW 128
                DEFW 296
                DEFB #04
                DEFW #16B0
                DEFW 160
                DEFW 348
                DEFB #04
                DEFW #18AC
                DEFW 180
                DEFW 392
                DEFB #04
                DEFW #1AE8
                DEFW 184
                DEFW 440
                DEFB #04
                DEFW #1D58
                DEFW 200
                DEFW 472
                DEFB #04
                DEFW #1FF8
                DEFW 228
                DEFW 444
                DEFB #04
                DEFW #2298
                DEFW 248
                DEFW 464
                DEFB #04
                DEFW #2560
                DEFW 248
                DEFW 472
                DEFB #04
                DEFW #2830
                DEFW 248
                DEFW 504
                DEFB #04
                DEFW #2B20
                DEFW 264
                DEFW 580
                DEFB #04
                DEFW #2E6C
                DEFW 256
                DEFW 608
                DEFB #04
                DEFW #31CC
                DEFW 252
                DEFW 644
                DEFB #04
                DEFW #354C
                DEFW 272
                DEFW 688
                DEFB #04
                DEFW #390C
                DEFW 288
                DEFW 700
                DEFB #07
                DEFW #0000
                DEFW 292
                DEFW 704
                DEFB #07
                DEFW #03E4
                DEFW 292
                DEFW 692
                DEFB #07
                DEFW #07BC
                DEFW 276
                DEFW 684
                DEFB #07
                DEFW #0B7C
                DEFW 264
                DEFW 692
                DEFB #07
                DEFW #0F38
                DEFW 264
                DEFW 656
                DEFB #07
                DEFW #12D0
                DEFW 260
                DEFW 620
                DEFB #07
                DEFW #1640
                DEFW 224
                DEFW 600
                DEFB #07
                DEFW #1978
                DEFW 192
                DEFW 580
                DEFB #07
                DEFW #1C7C
                DEFW 192
                DEFW 560
                DEFB #07
                DEFW #1F6C
                DEFW 128
                DEFW 296
                DEFB #07
                DEFW #2114
                DEFW 160
                DEFW 348
                DEFB #07
                DEFW #2310
                DEFW 180
                DEFW 392
                DEFB #07
                DEFW #254C
                DEFW 184
                DEFW 440
                DEFB #07
                DEFW #27BC
                DEFW 200
                DEFW 488
                DEFB #07
                DEFW #2A6C
                DEFW 228
                DEFW 476
                DEFB #07
                DEFW #2D2C
                DEFW 248
                DEFW 512
                DEFB #07
                DEFW #3024
                DEFW 248
                DEFW 536
                DEFB #07
                DEFW #3334
                DEFW 248
                DEFW 568
                DEFB #07
                DEFW #3664
                DEFW 264
                DEFW 644
                DEFB #07
                DEFW #39F0
                DEFW 256
                DEFW 684
                DEFB #08
                DEFW #0000
                DEFW 252
                DEFW 736
                DEFB #08
                DEFW #03DC
                DEFW 272
                DEFW 784
                DEFB #08
                DEFW #07FC
                DEFW 288
                DEFW 796
                DEFB #08
                DEFW #0C38
                DEFW 292
                DEFW 800
                DEFB #08
                DEFW #107C
                DEFW 292
                DEFW 788
                DEFB #08
                DEFW #14B4
                DEFW 276
                DEFW 780
                DEFB #08
                DEFW #18D4
                DEFW 264
                DEFW 788
                DEFB #08
                DEFW #1CF0
                DEFW 264
                DEFW 752
                DEFB #08
                DEFW #20E8
                DEFW 260
                DEFW 700
                DEFB #08
                DEFW #24A8
                DEFW 224
                DEFW 664
                DEFB #08
                DEFW #2820
                DEFW 192
                DEFW 628
                DEFB #08
                DEFW #2B54
                DEFW 192
                DEFW 592
                DEFB #08
                DEFW #2E64
                DEFW 160
                DEFW 308
                DEFB #08
                DEFW #3038
                DEFW 192
                DEFW 364
                DEFB #08
                DEFW #3264
                DEFW 212
                DEFW 408
                DEFB #08
                DEFW #34D0
                DEFW 216
                DEFW 452
                DEFB #08
                DEFW #376C
                DEFW 232
                DEFW 496
                DEFB #08
                DEFW #3A44
                DEFW 260
                DEFW 500
                DEFB #09
                DEFW #0000
                DEFW 280
                DEFW 536
                DEFB #09
                DEFW #0330
                DEFW 280
                DEFW 560
                DEFB #09
                DEFW #0678
                DEFW 280
                DEFW 608
                DEFB #09
                DEFW #09F0
                DEFW 296
                DEFW 700
                DEFB #09
                DEFW #0DD4
                DEFW 288
                DEFW 724
                DEFB #09
                DEFW #11C8
                DEFW 268
                DEFW 776
                DEFB #09
                DEFW #15DC
                DEFW 272
                DEFW 824
                DEFB #09
                DEFW #1A24
                DEFW 288
                DEFW 836
                DEFB #09
                DEFW #1E88
                DEFW 292
                DEFW 852
                DEFB #09
                DEFW #2300
                DEFW 292
                DEFW 836
                DEFB #09
                DEFW #2768
                DEFW 276
                DEFW 824
                DEFB #09
                DEFW #2BB4
                DEFW 264
                DEFW 832
                DEFB #09
                DEFW #2FFC
                DEFW 264
                DEFW 796
                DEFB #09
                DEFW #3420
                DEFW 260
                DEFW 744
                DEFB #09
                DEFW #380C
                DEFW 224
                DEFW 708
                DEFB #09
                DEFW #3BB0
                DEFW 192
                DEFW 672
                DEFB #0A
                DEFW #0000
                DEFW 192
                DEFW 636
                DEFB #0A
                DEFW #033C
                DEFW 176
                DEFW 356
                DEFB #0A
                DEFW #0550
                DEFW 208
                DEFW 412
                DEFB #0A
                DEFW #07BC
                DEFW 212
                DEFW 440
                DEFB #0A
                DEFW #0A48
                DEFW 216
                DEFW 484
                DEFB #0A
                DEFW #0D04
                DEFW 232
                DEFW 532
                DEFB #0A
                DEFW #1000
                DEFW 260
                DEFW 568
                DEFB #0A
                DEFW #133C
                DEFW 280
                DEFW 616
                DEFB #0A
                DEFW #16BC
                DEFW 280
                DEFW 660
                DEFB #0A
                DEFW #1A68
                DEFW 280
                DEFW 704
                DEFB #0A
                DEFW #1E40
                DEFW 296
                DEFW 780
                DEFB #0A
                DEFW #2274
                DEFW 288
                DEFW 792
                DEFB #0A
                DEFW #26AC
                DEFW 268
                DEFW 828
                DEFB #0A
                DEFW #2AF4
                DEFW 272
                DEFW 860
                DEFB #0A
                DEFW #2F60
                DEFW 288
                DEFW 876
                DEFB #0A
                DEFW #33EC
                DEFW 292
                DEFW 896
                DEFB #0A
                DEFW #3890
                DEFW 292
                DEFW 880
                DEFB #0B
                DEFW #0000
                DEFW 276
                DEFW 868
                DEFB #0B
                DEFW #0478
                DEFW 264
                DEFW 880
                DEFB #0B
                DEFW #08F0
                DEFW 264
                DEFW 832
                DEFB #0B
                DEFW #0D38
                DEFW 260
                DEFW 772
                DEFB #0B
                DEFW #1140
                DEFW 224
                DEFW 720
                DEFB #0B
                DEFW #14F0
                DEFW 192
                DEFW 684
                DEFB #0B
                DEFW #185C
                DEFW 192
                DEFW 648
                DEFB #0B
                DEFW #1BA4
                DEFW 232
                DEFW 368
                DEFB #0B
                DEFW #1DFC
                DEFW 264
                DEFW 408
                DEFB #0B
                DEFW #209C
                DEFW 268
                DEFW 424
                DEFB #0B
                DEFW #2350
                DEFW 272
                DEFW 468
                DEFB #0B
                DEFW #2634
                DEFW 256
                DEFW 516
                DEFB #0B
                DEFW #2938
                DEFW 260
                DEFW 564
                DEFB #0B
                DEFW #2C70
                DEFW 268
                DEFW 612
                DEFB #0B
                DEFW #2FE0
                DEFW 268
                DEFW 660
                DEFB #0B
                DEFW #3380
                DEFW 268
                DEFW 696
                DEFB #0B
                DEFW #3744
                DEFW 284
                DEFW 776
                DEFB #0B
                DEFW #3B68
                DEFW 264
                DEFW 772
                DEFB #0C
                DEFW #0000
                DEFW 232
                DEFW 792
                DEFB #0C
                DEFW #0400
                DEFW 236
                DEFW 808
                DEFB #0C
                DEFW #0814
                DEFW 252
                DEFW 824
                DEFB #0C
                DEFW #0C48
                DEFW 256
                DEFW 856
                DEFB #0C
                DEFW #10A0
                DEFW 252
                DEFW 856
                DEFB #0C
                DEFW #14F4
                DEFW 236
                DEFW 860
                DEFB #0C
                DEFW #193C
                DEFW 224
                DEFW 860
                DEFB #0C
                DEFW #1D78
                DEFW 224
                DEFW 812
                DEFB #0C
                DEFW #2184
                DEFW 224
                DEFW 752
                DEFB #0C
                DEFW #2554
                DEFW 208
                DEFW 700
                DEFB #0C
                DEFW #28E0
                DEFW 192
                DEFW 664
                DEFB #0C
                DEFW #2C38
                DEFW 192
                DEFW 624
                DEFB #0C
                DEFW #2F68
                DEFW 244
                DEFW 424
                DEFB #0C
                DEFW #3204
                DEFW 296
                DEFW 464
                DEFB #0C
                DEFW #34FC
                DEFW 300
                DEFW 480
                DEFB #0C
                DEFW #3808
                DEFW 304
                DEFW 524
                DEFB #0C
                DEFW #3B44
                DEFW 280
                DEFW 588
                DEFB #0D
                DEFW #0000
                DEFW 268
                DEFW 652
                DEFB #0D
                DEFW #0398
                DEFW 276
                DEFW 700
                DEFB #0D
                DEFW #0768
                DEFW 276
                DEFW 748
                DEFB #0D
                DEFW #0B68
                DEFW 276
                DEFW 768
                DEFB #0D
                DEFW #0F7C
                DEFW 280
                DEFW 820
                DEFB #0D
                DEFW #13C8
                DEFW 264
                DEFW 816
                DEFB #0D
                DEFW #1800
                DEFW 244
                DEFW 808
                DEFB #0D
                DEFW #1C1C
                DEFW 276
                DEFW 820
                DEFB #0D
                DEFW #2064
                DEFW 320
                DEFW 852
                DEFB #0D
                DEFW #24F8
                DEFW 324
                DEFW 888
                DEFB #0D
                DEFW #29B4
                DEFW 316
                DEFW 888
                DEFB #0D
                DEFW #2E68
                DEFW 296
                DEFW 892
                DEFB #0D
                DEFW #330C
                DEFW 284
                DEFW 892
                DEFB #0D
                DEFW #37A4
                DEFW 284
                DEFW 844
                DEFB #0E
                DEFW #0000
                DEFW 284
                DEFW 768
                DEFB #0E
                DEFW #041C
                DEFW 268
                DEFW 700
                DEFB #0E
                DEFW #07E4
                DEFW 252
                DEFW 664
                DEFB #0E
                DEFW #0B78
                DEFW 252
                DEFW 624
                DEFB #0E
                DEFW #0EE4
                DEFW 244
                DEFW 440
                DEFB #0E
                DEFW #1190
                DEFW 296
                DEFW 480
                DEFB #0E
                DEFW #1498
                DEFW 300
                DEFW 496
                DEFB #0E
                DEFW #17B4
                DEFW 304
                DEFW 556
                DEFB #0E
                DEFW #1B10
                DEFW 280
                DEFW 632
                DEFB #0E
                DEFW #1EA0
                DEFW 272
                DEFW 700
                DEFB #0E
                DEFW #226C
                DEFW 280
                DEFW 764
                DEFB #0E
                DEFW #2680
                DEFW 280
                DEFW 812
                DEFB #0E
                DEFW #2AC4
                DEFW 280
                DEFW 832
                DEFB #0E
                DEFW #2F1C
                DEFW 284
                DEFW 868
                DEFB #0E
                DEFW #339C
                DEFW 268
                DEFW 852
                DEFB #0E
                DEFW #37FC
                DEFW 248
                DEFW 832
                DEFB #0F
                DEFW #0000
                DEFW 260
                DEFW 844
                DEFB #0F
                DEFW #0450
                DEFW 304
                DEFW 876
                DEFB #0F
                DEFW #08EC
                DEFW 308
                DEFW 892
                DEFB #0F
                DEFW #0D9C
                DEFW 300
                DEFW 888
                DEFB #0F
                DEFW #1240
                DEFW 280
                DEFW 888
                DEFB #0F
                DEFW #16D0
                DEFW 268
                DEFW 888
                DEFB #0F
                DEFW #1B54
                DEFW 268
                DEFW 836
                DEFB #0F
                DEFW #1FA4
                DEFW 268
                DEFW 756
                DEFB #0F
                DEFW #23A4
                DEFW 248
                DEFW 688
                DEFB #0F
                DEFW #274C
                DEFW 240
                DEFW 636
                DEFB #0F
                DEFW #2AB8
                DEFW 240
                DEFW 596
                DEFB #0F
                DEFW #2DFC
                DEFW 244
                DEFW 440
                DEFB #0F
                DEFW #30A8
                DEFW 280
                DEFW 464
                DEFB #0F
                DEFW #3390
                DEFW 264
                DEFW 496
                DEFB #0F
                DEFW #3688
                DEFW 264
                DEFW 556
                DEFB #0F
                DEFW #39BC
                DEFW 240
                DEFW 612
                DEFB #15
                DEFW #0000
                DEFW 232
                DEFW 652
                DEFB #15
                DEFW #0374
                DEFW 240
                DEFW 696
                DEFB #15
                DEFW #071C
                DEFW 240
                DEFW 732
                DEFB #15
                DEFW #0AE8
                DEFW 240
                DEFW 752
                DEFB #15
                DEFW #0EC8
                DEFW 244
                DEFW 776
                DEFB #15
                DEFW #12C4
                DEFW 228
                DEFW 760
                DEFB #15
                DEFW #16A0
                DEFW 208
                DEFW 740
                DEFB #15
                DEFW #1A54
                DEFW 192
                DEFW 752
                DEFB #15
                DEFW #1E04
                DEFW 220
                DEFW 784
                DEFB #15
                DEFW #21F0
                DEFW 236
                DEFW 816
                DEFB #15
                DEFW #260C
                DEFW 228
                DEFW 840
                DEFB #15
                DEFW #2A38
                DEFW 212
                DEFW 868
                DEFB #15
                DEFW #2E70
                DEFW 220
                DEFW 864
                DEFB #15
                DEFW #32AC
                DEFW 236
                DEFW 812
                DEFB #15
                DEFW #36C4
                DEFW 236
                DEFW 732
                DEFB #15
                DEFW #3A8C
                DEFW 216
                DEFW 664
                DEFB #16
                DEFW #0000
                DEFW 208
                DEFW 628
                DEFB #16
                DEFW #0344
                DEFW 208
                DEFW 600
                DEFB #16
                DEFW #066C
                DEFW 212
                DEFW 480
                DEFB #16
                DEFW #0920
                DEFW 232
                DEFW 504
                DEFB #16
                DEFW #0C00
                DEFW 216
                DEFW 536
                DEFB #16
                DEFW #0EF0
                DEFW 216
                DEFW 580
                DEFB #16
                DEFW #120C
                DEFW 192
                DEFW 620
                DEFB #16
                DEFW #1538
                DEFW 184
                DEFW 660
                DEFB #16
                DEFW #1884
                DEFW 192
                DEFW 696
                DEFB #16
                DEFW #1BFC
                DEFW 192
                DEFW 724
                DEFB #16
                DEFW #1F90
                DEFW 192
                DEFW 744
                DEFB #16
                DEFW #2338
                DEFW 196
                DEFW 764
                DEFB #16
                DEFW #26F8
                DEFW 180
                DEFW 732
                DEFB #16
                DEFW #2A88
                DEFW 160
                DEFW 712
                DEFB #16
                DEFW #2DF0
                DEFW 160
                DEFW 724
                DEFB #16
                DEFW #3164
                DEFW 192
                DEFW 756
                DEFB #16
                DEFW #3518
                DEFW 208
                DEFW 772
                DEFB #16
                DEFW #38EC
                DEFW 200
                DEFW 780
                DEFB #17
                DEFW #0000
                DEFW 200
                DEFW 792
                DEFB #17
                DEFW #03E0
                DEFW 216
                DEFW 772
                DEFB #17
                DEFW #07BC
                DEFW 216
                DEFW 736
                DEFB #17
                DEFW #0B74
                DEFW 200
                DEFW 656
                DEFB #17
                DEFW #0ECC
                DEFW 180
                DEFW 588
                DEFB #17
                DEFW #11CC
                DEFW 172
                DEFW 548
                DEFB #17
                DEFW #149C
                DEFW 172
                DEFW 520
                DEFB #17
                DEFW #1750
                DEFW 220
                DEFW 468
                DEFB #17
                DEFW #1A00
                DEFW 240
                DEFW 476
                DEFB #17
                DEFW #1CCC
                DEFW 240
                DEFW 496
                DEFB #17
                DEFW #1FAC
                DEFW 260
                DEFW 524
                DEFB #17
                DEFW #22BC
                DEFW 248
                DEFW 564
                DEFB #17
                DEFW #25E8
                DEFW 228
                DEFW 604
                DEFB #17
                DEFW #2928
                DEFW 236
                DEFW 636
                DEFB #17
                DEFW #2C90
                DEFW 236
                DEFW 660
                DEFB #17
                DEFW #3010
                DEFW 236
                DEFW 672
                DEFB #17
                DEFW #339C
                DEFW 240
                DEFW 688
                DEFB #17
                DEFW #373C
                DEFW 224
                DEFW 644
                DEFB #17
                DEFW #3AA0
                DEFW 204
                DEFW 612
                DEFB #18
                DEFW #0000
                DEFW 200
                DEFW 608
                DEFB #18
                DEFW #0328
                DEFW 232
                DEFW 640
                DEFB #18
                DEFW #0690
                DEFW 248
                DEFW 656
                DEFB #18
                DEFW #0A18
                DEFW 240
                DEFW 664
                DEFB #18
                DEFW #0DA0
                DEFW 240
                DEFW 672
                DEFB #18
                DEFW #1130
                DEFW 252
                DEFW 652
                DEFB #18
                DEFW #14B8
                DEFW 232
                DEFW 632
                DEFB #18
                DEFW #1818
                DEFW 200
                DEFW 552
                DEFB #18
                DEFW #1B08
                DEFW 180
                DEFW 476
                DEFB #18
                DEFW #1D98
                DEFW 172
                DEFW 424
                DEFB #18
                DEFW #1FEC
                DEFW 172
                DEFW 400
                DEFB #18
                DEFW #2228
                DEFW 248
                DEFW 492
                DEFB #18
                DEFW #250C
                DEFW 268
                DEFW 500
                DEFB #18
                DEFW #280C
                DEFW 280
                DEFW 520
                DEFB #18
                DEFW #2B2C
                DEFW 316
                DEFW 536
                DEFB #18
                DEFW #2E80
                DEFW 316
                DEFW 548
                DEFB #18
                DEFW #31E0
                DEFW 292
                DEFW 604
                DEFB #18
                DEFW #3560
                DEFW 296
                DEFW 652
                DEFB #18
                DEFW #3914
                DEFW 296
                DEFW 672
                DEFB #19
                DEFW #0000
                DEFW 296
                DEFW 664
                DEFB #19
                DEFW #03C0
                DEFW 300
                DEFW 680
                DEFB #19
                DEFW #0794
                DEFW 284
                DEFW 636
                DEFB #19
                DEFW #0B2C
                DEFW 248
                DEFW 604
                DEFB #19
                DEFW #0E80
                DEFW 228
                DEFW 592
                DEFB #19
                DEFW #11B4
                DEFW 260
                DEFW 628
                DEFB #19
                DEFW #152C
                DEFW 276
                DEFW 644
                DEFB #19
                DEFW #18C4
                DEFW 268
                DEFW 652
                DEFB #19
                DEFW #1C5C
                DEFW 268
                DEFW 660
                DEFB #19
                DEFW #1FFC
                DEFW 280
                DEFW 640
                DEFB #19
                DEFW #2394
                DEFW 248
                DEFW 620
                DEFB #19
                DEFW #26F8
                DEFW 200
                DEFW 556
                DEFB #19
                DEFW #29EC
                DEFW 180
                DEFW 460
                DEFB #19
                DEFW #2C6C
                DEFW 172
                DEFW 396
                DEFB #19
                DEFW #2EA4
                DEFW 172
                DEFW 372
                DEFB #19
                DEFW #30C4
                DEFW 240
                DEFW 508
                DEFB #19
                DEFW #33B0
                DEFW 260
                DEFW 516
                DEFB #19
                DEFW #36B8
                DEFW 272
                DEFW 524
                DEFB #19
                DEFW #39D4
                DEFW 320
                DEFW 540
                DEFB #1A
                DEFW #0000
                DEFW 332
                DEFW 552
                DEFB #1A
                DEFW #0374
                DEFW 320
                DEFW 608
                DEFB #1A
                DEFW #0714
                DEFW 336
                DEFW 652
                DEFB #1A
                DEFW #0AF0
                DEFW 336
                DEFW 672
                DEFB #1A
                DEFW #0EE0
                DEFW 336
                DEFW 648
                DEFB #1A
                DEFW #12B8
                DEFW 340
                DEFW 636
                DEFB #1A
                DEFW #1688
                DEFW 328
                DEFW 592
                DEFB #1A
                DEFW #1A20
                DEFW 296
                DEFW 532
                DEFB #1A
                DEFW #1D5C
                DEFW 276
                DEFW 504
                DEFB #1A
                DEFW #2068
                DEFW 308
                DEFW 540
                DEFB #1A
                DEFW #23B8
                DEFW 324
                DEFW 556
                DEFB #1A
                DEFW #2728
                DEFW 304
                DEFW 564
                DEFB #1A
                DEFW #2A8C
                DEFW 288
                DEFW 572
                DEFB #1A
                DEFW #2DE8
                DEFW 296
                DEFW 552
                DEFB #1A
                DEFW #3138
                DEFW 252
                DEFW 532
                DEFB #1A
                DEFW #3448
                DEFW 204
                DEFW 468
                DEFB #1A
                DEFW #36E8
                DEFW 184
                DEFW 372
                DEFB #1A
                DEFW #3914
                DEFW 164
                DEFW 308
                DEFB #1A
                DEFW #3AEC
                DEFW 164
                DEFW 284
                DEFB #1A
                DEFW #3CAC
                DEFW 200
                DEFW 504
                DEFB #1B
                DEFW #0000
                DEFW 232
                DEFW 508
                DEFB #1B
                DEFW #02E4
                DEFW 244
                DEFW 516
                DEFB #1B
                DEFW #05DC
                DEFW 292
                DEFW 532
                DEFB #1B
                DEFW #0914
                DEFW 304
                DEFW 544
                DEFB #1B
                DEFW #0C64
                DEFW 292
                DEFW 600
                DEFB #1B
                DEFW #0FE0
                DEFW 308
                DEFW 644
                DEFB #1B
                DEFW #1398
                DEFW 308
                DEFW 664
                DEFB #1B
                DEFW #1764
                DEFW 308
                DEFW 640
                DEFB #1B
                DEFW #1B18
                DEFW 312
                DEFW 628
                DEFB #1B
                DEFW #1EC4
                DEFW 316
                DEFW 584
                DEFB #1B
                DEFW #2248
                DEFW 300
                DEFW 524
                DEFB #1B
                DEFW #2580
                DEFW 292
                DEFW 496
                DEFB #1B
                DEFW #2894
                DEFW 324
                DEFW 516
                DEFB #1B
                DEFW #2BDC
                DEFW 340
                DEFW 548
                DEFB #1B
                DEFW #2F54
                DEFW 320
                DEFW 560
                DEFB #1B
                DEFW #32C4
                DEFW 288
                DEFW 572
                DEFB #1B
                DEFW #3620
                DEFW 284
                DEFW 552
                DEFB #1B
                DEFW #3964
                DEFW 240
                DEFW 532
                DEFB #1B
                DEFW #3C68
                DEFW 192
                DEFW 468
                DEFB #1C
                DEFW #0000
                DEFW 172
                DEFW 372
                DEFB #1C
                DEFW #0220
                DEFW 152
                DEFW 308
                DEFB #1C
                DEFW #03EC
                DEFW 152
                DEFW 284
                DEFB #1C
                DEFW #05A0
                DEFW 200
                DEFW 504
                DEFB #1C
                DEFW #0860
                DEFW 232
                DEFW 524
                DEFB #1C
                DEFW #0B54
                DEFW 244
                DEFW 548
                DEFB #1C
                DEFW #0E6C
                DEFW 292
                DEFW 564
                DEFB #1C
                DEFW #11C4
                DEFW 304
                DEFW 576
                DEFB #1C
                DEFW #1534
                DEFW 292
                DEFW 632
                DEFB #1C
                DEFW #18D0
                DEFW 308
                DEFW 676
                DEFB #1C
                DEFW #1CA8
                DEFW 308
                DEFW 696
                DEFB #1C
                DEFW #2094
                DEFW 308
                DEFW 672
                DEFB #1C
                DEFW #2468
                DEFW 312
                DEFW 660
                DEFB #1C
                DEFW #2834
                DEFW 316
                DEFW 616
                DEFB #1C
                DEFW #2BD8
                DEFW 300
                DEFW 556
                DEFB #1C
                DEFW #2F30
                DEFW 292
                DEFW 512
                DEFB #1C
                DEFW #3254
                DEFW 324
                DEFW 516
                DEFB #1C
                DEFW #359C
                DEFW 356
                DEFW 552
                DEFB #1C
                DEFW #3928
                DEFW 352
                DEFW 564
                DEFB #1D
                DEFW #0000
                DEFW 320
                DEFW 560
                DEFB #1D
                DEFW #0370
                DEFW 316
                DEFW 524
                DEFB #1D
                DEFW #06B8
                DEFW 272
                DEFW 504
                DEFB #1D
                DEFW #09C0
                DEFW 224
                DEFW 440
                DEFB #1D
                DEFW #0C58
                DEFW 204
                DEFW 344
                DEFB #1D
                DEFW #0E7C
                DEFW 184
                DEFW 280
                DEFB #1D
                DEFW #104C
                DEFW 184
                DEFW 256
                DEFB #1D
                DEFW #1204
                DEFW 200
                DEFW 476
                DEFB #1D
                DEFW #14A8
                DEFW 232
                DEFW 496
                DEFB #1D
                DEFW #1780
                DEFW 244
                DEFW 520
                DEFB #1D
                DEFW #1A7C
                DEFW 292
                DEFW 536
                DEFB #1D
                DEFW #1DB8
                DEFW 304
                DEFW 560
                DEFB #1D
                DEFW #2118
                DEFW 292
                DEFW 624
                DEFB #1D
                DEFW #24AC
                DEFW 308
                DEFW 668
                DEFB #1D
                DEFW #287C
                DEFW 308
                DEFW 692
                DEFB #1D
                DEFW #2C64
                DEFW 308
                DEFW 672
                DEFB #1D
                DEFW #3038
                DEFW 312
                DEFW 660
                DEFB #1D
                DEFW #3404
                DEFW 316
                DEFW 616
                DEFB #1D
                DEFW #37A8
                DEFW 300
                DEFW 556
                DEFB #1D
                DEFW #3B00
                DEFW 292
                DEFW 512
                DEFB #1E
                DEFW #0000
                DEFW 324
                DEFW 516
                DEFB #1E
                DEFW #0348
                DEFW 356
                DEFW 552
                DEFB #1E
                DEFW #06D4
                DEFW 352
                DEFW 564
                DEFB #1E
                DEFW #0A68
                DEFW 320
                DEFW 560
                DEFB #1E
                DEFW #0DD8
                DEFW 316
                DEFW 524
                DEFB #1E
                DEFW #1120
                DEFW 272
                DEFW 504
                DEFB #1E
                DEFW #1428
                DEFW 224
                DEFW 440
                DEFB #1E
                DEFW #16C0
                DEFW 204
                DEFW 344
                DEFB #1E
                DEFW #18E4
                DEFW 184
                DEFW 280
                DEFB #1E
                DEFW #1AB4
                DEFW 184
                DEFW 256
                DEFB #1E
                DEFW #1C6C
                DEFW 232
                DEFW 428
                DEFB #1E
                DEFW #1F00
                DEFW 252
                DEFW 448
                DEFB #1E
                DEFW #21BC
                DEFW 264
                DEFW 488
                DEFB #1E
                DEFW #24AC
                DEFW 312
                DEFW 508
                DEFB #1E
                DEFW #27E0
                DEFW 336
                DEFW 532
                DEFB #1E
                DEFW #2B44
                DEFW 324
                DEFW 600
                DEFB #1E
                DEFW #2EE0
                DEFW 340
                DEFW 644
                DEFB #1E
                DEFW #32B8
                DEFW 340
                DEFW 668
                DEFB #1E
                DEFW #36A8
                DEFW 340
                DEFW 648
                DEFB #1E
                DEFW #3A84
                DEFW 344
                DEFW 624
                DEFB #1F
                DEFW #0000
                DEFW 348
                DEFW 596
                DEFB #1F
                DEFW #03B0
                DEFW 328
                DEFW 552
                DEFB #1F
                DEFW #0720
                DEFW 320
                DEFW 508
                DEFB #1F
                DEFW #0A5C
                DEFW 340
                DEFW 512
                DEFB #1F
                DEFW #0DB0
                DEFW 340
                DEFW 548
                DEFB #1F
                DEFW #1128
                DEFW 324
                DEFW 560
                DEFB #1F
                DEFW #149C
                DEFW 292
                DEFW 556
                DEFB #1F
                DEFW #17EC
                DEFW 288
                DEFW 516
                DEFB #1F
                DEFW #1B10
                DEFW 244
                DEFW 492
                DEFB #1F
                DEFW #1DF0
                DEFW 192
                DEFW 428
                DEFB #1F
                DEFW #205C
                DEFW 172
                DEFW 332
                DEFB #1F
                DEFW #2254
                DEFW 152
                DEFW 268
                DEFB #1F
                DEFW #23F8
                DEFW 152
                DEFW 244
                DEFB #1F
                DEFW #2584
                DEFW 232
                DEFW 428
                DEFB #1F
                DEFW #2818
                DEFW 252
                DEFW 452
                DEFB #1F
                DEFW #2AD8
                DEFW 264
                DEFW 492
                DEFB #1F
                DEFW #2DCC
                DEFW 312
                DEFW 512
                DEFB #1F
                DEFW #3104
                DEFW 336
                DEFW 520
                DEFB #1F
                DEFW #345C
                DEFW 324
                DEFW 572
                DEFB #1F
                DEFW #37DC
                DEFW 340
                DEFW 600
                DEFB #1F
                DEFW #3B88
                DEFW 340
                DEFW 608
                DEFB #96
                DEFW #0000
                DEFW 340
                DEFW 588
                DEFB #96
                DEFW #03A0
                DEFW 344
                DEFW 564
                DEFB #96
                DEFW #072C
                DEFW 348
                DEFW 532
                DEFB #96
                DEFW #0A9C
                DEFW 328
                DEFW 484
                DEFB #96
                DEFW #0DC8
                DEFW 320
                DEFW 440
                DEFB #96
                DEFW #10C0
                DEFW 340
                DEFW 444
                DEFB #96
                DEFW #13D0
                DEFW 340
                DEFW 480
                DEFB #96
                DEFW #1704
                DEFW 324
                DEFW 492
                DEFB #96
                DEFW #1A34
                DEFW 292
                DEFW 484
                DEFB #96
                DEFW #1D3C
                DEFW 288
                DEFW 444
                DEFB #96
                DEFW #2018
                DEFW 244
                DEFW 420
                DEFB #96
                DEFW #22B0
                DEFW 192
                DEFW 372
                DEFB #96
                DEFW #24E4
                DEFW 172
                DEFW 292
                DEFB #96
                DEFW #26B4
                DEFW 152
                DEFW 244
                DEFB #96
                DEFW #2840
                DEFW 152
                DEFW 224
                DEFB #96
                DEFW #29B8
                DEFW 200
                DEFW 376
                DEFB #96
                DEFW #2BF8
                DEFW 220
                DEFW 396
                DEFB #96
                DEFW #2E60
                DEFW 232
                DEFW 436
                DEFB #96
                DEFW #30FC
                DEFW 280
                DEFW 460
                DEFB #96
                DEFW #33E0
                DEFW 304
                DEFW 484
                DEFB #96
                DEFW #36F4
                DEFW 304
                DEFW 548
                DEFB #96
                DEFW #3A48
                DEFW 332
                DEFW 576
                DEFB #97
                DEFW #0000
                DEFW 332
                DEFW 584
                DEFB #97
                DEFW #0394
                DEFW 332
                DEFW 548
                DEFB #97
                DEFW #0704
                DEFW 336
                DEFW 520
                DEFB #97
                DEFW #0A5C
                DEFW 340
                DEFW 504
                DEFB #97
                DEFW #0DA8
                DEFW 324
                DEFW 456
                DEFB #97
                DEFW #10B4
                DEFW 320
                DEFW 412
                DEFB #97
                DEFW #1390
                DEFW 340
                DEFW 416
                DEFB #97
                DEFW #1684
                DEFW 340
                DEFW 436
                DEFB #97
                DEFW #198C
                DEFW 324
                DEFW 452
                DEFB #97
                DEFW #1C94
                DEFW 292
                DEFW 448
                DEFB #97
                DEFW #1F78
                DEFW 288
                DEFW 408
                DEFB #97
                DEFW #2230
                DEFW 244
                DEFW 384
                DEFB #97
                DEFW #24A4
                DEFW 192
                DEFW 336
                DEFB #97
                DEFW #26B4
                DEFW 172
                DEFW 256
                DEFB #97
                DEFW #2860
                DEFW 152
                DEFW 196
                DEFB #97
                DEFW #29BC
                DEFW 152
                DEFW 176
                DEFB #97
                DEFW #2B04
                DEFW 196
                DEFW 296
                DEFB #97
                DEFW #2CF0
                DEFW 216
                DEFW 316
                DEFB #97
                DEFW #2F04
                DEFW 232
                DEFW 356
                DEFB #97
                DEFW #3150
                DEFW 280
                DEFW 364
                DEFB #97
                DEFW #33D4
                DEFW 304
                DEFW 372
                DEFB #97
                DEFW #3678
                DEFW 304
                DEFW 424
                DEFB #97
                DEFW #3950
                DEFW 332
                DEFW 452
                DEFB #97
                DEFW #3C60
                DEFW 332
                DEFW 460
                DEFB #98
                DEFW #0000
                DEFW 332
                DEFW 436
                DEFB #98
                DEFW #0300
                DEFW 336
                DEFW 428
                DEFB #98
                DEFW #05FC
                DEFW 340
                DEFW 428
                DEFB #98
                DEFW #08FC
                DEFW 324
                DEFW 396
                DEFB #98
                DEFW #0BCC
                DEFW 320
                DEFW 364
                DEFB #98
                DEFW #0E78
                DEFW 340
                DEFW 364
                DEFB #98
                DEFW #1138
                DEFW 340
                DEFW 380
                DEFB #98
                DEFW #1408
                DEFW 324
                DEFW 396
                DEFB #98
                DEFW #16D8
                DEFW 292
                DEFW 392
                DEFB #98
                DEFW #1984
                DEFW 288
                DEFW 352
                DEFB #98
                DEFW #1C04
                DEFW 244
                DEFW 344
                DEFB #98
                DEFW #1E50
                DEFW 192
                DEFW 308
                DEFB #98
                DEFW #2044
                DEFW 172
                DEFW 244
                DEFB #98
                DEFW #21E4
                DEFW 152
                DEFW 184
                DEFB #98
                DEFW #2334
                DEFW 152
                DEFW 152
                DEFB #98
                DEFW #2464
                DEFW 156
                DEFW 268
                DEFB #98
                DEFW #260C
                DEFW 176
                DEFW 288
                DEFB #98
                DEFW #27DC
                DEFW 192
                DEFW 312
                DEFB #98
                DEFW #29D4
                DEFW 240
                DEFW 320
                DEFB #98
                DEFW #2C04
                DEFW 284
                DEFW 328
                DEFB #98
                DEFW #2E68
                DEFW 300
                DEFW 380
                DEFB #98
                DEFW #3110
                DEFW 328
                DEFW 408
                DEFB #98
                DEFW #33F0
                DEFW 328
                DEFW 400
                DEFB #98
                DEFW #36C8
                DEFW 328
                DEFW 376
                DEFB #98
                DEFW #3988
                DEFW 332
                DEFW 348
                DEFB #98
                DEFW #3C30
                DEFW 336
                DEFW 348
                DEFB #99
                DEFW #0000
                DEFW 320
                DEFW 316
                DEFB #99
                DEFW #027C
                DEFW 308
                DEFW 300
                DEFB #99
                DEFW #04DC
                DEFW 328
                DEFW 300
                DEFB #99
                DEFW #0750
                DEFW 328
                DEFW 316
                DEFB #99
                DEFW #09D4
                DEFW 324
                DEFW 332
                DEFB #99
                DEFW #0C64
                DEFW 292
                DEFW 328
                DEFB #99
                DEFW #0ED0
                DEFW 288
                DEFW 304
                DEFB #99
                DEFW #1120
                DEFW 244
                DEFW 296
                DEFB #99
                DEFW #133C
                DEFW 192
                DEFW 260
                DEFB #99
                DEFW #1500
                DEFW 172
                DEFW 196
                DEFB #99
                DEFW #1670
                DEFW 152
                DEFW 136
                DEFB #99
                DEFW #1790
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
