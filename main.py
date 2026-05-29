#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoFX Studio By Decoy - Editable timescale & duration divisors
"""
import os
import struct
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
import webbrowser

# ضبط حجم النافذة والخلفية لتطابق الـ UI الأصلي (#282828)
Window.size = (460, 640)
Window.clearcolor = (0.15, 0.15, 0.15, 1)

# تم تغيير الاسم هنا لـ MainApp لضمان قراءة دالة build على الأندرويد
class MainApp(App):
    def build(self):
        self.title = "VideoFX Studio By Decoy"
        
        # الأجزاء الخاصة بالـ Statistics من كودك الأصلي
        self.videos_processed = 0
        self.total_params = 0
        
        # الأجزاء الخاصة بالـ Tips من كودك الأصلي
        self.tips = [
            "هذي الأداة امانة, لا تشاركها مع اي احد",
            "المقطع لازم يكون 60 فريم",
            "استخدم مقطع قوي وحماسي لافضل النتائج",
            "احفظ نسخة أصلية قبل التعديل"
        ]
        self.current_tip = 0

        # الـ Layout الرئيسي للتطبيق
        self.main_frame = BoxLayout(orientation='vertical', padding=18, spacing=10)

        # Top Bar (Help Button & Version)
        top = BoxLayout(size_hint_y=None, height=35)
        help_btn = Button(text="?", font_size='12sp', bold=True, size_hint_x=None, width=40, background_color=(0.12, 0.12, 0.12, 1))
        help_btn.bind(on_press=self.show_help)
        ver = Label(text="v1.0.3", color=(0.4, 0.4, 0.4, 1), font_size='10sp', size_hint_x=None, width=50)
        top.add_widget(help_btn)
        top.add_widget(Label()) # مسافة فارغة للمحاذاة
        top.add_widget(ver)
        self.main_frame.add_widget(top)

        # Title & Subtitle
        title = Label(text="VideoFX Studio", font_size='24sp', bold=True, size_hint_y=None, height=40)
        self.main_frame.add_widget(title)

        subtitle = Button(text="By Decoy", font_size='14sp', bold=True, color=(0, 0.65, 1, 1), size_hint_y=None, height=30, background_kind='flat', background_color=(0,0,0,0))
        subtitle.bind(on_press=lambda x: webbrowser.open("https://www.discord.gg/lbdecoy"))
        self.main_frame.add_widget(subtitle)

        # Status Frame
        self.status_label = Label(text="🟢 Ready", color=(0.66, 0.66, 0.66, 1), font_size='12sp', size_hint_y=None, height=25)
        self.main_frame.add_widget(self.status_label)

        # Controls (Divisors Group)
        controls = BoxLayout(orientation='vertical', padding=10, spacing=8, size_hint_y=None, height=180)
        
        # timescale divisor row
        ts_row = BoxLayout(spacing=10, size_hint_y=None, height=35)
        ts_row.add_widget(Label(text="Timescale divisor:", size_hint_x=0.6))
        self.ts_input = TextInput(text="5", multiline=False, input_filter='float', size_hint_x=0.4, background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        self.ts_input.bind(text=self.update_speed_display)
        ts_row.add_widget(self.ts_input)
        controls.add_widget(ts_row)

        # duration divisor row
        dur_row = BoxLayout(spacing=10, size_hint_y=None, height=35)
        dur_row.add_widget(Label(text="Duration divisor:", size_hint_x=0.6))
        self.dur_input = TextInput(text="5", multiline=False, input_filter='float', size_hint_x=0.4, background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        self.dur_input.bind(text=self.update_speed_display)
        dur_row.add_widget(self.dur_input)
        controls.add_widget(dur_row)

        # computed speed display
        self.speed_display = Label(text="Speed: 1.000×", font_size='14sp', bold=True, color=(0, 1, 0.73, 1), size_hint_y=None, height=25)
        controls.add_widget(self.speed_display)
        self.main_frame.add_widget(controls)

        # Note
        note = Label(text="(الافتراضي 5 و5 → سرعة 1.00×). تأكد من حفظ نسخة أصلية قبل التجربة.", color=(0.4, 0.4, 0.4, 1), font_size='11sp', size_hint_y=None, height=30)
        self.main_frame.add_widget(note)

        # File info & Progress
        self.file_info_label = Label(text="", font_size='12sp', color=(0.66, 0.66, 0.66, 1), size_hint_y=None, height=25)
        self.main_frame.add_widget(self.file_info_label)
        
        self.progress = ProgressBar(max=100, size_hint_y=None, height=15)
        self.main_frame.add_widget(self.progress)

        # Patch Button
        self.patch_button = Button(text="Choose Video to Patch", font_size='16sp', bold=True, background_color=(0.12, 0.12, 0.12, 1), size_hint_y=None, height=50)
        self.patch_button.bind(on_press=self.on_click)
        self.main_frame.add_widget(self.patch_button)

        # Stats Frame
        stats_box = BoxLayout(orientation='vertical', size_hint_y=None, height=50, spacing=2)
        stats_box.add_widget(Label(text="Statistics", bold=True, font_size='13sp'))
        self.stats_label = Label(text=f"Videos Processed: {self.videos_processed}\nTotal Parameters: {self.total_params}", color=(0.66, 0.66, 0.66, 1), font_size='11sp')
        stats_box.add_widget(self.stats_label)
        self.main_frame.add_widget(stats_box)

        # Tips Label
        self.tip_label = Label(text="", color=(0.4, 0.4, 0.4, 1), font_size='12sp', bold=True)
        self.main_frame.add_widget(self.tip_label)
        
        # تشغيل تدوير الـ Tips
        Clock.schedule_interval(self.rotate_tips, 3.0)
        self.rotate_tips(0)

        return self.main_frame

    def update_speed_display(self, instance, value):
        try:
            ts = float(self.ts_input.text)
            dur = float(self.dur_input.text)
            if ts <= 0 or dur <= 0:
                raise ValueError
            speed = dur / ts
            self.speed_display.text = f"Speed: {speed:.3f}×"
        except Exception:
            self.speed_display.text = "Speed: —"

    def show_help(self, instance):
        txt = ("مساعدة:\n"
               "1) اضغط Choose Video to Patch\n"
               "2) عدّل Timescale Divisor و Duration Divisor (الافتراضي 5)\n"
               "3) سرعة التشغيل = duration_divisor / timescale_divisor\n"
               "4) سيتم حفظ ملف جديد بنفس المجلد\n\nحافظ على نسخة أصلية قبل الاختبار.")
        self.show_popup("مساعدة", txt)

    def rotate_tips(self, dt):
        self.tip_label.text = self.tips[self.current_tip]
        self.current_tip = (self.current_tip + 1) % len(self.tips)

    def on_click(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        start_path = "/sdcard" if os.path.exists("/sdcard") else "."
        filechooser = FileChooserIconView(filters=['*.mp4'], path=start_path)
        content.add_widget(filechooser)
        
        buttons = BoxLayout(size_hint_y=None, height=45, spacing=10)
        cancel_btn = Button(text="Cancel", background_color=(0.3, 0.1, 0.1, 1))
        select_btn = Button(text="Select Video", background_color=(0.1, 0.3, 0.1, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(select_btn)
        content.add_widget(buttons)
        
        popup = Popup(title="Select MP4 to patch", content=content, size_hint=(0.95, 0.95))
        
        cancel_btn.bind(on_press=popup.dismiss)
        select_btn.bind(on_press=lambda btn: self.process_selected_file(filechooser.selection, popup))
        
        popup.open()

    def process_selected_file(self, selection, popup):
        if not selection:
            return
        filepath = selection[0]
        popup.dismiss()

        try:
            ts_div = float(self.ts_input.text)
            dur_div = float(self.dur_input.text)
            if ts_div <= 0 or dur_div <= 0:
                raise ValueError
        except Exception:
            self.show_popup("Input error", "الرجاء إدخال أرقام صالحة أكبر من 0 لكل من Timescale و Duration divisors.")
            return

        size_mb = os.path.getsize(filepath) / (1024*1024)
        self.file_info_label.text = f"File: {os.path.basename(filepath)}\nSize: {size_mb:.1f} MB"
        self.status_label.text = "🟡 Processing..."
        
        self.progress.value = 0
        Clock.schedule_interval(lambda dt: self.simulate_progress(dt, filepath, ts_div, dur_div), 0.01)

    def simulate_progress(self, dt, filepath, ts_div, dur_div):
        if self.progress.value < 100:
            self.progress.value += 5
            return True
        else:
            self.run_actual_patch(filepath, ts_div, dur_div)
            return False

    def run_actual_patch(self, filepath, ts_div, dur_div):
        try:
            out, c1, c2 = run_patch(filepath, timescale_divisor=ts_div, duration_divisor=dur_div)
            total = c1 + c2
            self.videos_processed += 1
            self.total_params += total
            self.stats_label.text = f"Videos Processed: {self.videos_processed}\nTotal Parameters: {self.total_params}"
            self.status_label.text = "🟢 Success!"
            self.show_popup("Success", f"Patch complete!\nOutput: {os.path.basename(out)}\nPatched items: {total}\nApplied: timescale_div={ts_div}, duration_div={dur_div}")
        except Exception as e:
            self.status_label.text = "🔴 Error!"
            self.show_popup("Error", f"Invalid file or unsupported format.\n{e}")

    def show_popup(self, title, text):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=text, halign='center'))
        close_btn = Button(text="OK", size_hint_y=None, height=40)
        box.add_widget(close_btn)
        popup = Popup(title=title, content=box, size_hint=(0.85, 0.45))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

# ----------------- Binary patch functions -----------------
def patch_param1(buf, timescale_divisor, duration_divisor):
    patched = 0
    offset = 0
    while True:
        idx = buf.find(b'mvhd', offset)
        if idx < 0:
            break
        pos = idx - 4
        if pos < 0 or pos + 12 > len(buf):
            offset = idx + 4
            continue
        try:
            version = buf[pos+8]
            if version == 0:
                ts_off = pos + 20
                dur_off = pos + 24
                if ts_off + 4 > len(buf) or dur_off + 4 > len(buf):
                    offset = idx + 4
                    continue
                old_ts = struct.unpack_from('>I', buf, ts_off)[0]
                old_dur = struct.unpack_from('>I', buf, dur_off)[0]
                new_ts = max(1, int(round(old_ts / float(timescale_divisor))))
                new_dur = max(1, int(round(old_dur / float(duration_divisor))))
                struct.pack_into('>I', buf, ts_off, new_ts)
                struct.pack_into('>I', buf, dur_off, new_dur)
            else:
                ts_off = pos + 28
                dur_off = pos + 32
                if ts_off + 4 > len(buf) or dur_off + 8 > len(buf):
                    offset = idx + 4
                    continue
                old_ts = struct.unpack_from('>I', buf, ts_off)[0]
                old_dur = struct.unpack_from('>Q', buf, dur_off)[0]
                new_ts = max(1, int(round(old_ts / float(timescale_divisor))))
                new_dur = max(1, int(round(old_dur / float(duration_divisor))))
                struct.pack_into('>I', buf, ts_off, new_ts)
                struct.pack_into('>Q', buf, dur_off, new_dur)
        except Exception:
            offset = idx + 4
            continue
        patched += 1
        offset = idx + 4
    return patched

def patch_param2(buf, timescale_divisor, duration_divisor):
    patched = 0
    offset = 0
    while True:
        idx = buf.find(b'mdhd', offset)
        if idx < 0:
            break
        pos = idx - 4
        if pos < 0 or pos + 12 > len(buf):
            offset = idx + 4
            continue
        try:
            version = buf[pos+8]
            if version == 0:
                ts_off = pos + 20
                dur_off = pos + 24
                if ts_off + 4 > len(buf) or dur_off + 4 > len(buf):
                    offset = idx + 4
                    continue
                old_ts = struct.unpack_from('>I', buf, ts_off)[0]
                old_dur = struct.unpack_from('>I', buf, dur_off)[0]
                new_ts = max(1, int(round(old_ts / float(timescale_divisor))))
                new_dur = max(1, int(round(old_dur / float(duration_divisor))))
                struct.pack_into('>I', buf, ts_off, new_ts)
                struct.pack_into('>I', buf, dur_off, new_dur)
            else:
                ts_off = pos + 28
                dur_off = pos + 32
                if ts_off + 4 > len(buf) or dur_off + 8 > len(buf):
                    offset = idx + 4
                    continue
                old_ts = struct.unpack_from('>I', buf, ts_off)[0]
                old_dur = struct.unpack_from('>Q', buf, dur_off)[0]
                new_ts = max(1, int(round(old_ts / float(timescale_divisor))))
                new_dur = max(1, int(round(old_dur / float(duration_divisor))))
                struct.pack_into('>I', buf, ts_off, new_ts)
                struct.pack_into('>Q', buf, dur_off, new_dur)
        except Exception:
            offset = idx + 4
            continue
        patched += 1
        offset = idx + 4
    return patched

def run_patch(filepath, timescale_divisor=5.0, duration_divisor=5.0):
    with open(filepath, 'rb') as fh:
        buf = bytearray(fh.read())
    c1 = patch_param1(buf, timescale_divisor, duration_divisor)
    c2 = patch_param2(buf, timescale_divisor, duration_divisor)
    if c1 == 0 and c2 == 0:
        raise RuntimeError("No mvhd/mdhd atoms found or unsupported file structure.")
    out = filepath.replace('.mp4', f'_tsdiv{int(timescale_divisor)}_durdiv{int(duration_divisor)}.mp4')
    with open(out, 'wb') as fh:
        fh.write(buf)
    return out, c1, c2

# تم تعديل طريقة التشغيل لتعمل بالتوافق مع اسم الكلاس الجديد
if __name__ == '__main__':
    MainApp().run()
