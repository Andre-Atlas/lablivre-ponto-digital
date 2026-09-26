with open("desktop_app/app/core/api_client.py", "r") as f:
    content = f.read()

content = content.replace("with httpx.Client() as client:", "with httpx.Client(timeout=30.0) as client:")

with open("desktop_app/app/core/api_client.py", "w") as f:
    f.write(content)

with open("desktop_app/main.py", "r") as f:
    main_content = f.read()
    
main_content = main_content.replace('print("Erro de conexão:", ex)\n            show_error("Backend offline ou inacessível")',
                                    'print("Erro de conexão:", ex)\n            show_error(f"Backend offline: {ex}")')

with open("desktop_app/main.py", "w") as f:
    f.write(main_content)
