from django.test import TestCase
from .models import Cliente
from django.core.exceptions import ValidationError

class ClienteModelTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'nome': 'Empresa Teste',
            'instalacao': 'Instalação 1',
            'cnpj': '12.345.678/0001-95',
            'endereco': 'Rua X, 123',
            'cep': '12345-678',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'fator_potencia': 0.92,
            'classificacao_comercial': 'Comercial',
            'tipo_fornecimento': 'Trifásico',
            'tensao_nominal_disp': 220.0,
            'limite_min': 100.0,
            'limite_max': 500.0,
            'tipo_tarifa': 'Convencional',
        }

    def test_cliente_valido(self):
        cliente = Cliente(**self.valid_data)
        try:
            cliente.full_clean()
        except ValidationError:
            self.fail('ValidationError raised unexpectedly!')

    def test_cnpj_invalido(self):
        data = self.valid_data.copy()
        data['cnpj'] = '00.000.000/0000-00'  # CNPJ inválido
        cliente = Cliente(**data)
        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_limite_min_maior_que_limite_max(self):
        data = self.valid_data.copy()
        data['limite_min'] = 600.0
        data['limite_max'] = 500.0
        cliente = Cliente(**data)
        with self.assertRaises(ValidationError):
            cliente.full_clean()
