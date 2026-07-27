[app]
title = YT Downloader Pro
package.name = ytdownloader
package.domain = org.ytapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3,kivy,pyjnius,android,yt-dlp

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 28
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

log_level = 2
