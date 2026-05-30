[app]
title = VideoFX Studio
package.name = videofxstudio
package.domain = org.test.videofxstudio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# الأذونات المتوافقة تماماً مع الأكواد الجديدة في main.py لمنع الكراش
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, android.permission.READ_MEDIA_VIDEO, android.permission.READ_MEDIA_IMAGES

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

android.accept_sdk_license = True
android.enable_androidx = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
