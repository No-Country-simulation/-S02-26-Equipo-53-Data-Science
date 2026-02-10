# Pasos para contribuir y ejecutar el proyecto.

## Requisisto previo: 
Python 3.10 o superior
https://www.python.org/downloads/

Git
https://git-scm.com/

```bash
python --version
git --version
```
## Cómo contribuir

1. Haz un fork del repositorio.
   - Haz clic en el botón "Fork" en la esquina superior derecha de la página para crear tu propia copia del repositorio en tu cuenta de GitHub.
2. Clona el repositorio en tu máquina local.
 ```bash
 git clone https://github.com/LeoDataEngineer/ProyectoNoCountry.git
 ```
3. Crea una rama para tu contribución y cambiate a esa rama.
 ```bash
 git checkout -b <nombre-del-aporte>
 ```
4. Haz tus cambios en tu maquina local.
 ```bash
 git add .
 ```
5. Hacer commit de tus cambios.
 ```bash
 git commit -m "Add-Aporte: Descripción del aporte"
 ```
6. Sube tus cambios a tu repositorio.
 ```bash
 git push origin 
 ```
7. Trata de mantener el proyecto actualizado en tu maquina.
 ```bash
 git pull origin 
 ``` 
8. Ve a tu repositorio en GitHub y crea un pull request.
   - Haz clic en el botón "Compare & pull request".
   - Escribe un título y una descripción significativos para tu pull request.
   - Haz clic en el botón "Create pull request".

## Como trabajar en streamlit

1. Crear un entorno virtual en tu máquina local para aislar el proyecto.
 ```bash
 python -m venv env
 ```
2. Activar el entorno virtual (env).

 ```bash
  env/scripts/activate                                    
 ```
 o
 ```bash
  source env/Scripts/activate                                   
 ```
3. Salir del entorno virtual (env).

 ```bash
  deactivate                                   
 ```
4. Instalar dependencias con el archivo requirements.txt en el entorno virtual (env).

 ```bash
  pip install -r requirements.txt                                  
 ```

5. Si necesita actualizar pip que es el gestor de paquetes de python.

 ```bash
 python.exe -m pip install --upgrade pip                                  
 ```
6. Ejecutar la aplicación de streamlit .

 ```bash
 streamlit run main.py                             
 ```
