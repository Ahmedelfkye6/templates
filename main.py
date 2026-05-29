# -*- coding: utf-8 -*-
import os
import struct
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window

# إعداد لون خلفية افتراضي متناسق (رمادي غامق مثل كودك القديم)
Window.clearcolor = (0.15, 0.15, 0.15, 1)

class VideoFXAndroidApp(App):
    def build(self):
        self.title = "VideoFX Studio By Ahmed"
        
        # الحاوية الرئيسية
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # العنوان
        layout.add_widget(Label(text="VideoFX Studio", font_size='28sp', bold=True, color=(1, 1, 1, 1)))
        layout.add_widget(Label(text="By Ahmed", font_size='18sp', bold=True, color=(0, 0.65, 1, 1)))
        
        # مدخلات الـ Divisors
        input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='40dp')
        input_layout.add_widget(Label(text="Timescale Divisor:", size_hint_x=0.6, halign='left'))
        self.ts_input = TextInput(text="5", multiline=False, input_filter='float', size_hint_x=0.4)
        input_layout.add_widget(self.ts_input)
        layout.add_widget(input_layout)
        
        input_layout2 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height='40dp')
        input_layout2.add_widget(Label(text="Duration Divisor:", size_hint_x=0.6, halign='left'))
        self.dur_input = TextInput(text="5", multiline=False, input_filter='float', size_hint_x=0.4)
        input_layout2.add_widget(self.dur_input)
        layout.add_widget(input_layout2)
        
        # عرض السرعة المحسوبة
        self.speed_label = Label(text="Speed: 1.000x", font_size='16sp', bold=True, color=(0, 1, 0.73, 1))
        layout.add_widget(self.speed_label)
        
        # ربط التحديث التلقائي للسرعة عند تغيير الأرقام
        self.ts_input.bind(text=self.update_speed)
        self.dur_input.bind(text=self.update_speed)
        
        # نصائح وتنبيهات
        layout.add_widget(Label(text="تأكد من حفظ نسخة أصلية من الفيديو قبل تعديله.\nالمقطع يفضل أن يكون 60 فريم.", 
                                font_size='12sp', color=(0.5, 0.5, 0.5, 1), halign='center'))
        
        # زر اختيار الفيديو والبدء
        self.patch_btn = Button(text="Choose Video to Patch", size_hint_y=None, height='60dp',
                                background_color=(0.1, 0.1, 0.1, 1), font_size='18sp')
        self.patch_btn.bind(on_press=self.open_file_chooser)
        layout.add_widget(self.patch_btn)
        
        return layout

    def update_speed(self, instance, value):
        try:
            ts = float(self.ts_input.text)
            dur = float(self.dur_input.text)
            if ts <= 0 or dur <= 0:
                raise ValueError
            self.speed_label.text = f"Speed: {(dur / ts):.3f}x"
        except ValueError:
            self.speed_label.text = "Speed: --"

    def open_file_chooser(self, instance):
        # فتح نافذة بوب أب داخل التطبيق لاختيار الملف (بديل الـ filedialog)
        popup_layout = BoxLayout(orientation='vertical')
        file_chooser = FileChooserIconView(filters=['*.mp4'], path='/sdcard')
        popup_layout.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        select_btn = Button(text="Select Video")
        cancel_btn = Button(text="Cancel")
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        popup_layout.add_widget(btn_layout)
        
        popup = Popup(title="Select MP4 File", content=popup_layout, size_hint=(0.9, 0.9))
        
        cancel_btn.bind(on_press=popup.dismiss)
        
        def on_select(btn_instance):
            if file_chooser.selection:
                selected_file = file_chooser.selection[0]
                popup.dismiss()
                self.process_video(selected_file)
        
        select_btn.bind(on_press=on_select)
        popup.open()

    def process_video(self, filepath):
        try:
            ts_div = float(self.ts_input.text)
            dur_div = float(self.dur_input.text)
            if ts_div <= 0 or dur_div <= 0:
                raise ValueError
        except ValueError:
            self.show_popup("Error", "الرجاء إدخال قيم صالحة أكبر من صفر")
            return

        try:
            # دالة المعالجة المباشرة (نفس منطق كودك الأصلي الباينري)
            with open(filepath, 'rb') as fh:
                buf = bytearray(fh.read())
            
            c1 = self.patch_atom(buf, b'mvhd', ts_div, dur_div)
            c2 = self.patch_atom(buf, b'mdhd', ts_div, dur_div)
            
            if c1 == 0 and c2 == 0:
                raise RuntimeError("لم يتم العثور على ذرات mvhd/mdhd في الملف.")
                
            out_path = filepath.replace('.mp4', f'_tsdiv{int(ts_div)}_durdiv{int(dur_div)}.mp4')
            with open(out_path, 'wb') as fh:
                fh.write(buf)
                
            self.show_popup("Success", f"تم التعديل بنجاح!\nالملف الجديد يحمل اسم:\n{os.path.basename(out_path)}")
        except Exception as e:
            self.show_popup("Error", f"فشلت العملية:\n{str(e)}")

    def patch_atom(self, buf, atom_name, ts_div, dur_div):
        patched = 0
        offset = 0
        while True:
            idx = buf.find(atom_name, offset)
            if idx < 0: break
            pos = idx - 4
            if pos < 0 or pos + 12 > len(buf):
                offset = idx + 4
                continue
            try:
                version = buf[pos+8]
                if version == 0:
                    ts_off, dur_off = pos + 20, pos + 24
                    old_ts = struct.unpack_from('>I', buf, ts_off)[0]
                    old_dur = struct.unpack_from('>I', buf, dur_off)[0]
                    new_ts = max(1, int(round(old_ts / float(ts_div))))
                    new_dur = max(1, int(round(old_dur / float(dur_div))))
                    struct.pack_into('>I', buf, ts_off, new_ts)
                    struct.pack_into('>I', buf, dur_off, new_dur)
                else:
                    ts_off, dur_off = pos + 28, pos + 32
                    old_ts = struct.unpack_from('>I', buf, ts_off)[0]
                    old_dur = struct.unpack_from('>Q', buf, dur_off)[0]
                    new_ts = max(1, int(round(old_ts / float(ts_div))))
                    new_dur = max(1, int(round(old_dur / float(dur_div))))
                    struct.pack_into('>I', buf, ts_off, new_ts)
                    struct.pack_into('>Q', buf, dur_off, new_dur)
                patched += 1
            except Exception:
                pass
            offset = idx + 4
        return patched

    def show_popup(self, title, message):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=message, halign='center'))
        btn = Button(text="OK", size_hint_y=None, height='40dp')
        box.add_widget(btn)
        popup = Popup(title=title, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    VideoFXAndroidApp().run()
    print("ahmed")
