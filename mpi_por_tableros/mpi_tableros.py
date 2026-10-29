
import argparse
import sys
import threading
import time
from pathlib import Path

from mpi4py import MPI

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from baseline_secuencial import leer_seeds  # noqa: E402
from sudoku import resolver_con_tiempo  # noqa: E402

TAG_PEDIR, TAG_TAREA, TAG_FIN = 1, 2, 3


class Cola:
    """Cola de índices de tableros y registro de resultados (rank 0)."""

    def __init__(self, seleccionados, un_solo_id):
        self.seleccionados = seleccionados
        self.un_solo_id = un_solo_id
        self.pendientes = list(range(len(seleccionados)))
        self.candado = threading.Lock()
        self.procesados = 0
        self.resueltos = 0
        self.suma_cpu = 0.0

    def tomar(self):
        with self.candado:
            return self.pendientes.pop(0) if self.pendientes else None

    def registrar(self, idx, resuelto, segundos, rank):
        with self.candado:
            self.procesados += 1
            self.resueltos += 1 if resuelto else 0
            self.suma_cpu += segundos
            etiqueta = "Tiempo" if self.un_solo_id else "Tiempo parcial"
            print(f"\nID: {self.seleccionados[idx][0]}  (proceso {rank})")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"{etiqueta}: {segundos:.6f} segundos", flush=True)


def atender_peticiones(comm, cola):
    """Hilo del rank 0: recibe resultados y asigna el siguiente tablero."""
    size = comm.Get_size()
    finalizados = 0
    while finalizados < size - 1:
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


def proceso_principal(comm, seleccionados, un_solo_id):
    cola = Cola(seleccionados, un_solo_id)
    hilo = threading.Thread(target=atender_peticiones, args=(comm, cola))

    comm.Barrier()
    inicio = time.perf_counter()
    hilo.start()

    while True:  # el rank 0 también resuelve tableros
        idx = cola.tomar()
        if idx is None:
            break
        tablero = [f[:] for f in seleccionados[idx][1]]
        resuelto, seg = resolver_con_tiempo(tablero)
        cola.registrar(idx, resuelto, seg, 0)

    hilo.join()
    total = time.perf_counter() - inicio
    print(f"\nTableros procesados: {cola.procesados}/{len(seleccionados)} "
          f"(resueltos: {cola.resueltos})")
    print(f"Suma de tiempos de proceso (solo informativa): {cola.suma_cpu:.6f} segundos")
    print(f"Tiempo total (reloj real): {total:.6f} segundos")


def trabajador(comm, seleccionados):
    comm.Barrier()
    previo = None
    while True:
        comm.send(previo, dest=0, tag=TAG_PEDIR)
        estado = MPI.Status()
        idx = comm.recv(source=0, tag=MPI.ANY_TAG, status=estado)
        if estado.Get_tag() == TAG_FIN:
            break
        tablero = [fila[:] for fila in seleccionados[idx][1]]
        resuelto, segundos = resolver_con_tiempo(tablero)
        previo = (idx, resuelto, segundos)


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
        proceso_principal(comm, seleccionados, bool(args.id))
    else:
        trabajador(comm, seleccionados)


if __name__ == "__main__":
    main()