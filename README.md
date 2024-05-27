# Pasos
Crear el virtual enviroment:
`python -m venv .venv`

Activarlo:
- con pwsh:
    `.venv\Scripts\activate.ps1`
-  con CMD:
    `.venv\Scripts\activate.bat`

Instalar las dependencias:
(Panel tiene que estar instalado en el global, no en el virtual enviroment)
pip install pyparsing
pip install SciPy

Crear el requeriments.txt ejecutando:
`pip freeze > requirements.txt`

borrar:
- pywin32==306
- pywinpty==2.0.13


sino el req puede ser
panel
jupyter
transformers
numpy
torch
aiohttp
pandas
numpy
hvplot
SciPy
pyparsing
