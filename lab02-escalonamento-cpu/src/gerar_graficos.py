"""
Gera os gráficos e as métricas complementares do Laboratório 02.

Reimplementa FCFS, SJF (não-preemptivo) e Round Robin retornando a linha do
tempo de execução (necessária para os diagramas de Gantt) e confere os
resultados com a saída do simulador_escalonador.py.

Uso (a partir da raiz do repositório):
    python3 src/gerar_graficos.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens")
RES = os.path.join(BASE, "resultados")
os.makedirs(IMG, exist_ok=True)
os.makedirs(RES, exist_ok=True)

# pid: (chegada, duração)
PROCESSOS = {"P1": (0, 8), "P2": (1, 4), "P3": (2, 9), "P4": (3, 5)}
CORES = {"P1": "#4C78A8", "P2": "#F58518", "P3": "#54A24B", "P4": "#B279A2"}


# ---------------------------------------------------------------- algoritmos
def fcfs():
    t, seg, fins = 0, [], {}
    for pid, (ch, du) in sorted(PROCESSOS.items(), key=lambda x: x[1][0]):
        t = max(t, ch)
        seg.append((pid, t, t + du))
        t += du
        fins[pid] = t
    return seg, fins


def sjf():
    t, seg, fins = 0, [], {}
    pend = dict(PROCESSOS)
    while pend:
        prontos = [p for p, (ch, _) in pend.items() if ch <= t]
        if not prontos:
            t = min(ch for ch, _ in pend.values())
            continue
        p = min(prontos, key=lambda x: (pend[x][1], pend[x][0]))
        du = pend.pop(p)[1]
        seg.append((p, t, t + du))
        t += du
        fins[p] = t
    return seg, fins


def round_robin(q):
    rest = {p: du for p, (_, du) in PROCESSOS.items()}
    ordem = sorted(PROCESSOS, key=lambda p: PROCESSOS[p][0])
    t, fila, add, seg, fins = 0, [], set(), [], {}

    def add_fila(tempo):
        for p in ordem:
            if PROCESSOS[p][0] <= tempo and p not in add:
                fila.append(p)
                add.add(p)

    add_fila(t)
    while fila:
        p = fila.pop(0)
        ex = min(rest[p], q)
        seg.append((p, t, t + ex))
        t += ex
        rest[p] -= ex
        add_fila(t)
        if rest[p] > 0:
            fila.append(p)
        else:
            fins[p] = t
    return seg, fins


# ------------------------------------------------------------------ métricas
def metricas(fins):
    res = {}
    for pid, (ch, du) in PROCESSOS.items():
        ret = fins[pid] - ch
        res[pid] = {"fim": fins[pid], "retorno": ret, "espera": ret - du}
    n = len(res)
    return (res,
            sum(r["espera"] for r in res.values()) / n,
            sum(r["retorno"] for r in res.values()) / n)


def trocas_contexto(seg):
    """Número de vezes em que a CPU passa de um processo para OUTRO processo."""
    return sum(1 for i in range(1, len(seg)) if seg[i][0] != seg[i - 1][0])


# ------------------------------------------------------------------- gráficos
def gantt(seg, titulo, arquivo):
    fig, ax = plt.subplots(figsize=(10, 2.4))
    for pid, ini, fim in seg:
        ax.barh(0, fim - ini, left=ini, color=CORES[pid], edgecolor="white", height=0.6)
        ax.text((ini + fim) / 2, 0, pid, ha="center", va="center",
                color="white", fontweight="bold", fontsize=10)
    marcos = sorted({s[1] for s in seg} | {s[2] for s in seg})
    ax.set_xticks(marcos)
    ax.set_xlim(0, marcos[-1])
    ax.set_yticks([])
    ax.set_xlabel("Tempo (ms)")
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, arquivo), dpi=150)
    plt.close(fig)


def grafico_comboio(seg_fcfs):
    inicio = {p: i for p, i, _ in seg_fcfs}
    fim = {p: f for p, _, f in seg_fcfs}
    ordem = list(PROCESSOS)[::-1]  # P1 no topo
    fig, ax = plt.subplots(figsize=(10, 4))
    for y, p in enumerate(ordem):
        ch, du = PROCESSOS[p]
        ax.barh(y, inicio[p] - ch, left=ch, color="#E8E8E8", edgecolor="#999999",
                hatch="//", height=0.55)
        ax.barh(y, du, left=inicio[p], color=CORES[p], height=0.55)
        if inicio[p] - ch > 0:
            ax.text((ch + inicio[p]) / 2, y, f"espera {inicio[p] - ch} ms",
                    ha="center", va="center", fontsize=9, color="#333333")
        ax.text(inicio[p] + du / 2, y, f"{p} executa {du} ms",
                ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        ax.plot(ch, y + 0.38, marker="v", color="black", markersize=6)
    # destaque do caso P2 (espaço livre à direita da barra do P2)
    y2 = ordem.index("P2")
    ax.text(12.6, y2, "\u25c4 P2 (4 ms) esperou 7 ms\n    porque o P1 (8 ms) ocupava a CPU",
            va="center", ha="left", fontsize=10, color="#C0392B", fontweight="bold")
    ax.set_yticks(range(len(ordem)))
    ax.set_yticklabels(ordem)
    ax.set_xticks(range(0, 27, 2))
    ax.set_xlabel("Tempo (ms)   (▼ = chegada do processo)")
    ax.set_title("Efeito comboio no FCFS: espera (hachurado) x execução (colorido)",
                 fontsize=12, fontweight="bold")
    ax.set_xlim(-0.5, 27.5)
    ax.set_ylim(-0.6, len(ordem) - 0.4)
    ax.legend(handles=[Patch(facecolor="#E8E8E8", edgecolor="#999999", hatch="//", label="Esperando na fila de prontos"),
                       Patch(facecolor="#777777", label="Executando na CPU")],
              loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "efeito_comboio.png"), dpi=150)
    plt.close(fig)


def grafico_comparacao(dados):
    nomes = list(dados)
    esp = [dados[n][0] for n in nomes]
    ret = [dados[n][1] for n in nomes]
    x = range(len(nomes))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5))
    b1 = ax.bar([i - w / 2 for i in x], esp, w, label="Espera média", color="#4C78A8")
    b2 = ax.bar([i + w / 2 for i in x], ret, w, label="Retorno médio", color="#F58518")
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.25,
                f"{b.get_height():.2f}", ha="center", fontsize=10)
    ax.set_xticks(list(x))
    ax.set_xticklabels(nomes)
    ax.set_ylabel("Tempo (ms)")
    ax.set_title("Comparação dos algoritmos (menor é melhor)", fontsize=12, fontweight="bold")
    ax.legend()
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "comparacao_metricas.png"), dpi=150)
    plt.close(fig)


def grafico_quantum(qs, trocas):
    fig, ax = plt.subplots(figsize=(7, 4))
    barras = ax.bar([f"{q} ms" for q in qs], trocas, color=["#E45756", "#4C78A8", "#54A24B"])
    for b in barras:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                str(int(b.get_height())), ha="center", fontsize=11, fontweight="bold")
    ax.set_xlabel("Quantum")
    ax.set_ylabel("Trocas de contexto")
    ax.set_title("Round Robin: trocas de contexto x quantum", fontsize=12, fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "quantum_trocas_contexto.png"), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------- main
if __name__ == "__main__":
    linhas = []

    def log(txt=""):
        print(txt)
        linhas.append(txt)

    seg_f, fin_f = fcfs()
    seg_s, fin_s = sjf()
    seg_r, fin_r = round_robin(3)
    m_f, me_f, mr_f = metricas(fin_f)
    m_s, me_s, mr_s = metricas(fin_s)
    m_r, me_r, mr_r = metricas(fin_r)

    # Conferência com o simulador original
    assert (me_f, mr_f) == (8.75, 15.25), "FCFS diverge do simulador"
    assert (me_r, mr_r) == (13.5, 20.0), "Round Robin diverge do simulador"

    for nome, m, me, mr, seg in (("FCFS", m_f, me_f, mr_f, seg_f),
                                 ("SJF (nao-preemptivo)", m_s, me_s, mr_s, seg_s),
                                 ("ROUND ROBIN (q=3)", m_r, me_r, mr_r, seg_r)):
        log(f"--- {nome} ---")
        log("Linha do tempo: " + " | ".join(f"{p}[{i}-{f}]" for p, i, f in seg))
        for p in PROCESSOS:
            log(f"Proc {p}: Fim = {m[p]['fim']}ms, Espera = {m[p]['espera']}ms, Retorno = {m[p]['retorno']}ms")
        log(f"Tempo Medio de Espera: {me:.2f} ms")
        log(f"Tempo Medio de Retorno: {mr:.2f} ms")
        log(f"Trocas de contexto: {trocas_contexto(seg)}")
        log()

    log("--- VARIACAO DO QUANTUM (Round Robin) ---")
    qs, trocas = [1, 3, 50], []
    for q in qs:
        seg, fins = round_robin(q)
        _, me, mr = metricas(fins)
        t = trocas_contexto(seg)
        trocas.append(t)
        log(f"Quantum {q:>2} ms: fatias = {len(seg):>2}, trocas de contexto = {t:>2}, "
            f"espera media = {me:.2f} ms, retorno medio = {mr:.2f} ms")

    gantt(seg_f, "FCFS - Diagrama de Gantt", "gantt_fcfs.png")
    gantt(seg_s, "SJF (não-preemptivo) - Diagrama de Gantt", "gantt_sjf.png")
    gantt(seg_r, "Round Robin (quantum = 3 ms) - Diagrama de Gantt", "gantt_round_robin.png")
    grafico_comboio(seg_f)
    grafico_comparacao({"FCFS": (me_f, mr_f), "SJF": (me_s, mr_s), "RR (q=3)": (me_r, mr_r)})
    grafico_quantum(qs, trocas)

    with open(os.path.join(RES, "metricas_calculadas.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\nGraficos salvos em imagens/ e metricas em resultados/metricas_calculadas.txt")
