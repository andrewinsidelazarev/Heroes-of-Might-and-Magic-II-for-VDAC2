# Reference из Zuma VDAC2

Эта папка содержит локальные копии ASM-модулей из:

```text
C:\Users\Администратор\Desktop\Zuma Deluxe VDAC2\Source\ASM
```

Скопировано:

- `Input.asm`
- `sd_zc.asm`
- `ts-dos.asm`
- `loader_resident.asm`

Это reference-код, не подключённый к сборке HMM2.

Правило архитектуры: не тянуть эти модули целиком в Core. Перед использованием
разложить на резидентную минимальную часть и страничные/оверлейные части.
