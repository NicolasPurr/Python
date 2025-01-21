# Porównanie szybkości oraz pamięci wykorzystanej przez programy wersja_1.py i wersja_2.py

## Metodologia

### Pomiaru szybkości w Windows PowerShell

```shell
$scripts = @("wersja_1.py", "wersja_2.py")
$memtests = @("memtest_1.py", "memtest_2.py")
$inputSets = @(
    @(0, 0),
    @(1, 1),
    @(1, 1000),
    @(100, 100),
    @(1000, 1000),
    @(500000, 50000),
    @(1000000, 1),
    @(1000000, 1000),
    @(1000000, 30000),
    @(3000000, 3000)
)

# Loop through each script and input set
$i = -1
foreach ($script in $scripts) {
  $i = $i + 1
    foreach ($input in $inputSets) {
        $n = $input[0]
        $k = $input[1]
        Write-Output "Running $script with input: $n $k"
        
        Measure-Command {
            python $script $n $k
        } | ForEach-Object {
            Write-Output "Total time for $script with input '$n $k': $($_.TotalSeconds) seconds"
        }
        
        python $memtests[$i] $n $k
    }
}
```
## Wyniki

| Input       | `wersja_1.py` Time (seconds) | `wersja_1.py` Memory Used (MB) | `wersja_2.py` Time (seconds) | `wersja_2.py` Memory Used (MB) |
|-------------|------------------------------|--------------------------------|------------------------------|--------------------------------|
| 0 0         | 0.0595                       | 0.01                           | 0.0406                       | 0.01                           |
| 1 1         | 0.0429                       | 0.01                           | 0.0391                       | 0.01                           |
| 1 1000      | 0.0406                       | 0.01                           | 0.0370                       | 0.01                           |
| 100 100     | 0.0407                       | 0.02                           | 0.0366                       | 0.02                           |
| 1000 1000   | 0.0427                       | -0.02                          | 0.0414                       | 0.09                           |
| 500000 50000 | 0.5699                       | 53.59                          | 0.4766                       | 28.97                          |
| 1000000 1   | 1.0977                       | 99.60                          | 0.9192                       | 54.59                          |
| 1000000 1000 | 1.3594                       | 100.25                         | 0.9173                       | 54.60                          |
| 1000000 30000 | 1.1885                      | 101.59                         | 0.9978                       | 54.91                          |
| 3000000 3000 | 3.4021                       | 299.81                         | 2.9080                       | 161.98                         |
