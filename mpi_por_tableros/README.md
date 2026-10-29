# Tarea 1: repartir tableros

Cada ID es una tarea. El proceso 0 reparte IDs de forma dinámica (cada proceso
recibe un tablero nuevo en cuanto termina el anterior), lo que equilibra la carga
porque los tableros tardan entre 2 y 10 s. El proceso 0 también resuelve tableros:
un hilo auxiliar atiende las peticiones mientras el hilo principal resuelve. Todos
reutilizan `../sudoku.py`, y el proceso 0 reúne los estados y confirma que se
procesaron los 30 IDs. El tiempo total es de reloj real, medido en el proceso 0.
Los trabajadores envían su resultado junto con la petición del siguiente tablero,
así que la comunicación se reduce a mensajes pequeños.

## Ejecución con el contenedor

Sustituye `N` por el valor elegido en `INFORME.md`.

### macOS (Terminal)

```bash
docker run --rm -v "$(pwd):/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --all
```

### Windows (PowerShell)

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_por_tableros/mpi_tableros.py --all
```

Un solo tablero: reemplaza `--all` por `--id 7`.

## Resultados

Ver `../INFORME.md`.