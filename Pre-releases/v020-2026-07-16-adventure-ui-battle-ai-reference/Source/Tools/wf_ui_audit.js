export const meta = {
  name: 'hmm2-adventure-ui-audit',
  description: 'Аудит adventure-UI HMM2 VDAC2 против OpenHMM2: эталон → текущее → дефекты+правки',
  phases: [
    { title: 'Subsystem audit', detail: 'по подсистемам: эталон OpenHMM2 + текущий render.asm + дефекты' },
    { title: 'Synthesis', detail: 'приоритизированный список правок + аппаратные ограничения' },
  ],
}

const OPEN = 'C:/Users/Администратор/Desktop/OpenHMM2/src/fheroes2'
const ASM = 'C:/Users/Администратор/Desktop/HMM2/Source/ASM'

const COMMON = `
КОНТЕКСТ. Идёт порт HMM2 (adventure screen) на TS-Conf Z80 + FT812/VDAC2. Логические координаты
640×480 как в OpenHMM2 (fheroes2), FT812 апскейлит ×1.6 до 1024×768 (NEAREST). Константы OpenHMM2:
borderWidthPx=16, radarWidthPx=144, tileWidthPx=32, база 640×480. Радар 144×144 в (480,16).
Правая панель рисуется в ${ASM}/render.asm (статические DL-блобы + Render_*Cmd), ассеты в RAM_G
(PALETTED4444), геометрия в ${ASM}/generated_objects.inc, ввод/хит-тест в ${ASM}/game_state.asm.
ЦЕЛЬ: всё строго по оригиналу OpenHMM2, КРОМЕ honest hardware-ограничений FT812 (бюджет RAM_DL 8192,
CMD-FIFO 4096 байт/кадр, RAM_G ~1МБ). Текущий снимок adventure показывает: радар вверху (в основном
чёрный = туман, это норма), ниже — сетка пустых ячеек с рамками на чёрном (список героев/замков, лишь
1 карточка героя нарисована), ряд кнопок (2×4), внизу полоса ресурсов (дерево/ртуть/руда/сера/кристалл/
самоцветы/золото). Фон панели местами чёрный.

ЗАДАЧА. Разобрать ОДНУ подсистему. Прочитать эталон в OpenHMM2 И текущую реализацию в render.asm/
game_state.asm/generated_objects.inc. Вернуть СТРОГО структуру по схеме: точная геометрия эталона
(координаты/размеры в логических 640×480), как это сейчас в нашем коде (с file:line), и список
конкретных отклонений с приоритетом и предлагаемой правкой (конкретный DL/ASM-шаг или нужный ассет).
Помечай honest hardware-ограничения (что нельзя 1:1 из-за бюджетов). Кратко, без воды.`

const SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['subsystem', 'openHmm2Spec', 'currentState', 'deviations'],
  properties: {
    subsystem: { type: 'string' },
    openHmm2Spec: { type: 'string', description: 'точная геометрия/ассеты/поведение эталона, координаты 640×480' },
    currentState: { type: 'string', description: 'как реализовано сейчас, с file:line' },
    deviations: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['title', 'severity', 'target', 'fix', 'hardwareLimit'],
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          target: { type: 'string', description: 'целевая геометрия/поведение по OpenHMM2' },
          fix: { type: 'string', description: 'конкретный шаг: какой DL/ASM/ассет менять' },
          hardwareLimit: { type: 'boolean' },
        },
      },
    },
  },
}

const SUBSYS = [
  { key: 'radar',   ref: `${OPEN}/gui/interface_radar.cpp`,  hint: 'миникарта/радар: размер 144×144, позиция, рамка, отрисовка тайлов и viewport-прямоугольника, hero-dot, туман.' },
  { key: 'icons',   ref: `${OPEN}/gui/interface_icons.cpp`,  hint: 'список героев/замков: ячейка 56×32, колонки, фон пустых ячеек (ICN::ICONS), скролл, портреты, рамка ICON BORDER.' },
  { key: 'status',  ref: `${OPEN}/gui/interface_status.cpp`, hint: 'статус-окно: дата/ресурсы/инфо героя, позиция под кнопками, полоса 7 ресурсов и числа.' },
  { key: 'buttons', ref: `${OPEN}/gui/interface_buttons.cpp`,hint: 'кнопки adventure: 9 кнопок (или 2×4+?), порядок/иконки/позиции/состояния (normal/pressed/disabled).' },
  { key: 'border',  ref: `${OPEN}/gui/interface_border.cpp`, hint: 'рамка/фон панели ADVBORD: где чёрные дыры быть НЕ должно, какой фон под элементами.' },
  { key: 'cpanel',  ref: `${OPEN}/gui/interface_cpanel.cpp`, hint: 'control panel / прочие элементы правой панели (если есть): кнопки управления.' },
]

phase('Subsystem audit')
const results = await pipeline(
  SUBSYS,
  s => agent(
    `${COMMON}\n\nПОДСИСТЕМА: ${s.key}. ${s.hint}\nЭталон: ${s.ref}\nНаш код: ${ASM}/render.asm, ${ASM}/game_state.asm, ${ASM}/generated_objects.inc.`,
    { label: `audit:${s.key}`, phase: 'Subsystem audit', schema: SCHEMA, agentType: 'Explore' }
  )
)

phase('Synthesis')
const valid = results.filter(Boolean)
const synthesis = await agent(
  `${COMMON}\n\nНиже — аудиты подсистем adventure-UI (JSON). Сведи их в ЕДИНЫЙ приоритизированный план доводки UI
до OpenHMM2 для автономной реализации. Выведи markdown-документ:
1) Таблица дефектов: подсистема | дефект | severity | целевая геометрия | конкретная правка (DL/ASM/ассет).
   Отсортировано по severity (high→low) и по дешевизне правки.
2) Отдельный раздел «Аппаратные ограничения FT812» — только honest hardware-ограничения (hardwareLimit=true),
   с причиной (бюджет RAM_DL/CMD-FIFO/RAM_G).
3) Раздел «Быстрые победы» — 5-8 правок, которые дёшевы и заметно повышают точность, в порядке выполнения.
Без воды, конкретные числа и имена символов render.asm где возможно.\n\nАУДИТЫ:\n${JSON.stringify(valid, null, 1)}`,
  { label: 'synthesis', phase: 'Synthesis' }
)

return { audits: valid, plan: synthesis }
