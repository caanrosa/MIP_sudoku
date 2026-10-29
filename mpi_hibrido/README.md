# Tarea 3: combinar tableros y ramas

Los `N` procesos se dividen en grupos de tamaño `g` (`--grupo g`) con
`comm.Split`. Los líderes de grupo piden IDs de forma dinámica al proceso 0 (cada
grupo recibe un tablero nuevo al terminar el anterior). Dentro de un grupo, los
procesos reparten las ramas del tablero asignado con el mismo protocolo que
`mpi_por_ramas` (parada anticipada cuando alguien encuentra la solución). Un grupo
de tamaño 1 resuelve su tablero con el backtracking serial. El tiempo total es de
reloj real, medido en el proceso 0.

## Elección del tamaño de los grupos

Con `N=2` solo hay dos configuraciones: 2 grupos de 1 (equivale a repartir
tableros) o 1 grupo de 2 (equivale a repartir ramas). Se eligió `g` midiendo las
dos; los resultados están en `../INFORME.md`.

## Ejecución con el contenedor

Sustituye `N` por el valor elegido en `INFORME.md` y `G` por el tamaño de grupo.

### Windows (PowerShell)

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n N python /app/mpi_hibrido/mpi_hibrido.py --all --grupo G
```

### macOS (Terminal)

Cambia `"${PWD}:/app"` por `"$(pwd):/app"`.

## Resultados

Ver `../INFORME.md`.