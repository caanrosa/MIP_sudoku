# Tarea 3: combinar tableros y ramas

Los `N` procesos se dividen en grupos de tamaño `g` (`--grupo g`) con
`comm.Split`. El líder de cada grupo (su proceso de rango 0 dentro del grupo) pide
IDs al proceso 0 del programa: cada grupo recibe un tablero nuevo al terminar el
anterior. Dentro de un grupo, los procesos reparten las ramas del tablero asignado
igual que `mpi_por_ramas` (paran antes cuando alguien encuentra la solución).
Un grupo de tamaño 1 resuelve su tablero con backtracking. El tiempo total
es de reloj real, medido en el proceso 0.

Tamaño de los grupos: con `N=2` se usó `g=1`, es decir, dos grupos de un proceso.
Cada proceso resuelve un tablero completo, sin mensajes entre procesos de un mismo
grupo ni espera al final de cada tablero, y los tableros son independientes. Con un
`N` mayor se podría usar `g` de 2 o más para combinar mejor ambas estrategias.

## Resultado

Con `N=2` y `g=1`, la mediana de 3 repeticiones del tiempo total de los 30 IDs fue
**81,05 s** (secuencial: 108,83 s). En todas las corridas se procesaron los 30 IDs (30/30 resueltos).

## Ejecución con el contenedor

Valores usados: `N=2` (calibrado) y `g=1`.

### Windows (PowerShell)

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 2 python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 1
```

### macOS (Terminal)

```bash
docker run --rm -v "$(pwd):/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 2 python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 1
```

Un solo tablero: reemplaza `--all` por `--id 7`.