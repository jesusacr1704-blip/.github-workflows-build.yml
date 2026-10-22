AJEDREZ DE MADERA — VERSIÓN 2

Incluye:
- Dos jugadores en el mismo teléfono, por turnos.
- El tablero gira 180° después de cada movimiento para que el jugador activo quede abajo.
- Menú inicial: “Jugar partida nueva” y “Reanudar partida”.
- Botón “Pausa” en la esquina superior derecha.
- Menú de pausa: “Reanudar partida”, “Guardar partida y salir” y “Salir sin guardar”.
- Guardado local de la partida y puntuaciones.
- Tablero con colores de madera, selección de piezas y casillas legales resaltadas.
- Puntuación por captura: peón 1, caballo/alfil 3, torre 5, dama 9; +10 por jaque mate.

IMPORTANTE
Este ZIP contiene el código fuente del proyecto Android; no es un APK ya compilado.
Para compilar necesitas Linux o WSL con Buildozer y Android SDK/NDK instalados.

Pasos típicos en Linux/WSL:
1. Descomprime el ZIP.
2. Abre una terminal dentro de la carpeta del proyecto.
3. Instala dependencias del sistema para Buildozer y Python.
4. Ejecuta:
   pip install buildozer
   buildozer -v android debug
5. El APK se genera normalmente en la carpeta bin/.

Notas:
- “Salir sin guardar” vuelve al menú y no guarda los cambios actuales; conserva cualquier guardado anterior.
- “Guardar partida y salir” escribe el estado actual en el almacenamiento privado de la app y vuelve al menú.
- “Reanudar partida” se habilita cuando existe un archivo guardado.
