Backlog en historias de usuario
HU01 — Estructura general de la base de datos
Como desarrollador, quiero disponer de una estructura base común para la base de datos, para poder especializarla posteriormente según las necesidades de cada departamento.
Criterios de aceptación:
- Existe una estructura base funcional.
- Se puede crear la configuración de un nuevo departamento sin modificar el funcionamiento de los demás.
- Dos departamentos pueden tener configuraciones diferentes.
- Los datos de un departamento no interfieren con los de otro.
INVEST: es independiente, aporta valor al facilitar la ampliación del sistema, puede estimarse, puede implementarse en una iteración y los criterios anteriores permiten probarla.
HU02 — Migración de Excel
Como usuario, quiero importar los datos estructurados existentes en ficheros Excel a la base de datos, para poder consultar la información sin depender de los ficheros originales.
Criterios de aceptación:
- El sistema puede leer el formato Excel utilizado actualmente.
- Cada registro válido del Excel se convierte en una entrada de la base de datos.
- Al terminar la importación, el número de registros importados coincide con el número de registros válidos del fichero.
- Los valores importados coinciden con los valores originales.
- Si existe una fila que no puede importarse, el sistema la identifica.
HU03 — Almacenamiento clave-valor
Como desarrollador, quiero almacenar la información mediante pares clave-valor, para simplificar el acceso e indexar los datos de forma eficiente.
Por ejemplo:
numero_pedido -> datos_pedido

Criterios de aceptación:
- Cada registro tiene una clave.
- Dada una clave existente, el sistema devuelve su valor correspondiente.
- Una búsqueda de una clave inexistente devuelve un resultado indicando que no existe.
- No pueden existir dos entradas diferentes con la misma clave dentro del mismo espacio de datos.
HU04 — Operaciones CRUD
Como usuario autorizado, quiero crear, consultar, modificar y eliminar registros, para gestionar la información almacenada.
Criterios de aceptación:
- Se puede crear un registro nuevo.
- Se puede consultar mediante su clave.
- Se puede modificar el valor asociado a una clave.
- Se puede eliminar un registro.
- Después de eliminarlo, una búsqueda de esa clave indica que no existe.
HU05 — Persistencia
Como usuario, quiero que los cambios realizados permanezcan guardados, para no perder información cuando el programa se cierre.
Criterios de aceptación:
- Se introduce un registro y se cierra el programa.
- Al volver a iniciar el programa, el registro continúa disponible.
- Las modificaciones realizadas antes del cierre se conservan.
- Los registros eliminados no reaparecen después de reiniciar.
HU06 — Separación por departamentos
Como usuario de un departamento, quiero acceder únicamente a los datos correspondientes a mi departamento, para evitar acceder a información que no me corresponde.
Criterios de aceptación:
- Cada registro está asociado a un departamento o espacio de datos.
- Un usuario autorizado para el departamento A puede acceder a sus registros.
- Ese mismo usuario no puede consultar registros exclusivos del departamento B.
- Añadir un nuevo departamento no modifica los datos existentes de los demás.
HU07 — Sistema de permisos
Como administrador, quiero asignar permisos a los usuarios, para controlar qué operaciones puede realizar cada uno.
Criterios de aceptación:
- Se pueden definir usuarios con diferentes permisos.
- Un usuario sin permiso de escritura no puede crear ni modificar registros.
- Un usuario sin permiso de borrado no puede eliminar registros.
- Un usuario autorizado puede realizar las operaciones correspondientes.
- Los desarrolladores/administradores pueden disponer de permisos distintos de los usuarios normales.
HU08 — Soporte de texto y símbolos
Como usuario, quiero almacenar texto con los caracteres que utilizo habitualmente, para conservar los datos sin alteraciones.
Criterios de aceptación:
- El sistema almacena correctamente letras con tildes y ñ.
- Admite mayúsculas y minúsculas.
- Admite números.
- Admite espacios.
- Admite símbolos como @, #, %, &, /, -, _, €, etc.
- El texto recuperado es exactamente igual al introducido.
Esto convierte el requisito original "aceptar todo tipo de símbolos", que no era realmente verificable, en algo que sí podemos comprobar.
HU09 — Consultas rápidas
Aquí hay que corregir otro requisito que teníamos: "respuestas instantáneas" no es verificable porque instantáneo no tiene una medida concreta.
Podemos escribirlo como:
Como usuario, quiero que las consultas por clave se realicen rápidamente, para acceder a la información sin esperas apreciables.
Criterios de aceptación:
- Con una base de datos de al menos 500 clientes/registros de prueba, una consulta individual por clave debe completarse en menos de 100 ms en el entorno de pruebas acordado.
- El test se realizará sobre registros existentes y no existentes.
- El tiempo puede medirse mediante un test automatizado.
El límite de 100 ms se puede negociar con el profesor/equipo; lo importante para INVEST es que exista una cifra comprobable.
HU10 — Simplicidad de despliegue
El requisito "algo más simple que Redis" tampoco es directamente verificable. Yo lo transformaría en:
Como desarrollador, quiero que la base de datos funcione sin necesitar un servidor de base de datos independiente, para reducir la configuración y mantenimiento del sistema.
Criterios de aceptación:
- La aplicación puede iniciarse sin ejecutar manualmente un servidor de base de datos.
- La base de datos se crea o abre desde la propia aplicación.
- Un entorno nuevo puede ejecutar el sistema instalando únicamente las dependencias documentadas del proyecto.
Esto captura lo que realmente queríais conseguir al decir más simple que Redis.
HU11 — Bajo consumo de memoria
Como desarrollador, quiero que los datos persistentes no tengan que mantenerse completamente en memoria, para evitar los problemas de memoria del sistema anterior.
Criterios de aceptación:
- Los datos permanecen almacenados en disco.
- Reiniciar el proceso no elimina los datos.
- El funcionamiento normal no requiere cargar explícitamente toda la base de datos en un único dict de Python.
HU12 — Consistencia de los datos
Como usuario, quiero que una operación completada correctamente deje los datos en un estado consistente, para evitar consultar información obsoleta o parcialmente modificada.
Criterios de aceptación:
- Después de una escritura completada correctamente, una lectura posterior devuelve el nuevo valor.
- Después de una eliminación completada correctamente, el registro deja de estar disponible.
- Una operación que devuelve un error no debe notificarse al usuario como completada correctamente.
