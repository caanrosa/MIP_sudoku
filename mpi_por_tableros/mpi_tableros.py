"""MPI por tableros: cada ID es una tarea que se asigna dinámicamente."""

import argparse
import sys
import time
from pathlib import Path

from mpi4py import MPI

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from baseline_secuencial import leer_seeds  
from sudoku import resolver_con_tiempo  

TAG_TAREA, TAG_RESULTADO, TAG_FIN = 1, 2, 3


def coordinador(comm, seleccionados, un_solo_id):
    size = comm.Get_size()
    pendientes = list(range(len(seleccionados)))
    resueltos = 0
    procesados = 0
    suma_cpu = 0.0
    
    def reportar(idx, resuelto, segundos, rank):
        nonlocal resueltos, procesados, suma_cpu
        procesados += 1
        resueltos += 1 if resuelto else 0
        suma_cpu += segundos
        etiqueta = "Tiempo" if un_solo_id else "Tiempo parcial"
        print(f"\nID: {seleccionados[idx][0]}  (proceso {rank})")
        print("Resuelto" if resuelto else "Sin solución")
        print(f"{etiqueta}: {segundos:.6f} segundos", flush=True)

    comm.Barrier()
    inicio = time.perf_counter()
    
    if size == 1:  # sin trabajadores: el coordinador resuelve todo
        
        for idx in pendientes:
            tablero = [f[:] for f in seleccionados[idx][1]]
            resuelto, seg = resolver_con_tiempo(tablero)
            reportar(idx, resuelto, seg, 0)
    else:
        activos = 0
        for w in range(1, size):  # primera tarea para cada trabajador
            if pendientes:
                comm.send(pendientes.pop(0), dest=w, tag=TAG_TAREA)
                activos += 1
            else:
                comm.send(None, dest=w, tag=TAG_FIN)
        while activos:
            
            estado = MPI.Status()
            idx, resuelto, seg = comm.recv(source=MPI.ANY_SOURCE,
                                           tag=TAG_RESULTADO, status=estado)
            
            reportar(idx, resuelto, seg, estado.Get_source())
            if pendientes:
                comm.send(pendientes.pop(0), dest=estado.Get_source(), tag=TAG_TAREA)
            else:
                comm.send(None, dest=estado.Get_source(), tag=TAG_FIN)
                activos -= 1

    total = time.perf_counter() - inicio
    print(f"\nTableros procesados: {procesados}/{len(seleccionados)} "
          f"(resueltos: {resueltos})")
    print(f"Suma de tiempos de proceso (solo informativa): {suma_cpu:.6f} segundos")
    print(f"Tiempo total (reloj real): {total:.6f} segundos")
    
def trabajador(comm, seleccionados):
    comm.Barrier()
    while True:
        estado = MPI.Status()
        idx = comm.recv(source=0, tag=MPI.ANY_TAG, status=estado)
        if estado.Get_tag() == TAG_FIN:
            break
        tablero = [fila[:] for fila in seleccionados[idx][1]]
        resuelto, segundos = resolver_con_tiempo(tablero)
        comm.send((idx, resuelto, segundos), dest=0, tag=TAG_RESULTADO)

def main():
    parser = argparse.ArgumentParser(description="Sudoku con MPI: reparto de tableros.")
    parser.add_argument("--archivo", type=Path, default=RAIZ / "seeds.txt")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--id", "--seed", dest="id")
    grupo.add_argument("--all", action="store_true")
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    seeds = leer_seeds(args.archivo)
    if args.id:
        if args.id not in seeds:
            if comm.Get_rank() == 0:
                print(f"ID '{args.id}' no existe. Disponibles: {', '.join(seeds)}")
            return
        seleccionados = [(args.id, seeds[args.id])]
    else:
        seleccionados = list(seeds.items())

    if comm.Get_rank() == 0:
        coordinador(comm, seleccionados, bool(args.id))
    else:
        trabajador(comm, seleccionados)


if __name__ == "__main__":
    main()