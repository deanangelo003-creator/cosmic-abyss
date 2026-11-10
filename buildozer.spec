[app]

# (str) Title of your application
title = Cosmic Abyss

# (str) Package name
package.name = cosmicabyss

# (str) Package domain (needed for android packaging)
package.domain = org.abyss

# (str) Application versioning
version = 0.1

# (str) Source files where the app lives
source.dir = .

# (list) Source files to include (add image/font extensions used by your game)
source.include_exts = py,png,jpg,atlas,ttf

# (list) Application requirements
requirements = python3,pygame,sdl2_ttf,sdl2_image,sdl2_mixer,sdl2

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.min_api = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Automatically accept Android SDK licenses
android.accept_sdk_license = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
