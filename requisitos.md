Requisitos del sistema de base de datos
1. Base de datos general y extensible
   - Crear un esqueleto de base de datos común.
   - Este esqueleto se podrá especializar dependiendo del departamento.
   - Cada departamento podrá tener su propia estructura/necesidades sin rehacer todo el sistema.
2. Migración de los datos existentes
   - Actualmente los datos están almacenados en ficheros Excel.
   - Los datos de estos ficheros son estructurados.
   - Hay que convertir/migrar estos datos a la nueva base de datos.
   - La migración debe mantener correctamente la información existente.
3. Modelo clave-valor / HashMap
   - Utilizar un modelo sencillo de clave → valor.
   - La estructura debería funcionar de forma similar a un HashMap.
   - El objetivo es conseguir búsquedas e indexación rápidas.
   - Por ejemplo:número_pedido → datos_pedido
   - El número de pedido puede utilizarse como clave cuando corresponda.
4. Rendimiento
   - Las consultas deben tener una respuesta prácticamente instantánea.
   - La indexación y búsqueda deben ser más rápidas que trabajar directamente con los ficheros.
   - Debe poder trabajar aproximadamente con 500 clientes.
   - Debe evitar problemas de consumo excesivo de memoria.
5. Simplicidad
   - Maximizar la simplicidad del código.
   - Evitar sistemas demasiado complejos para las necesidades del proyecto.
   - Se busca algo más simple que Redis.
   - Evitar infraestructura o servicios adicionales si no son necesarios.
   - La base de datos debe poder estar siempre disponible/activa para el programa.
6. Datos almacenados
   - Se almacenará solo texto.
   - Tanto las claves como los valores pueden representarse mediante cadenas de texto.
   - Debe aceptar todo tipo de símbolos/caracteres necesarios en los datos.
   - No es necesario almacenar estructuras complejas o datos anidados.
7. Operaciones
   Debe permitir las operaciones básicas CRUD:
   - Crear.
   - Leer.
   - Modificar.
   - Borrar.
8. Sistema de permisos
   - Implementar permisos dependiendo del departamento.
   - Cada departamento debe poder acceder únicamente a los datos que le correspondan.
   - Diferenciar, cuando sea necesario, entre permisos de usuario y de desarrollador/administrador.
   - Poder restringir determinadas operaciones o peticiones.
9. Persistencia
   - Los datos deben ser persistentes.
   - No deben desaparecer al cerrar o reiniciar el programa.
   - Los cambios realizados deben guardarse en almacenamiento permanente.
10. Consistencia
    - Mantener los datos en un estado válido después de las operaciones.
    - Tener en cuenta conceptos como ACID y BASE, escogiendo únicamente las garantías necesarias para no complicar innecesariamente el sistema.
11. Caché
    - Si se utiliza caché para mejorar el rendimiento, debe definirse su tiempo de validez.
    - La caché no debe provocar que se devuelvan datos antiguos o inconsistentes.
12. Tecnología candidata: dbm
    - dbm encaja como posible solución por ser un almacén clave-valor muy ligero.
    - Es una opción de bajo nivel disponible directamente desde Python.
    - No requiere montar un servidor de base de datos independiente.
    - Es considerablemente más sencillo que Redis.
    - Su limitación principal encaja inicialmente con el proyecto: claves y valores son datos simples (str/bytes), y el sistema solo necesita almacenar texto.
Objetivo resumido
Diseñar una base de datos persistente, ligera y sencilla basada en un modelo clave-valor similar a un HashMap, destinada a sustituir datos estructurados almacenados actualmente en ficheros Excel. El sistema debe proporcionar consultas e indexación rápidas, operaciones CRUD, soporte para texto y símbolos, separación y permisos por departamentos, y una arquitectura general que pueda especializarse para las necesidades de cada departamento. Se priorizarán la simplicidad del código y el bajo consumo de recursos, evitando soluciones más complejas como Redis cuando no sean necesarias. dbm se considera una posible implementación debido a su simplicidad, persistencia y modelo clave-valor.
