from django.test import TestCase
from .models import ContaEnergia, ItensFatura
from apps.clientes.models import Cliente
from django.core.exceptions import ValidationError
from datetime import date, timedelta

class ContaEnergiaModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome='Empresa Teste',
            instalacao='Instalação 1',
            cnpj='12.345.678/0001-95',
            endereco='Rua X, 123',
            cep='12345-678',
            cidade='São Paulo',
            estado='SP',
            fator_potencia=0.92,
            classificacao_comercial='Comercial',
            tipo_fornecimento='Trifásico',
            tensao_nominal_disp=220.0,
            limite_min=100.0,
            limite_max=500.0,
            tipo_tarifa='Convencional',
        )
        self.valid_data = {
            'cliente': self.cliente,
            'mes': date(2023, 8, 1),
            'vencimento': date(2023, 8, 20),
            'total_pagar': 1500.75,
            'leitura_anterior': 5000.0,
            'leitura_atual': 5500.0,
            'numero_dias': 30,
            'proxima_leitura': date.today() + timedelta(days=30),
        }

    def test_conta_energia_valida(self):
        conta = ContaEnergia(**self.valid_data)
        try:
            conta.full_clean()
        except ValidationError:
            self.fail('ValidationError raised unexpectedly!')

    def test_leitura_atual_menor_que_leitura_anterior(self):
        data = self.valid_data.copy()
        data['leitura_atual'] = 4000.0
        conta = ContaEnergia(**data)
        with self.assertRaises(ValidationError):
            conta.full_clean()

    def test_vencimento_anterior_ao_mes(self):
        data = self.valid_data.copy()
        data['vencimento'] = date(2023, 7, 31)
        conta = ContaEnergia(**data)
        with self.assertRaises(ValidationError):
            conta.full_clean()

    def test_proxima_leitura_passada(self):
        data = self.valid_data.copy()
        data['proxima_leitura'] = date.today() - timedelta(days=1)
        conta = ContaEnergia(**data)
        with self.assertRaises(ValidationError):
            conta.full_clean()

class ItensFaturaModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nome='Empresa Teste',
            instalacao='Instalação 1',
            cnpj='12.345.678/0001-95',
            endereco='Rua X, 123',
            cep='12345-678',
            cidade='São Paulo',
            estado='SP',
            fator_potencia=0.92,
            classificacao_comercial='Comercial',
            tipo_fornecimento='Trifásico',
            tensao_nominal_disp=220.0,
            limite_min=100.0,
            limite_max=500.0,
            tipo_tarifa='Convencional',
        )
        self.conta = ContaEnergia.objects.create(
            cliente=self.cliente,
            mes=date(2023, 8, 1),
            vencimento=date(2023, 8, 20),
            total_pagar=1500.75,
            leitura_anterior=5000.0,
            leitura_atual=5500.0,
            numero_dias=30,
            proxima_leitura=date.today() + timedelta(days=30),
        )
        self.valid_data = {
            'conta_energia': self.conta,
            'consumo_ponta': 300.0,
            'consumo_fora_ponta': 200.0,
            'demanda_ativa': 50.0,
        }

    def test_itens_fatura_valido(self):
        item = ItensFatura(**self.valid_data)
        try:
            item.full_clean()
        except ValidationError:
            self.fail('ValidationError raised unexpectedly!')

    def test_consumo_ponta_negativo(self):
        data = self.valid_data.copy()
        data['consumo_ponta'] = -100.0
        item = ItensFatura(**data)
        with self.assertRaises(ValidationError):
            item.full_clean()
