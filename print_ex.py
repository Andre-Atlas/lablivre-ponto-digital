with open("desktop_app/app/views/checkin_view.py", "r") as f:
    content = f.read()
content = content.replace("except Exception as ex:", "except Exception as ex:\n            print(f'ERRO CHECKIN: {ex}')\n            import traceback; traceback.print_exc()")
with open("desktop_app/app/views/checkin_view.py", "w") as f:
    f.write(content)
