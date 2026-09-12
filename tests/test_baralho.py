import unittest

from EntreLinhas.src.Baralho import Baralho

class TestBaralho(unittest.TestCase):
    def setUp(self):
        self.linhas = ['A', 'B', 'C', 'D']
        self.colunas = ['1', '2', '3', '4']
        self.baralho = Baralho(self.linhas, self.colunas)
        self.cartas_originais = self.baralho.cartas.copy()

    def test_embaralhar_mantem_quantidade_total_de_cartas(self):
        self.baralho.embaralhar()
        self.assertEqual(len(self.baralho.cartas), len(self.cartas_originais))

    def test_embaralhar_mantem_exatamente_os_mesmos_elementos(self):
        self.baralho.embaralhar()
        self.assertCountEqual(self.baralho.cartas, self.cartas_originais)

    def test_embaralhar_modifica_a_ordem_das_cartas(self):
        self.baralho.embaralhar()
        self.assertNotEqual(self.baralho.cartas, self.cartas_originais)


    def test_distribuir_retorna_o_tamanho_da_mao_correto(self):
        mao = self.baralho.distribuir(3)
        self.assertEqual(len(mao), 3)

    def test_distribuir_subtrai_as_cartas_do_tamanho_do_baralho(self):
        tamanho_inicial = len(self.baralho.cartas)
        self.baralho.distribuir(3)
        self.assertEqual(len(self.baralho.cartas), tamanho_inicial - 3)

    def test_distribuir_cartas_alem_do_limite_lanca_value_error(self):
        with self.assertRaises(ValueError):
            self.baralho.distribuir(20)

if __name__ == '__main__':
    unittest.main()