# Informe de resultados

Completa este informe después de implementar las tres tareas MPI. Ejecuta las comparaciones con el mismo archivo `seeds.txt`, en el mismo equipo y con el contenedor del taller.

## Entorno

- Equipo: procesador Intel Core i3-1115G4 (2 núcleos / 4 hilos), 16 GB de RAM (2 × 8 GB), Windows + Docker Desktop>
- Versión del contenedor: augustosalazar/slim-mpi:2
- Cantidad de repeticiones por medición: 3
- Valor común de `N` elegido: 2 (recomendado por `detectar_procesos_mpi.py`)

## Comparación final con el mismo `N`

Repite tres veces cada ejecución y registra la mediana. Mantén fijo el `N` elegido en todas las filas MPI. Incluye `--allow-run-as-root --use-hwthread-cpus --oversubscribe` en `mpiexec`, igual que en la calibración, para permitir valores de `N` mayores que los slots detectados.

| Implementación | Caso | Procesos | Mediana del tiempo total (s) | Aceleración frente a secuencial |
| --- | --- | ---: | ---: | ---: |
| Secuencial | Todos los IDs | 1 |  | 1,00 |
| MPI por tableros | Todos los IDs | N |  |  |
| MPI por ramas | Todos los IDs, uno después de otro | N |  |  |
| MPI híbrido | Todos los IDs | N |  |  |

Calcula la aceleración como `tiempo secuencial / tiempo MPI`. Mide el tiempo MPI desde el inicio del reparto hasta recibir todos los resultados necesarios.

## Conclusiones

- ¿Qué estrategia obtuvo el menor tiempo para los 30 tableros? ¿Cuánto mejoró respecto a la versión secuencial?
- ¿Cómo afectaron la comunicación y las diferencias de duración entre tableros?
- ¿Cómo se comparó repartir tableros con resolverlos en orden y repartir las ramas de cada uno?
