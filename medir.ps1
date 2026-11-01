param([int]$N = 2, [int]$Reps = 3)

$imagen = "augustosalazar/slim-mpi:2"
$mpi = "mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N"

$casos = [ordered]@{
    "Secuencial"       = "python /app/baseline_secuencial.py --all"
    "MPI por tableros" = "$mpi python /app/mpi_por_tableros/mpi_tableros.py --all"
    "MPI por ramas"    = "$mpi python /app/mpi_por_ramas/mpi_ramas.py --all"
    "Hibrido g=1"      = "$mpi python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 1"
    "Hibrido g=2"      = "$mpi python /app/mpi_hibrido/mpi_hibrido.py --all --grupo 2"
}

$tiempos = @{}
foreach ($nombre in $casos.Keys) { $tiempos[$nombre] = @() }

for ($rep = 1; $rep -le $Reps; $rep++) {
    foreach ($nombre in $casos.Keys) {
        Write-Host "Repeticion $rep/$Reps - $nombre ..." -NoNewline
        $argumentos = $casos[$nombre] -split ' '
        $salida = docker run --rm -v "${PWD}:/app" $imagen @argumentos 2>&1 | Out-String
        $resueltos = ([regex]::Matches($salida, "(?m)^Resuelto")).Count
        if ($salida -match "Tiempo total[^:]*:\s*([0-9.]+)" -and $resueltos -eq 30) {
            $segundos = [double]::Parse($Matches[1], [Globalization.CultureInfo]::InvariantCulture)
            $tiempos[$nombre] += $segundos
            Write-Host (" {0:N2} s" -f $segundos)
        } else {
            Write-Host " FALLO (resueltos: $resueltos)"
            Write-Host $salida
        }
    }
}

function Mediana($valores) {
    $orden = $valores | Sort-Object
    $n = $orden.Count
    if ($n -eq 0) { return [double]::NaN }
    if ($n % 2 -eq 1) { return $orden[($n - 1) / 2] }
    return ($orden[$n / 2 - 1] + $orden[$n / 2]) / 2
}

$base = Mediana $tiempos["Secuencial"]
Write-Host "`nN = $N, repeticiones = $Reps`n"
foreach ($nombre in $casos.Keys) {
    $m = Mediana $tiempos[$nombre]
    $lista = ($tiempos[$nombre] | ForEach-Object { "{0:N2}" -f $_ }) -join "; "
    Write-Host ("{0,-18} mediana {1,8:N2} s   aceleracion {2,5:N2}   [{3}]" -f $nombre, $m, ($base / $m), $lista)
}