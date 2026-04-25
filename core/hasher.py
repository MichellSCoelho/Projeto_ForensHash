import hashlib
import os
from datetime import datetime


def calcular_hashes(caminho_arquivo: str) -> dict:
    """
    Calcula MD5, SHA-1 e SHA-256 de um arquivo.
    Retorna um dicionário com os resultados e metadados.
    """

    # Verifica se o arquivo existe
    if not os.path.isfile(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    # Inicializa os algoritmos de hash
    md5    = hashlib.md5()
    sha1   = hashlib.sha1()
    sha256 = hashlib.sha256()

    # Lê o arquivo em blocos para suportar arquivos grandes
    tamanho_bloco = 65536  # 64KB por vez

    with open(caminho_arquivo, "rb") as f:
        while True:
            bloco = f.read(tamanho_bloco)
            if not bloco:
                break
            md5.update(bloco)
            sha1.update(bloco)
            sha256.update(bloco)

    # Coleta metadados do arquivo
    stat = os.stat(caminho_arquivo)
    tamanho_bytes = stat.st_size

    return {
        "arquivo": os.path.basename(caminho_arquivo),
        "caminho_completo": os.path.abspath(caminho_arquivo),
        "tamanho_bytes": tamanho_bytes,
        "tamanho_legivel": formatar_tamanho(tamanho_bytes),
        "data_analise": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "md5":    md5.hexdigest(),
        "sha1":   sha1.hexdigest(),
        "sha256": sha256.hexdigest(),
    }


def formatar_tamanho(bytes: int) -> str:
    """Converte bytes para formato legível (KB, MB, GB)."""
    for unidade in ["B", "KB", "MB", "GB", "TB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unidade}"
        bytes /= 1024


def verificar_integridade(caminho_arquivo: str, hash_referencia: str, algoritmo: str = "sha256") -> dict:
    """
    Compara o hash de um arquivo com um valor de referência.
    Útil para verificar se uma evidência foi adulterada.
    """

    algoritmos_suportados = ["md5", "sha1", "sha256"]

    if algoritmo not in algoritmos_suportados:
        raise ValueError(f"Algoritmo inválido. Use: {algoritmos_suportados}")

    resultado = calcular_hashes(caminho_arquivo)
    hash_calculado = resultado[algoritmo]
    hash_referencia = hash_referencia.strip().lower()

    integro = hash_calculado == hash_referencia

    return {
        "arquivo": resultado["arquivo"],
        "algoritmo": algoritmo.upper(),
        "hash_calculado": hash_calculado,
        "hash_referencia": hash_referencia,
        "integro": integro,
        "status": "✅ ÍNTEGRO — Hashes correspondem" if integro else "❌ ADULTERADO — Hashes divergem",
        "data_verificacao": resultado["data_analise"],
    }


# ─── Teste rápido ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print("Uso: python3 hasher.py <caminho_do_arquivo>")
        sys.exit(1)

    arquivo = sys.argv[1]

    print("\n" + "="*60)
    print("   FORENSHASH — Calculadora de Hash Forense")
    print("="*60)

    resultado = calcular_hashes(arquivo)

    print(f"\n📁 Arquivo     : {resultado['arquivo']}")
    print(f"📍 Caminho     : {resultado['caminho_completo']}")
    print(f"📦 Tamanho     : {resultado['tamanho_legivel']}")
    print(f"🕐 Data/Hora   : {resultado['data_analise']}")
    print(f"\n🔑 MD5         : {resultado['md5']}")
    print(f"🔑 SHA-1        : {resultado['sha1']}")
    print(f"🔑 SHA-256      : {resultado['sha256']}")
    print("\n" + "="*60)