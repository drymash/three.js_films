"""Score for the Bayraktar blueprint film: a slow D-minor pad under everything, paper and pencil in the book,
whooshes and pops for the exploded view, the pusher engine as a low hum that follows the camera's distance.

    python run_sfx.py <this file>
"""

import math
import os

from sfx.score_kit import airy, hz, rumble, thud
from sfx.synth import chime, click, envelope, pad, pop, riser, scratch, whoosh

TIMELINE = "timeline.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "score.wav")
TARGET_LUFS = -14.0
SEED = 23


def notes(*names):
    return [hz(n) for n in names]


def score(mix, tl):
    dur = tl["duration"]
    b, ex, fo, fd = tl["book"], tl["explode"], tl["flyoff"], tl["field"]

    # music bed: Dm9 · Bbmaj7 · Fmaj7 · Csus2, a chord every ~4.3 s, swelling into the sun shot
    prog = [notes("D3", "F3", "A3", "E4"), notes("A#2", "D3", "F3", "A3"), notes("F2", "C3", "E3", "A3"), notes("C3", "D3", "G3", "E4")]
    step = dur / 8
    chords = [(i * step, prog[i % 4]) for i in range(8)]
    vol = envelope([(0, 0.0), (1.0, 0.55), (fo["cut"] - 0.4, 0.7), (fo["cut"], 0.35), (fd["sun"], 0.55), (fd["sun_cross"], 1.0), (dur, 0.7)])
    left, right = pad(dur, chords, volume=vol)
    mix.put_stereo(0, left, right, 0.16)

    # the book
    mix.put(b["cover_open"], whoosh(1.7, 260, 1100, peak=0.5), 0.05, pan=0.3)
    mix.put(b["cover_land"], thud(70, 0.09, 0.45), 0.12)
    mix.put(b["draw"][0], scratch(b["draw"][1] - b["draw"][0]), 0.06, pan=0.35)
    mix.put(b["dims"], pop(hz("A5"), hz("D6")), 0.04)
    mix.put(b["dims"] + 0.15, pop(hz("D6"), hz("F6")), 0.04)
    mix.put(b["rise"], airy(1.3, 300, 1800, 0.8), 0.05)

    # pusher engine in the book: spins up, hums, climbs away on the fly-off
    hum_len = fo["cut"] - b["prop_start"]
    def book_f(t):
        up = min(1.0, t / 1.2)
        away = max(0.0, (t - (fo["start"] - b["prop_start"])) / 1.5)
        return 55 + 30 * up + 35 * away
    mix.put(b["prop_start"], rumble(hum_len, book_f, 0.5), 0.05)

    # exploded view
    mix.put(ex["out"], whoosh(1.0, 1800, 380, peak=0.35), 0.07)
    for i, t in enumerate(ex["labels"]):
        mix.put(t, pop(hz("D5") * 2 ** (i * 2 / 12), hz("A5") * 2 ** (i * 2 / 12)), 0.035, pan=-0.4 + i * 0.13)
    mix.put(ex["back"], whoosh(0.85, 380, 1800, peak=0.7), 0.07)
    mix.put(ex["snap"], click(1600, 0.04), 0.09)
    mix.put(ex["snap"] + 0.03, thud(110, 0.05, 0.25), 0.06)

    # fly-off into the cut
    mix.put(fo["start"], whoosh(1.3, 500, 2600, peak=0.75), 0.06)
    mix.put(fo["cut"] - 1.4, riser(1.4, 300, 4200), 0.05)

    # the field: wind across everything
    mix.put(fo["cut"], airy(dur - fo["cut"], 500, 800, 0.7), 0.025)

    # engine level by shot: distant, close chase, inside the sensor, overhead pass, turn, sun
    t0 = fo["cut"]
    def field_gain(t):
        T = t + t0
        if T < fd["chase"]:
            return 0.25 + 0.2 * (T - t0) / (fd["chase"] - t0)
        if T < fd["sensor"]:
            return 1.0
        if T < fd["flyby"]:
            return 0.35
        if T < fd["turn"]:
            return 0.3 + 0.9 * math.exp(-((T - fd["overhead"]) / 0.9) ** 2)
        if T < fd["sun"]:
            return 0.4
        return 0.3 + 0.35 * math.exp(-((T - fd["sun_cross"]) / 1.2) ** 2)
    def field_f(t):
        T = t + t0
        if fd["flyby"] <= T < fd["turn"]:
            return 82 - 14 * math.tanh((T - fd["overhead"]) / 0.5)   # pitch drops as it passes
        return 80 + 2 * math.sin(T * 0.7)
    eng = rumble(dur - t0, field_f, 0.5)
    sr = len(eng) / (dur - t0)
    eng = [s * field_gain(k / sr) for k, s in enumerate(eng)]
    mix.put(t0, eng, 0.06)

    # cuts and the sensor readouts
    mix.put(fd["sensor"], click(2600, 0.03), 0.06)
    for k in range(5):
        mix.put(fd["sensor"] + 0.4 + k * 0.55, click(3200, 0.02), 0.03)
    mix.put(fd["overhead"] - 0.9, whoosh(1.8, 300, 900, peak=0.5), 0.06)
    mix.put(fd["sun_cross"] - 0.2, chime(notes("D5", "A5", "E6"), dur=2.4, tau=0.9), 0.05)
