# Tarea 3: combinar tableros y ramas

Los `N` procesos se dividen en grupos de tamaño `g` (`--grupo g`) con
`comm.Split`. El líder de cada grupo (su proceso de rango 0 dentro del grupo) pide
IDs al proceso 0 del programa: cada grupo recibe un tablero nuevo al terminar el anterior. Dentro de un grupo, los procesos reparten las ramas del tablero asignado igual que `mpi_por_ramas` (parada anticipada cuando alguien encuentra la solución). Un grupo de tamaño 1 resuelve su tablero con el backtracking serial. El tiempo total es de reloj real, medido en el proceso 0.

## Elección del tamaño de los grupos

Con `N=2` solo hay dos opciones: 2 grupos de 1 proceso (`g=1`) o 1 grupo de 2
(`g=2`). Se eligió `g=1`: cada proceso resuelve un tablero completo, sin mensajes
entre procesos de un mismo grupo ni espera al final de cada tablero, y los tableros
son independientes. Con `g=1` el híbrido equivale a repartir tableros; con un `N`
mayor, un `g` de 2 o más permitiría combinar mejor ambas estrategias.

## Resultado

Con `N=2` y `g=1`, la mediana de 3 repeticiones del tiempo total de los 30 IDs fue
**81,05 s** (secuencial: 108,83 s). Detalle en `../INFORME.md`.

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