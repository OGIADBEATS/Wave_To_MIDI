import mido
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# ピッチと楽器のマッピング
pitch_to_instrument = {
    36: 'Bass Drum 1',
    38: 'Acoustic Snare',
    40: 'Electric Snare',
    37: 'Side Stick',
    48: 'Hi-Mid Tom',
    50: 'High Tom',
    45: 'Low Tom',
    47: 'Low-Mid Tom',
    43: 'High Floor Tom',
    58: 'Vibraslap',
    46: 'Open Hi-Hat',
    26: 'Open Hi-Hat Edge',
    42: 'Closed Hi-Hat',
    22: 'Closed Hi-Hat Edge',
    44: 'Pedal Hi-Hat',
    49: 'Crash Cymbal 1',
    55: 'Splash Cymbal',
    57: 'Crash Cymbal 2',
    52: 'Chinese Cymbal',
    51: 'Ride Cymbal 1',
    59: 'Ride Cymbal 2',
    53: 'Ride Bell'
}

# MIDIファイルの読み込み
midi_file = '/content/drive/MyDrive/groove/drummer1/session1/100_neworleans-secondline_94_beat_4-4.mid'
mid = mido.MidiFile(midi_file)

# ドラムトラックを抽出
drum_track = None
for track in mid.tracks:
    for msg in track:
        if msg.type == 'note_on' and msg.channel == 9:  # Channel 10 (index 9) is typically used for drums
            drum_track = track
            break
    if drum_track:
        break

if not drum_track:
    raise ValueError("No drum track found in the MIDI file")

# ノートごとの発音タイミングを記録する辞書を作成
note_timings = defaultdict(list)
current_time = 0
for msg in drum_track:
    if msg.type in ['note_on', 'note_off']:
        current_time += mido.tick2second(msg.time, mid.ticks_per_beat, 500000)  # 500000 is the default tempo (μs per beat)
        if msg.type == 'note_on' and msg.velocity > 0:
            note_timings[msg.note].append(current_time)

# 発音タイミングをデータフレームに保存
data = []
for note, times in note_timings.items():
    instrument = pitch_to_instrument.get(note, f'Unknown ({note})')
    for time in times:
        data.append({'Note': note, 'Instrument': instrument, 'Time': time})

df = pd.DataFrame(data)

# データをCSVファイルに出力
output_file = 'note_times.csv'
df.to_csv(output_file, index=False)

# データの表示
print(df.head())

# ノートごとの発音タイミングを可視化
plt.figure(figsize=(12, 8))
for note, times in note_timings.items():
    plt.scatter(times, [note] * len(times), label=f'Note {note}')

plt.xlabel('Time (s)')
plt.ylabel('MIDI Note')
plt.title('Drum MIDI Notes over Time')
plt.grid(True)
plt.legend(title='MIDI Note')
plt.show()
