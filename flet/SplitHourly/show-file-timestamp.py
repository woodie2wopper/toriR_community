#!/usr/bin/env python3

import sys
import os
import wave

import datetime

def convert_epoch_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%y%m%d_%H%M%S')

path = sys.argv[1]
print(path)

fileTimestamps = []

for file in os.listdir(path):
    file_stat = os.stat(os.path.join(path, file))
    file_timestamp = file_stat.st_mtime
    if file.lower().endswith('.wav') or file.lower().endswith('.mp3'):
        with wave.open(os.path.join(path, file), 'r') as wav_file:
            duration = wav_file.getnframes() / wav_file.getframerate()
            fileTimestamps.append({ 'ファイル名': file, 'mtime': file_timestamp, 'duration': duration })

# ファイル名順に並び替える
#fileTimestamps.sort(key=lambda x: x['ファイル名'], reverse=True)
msg_inputfile='''
## 仮定：
- 複数に分割されたファイルを一つの音声ファイルに結合します。
- 1時間ごとにファイル分割します。
- ファイル名は名前でソートした時に録音順になったいる。
- 引数はファイルを一つ指定する、もしくはディレクトリを指定する。
- ソートした時にファイルのタイムスタンプが同じなら連続録音の分割だと判断する
- ファイル名の逆ソート順で一番若いファイルの録音開始時間と、終了時間を設定する
- 逆ソートで２番目の終了時間は１番目の開始時間に同じである
- ３番目以降は同じ。

'''
prev_mtime = 0
for timestamp in sorted(fileTimestamps, key=lambda x: x['ファイル名'], reverse=True):
    mtime_epoch = timestamp['mtime']
    if mtime_epoch == prev_mtime:
        print("同じmtime", mtime_epoch)
        stop_epoch = prev_start_epoch
    else:
        stop_epoch = timestamp['mtime']
        #mtime_formatted = convert_epoch_to_string(mtime_epoch)
    
    duration = timestamp['duration']
    start_epoch = stop_epoch - duration
    # フォーマットをを揃える
    duration_formatted = str(datetime.timedelta(seconds=timestamp['duration']))
    start_formatted = convert_epoch_to_string(start_epoch)
    stop_formatted = convert_epoch_to_string(stop_epoch)
    print(f"ファイル名: {timestamp['ファイル名']}, mtime:{mtime_epoch},start: {start_formatted}, stop: {stop_formatted}, duration: {duration_formatted}")
    # 一つ前を記憶する
    prev_mtime = mtime_epoch
    prev_start_epoch = start_epoch

#for timestamp in fileTimestamps:
#    #print(f"ファイル名: {timestamp['ファイル名']}, mtime: {timestamp['mtime']}, length: {timestamp['duration']} seconds")
#
#    mtime_epoch = timestamp['mtime']
#    #mtime_datetime = datetime.datetime.fromtimestamp(mtime_epoch)
#    #mtime_formatted = mtime_datetime.strftime('%Y-%m-%d %H:%M:%S')
#    mtime_formatted = convert_epoch_to_string(mtime_epoch)
#    
#    duration = timestamp['duration']
#    start_epoch = mtime_epoch - duration
#    #start_datetime = datetime.datetime.fromtimestamp(start_epoch)
#    #start_formatted = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
#    start_formatted = convert_epoch_to_string(start_epoch)
#    # print(f"ファイル名: {timestamp['ファイル名']}, starttime: {start_formatted},mtime: {mtime_formatted}, length: {timestamp['duration']} seconds")
#
#    duration_formatted = str(datetime.timedelta(seconds=timestamp['duration']))
#    #duration_formatted = convert_epoch_to_string(timestamp['duration'])
#    print(f"ファイル名: {timestamp['ファイル名']}, starttime: {start_formatted}, mtime: {mtime_formatted}, length: {duration_formatted}")
#