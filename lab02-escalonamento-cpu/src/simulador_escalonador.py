class Processo:
    def __init__(self, pid, chegada, duracao):
        self.pid = pid
        self.chegada = chegada
        self.duracao = duracao
        self.restante = duracao
        self.finalizacao = 0
        self.espera = 0
        self.retorno = 0


def simular_fcfs(processos):
    procs = sorted(processos, key=lambda x: x.chegada)
    tempo_atual = 0
    print("\n--- SIMULACAO FCFS ---")
    for p in procs:
        if tempo_atual < p.chegada:
            tempo_atual = p.chegada
        tempo_atual += p.duracao
        p.finalizacao = tempo_atual
        p.retorno = p.finalizacao - p.chegada
        p.espera = p.retorno - p.duracao
        print(f"Proc {p.pid}: Fim = {p.finalizacao}ms, Espera = {p.espera}ms, Retorno = {p.retorno}ms")

    media_esp = sum(p.espera for p in procs) / len(procs)
    media_ret = sum(p.retorno for p in procs) / len(procs)
    print(f"Tempo Medio de Espera: {media_esp:.2f} ms")
    print(f"Tempo Medio de Retorno: {media_ret:.2f} ms")


def simular_round_robin(processos, quantum=3):
    import copy
    procs = copy.deepcopy(processos)
    tempo_atual = 0
    fila, concluidos = [], []
    procs_ord = sorted(procs, key=lambda x: x.chegada)
    adicionados = set()

    def add_fila(t):
        for i, p in enumerate(procs_ord):
            if p.chegada <= t and i not in adicionados:
                fila.append(p)
                adicionados.add(i)

    add_fila(tempo_atual)
    print(f"\n--- SIMULACAO ROUND ROBIN (Quantum {quantum} ms) ---")
    while fila:
        p_atual = fila.pop(0)
        tempo_exec = min(p_atual.restante, quantum)
        tempo_atual += tempo_exec
        p_atual.restante -= tempo_exec
        add_fila(tempo_atual)
        if p_atual.restante > 0:
            fila.append(p_atual)
        else:
            p_atual.finalizacao = tempo_atual
            p_atual.retorno = p_atual.finalizacao - p_atual.chegada
            p_atual.espera = p_atual.retorno - p_atual.duracao
            concluidos.append(p_atual)

    for p in sorted(concluidos, key=lambda x: x.pid):
        print(f"Proc {p.pid}: Fim = {p.finalizacao}ms, Espera = {p.espera}ms, Retorno = {p.retorno}ms")

    media_esp = sum(p.espera for p in concluidos) / len(concluidos)
    media_ret = sum(p.retorno for p in concluidos) / len(concluidos)
    print(f"Tempo Medio de Espera: {media_esp:.2f} ms")
    print(f"Tempo Medio de Retorno: {media_ret:.2f} ms")


if __name__ == "__main__":
    workload = [
        Processo("P1", 0, 8), Processo("P2", 1, 4),
        Processo("P3", 2, 9), Processo("P4", 3, 5)
    ]
    simular_fcfs(workload)
    simular_round_robin(workload, quantum=3)
