"""
The webhook where promotion codes will be sent.
"""
webhook_url = "https://discord.com/api/webhooks/.../..."

"""
The mode to use when getting the promotion codes.
You can either use 'webdriver' which is more reliable, but slower...
... or you can use 'request' which is insanely fast, but probably unreliable.
"""
mode = "request"

"""
The proxy to use when acquiring the promotion codes.
This cannot be an http proxy if you use 'webdriver' mode.
Set to None to disable.
"""
proxy = None
# using tor:
# proxy = "socks5://127.0.0.1:9000"

"""
You only need to fill these out if you use 'webdriver' mode.
"""

r"""
The executable file of opera gx.
Can be one of the following:
'C:\Program Files\Opera GX\opera.exe' (installed for all users)
'C:\Users\YOURUSERFOLDER\AppData\Local\Programs\Opera GX\opera.exe' (installed only for you)
"""
opera_gx_executable = r'C:\Program Files\Opera GX\opera.exe'

"""
Download from here: https://github.com/operasoftware/operachromiumdriver/releases
"""
opera_driver = r'C:\Users\YOURUSERFOLDER\Downloads\operadriver_win64\operadriver.exe'
