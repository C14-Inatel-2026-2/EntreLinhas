import unittest

from src.Baralho import Baralho

class TestBaralho(unittest.TestCase):
    def setUp(self):
        self.linhas = ['A', 'B', 'C', 'D']
        self.colunas = ['1', '2', '3', '4']
        self.baralho = Baralho(self.linhas, self.colunas)
        self.cartas_originais = self.baralho.cartas.copy()

    # --- Testes de __init__ ---
    def test_inicializacao_gera_todas_as_combinacoes_de_cartas(self):
        esperadas = [f"{l}{c}" for l in self.linhas for c in self.colunas]
        self.assertEqual(self.baralho.cartas, esperadas)

    def test_inicializacao_com_linhas_vazias_lanca_value_error(self):
        with self.assertRaises(ValueError):
            Baralho([], ['1', '2'])

    def test_inicializacao_com_colunas_vazias_lanca_value_error(self):
        with self.assertRaises(ValueError):
            Baralho(['A', 'B'], [])

    # --- Testes de embaralhar ---
    def test_embaralhar_mantem_quantidade_total_de_cartas(self):
        self.baralho.embaralhar()
        self.assertEqual(len(self.baralho.cartas), len(self.cartas_originais))

    def test_embaralhar_mantem_exatamente_os_mesmos_elementos(self):
        self.baralho.embaralhar()
        self.assertCountEqual(self.baralho.cartas, self.cartas_originais)

    def test_embaralhar_modifica_a_ordem_das_cartas(self):
        self.baralho.embaralhar()
        self.assertNotEqual(self.baralho.cartas, self.cartas_originais)

    # --- Testes de distribuir ---
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

    def test_distribuir_quantidade_zero_lanca_value_error(self):
        with self.assertRaises(ValueError):
            self.baralho.distribuir(0)

    def test_distribuir_quantidade_negativa_lanca_value_error(self):
        with self.assertRaises(ValueError):
            self.baralho.distribuir(-1)

    # --- Testes dos métodos utilitários ---
    def test_len_retorna_quantidade_de_cartas(self):
        self.assertEqual(len(self.baralho), len(self.cartas_originais))

    def test_len_atualiza_apos_distribuicao(self):
        self.baralho.distribuir(2)
        self.assertEqual(len(self.baralho), len(self.cartas_originais) - 2)

    def test_esta_vazio_retorna_false_quando_ha_cartas(self):
        self.assertFalse(self.baralho.esta_vazio())

    def test_esta_vazio_retorna_true_apos_distribuir_todas_as_cartas(self):
        self.baralho.distribuir(len(self.baralho))
        self.assertTrue(self.baralho.esta_vazio())

    def test_puxar_carta_retorna_a_primeira_carta(self):
        primeira_carta = self.baralho.cartas[0]
        carta = self.baralho.puxar_carta()
        self.assertEqual(carta, primeira_carta)

    def test_puxar_carta_reduz_o_tamanho_do_baralho(self):
        tamanho_inicial = len(self.baralho)
        self.baralho.puxar_carta()
        self.assertEqual(len(self.baralho), tamanho_inicial - 1)


if __name__ == '__main__':
    unittest.main()