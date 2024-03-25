import flet as ft
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Text,
    icons,
)
import os
import wave
import datetime

# 関数の定義
name = "Add items to dropdown options"


def example():
    async def add_clicked(e):
        d.options.append(ft.dropdown.Option(option_textbox.value))
        d.value = option_textbox.value
        option_textbox.value = ""
        await option_textbox.update_async()
        await d.update_async()

    d = ft.Dropdown()
    option_textbox = ft.TextField(hint_text="Enter item name")
    add = ft.ElevatedButton("Add", on_click=add_clicked)

    return ft.Column(controls=[d, ft.Row(controls=[option_textbox, add])])
example()

def convert_epoch_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%Y-%m-%d %H:%M:%S')
def main(page: Page):
    fileTimestamps = []
    # Pick files dialog
    def pick_files_result(e: FilePickerResultEvent):
        selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        )
        selected_files.update()

    pick_files_dialog = FilePicker(on_result=pick_files_result)
    selected_files = Text()

    # Save file dialog
    def save_file_result(e: FilePickerResultEvent):
        save_file_path.value = e.path if e.path else "Cancelled!"
        save_file_path.update()

    save_file_dialog = FilePicker(on_result=save_file_result)
    save_file_path = Text()

    def list_audio_files(directory):
        file_groups = {}
        # 対象の音声ファイルの拡張子
        audio_extensions = ['.wav']
        # ディレクトリ内の全ファイルを取得
        all_files = os.listdir(directory)
        # 音声ファイルのみをフィルタリング
        audio_files = [file for file in all_files if os.path.splitext(file)[1].lower() in audio_extensions]
        # テキストウィジェットに表示するための文字列を生成
        audio_files_list = "\n".join(audio_files)
        print(audio_files)

        for file in audio_files:
            file_stat = os.stat(os.path.join(directory, file))
            file_timestamp = file_stat.st_mtime
            with wave.open(os.path.join(directory, file), 'r') as wav_file:
                duration = wav_file.getnframes() / wav_file.getframerate()
                fileTimestamps.append({ 'filname': file, 'mtime': file_timestamp, 'duration': duration })

        prev_mtime = 0
        groups = 0 # 同じmtimeを持っているグループ数
        msg = ""
        for timestamp in sorted(fileTimestamps, key=lambda x: x['filname'], reverse=True):
            mtime_epoch = timestamp['mtime']
            mtime_formatted = convert_epoch_to_string(mtime_epoch)
            print(f"mtime_epoch: {mtime_epoch}, ファイル名: {timestamp['filname']}")
            if mtime_epoch not in file_groups:
                file_groups[mtime_epoch] = []
                if mtime_epoch == prev_mtime:
                    groups += 1
                    stop_epoch = prev_start_epoch
                else:
                    stop_epoch = timestamp['mtime']
            file_groups[mtime_epoch].append(timestamp['filname'])

            duration = timestamp['duration']
            start_epoch = stop_epoch - duration
            # フォーマットをを揃える:w
            duration_formatted = str(datetime.timedelta(seconds=timestamp['duration']))
            start_formatted = convert_epoch_to_string(start_epoch)
            stop_formatted = convert_epoch_to_string(stop_epoch)
            #msg += f" {timestamp['filname']}, mtime:{mtime_formatted},start: {start_formatted}, stop: {stop_formatted}, duration: {duration_formatted}\n"
            msg += f" {timestamp['filname']}: 最終変更時刻: {mtime_formatted}, 録音時間: {duration_formatted}\n"
        # テキストウィジェットに音声ファイルのリストを設定   
            # 一つ前を記憶する
            prev_mtime = mtime_epoch
            prev_start_epoch = start_epoch
        for group_mtime, filenames in file_groups.items():
            msg += f"同一録音の分割ファイルグループ：{filenames}\n"
            print(f"グループのmtime: {group_mtime}, ファイル数: {len(filenames)},ファイル名:{filenames}")
        print(msg)
        list_files_in_directory.value = msg
        list_files_in_directory.update()

    files_group = []
    def merge_sounds_group():
        # files_groupに含まれる複数のファイルをffmpegを使用してマージするコード
        import subprocess

        # マージするファイルの一時リストファイルを作成
        with open('files_to_merge.txt', 'w') as merge_file:
            for filename in files_group:
                merge_file.write(f"file '{filename}'\n")

        # ffmpegを使用してファイルをマージ
        merged_filename = 'merged_output.wav'
        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'files_to_merge.txt', '-c', 'copy', merged_filename])

        # 一時リストファイルを削除
        os.remove('files_to_merge.txt')

        print(f"マージ完了: {merged_filename}")
        print("merge_sounds_group")

    # ディレクトリ選択結果の処理を変更して音声ファイルのリストを表示
    def get_directory_result(e: FilePickerResultEvent):
        if e.path:
            directory_path.value = e.path
            list_audio_files(e.path)
        else:
            directory_path.value = "Cancelled!"
        directory_path.update()

    get_directory_dialog = FilePicker(on_result=get_directory_result)
    directory_path = Text()
    

    # hide all dialogs in overlay
    page.overlay.extend([pick_files_dialog, save_file_dialog, get_directory_dialog])

    #default_list_files_in_dir = f"ファイル名: \nduration: \nファイル: \nパス: \nフルパス: "
    default_list_files_in_dir = f""
    list_files_in_directory = ft.TextField(
        label="選択したファイル情報",
        multiline=True,
        min_lines=4,
        read_only=True,
        max_lines=None,
        value=default_list_files_in_dir,
    )
    page.add(
        Text("位置の登録・選択", size=20, weight="bold"),
        Row(
            [
                ElevatedButton(
                    "Open directory",
                    icon=icons.FOLDER_OPEN,
                    on_click=lambda _: get_directory_dialog.get_directory_path(),
                    disabled=page.web,
                ),
                directory_path,
            ]
        ),
        list_files_in_directory,
        Row(
            [
                ElevatedButton(
                    "同一録音のマージ",
                    icon=icons.UPLOAD_FILE,
                    on_click= merge_sounds_group(),
                    disabled=False,
                ),
                selected_files,
            ]
        ),
        Row(
            [
                ElevatedButton(
                    "Save file",
                    icon=icons.SAVE,
                    on_click=lambda _: save_file_dialog.save_file(),
                    disabled=page.web,
                ),
                save_file_path,
            ]
        ),
    )
    


ft.app(target=main)

