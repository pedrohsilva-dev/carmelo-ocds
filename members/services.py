from members.models import Member


def generate_registry_contribution_member(member: Member):
    """Gera a contribuição de registro para um membro.

    A contribuição de registro é uma taxa única paga pelo membro ao se registrar.
    """
    # Lógica para gerar a contribuição de registro
    # Exemplo: criar um objeto de contribuição no banco de dados

    pays_month = [
        for pay in pays : {
            "month": pay.month,
            "year": pay.year,
            "price_pay": pay.price,
            "status": pay.status
        }
    ]

    contribution = {
        "member_id": member.id,
        "amount": 100.00,  # Valor da contribuição de registro
        "description": "Contribuição de Registro",

        "pay_missing": pays_month,
    }



    return contribution
