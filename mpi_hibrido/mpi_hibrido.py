
import argparse
import sys
import threading
import time
from pathlib import Path

from mpi4py import MPI

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "mpi_por_ramas"))
sys.path.insert(0, str(RAIZ / "mpi_por_tableros"))

from baseline_secuencial import leer_seeds  
from mpi_ramas import resolver_paralelo  
from mpi_tableros import Cola  
from sudoku import resolver_con_tiempo  

TAG_PEDIR, TAG_TAREA, TAG_FIN = 1, 2, 3


def atender_peticiones(comm, cola, lideres):
    """Hilo del rank 0: recibe resultados de los líderes y les asigna tableros."""
    finalizados = 0
    while finalizados < lideres:
        estado = MPI.Status()
        if not comm.Iprobe(source=MPI.ANY_SOURCE, tag=TAG_PEDIR, status=estado):
            time.sleep(0.001)
            continue
        origen = estado.Get_source()
        previo = comm.recv(source=origen, tag=TAG_PEDIR)
        if previo is not None:
            cola.registrar(*previo, origen)
        idx = cola.tomar()
        if idx is None:
            comm.send(None, dest=origen, tag=TAG_FIN)
            finalizados += 1
        else:
            comm.send(idx, dest=origen, tag=TAG_TAREA)


def resolver_en_grupo(gcomm, idx, original, buzon):
    if gcomm.Get_size() == 1:  # grupo de un proceso: backtracking serial
        resuelto, _ = resolver_con_tiempo([f[:] for f in original])
        return resuelto
    return resolver_paralelo(gcomm, idx, original, buzon)


def ejecutar_lider(comm, gcomm, seleccionados, un_solo_id, grupos):
    rank = comm.Get_rank()
    cola = Cola(seleccionados, un_solo_id) if rank == 0 else None
    hilo = None
    if rank == 0 and grupos > 1:
        hilo = threading.Thread(target=atender_peticiones,
                                args=(comm, cola, grupos - 1))
        hilo.start()

    buzon = {}
    previo = None
    while True:
        if rank == 0:
            idx = cola.tomar()
        else:
            comm.send(previo, dest=0, tag=TAG_PEDIR)
            estado = MPI.Status()
            idx = comm.recv(source=0, tag=MPI.ANY_TAG, status=estado)
            if estado.Get_tag() == TAG_FIN:
                idx = None
        gcomm.bcast(-1 if idx is None else idx, root=0)
        if idx is None:
            break
        t0 = time.perf_counter()
        resuelto = resolver_en_grupo(gcomm, idx, seleccionados[idx][1], buzon)
        segundos = time.perf_counter() - t0
        if rank == 0:
            cola.registrar(idx, resuelto, segundos, 0)
        else:
            previo = (idx, resuelto, segundos)

    if hilo is not None:
        hilo.join()
    return cola


def ejecutar_miembro(gcomm, seleccionados):
    buzon = {}
    while True:
        idx = gcomm.bcast(None, root=0)
        if idx < 0:
            break
        resolver_en_grupo(gcomm, idx, seleccionados[idx][1], buzon)


def main():
    parser = argparse.ArgumentParser(description="Sudoku con MPI: tableros y ramas.")
    parser.add_argument("--archivo", type=Path, default=RAIZ / "seeds.txt")
    parser.add_argument("--grupo", type=int, default=2,
                        help="procesos por grupo (por defecto: 2)")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--id", "--seed", dest="id")
    grupo.add_argument("--all", action="store_true")
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank, size = comm.Get_rank(), comm.Get_size()
    seeds = leer_seeds(args.archivo)
    if args.id:
        if args.id not in seeds:
            if rank == 0:
                print(f"ID '{args.id}' no existe. Disponibles: {', '.join(seeds)}")
            return
        seleccionados = [(args.id, seeds[args.id])]
    else:
        seleccionados = list(seeds.items())

    g = max(1, min(args.grupo, size))
    grupos = (size + g - 1) // g
    gcomm = comm.Split(rank // g, rank)

    comm.Barrier()
    inicio = time.perf_counter()
    if gcomm.Get_rank() == 0:
        cola = ejecutar_lider(comm, gcomm, seleccionados, bool(args.id), grupos)
    else:
        ejecutar_miembro(gcomm, seleccionados)

    if rank == 0:
        total = time.perf_counter() - inicio
        print(f"\nConfiguración: {size} procesos = {grupos} grupo(s) de tamaño {g}")
        print(f"Tableros procesados: {cola.procesados}/{len(seleccionados)} "
              f"(resueltos: {cola.resueltos})")
        print(f"Tiempo total (reloj real): {total:.6f} segundos")


if __name__ == "__main__":
    main()