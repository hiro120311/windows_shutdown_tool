import os
import re
import sys
import tkinter as tk
from datetime import datetime, timedelta
import subprocess

# 即時シャットダウンタイマーの終了時刻を保持
immediate_shutdown_end_time = None

# ソフトウェアのバージョン情報
software_version = "1.0.0"

def set_timer():
    """即時シャットダウンタイマーを設定"""
    global immediate_shutdown_end_time
    try:
        time_in_seconds = int(entry_timer.get())
        if time_in_seconds > 0:
            os.system(f"shutdown /s /t {time_in_seconds}")
            immediate_shutdown_end_time = datetime.now() + timedelta(seconds=time_in_seconds)
            response_label.config(text=f"{time_in_seconds}秒後にシャットダウンが実行されます。", fg="green")
        else:
            response_label.config(text="正の整数を入力してください。", fg="red")
    except ValueError:
        response_label.config(text="有効な整数を入力してください。", fg="red")

def cancel_shutdown():
    """即時シャットダウンタイマーをキャンセル"""
    global immediate_shutdown_end_time
    os.system("shutdown /a")
    immediate_shutdown_end_time = None
    response_label.config(text="シャットダウンがキャンセルされました。", fg="blue")

def get_timer():
    """現在の即時シャットダウンタイマー設定を取得"""
    if immediate_shutdown_end_time is not None:
        remaining_time = immediate_shutdown_end_time - datetime.now()
        if remaining_time.total_seconds() > 0:
            response_label.config(
                text=f"現在の即時タイマー: 残り {int(remaining_time.total_seconds())} 秒", fg="blue"
            )
        else:
            response_label.config(text="即時タイマーは期限切れです。", fg="red")
    else:
        response_label.config(text="即時タイマーは設定されていません。", fg="red")

def set_daily_shutdown():
    """毎日決まった時刻にシャットダウンを設定"""
    time_str = entry_daily_time.get()
    task_name = "DailyShutdownTask"
    try:
        # 入力された時刻を検証
        shutdown_time = datetime.strptime(time_str, "%H:%M").time()
        # 既存タスクがあれば削除して新規作成
        delete_command = f"schtasks /delete /tn {task_name} /f"
        subprocess.run(delete_command, shell=True)

        create_command = f"schtasks /create /tn {task_name} /tr \"shutdown /s /t 0\" /sc daily /st {shutdown_time.strftime('%H:%M')} /f"
        subprocess.run(create_command, shell=True)

        response_label.config(text=f"毎日 {shutdown_time.strftime('%H:%M')} にシャットダウンを設定しました。", fg="green")
    except ValueError:
        response_label.config(text="有効な時刻を HH:MM の形式で入力してください。", fg="red")
    except subprocess.CalledProcessError:
        response_label.config(text="タスクスケジューラの設定に失敗しました。", fg="red")

def delete_daily_shutdown():
    """毎日のシャットダウンタスクを削除"""
    task_name = "DailyShutdownTask"
    try:
        delete_command = f"schtasks /delete /tn {task_name} /f"
        subprocess.run(delete_command, shell=True)
        response_label.config(text="毎日のシャットダウンを削除しました。", fg="blue")
    except subprocess.CalledProcessError:
        response_label.config(text="タスクの削除に失敗しました。", fg="red")

def get_daily_shutdown_time():
    """現在のタスクスケジューラ設定を取得"""
    task_name = "DailyShutdownTask"
    command = f"schtasks /query /tn {task_name} /fo LIST"
    try:
        # capture_output=True を使って標準出力を取得
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout  # コマンドの出力内容を取得
        task_found = False
        for line in output.splitlines():
            if "次回の実行時刻" in line:  # 「次回の実行時刻」を確認
                # 「次回の実行時刻: 2025/01/02 08:30:00」の形式にマッチする
                header_str = line.split(":")[0]
                next_run_time = line.replace(header_str, '')
                response_label.config(text=f"毎日シャットダウン時刻: {next_run_time}", fg="blue")
                task_found = True
                break
        if not task_found:
            response_label.config(text="毎日シャットダウンが設定されていません。", fg="red")
    except subprocess.CalledProcessError as e:
        # コマンド実行時のエラーを処理
        response_label.config(text=f"タスクの取得に失敗しました: {e}", fg="red")

def show_help():
    """ヘルプ情報をポップアップウィンドウで表示"""
    help_text = (
        "1. 即時シャットダウン:\n"
        "   - 秒数を入力して「タイマーを設定」をクリックします。\n"
        "   - 「シャットダウンをキャンセル」で即時タイマーを停止します。\n"
        "   - 「現在の即時タイマーを取得」で設定中のタイマー残り時間を確認できます。\n\n"
        "2. 毎日シャットダウン:\n"
        "   - 時刻を HH:MM 形式で入力して「毎日タイマーを設定」をクリックします。\n"
        "   - 「毎日タイマーを削除」で設定を解除します。\n"
        "   - 「現在の毎日タイマーを取得」で設定された時間を確認できます。\n\n"
        "注意: 管理者権限が必要な場合があります。\n\n"
        "バージョン情報:\n"
        f"ソフトウェア バージョン: {software_version}\n"
        f"Python バージョン: {sys.version}\n"
        f"tkinter バージョン: {tk.TkVersion}\n"
    )

    # ポップアップウィンドウの作成
    help_window = tk.Toplevel(root)
    help_window.title("ヘルプ")
    help_window.geometry("800x400")  # ウィンドウサイズ変更

    # ヘルプテキストを表示するラベル
    help_label = tk.Label(help_window, text=help_text, font=("Arial", 12), justify="left", anchor="nw", padx=10, pady=10)
    help_label.pack(fill="both", expand=True)

    # ヘルプウィンドウをテキストに合わせてサイズ調整
    help_window.grid_rowconfigure(0, weight=1)
    help_window.grid_columnconfigure(0, weight=1)

    # 閉じるボタン
    close_button = tk.Button(help_window, text="閉じる", command=help_window.destroy)
    close_button.pack(pady=10)


# GUIの作成
root = tk.Tk()
root.title("Windows シャットダウンツール")

# 既存のGUIコードの中で、ヘルプボタンを使用してポップアップウィンドウを表示
help_button = tk.Button(root, text="ヘルプ", font=("Arial", 12), command=show_help)
help_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# 即時タイマーセクション
frame_timer = tk.Frame(root)
frame_timer.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

tk.Label(frame_timer, text="シャットダウンまでの時間 (秒):").grid(row=0, column=0, pady=5, sticky="ew")
entry_timer = tk.Entry(frame_timer)
entry_timer.grid(row=1, column=0, pady=5, sticky="ew")
tk.Button(frame_timer, text="タイマーを設定", command=set_timer).grid(row=2, column=0, pady=5, sticky="ew")
tk.Button(frame_timer, text="シャットダウンをキャンセル", command=cancel_shutdown).grid(row=3, column=0, pady=5, sticky="ew")
tk.Button(frame_timer, text="現在の即時タイマーを取得", command=get_timer).grid(row=4, column=0, pady=5, sticky="ew")

# 毎日タイマーセクション
frame_daily = tk.Frame(root)
frame_daily.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

tk.Label(frame_daily, text="毎日シャットダウン時刻 (HH:MM):").grid(row=0, column=0, pady=5, sticky="ew")
entry_daily_time = tk.Entry(frame_daily)
entry_daily_time.grid(row=1, column=0, pady=5, sticky="ew")
tk.Button(frame_daily, text="毎日タイマーを設定", command=set_daily_shutdown).grid(row=2, column=0, pady=5, sticky="ew")
tk.Button(frame_daily, text="毎日タイマーを削除", command=delete_daily_shutdown).grid(row=3, column=0, pady=5, sticky="ew")
tk.Button(frame_daily, text="現在の毎日タイマーを取得", command=get_daily_shutdown_time).grid(row=4, column=0, pady=5, sticky="ew")

# 結果表示用ラベル
response_label = tk.Label(root, text="", font=("Arial", 10), fg="black")
response_label.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

# ウィンドウサイズ
root.geometry("400x600")
root.mainloop()
