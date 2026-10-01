import csv
import random
import uuid
from datetime import datetime
from pathlib import Path

arquivo = Path("dados_nutrimetrics.csv")

objetivos = [
    "Reducao de peso",
    "Ganho de massa",
    "Acompanhamento",
    "Melhora de habitos"
]

campos = [
    "registro_id",
    "paciente_id",
    "peso",
    "altura",
    "imc",
    "circunferencia_abdominal",
    "objetivo",
    "data_hora"
]

novo_arquivo = not arquivo.exists()

with arquivo.open("a", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=campos)

    if novo_arquivo:
        writer.writeheader()

    for _ in range(15):
        altura = round(random.uniform(1.50, 1.95), 2)
        peso = round(random.uniform(50, 120), 2)
        imc = round(peso / (altura ** 2), 2)

        writer.writerow({
            "registro_id": uuid.uuid4().hex[:8],
            "paciente_id": f"PAC{random.randint(1, 200):04d}",
            "peso": peso,
            "altura": altura,
            "imc": imc,
            "circunferencia_abdominal": round(random.uniform(65, 120), 2),
            "objetivo": random.choice(objetivos),
            "data_hora": datetime.now().isoformat(timespec="seconds")
        })

print("15 registros foram gerados.")
print(f"Arquivo salvo em: {arquivo.resolve()}")
