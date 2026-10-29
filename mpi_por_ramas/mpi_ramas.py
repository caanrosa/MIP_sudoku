import argparse
import sys
import time
from pathlib import Path

from mpi4py import MPI

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from baseline_secuencial import leer_seeds  
from sudoku import puede_colocar  

TAG = 7
REVISAR_CADA = 5000  # nodos de búsqueda entre consultas de mensajes


class Interrumpido(Exception):
    # Excepción para interrumpir la busqueda
    pass

def primera_vacia(tablero):
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] == 0:
                return fila, columna
    return None


def generar_ramas(tablero, minimo):
# Genera al menos `minimo` tableros a partir de `tablero`, rellenando celdas vacías.
 
 
    ramas = [[f[:] for f in tablero]]
    while len(ramas) < minimo:
        nuevas = []
        hubo_vacias = False
        for rama in ramas:
            celda = primera_vacia(rama)
            if celda is None:
                nuevas.append(rama)
                continue
            hubo_vacias = True
            fila, columna = celda
            for valor in range(1, 10):
                if puede_colocar(rama, fila, columna, valor):
                    hija = [f[:] for f in rama]
                    hija[fila][columna] = valor
                    nuevas.append(hija)
        ramas = nuevas
        if not hubo_vacias or not ramas:
            break
    return ramas


def resolver_interrumpible(tablero, revisar):
# Resuelve un tablero de sudoku, interrumpiendo la búsqueda si `revisar()` devuelve True.
    
    nodos = 0

    def rec():
        nonlocal nodos
        for fila in range(9):
            for columna in range(9):
                if tablero[fila][columna] != 0:
                    continue
                for valor in range(1, 10):
                    if puede_colocar(tablero, fila, columna, valor):
                        tablero[fila][columna] = valor
                        nodos += 1
                        if nodos % REVISAR_CADA == 0:
                            revisar()
                        if rec():
                            return True
                        tablero[fila][columna] = 0
                return False
        return True

    return rec()


def drenar(comm, buzon):

    estado = MPI.Status()
    while comm.Iprobe(source=MPI.ANY_SOURCE, tag=TAG, status=estado):
        tipo, idx, solucion = comm.recv(source=estado.Get_source(), tag=TAG)
        buzon.setdefault(idx, []).append((tipo, solucion))


def resolver_paralelo(comm, idx, original, buzon):
    #Resuelve un tablero repartiendo sus ramas. Devuelve True si se resolvió.
    rank, size = comm.Get_rank(), comm.Get_size()
    ramas = generar_ramas(original, max(16, 8 * size))

    def alguien_encontro():
        drenar(comm, buzon)
        return any(t == "FOUND" for t, _ in buzon.get(idx, []))

    def revisar():
        if alguien_encontro():
            raise Interrumpido

    solucion = None
    try:
        for i in range(rank, len(ramas), size):
            if alguien_encontro():
                break
            tablero = [f[:] for f in ramas[i]]
            if resolver_interrumpible(tablero, revisar):
                solucion = tablero
                break
    except Interrumpido:
        pass

    tipo = "FOUND" if solucion is not None else "DONE"
    envios = [comm.isend((tipo, idx, solucion), dest=d, tag=TAG)
              for d in range(size) if d != rank]

    while len(buzon.get(idx, [])) < size - 1:  # un mensaje por cada otro proceso
        drenar(comm, buzon)
        if len(buzon.get(idx, [])) < size - 1:
            time.sleep(0.0005)
    MPI.Request.waitall(envios)

    resuelto = solucion is not None or any(
        t == "FOUND" for t, _ in buzon.pop(idx, []))
    return resuelto


def main():
    parser = argparse.ArgumentParser(description="Sudoku con MPI: reparto de ramas.")
    parser.add_argument("--archivo", type=Path, default=RAIZ / "seeds.txt")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--id", "--seed", dest="id")
    grupo.add_argument("--all", action="store_true")
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    seeds = leer_seeds(args.archivo)
    if args.id:
        if args.id not in seeds:
            if rank == 0:
                print(f"ID '{args.id}' no existe. Disponibles: {', '.join(seeds)}")
            return
        seleccionados = [(args.id, seeds[args.id])]
    else:
        seleccionados = list(seeds.items())

    buzon = {}
    resueltos = 0
    comm.Barrier()
    inicio = time.perf_counter()
    for idx, (nombre, original) in enumerate(seleccionados):
        t0 = time.perf_counter()
        resuelto = resolver_paralelo(comm, idx, original, buzon)
        segundos = time.perf_counter() - t0
        resueltos += 1 if resuelto else 0
        if rank == 0:
            etiqueta = "Tiempo" if args.id else "Tiempo parcial"
            print(f"\nID: {nombre}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"{etiqueta}: {segundos:.6f} segundos", flush=True)

    total = time.perf_counter() - inicio
    if rank == 0:
        print(f"\nTableros procesados: {len(seleccionados)}/{len(seleccionados)} "
              f"(resueltos: {resueltos})")
        print(f"Tiempo total (reloj real): {total:.6f} segundos")


if __name__ == "__main__":
    main()