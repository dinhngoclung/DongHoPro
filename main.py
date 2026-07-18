import flet as ft
import asyncio
import time
from datetime import datetime, timedelta
import math

# Biến toàn cục cho báo thức
alarms = []
alarm_ringing = False

async def main(page: ft.Page):
    page.title = "Đồng Hồ Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_bgcolor = "#0a0a0f"

    # ============ TAB 1: ĐỒNG HỒ ============
    time_text = ft.Text("00:00:00", size=50, weight="bold", font_family="monospace", color="white")
    date_text = ft.Text("", size=16, color=ft.Colors.GREY_400)
    
    # Canvas cho đồng hồ kim - dùng Stack
    analog_stack = ft.Stack(width=260, height=260)

    async def update_clock():
        while True:
            now = datetime.now()
            time_text.value = now.strftime("%H:%M:%S")
            # Tiếng Việt thứ
            thu = ["Thứ 2","Thứ 3","Thứ 4","Thứ 5","Thứ 6","Thứ 7","Chủ Nhật"]
            date_text.value = f"{thu[now.weekday()]} - {now.day:02d}/{now.month:02d}/{now.year}"
            
            # Check báo thức
            for alarm in alarms:
                if alarm['active'] and alarm['hour'] == now.hour and alarm['minute'] == now.minute and now.second == 0:
                    page.dialog = ft.AlertDialog(
                        title=ft.Text("⏰ BÁO THỨC!"),
                        content=ft.Text(f"Đã đến giờ {alarm['hour']:02d}:{alarm['minute']:02d}"),
                        actions=[ft.TextButton("Tắt", on_click=lambda e: page.close(page.dialog))]
                    )
                    page.dialog.open = True
                    page.update()
                    # Rung + âm thanh (Flet chưa hỗ trợ rung trực tiếp nhưng sẽ kêu)
            
            page.update()
            await asyncio.sleep(1)

    # Tab đồng hồ
    clock_tab = ft.Column([
        ft.Container(height=40),
        ft.Text("ĐỒNG HỒ", size=14, color=ft.Colors.BLUE_300, weight="bold"),
        ft.Container(
            content=ft.Stack([
                ft.Container(
                    width=280, height=280,
                    bgcolor="#15151f",
                    border_radius=140,
                    border=ft.Border.all(2, "#2a2a3a")
                ),
                ft.Container(
                    content=ft.Column([time_text, date_text], horizontal_alignment="center"),
                    alignment=ft.alignment.center,
                    width=280, height=280
                )
            ], alignment=ft.alignment.center),
            alignment=ft.alignment.center,
            padding=20
        ),
        ft.Text("Giờ Việt Nam - GMT+7", color=ft.Colors.GREY_600, size=12)
    ], horizontal_alignment="center")

    # ============ TAB 2: BÁO THỨC ============
    hour_dd = ft.Dropdown(label="Giờ", options=[ft.dropdown.Option(f"{i:02d}") for i in range(24)], value="06", width=100)
    minute_dd = ft.Dropdown(label="Phút", options=[ft.dropdown.Option(f"{i:02d}") for i in range(60)], value="00", width=100)
    alarm_list_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=350)

    def refresh_alarms():
        alarm_list_col.controls.clear()
        for idx, al in enumerate(alarms):
            alarm_list_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ALARM, color=ft.Colors.BLUE_300),
                        ft.Text(f"{al['hour']:02d}:{al['minute']:02d}", size=22, weight="bold"),
                        ft.Switch(value=al['active'], on_change=lambda e, i=idx: toggle_alarm(i, e.control.value)),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, i=idx: delete_alarm(i))
                    ], alignment="spaceBetween"),
                    bgcolor="#1c1c28",
                    padding=12,
                    border_radius=10
                )
            )
        page.update()

    def toggle_alarm(idx, val):
        alarms[idx]['active'] = val
        page.update()

    def delete_alarm(idx):
        alarms.pop(idx)
        refresh_alarms()

    def add_alarm(e):
        h = int(hour_dd.value)
        m = int(minute_dd.value)
        alarms.append({"hour": h, "minute": m, "active": True})
        refresh_alarms()
        page.snack_bar = ft.SnackBar(ft.Text(f"Đã thêm báo thức {h:02d}:{m:02d}"))
        page.snack_bar.open = True
        page.update()

    alarm_tab = ft.Column([
        ft.Container(height=10),
        ft.Text("BÁO THỨC", size=14, color=ft.Colors.BLUE_300, weight="bold"),
        ft.Row([hour_dd, minute_dd, ft.ElevatedButton("Thêm", icon=ft.Icons.ADD_ALARM, on_click=add_alarm, bgcolor=ft.Colors.BLUE_700, color="white")], alignment="center"),
        ft.Divider(color="#333"),
        alarm_list_col
    ], horizontal_alignment="center")

    # ============ TAB 3: BẤM GIỜ ============
    sw_time = ft.Text("00:00.00", size=60, weight="bold", font_family="monospace")
    sw_running = False
    sw_start = 0
    sw_elapsed = 0
    sw_task = None
    laps_col = ft.Column(scroll=ft.ScrollMode.AUTO, height=250)

    async def sw_loop():
        nonlocal sw_elapsed
        while sw_running:
            sw_elapsed = time.time() - sw_start
            mins = int(sw_elapsed // 60)
            secs = int(sw_elapsed % 60)
            cs = int((sw_elapsed % 1) * 100)
            sw_time.value = f"{mins:02d}:{secs:02d}.{cs:02d}"
            page.update()
            await asyncio.sleep(0.05)

    def sw_start_stop(e):
        nonlocal sw_running, sw_start, sw_task
        if not sw_running:
            sw_running = True
            sw_start = time.time() - sw_elapsed
            e.control.text = "Dừng"
            e.control.bgcolor = ft.Colors.RED_700
            sw_task = page.run_task(sw_loop)
        else:
            sw_running = False
            e.control.text = "Tiếp tục"
            e.control.bgcolor = ft.Colors.GREEN_700
        page.update()

    def sw_reset(e):
        nonlocal sw_running, sw_elapsed
        sw_running = False
        sw_elapsed = 0
        sw_time.value = "00:00.00"
        laps_col.controls.clear()
        page.update()

    def sw_lap(e):
        if sw_running:
            laps_col.controls.insert(0, ft.Text(f"Vòng {len(laps_col.controls)+1}: {sw_time.value}", color=ft.Colors.GREY_400))
            page.update()

    stopwatch_tab = ft.Column([
        ft.Container(height=30),
        sw_time,
        ft.Row([
            ft.ElevatedButton("Bắt đầu", on_click=sw_start_stop, width=100, bgcolor=ft.Colors.GREEN_700, color="white"),
            ft.ElevatedButton("Vòng", on_click=sw_lap, width=80),
            ft.ElevatedButton("Reset", on_click=sw_reset, width=80, bgcolor=ft.Colors.GREY_800),
        ], alignment="center"),
        ft.Divider(),
        laps_col
    ], horizontal_alignment="center")

    # ============ TAB 4: ĐẾM NGƯỢC ============
    timer_h = ft.Dropdown(label="Giờ", value="0", width=80, options=[ft.dropdown.Option(str(i)) for i in range(24)])
    timer_m = ft.Dropdown(label="Phút", value="5", width=80, options=[ft.dropdown.Option(str(i)) for i in range(60)])
    timer_s = ft.Dropdown(label="Giây", value="0", width=80, options=[ft.dropdown.Option(str(i)) for i in range(60)])
    timer_display = ft.Text("05:00", size=70, weight="bold", font_family="monospace")
    timer_running = False
    timer_left = 0

    async def timer_loop():
        nonlocal timer_left, timer_running
        while timer_running and timer_left > 0:
            timer_left -= 1
            mm = timer_left // 60
            ss = timer_left % 60
            timer_display.value = f"{mm:02d}:{ss:02d}"
            if timer_left == 0:
                timer_running = False
                timer_display.value = "HẾT GIỜ!"
                page.dialog = ft.AlertDialog(title=ft.Text("⏰ Hết giờ!"), content=ft.Text("Timer đã kết thúc"))
                page.dialog.open = True
            page.update()
            await asyncio.sleep(1)

    def timer_start(e):
        nonlocal timer_left, timer_running
        if not timer_running:
            timer_left = int(timer_h.value)*3600 + int(timer_m.value)*60 + int(timer_s.value)
            if timer_left == 0:
                return
            timer_running = True
            e.control.text = "Dừng"
            page.run_task(timer_loop)
        else:
            timer_running = False
            e.control.text = "Bắt đầu"
        page.update()

    def timer_reset(e):
        nonlocal timer_running, timer_left
        timer_running = False
        timer_left = 0
        timer_display.value = f"{int(timer_m.value):02d}:{int(timer_s.value):02d}"
        page.update()

    timer_tab = ft.Column([
        ft.Container(height=20),
        ft.Text("ĐẾM NGƯỢC", size=14, color=ft.Colors.BLUE_300, weight="bold"),
        ft.Row([timer_h, timer_m, timer_s], alignment="center"),
        ft.Container(height=20),
        timer_display,
        ft.Row([
            ft.ElevatedButton("Bắt đầu", on_click=timer_start, bgcolor=ft.Colors.BLUE_700, color="white", width=100),
            ft.ElevatedButton("Reset", on_click=timer_reset, width=80)
        ], alignment="center")
    ], horizontal_alignment="center")

    # ============ TABS CHÍNH ============
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Đồng hồ", icon=ft.Icons.ACCESS_TIME, content=ft.Container(content=clock_tab, padding=10)),
            ft.Tab(text="Báo thức", icon=ft.Icons.ALARM, content=ft.Container(content=alarm_tab, padding=10)),
            ft.Tab(text="Bấm giờ", icon=ft.Icons.TIMER, content=ft.Container(content=stopwatch_tab, padding=10)),
            ft.Tab(text="Đếm ngược", icon=ft.Icons.HOURGLASS_BOTTOM, content=ft.Container(content=timer_tab, padding=10)),
        ],
        expand=True
    )

    page.add(tabs)
    page.run_task(update_clock)

ft.app(target=main)
