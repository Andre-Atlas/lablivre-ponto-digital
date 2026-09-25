#!/bin/bash
echo "Instalando dependências de empacotamento..."
pip install flet
echo "Empacotando o aplicativo Ponto Digital..."
flet pack main.py --name "Ponto Digital" --icon assets/icon.png
echo "Pronto! Verifique a pasta 'dist' ou o diretório atual."
