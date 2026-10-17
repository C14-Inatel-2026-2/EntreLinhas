import unittest
from unittest.mock import Mock

from src.Baralho import Baralho
from src.jogo import Jogo


class TestJogo(unittest.TestCase):
    # --- Testes de __init__ ---
    def test_inicializacao_com_jogadores_validos(self):
        baralho, tabuleiro = object(), object()
        jogadores = ['Ana', 'Bruno']

        jogo = Jogo(baralho, tabuleiro, jogadores)

        self.assertEqual(jogo.jogadores, jogadores)
        self.assertIs(jogo.baralho, baralho)
        self.assertIs(jogo.tabuleiro, tabuleiro)
        self.assertIsNone(jogo.carta_secreta)

    def test_jogadores_que_nao_sao_lista_lancam_type_error(self):
        with self.assertRaises(TypeError):
            Jogo(None, None, 'Ana')

    def test_lista_de_jogadores_vazia_lanca_value_error(self):
        with self.assertRaises(ValueError):
            Jogo(None, None, [])

    # --- Testes de preparar_rodada ---
    def test_preparar_rodada_chama_puxar_carta_uma_vez_e_usa_retorno(self):
        baralho = Mock(spec=Baralho)
        baralho.puxar_carta.return_value = 'E5'
        jogo = Jogo(baralho, None, ['Ana', 'Bruno'])

        carta = jogo.preparar_rodada()

        baralho.puxar_carta.assert_called_once_with()
        self.assertEqual(carta, 'E5')
        self.assertEqual(jogo.carta_secreta, 'E5')


if __name__ == '__main__':
    unittest.main()
