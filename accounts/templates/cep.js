const cep = document.querySelector("#cep_member")
const response = fetch(`https://viacep.com.br/ws/${cep}/json/`)
