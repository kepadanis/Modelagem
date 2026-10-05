# G112 - D08 - Modelo computacional dos navios (PRO3342)

Estrutura (caminhos relativos; executar a partir desta pasta):

- `G112_D08.ipynb` / `G112_D08.html`: relatório oficial (notebook executado e sua exportação).
- `entrada/`: `terminais.csv`, `cenario.csv`, `distancias.csv` (não usado pelos navios) e o arquivo oficial de dados `.md`.
- `preparar_entradas.py`: gera `terminais.csv` e `distancias.csv` a partir do arquivo `.md`.
- `modelo_navios.py`: modelo SimPy (mesmo código da seção 3 do notebook). Uso: `python modelo_navios.py entrada saida`.
- `saida/log_navios.csv`: log do cenário-base (365 dias, semente de `cenario.csv`).
- `requirements.txt`: dependências.

Reexecutar o notebook: `jupyter nbconvert --to notebook --execute G112_D08.ipynb --output G112_D08.ipynb` e depois `jupyter nbconvert --to html G112_D08.ipynb`.
