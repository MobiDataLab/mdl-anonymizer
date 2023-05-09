import json
import sys
from mob_data_anonymizer import CONFIG_DB_FILE
from mob_data_anonymizer.utils.sqlite import BinaryFileManager


# Creamos una instancia de la clase BinaryFileManager y conectamos a la base de datos
with open(CONFIG_DB_FILE) as param_file:
    data = json.load(param_file)
binary_file_manager = BinaryFileManager(data['db_folder'] + data['db_file'])
binary_file_manager.connect()

# # Inicializar bd
# binary_file_manager.initialize_db()
# sys.exit(0)

# Creamos las tablas en la base de datos (solo se ejecutará si no existen ya)
binary_file_manager.create_tables()

# Leemos un archivo de prueba
filename = data['db_folder'] + "prova.json"
binary_data = binary_file_manager.convert_to_binary(filename)

# Insertamos el archivo en la base de datos y guardamos el ID generado
filename = data['db_folder'] + "prova_db.json"
file_id = binary_file_manager.insert_file(binary_data, filename)

# Obtenemos el estado del archivo y lo imprimimos
file_state = binary_file_manager.get_file_state(file_id)
print(f"Estado del archivo con ID {file_id}: {file_state}")

# Cambiamos el estado del archivo a "procesado"
binary_file_manager.update_file_state(file_id, "processed")

# Obtenemos el estado del archivo y lo imprimimos de nuevo
file_state = binary_file_manager.get_file_state(file_id)
print(f"Nuevo estado del archivo con ID {file_id}: {file_state}")

# Obtenemos el archivo binario y lo guardamos en un archivo local
binary_file = binary_file_manager.get_file_binary(file_id)
filename = binary_file_manager.get_file_name(file_id)
if binary_file is not None:
    with open(filename, "wb") as f:
        f.write(binary_file)

# # Borramos el archivo de la base de datos
binary_file_manager.delete_file(file_id)

# Cerramos la conexión a la base de datos
binary_file_manager.close()
