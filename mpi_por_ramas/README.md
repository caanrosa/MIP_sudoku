# Tarea 2: repartir ramas de cada tablero

Los 30 IDs se procesan en orden; cada tablero termina antes de empezar el
siguiente. Para cada tablero, todos los procesos generan la misma lista de ramas y 
el proceso `r` explora las ramas `r, r+N, r+2N, ...` con backtracking.

Cada proceso consulta mensajes cada 5000 nodos. Al terminar su parte, envía a los
demás `FOUND` (con la solución) o `DONE`. Si alguien envía `FOUND`, los demás
abandonan la búsqueda de ese tablero. El tablero acaba cuando todos han
respondido. El proceso 0 imprime el estado y el tiempo (reloj real) de cada ID y
el total de los 30.

## Ejecución con el contenedor

Sustituye `N` por el valor elegido en `INFORME.md`.

### Windows (PowerShell)

Un tablero:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --id 7
```

Todos los tableros:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_ramas/mpi_ramas.py --all
```

### macOS (Terminal)

Cambia `"${PWD}:/app"` por `"$(pwd):/app"` en los comandos anteriores.

## Resultados

Ver `../INFORME.md`.