                ifndef _HMM2_ASSETS_
                define _HMM2_ASSETS_

; Черновое распределение FT812 RAM_G.
RAMG_ADVENTURE_BASE EQU #000000
RAMG_UI_BASE        EQU #040000
RAMG_FONT_BASE      EQU #060000

                include "generated_map.inc"
                include "generated_terrain.inc"
                include "generated_dxt_background.inc"
                include "generated_fullmap_dxt.inc"
                include "generated_background.inc"
                include "generated_objects.inc"

                endif
