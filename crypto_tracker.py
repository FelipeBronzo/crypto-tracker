import time
import requests
import json

class CryptoTracker:
    def __init__(self, crypto_id, interval=60):
        self.crypto_id = crypto_id
        self.interval = interval
        self.api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={self.crypto_id}&vs_currencies=brl"
        self.investment_file = 'investment_data.json'

    def get_crypto_price(self):

        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                data = response.json()
                return data[self.crypto_id]['brl']
            elif response.status_code == 429:
                print("Erro 429: Muitas requisições. Aguardando 1 minuto antes de tentar novamente.")
                time.sleep(60)
                return None
            else:
                print(f"Erro: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão: {e}")
            return None

    def monitor_price(self):

        while True:
            price = self.get_crypto_price()
            if price:
                print(f"O preço atual do {self.crypto_id.capitalize()} é: R${price}")
            time.sleep(self.interval)

    def save_investment(self, valor_investido):
        """Salva os dados do investimento em um arquivo JSON."""
        price_inicial = self.get_crypto_price()
        if price_inicial is None:
            print("Erro ao obter o preço inicial. Tente novamente mais tarde.")
            return

        quantidade_comprada = valor_investido / price_inicial

        # Dados a serem salvos no arquivo
        investment_data = {
            "crypto_id": self.crypto_id,
            "valor_investido": valor_investido,
            "quantidade_comprada": quantidade_comprada,
            "price_inicial": price_inicial
        }

        # Escreve os dados no arquivo JSON
        with open(self.investment_file, 'w') as f:
            json.dump(investment_data, f)

        print(f"Investimento salvo com sucesso! Você comprou {quantidade_comprada:.6f} {self.crypto_id} a R${price_inicial:.2f}.")

    def load_investment(self):
        """Carrega as informações do investimento do arquivo JSON e calcula o valor atual."""
        try:
            with open(self.investment_file, 'r') as f:
                investment_data = json.load(f)

            # Pega o preço atual da criptomoeda
            price_atual = self.get_crypto_price()

            if price_atual is None:
                print("Erro ao obter o preço atual.")
                return

            valor_atual = investment_data["quantidade_comprada"] * price_atual

            print(f"Você investiu {investment_data['valor_investido']:.2f} quando o {self.crypto_id.capitalize()} estava R${investment_data['price_inicial']:.2f}.")

            if investment_data["valor_investido"] < valor_atual:
                print(f"Atualmente, o {self.crypto_id.capitalize()} está R${price_atual:.2f} e seu investimento vale R${valor_atual:.2f}.\nParabéns, você está com um lucro de R${valor_atual-investment_data['valor_investido']:.2f}!")
            else:
                print(f"Atualmente, o {self.crypto_id.capitalize()} está R${price_atual:.2f} e seu investimento vale R${valor_atual:.2f}.\nQue pena, você está com um prejuízo de R${investment_data['valor_investido']-valor_atual:.2f}!")

        except FileNotFoundError:
            print("Nenhum investimento encontrado. Por favor, faça um investimento primeiro.")

if __name__ == "__main__":
    tracker = CryptoTracker(crypto_id='bitcoin', interval=60)

    while True:
        escolha = input("Você deseja (1) Fazer um novo investimento ou (2) Verificar investimento existente? (1/2): ")

        if escolha == '1':
            valor_investido = float(input("Quanto você quer investir? "))
            tracker.save_investment(valor_investido)
        elif escolha == '2':
            tracker.load_investment()
        else:
            break