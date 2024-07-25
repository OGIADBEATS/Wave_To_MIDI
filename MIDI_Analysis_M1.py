import mido
import pandas as pd
import os
from collections import defaultdict, Counter

# ピッチと楽器のマッピング
pitch_to_instrument = {
    36: 'Bass Drum 1', 38: 'Acoustic Snare', 40: 'Electric Snare', 37: 'Side Stick',
    48: 'Hi-Mid Tom', 50: 'High Tom', 45: 'Low Tom', 47: 'Low-Mid Tom', 43: 'High Floor Tom',
    58: 'Vibraslap', 46: 'Open Hi-Hat', 26: 'Open Hi-Hat Edge', 42: 'Closed Hi-Hat',
    22: 'Closed Hi-Hat Edge', 44: 'Pedal Hi-Hat', 49: 'Crash Cymbal 1', 55: 'Splash Cymbal',
    57: 'Crash Cymbal 2', 52: 'Chinese Cymbal', 51: 'Ride Cymbal 1', 59: 'Ride Cymbal 2',
    53: 'Ride Bell'
}

# 親ディレクトリ
parent_directory = '/content/drive/MyDrive/groove'
output_data = []

def extract_genre_and_bpm_from_filename(filename):
    parts = filename.split('_')
    if len(parts) > 2:
        genre = parts[1]
        try:
            bpm = int(parts[2])
            return genre, bpm
        except ValueError:
            return genre, None
    return None, None

def process_midi_file(file_path, genre, bpm, unique_filename):
    mid = mido.MidiFile(file_path)
    ticks_per_beat = mid.ticks_per_beat
    default_tempo = mido.bpm2tempo(bpm)
    current_tempo = default_tempo

    # ドラムトラックを抽出
    drum_track = None
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.channel == 9:
                drum_track = track
                break
        if drum_track:
            break

    if not drum_track:
        print(f"No drum track found in the MIDI file: {file_path}")
        return []

    # ノートごとの発音タイミングを記録するリストを作成
    note_timings = defaultdict(list)
    current_time = 0

    for msg in drum_track:
        current_time += mido.tick2second(msg.time, ticks_per_beat, current_tempo)
        if msg.type == 'set_tempo':
            current_tempo = msg.tempo
        if msg.type == 'note_on' and msg.velocity > 0:
            note_timings[msg.note].append((current_time, msg.velocity))

    # 発音タイミングをデータリストに追加
    data = []
    for note, values in note_timings.items():
        instrument = pitch_to_instrument.get(note, f'Unknown ({note})')
        for time, velocity in values:
            data.append({'File': unique_filename, 'File_Path': file_path, 'Genre': genre, 'BPM': bpm, 'Note': note, 'Instrument': instrument, 'Time': time, 'Velocity': velocity})
    return data

# ファイル名のカウンタを初期化
filename_counter = Counter()

# 再帰的にディレクトリ内の全MIDIファイルを処理
for drummer_dir in os.listdir(parent_directory):
    drummer_path = os.path.join(parent_directory, drummer_dir)
    if os.path.isdir(drummer_path):
        for root, dirs, files in os.walk(drummer_path):
            for filename in files:
                if filename.endswith('.mid') or filename.endswith('.midi'):
                    print(f"Processing file: {filename}")
                    genre, bpm = extract_genre_and_bpm_from_filename(filename)
                    if genre is not None and bpm is not None:
                        midi_file_path = os.path.join(root, filename)
                        # ファイル名のカウントを増加させて一意のファイル名を生成
                        filename_counter[filename] += 1
                        if filename_counter[filename] > 1:
                            unique_filename = f"{os.path.splitext(filename)[0]}({filename_counter[filename]}).mid"
                        else:
                            unique_filename = filename
                        file_data = process_midi_file(midi_file_path, genre, bpm, unique_filename)
                        output_data.extend(file_data)
                        print(f"Finished processing file: {filename}")
                    else:
                        print(f"Skipping file (invalid BPM or genre): {filename}")

# データをデータフレームに変換
df = pd.DataFrame(output_data)

# データをCSVファイルに出力
output_file = 'midi_memory.csv'
df.to_csv(output_file, index=False)

# データの表示
print("Processing complete. Here is the dataframe:")
print(df.head())
