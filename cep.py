import requests
import json


def buscar_cep(cep):
    # Remove qualquer caractere que não seja número
    cep_limpo = "".join(filter(str.isdigit, str(cep)))

    # URL da API do ViaCEP
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

    try:
        response = requests.get(url)
        # Transforma o resultado em um dicionário Python
        dados = response.json()

        if "erro" in dados:
            return {"status": "erro", "mensagem": "CEP não encontrado"}

        return dados
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}


# Testando com o CEP da Praça da Sé (SP)
resultado = buscar_cep("18230-971")

# Exibe o resultado como um JSON formatado (string)
print(json.dumps(resultado, indent=4, ensure_ascii=False))
