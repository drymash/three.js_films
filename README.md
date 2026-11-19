# three.js films

Короткі 3D-ролики на Three.js. Кожен ролик — одна HTML-сторінка, де будь-який кадр можна відтворити за часом, тому з неї можна записати відео кадр у кадр.

## Структура

```
films/
  bayraktar-tb2/
    index.html       сторінка з анімацією (відкривається в браузері)
    timeline.json    ключові моменти в секундах, з нього береться звук
    score.py         звукова доріжка, генерується кодом
    renders/         готові MP4: 16x9 і 9x16 (Reels)
references/
  patterns.md        розбори референсів: структура, прийоми, ритм
```

## Ролики

| Ролик | Тривалість | Що всередині |
|---|---|---|
| `bayraktar-tb2` | 34,3 с | Креслярська книга, дрон виростає з креслення, розбір на вузли з підписами, виліт, політ над колоною, оптика, проліт, розворот, силует на тлі сонця |

Жива версія: https://claude.ai/artifact/QHt8Qpg3pcQGmUFabh8M3N

## Як записати відео

Запис і звук роблять скрипти навички [teardown](https://github.com/elvarofficial/teardown) (MIT). Потрібні Node.js 20+, ffmpeg, Python 3 і Chromium із Playwright.

Сторінка підтримує режим запису: з `?render` годинник зупиняється, а `window.seek(t)` малює кадр `t`. Скрипт запису очікує повноцінний HTML-документ, тому перед записом сторінку загортають у `<!doctype html><html><head><meta charset="utf-8"></head><body>…</body></html>` (файл `bayraktar.html` нижче).

```bash
TD=~/.claude/skills/teardown
```

Горизонтальне відео 1920×1080:

```bash
node $TD/sims/capture.mjs bayraktar.html --size 1600x900 --dpr 1.2 --fps 30 --out silent-16x9.mp4
```

Вертикальне відео 1080×1920:

```bash
node $TD/sims/capture.mjs bayraktar.html --size 900x1600 --dpr 1.2 --fps 30 --out silent-9x16.mp4
```

Звук:

```bash
python3 $TD/run_sfx.py films/bayraktar-tb2/score.py
```

Звести картинку зі звуком:

```bash
ffmpeg -i silent-9x16.mp4 -i films/bayraktar-tb2/renders/score.wav -map 0:v -map 1:a -c:v libx264 -crf 21 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart out.mp4
```

Аркуш кадрів для перевірки:

```bash
node $TD/sims/capture.mjs bayraktar.html --size 900x1600 --dpr 1 --stills 2,5,7.4,12,20,32.5 --cols 6 --out check.png
```

На машині без відеокарти запис 34 секунд займає близько 13–20 хвилин.
