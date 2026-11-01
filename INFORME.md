# Informe de resultados

## Entorno

- Equipo: procesador Intel Core i3-1115G4 (2 núcleos / 4 hilos), 16 GB de RAM (2 × 8 GB), Windows + Docker Desktop
- Versión del contenedor: augustosalazar/slim-mpi:2
- Cantidad de repeticiones por medición: 3
- Valor común de `N` elegido: 2 (recomendado por `detectar_procesos_mpi.py`)

## Comparación final con el mismo `N`

Valor común de `N`: **2**, usado en todas las filas MPI. Cada `mpiexec` lleva
`--allow-run-as-root --use-hwthread-cpus --oversubscribe`. El tiempo MPI es el
tiempo real medido en el proceso 0, desde el inicio del reparto hasta recibir todos
los resultados. En todas las corridas se procesaron los 30 IDs (30/30 resueltos).

Mediciones individuales (s):

| Implementación | Procesos | Rep. 1 | Rep. 2 | Rep. 3 | Mediana |
| --- | ---: | ---: | ---: | ---: | ---: |
| Secuencial | 1 | 113,63 | 104,36 | 108,83 | 108,83 |
| MPI por tableros | 2 | 80,71 | 83,58 | 80,30 | 80,71 |
| MPI por ramas | 2 | 80,54 | 85,38 | 84,34 | 84,34 |
| MPI híbrido (g=1) | 2 | 81,05 | 82,11 | 78,82 | 81,05 |

## Aceleración

Aceleración = tiempo secuencial / tiempo MPI (medianas de 3 repeticiones).
Tiempo secuencial = 108,83 s. Con N = 2, el ideal sería 2,00.
Eficiencia = aceleración / N.

| Implementación | Tiempo MPI (s) | Cálculo | Aceleración | Eficiencia |
| --- | ---: | --- | ---: | ---: |
| MPI por tableros | 80,71 | 108,83 / 80,71 | 1,35 | 0,67 |
| MPI por ramas | 84,34 | 108,83 / 84,34 | 1,29 | 0,65 |
| MPI híbrido (g=1) | 81,05 | 108,83 / 81,05 | 1,34 | 0,67 |

## Conclusiones

- **¿Qué estrategia obtuvo el menor tiempo para los 30 tableros? ¿Cuánto mejoró
  respecto a la versión secuencial?**

  Repartir tableros tuvo la menor mediana: 80,71 s frente a 108,83 s en secuencial
  (aceleración 1,35, unos 26 % menos de tiempo). El híbrido con g=1 quedó casi
  igual (81,05 s) porque, con N=2, es el mismo reparto. Las tres versiones MPI
  quedaron entre 80 y 85 s, una diferencia pequeña que se confunde con la variación
  entre repeticiones. Lo claro es que las tres mejoran al secuencial.

- **¿Cómo afectaron la comunicación y las diferencias de duración entre tableros?**

  Los mensajes son muy pequeños, así que la comunicación casi no pesa. Como cada
  proceso pide un tablero nuevo al terminar, ninguno quedó esperando aunque los
  tableros duren entre 2 y 10 s. Aun así, la aceleración no llegó al ideal de 2,0
  (eficiencia entre 0,65 y 0,67).

- **¿Cómo se comparó repartir tableros con resolverlos en orden y repartir las
  ramas de cada uno?**

  Repartir tableros completos fue un poco mejor y más simple, porque cada tablero
  es independiente. Repartir ramas obliga a sincronizar al final de cada tablero,
  y su mediana fue algo mayor (84,34 s frente a 80,71 s), aunque la diferencia es
  pequeña. El híbrido, con N=2 y g=1, coincidió con el reparto de tableros.