import re
from pathlib import Path

import pandas as pd

HORAS_POR_DIA = 24.0


def _num(txt):
    return float(txt.replace(".", "").replace(",", ".")) if re.search(r"\d\.\d{3}\b", txt) else float(txt.replace(",", "."))


def _secao(md, n):
    m = re.search(rf"^## {n}\.[^\n]*\n(.*?)(?=^## \d+\.|\Z)", md, flags=re.S | re.M)
    return m.group(1)


def _por_terminal(texto, padrao):
    out = {}
    for m in re.finditer(rf"^- (T\d+): {padrao}\s*$", texto, flags=re.M):
        out[m.group(1)] = m.groups()[1:]
    return out


def _horas(txt):
    h = re.search(r"(\d+)\s*h", txt)
    mi = re.search(r"(\d+)\s*min", txt)
    return (int(h.group(1)) if h else 0) + (int(mi.group(1)) if mi else 0) / 60.0


def ler_dados_md(caminho_md):
    md = Path(caminho_md).read_text(encoding="utf-8")

    s1 = _secao(md, 1)
    bercos = {k: int(v[0]) for k, v in _por_terminal(s1, r"(\d+) ber[çc]os?").items()}

    s3 = _secao(md, 3)
    taxa_dia = {k: _num(v[0]) for k, v in _por_terminal(s3, r"([\d,]+) navios?/dia").items()}

    s5 = _secao(md, 5)
    antecedencia = float(re.search(r"(\d+)\s*h", s5).group(1))

    s7 = _secao(md, 7)
    manobra = {k: _horas(v[0]) for k, v in _por_terminal(s7, r"(.+?)").items()}

    s8 = _secao(md, 8)
    operacao = {k: tuple(_num(x) for x in v) for k, v in
                _por_terminal(s8, r"Tri\(([\d,]+),\s*([\d,]+),\s*([\d,]+)\)\s*h").items()}

    s9 = _secao(md, 9)
    prob = {k: _num(v[0]) / 100.0 for k, v in _por_terminal(s9, r"(\d+)%").items()}

    s10 = _secao(md, 10)
    volume = {k: tuple(_num(x) for x in v) for k, v in
              _por_terminal(s10, r"Tri\(([\d,]+),\s*([\d,]+),\s*([\d,]+)\)\s*t").items()}

    linhas = [l for l in _secao(md, 11).splitlines() if l.startswith("|")]
    cab = [c.strip() for c in linhas[0].strip("|").split("|")]
    destinos = cab[1:]
    dist = []
    for l in linhas[2:]:
        cel = [c.strip() for c in l.strip("|").split("|")]
        for dest, v in zip(destinos, cel[1:]):
            dist.append({"origem": cel[0], "destino": dest, "distancia": _num(v)})

    return {"bercos": bercos, "taxa_dia": taxa_dia, "antecedencia": antecedencia, "manobra": manobra,
            "operacao": operacao, "prob": prob, "volume": volume, "distancias": pd.DataFrame(dist)}


def montar_terminais(d):
    linhas = []
    for t in sorted(d["bercos"], key=lambda x: int(x[1:])):
        linhas.append({
            "id_terminal": t,
            "id_classe": "C" + t[1:],
            "n_bercos": d["bercos"][t],
            "taxa_chegada": d["taxa_dia"][t] / HORAS_POR_DIA,
            "antecedencia": d["antecedencia"],
            "tempo_manobra": d["manobra"][t],
            "dist_operacao": "triangular",
            "op_p1": d["operacao"][t][0], "op_p2": d["operacao"][t][1], "op_p3": d["operacao"][t][2],
            "prob_compra": d["prob"][t],
            "dist_volume": "triangular",
            "vl_p1": d["volume"][t][0], "vl_p2": d["volume"][t][1], "vl_p3": d["volume"][t][2],
        })
    return pd.DataFrame(linhas)


def preparar_entradas(caminho_md, pasta_saida):
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)
    d = ler_dados_md(caminho_md)
    terminais = montar_terminais(d)
    terminais.to_csv(pasta / "terminais.csv", index=False)
    d["distancias"].to_csv(pasta / "distancias.csv", index=False)
    return terminais, d["distancias"]


if __name__ == "__main__":
    import sys
    md, saida = sys.argv[1], sys.argv[2]
    t, di = preparar_entradas(md, saida)
    print(t.to_string(index=False))
    print(len(di), "linhas em distancias.csv")
