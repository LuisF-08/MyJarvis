"""
    Jarvis - Versão Ultra Rápida com Voz Neural do Microsoft Edge
"""
import os
import sys
import time
import asyncio
from io import BytesIO

# Oculta logs do ALSA/JACK no Linux
stderr_fd = os.dup(2)
devnull_fd = os.open(os.devnull, os.O_WRONLY)

def ocultar_logs():
    os.dup2(devnull_fd, 2)

def restaurar_logs():
    os.dup2(stderr_fd, 2)

ocultar_logs()
import speech_recognition as sr
import pygame
import ollama
import edge_tts
from dotenv import load_dotenv
restaurar_logs()

load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
PAUSA_SILENCIO = 1.0

# Voz masculina brasileira do Microsoft Edge Neural
VOZ_JARVIS = "pt-BR-AntonioNeural"

class Jarvis:
    def __init__(self):
        self.cliente = ollama
        
        # Inicializa o Pygame Áudio
        pygame.mixer.init()
        
        ocultar_logs()
        self.reconhecedor = sr.Recognizer()
        self.microfone = sr.Microphone()
        self.reconhecedor.pause_threshold = PAUSA_SILENCIO
        
        print("Calibrando Microfone... Por favor, aguarde.")
        with self.microfone as fonte:
            self.reconhecedor.adjust_for_ambient_noise(fonte, duration=1.2)
        restaurar_logs()
            
        print(f"Microfone calibrado! Ruído: {self.reconhecedor.energy_threshold:.1f}\n")

    def ouvir(self):
        ocultar_logs()
        with self.microfone as fonte:
            print("Ouvindo ...")
            try:
                audio = self.reconhecedor.listen(fonte, timeout=8, phrase_time_limit=8)
                restaurar_logs()
                texto = self.reconhecedor.recognize_google(audio, language="pt-BR")
                print(f"Você disse: {texto}")
                return texto
            except sr.UnknownValueError:
                restaurar_logs()
                print("Jarvis não conseguiu compreender...")
                return None
            except Exception:
                restaurar_logs()
                return None

    def pensar(self, texto):
        try:
            print("Jarvis está processando...")
            resposta = self.cliente.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é o Jarvis. Responda em português de forma direta, formal, refinada e objetiva (no máximo 2 ou 3 frases)."
                    },
                    {"role": "user", "content": texto}
                ]
            )
            texto_resposta = resposta["message"]["content"].strip()
            print(f"\n🤖 Jarvis: {texto_resposta}\n")
            return texto_resposta
        except Exception as e:
            print(f"Erro no Ollama: {e}")
            return "Ocorreu um erro ao processar."

    async def _gerar_audio(self, texto):
        """Gera o áudio usando a API Neural do Edge de forma assíncrona com velocidade +15%"""
        communicate = edge_tts.Communicate(
            text=texto, 
            voice=VOZ_JARVIS,
            rate="+15%",  # Aumenta a velocidade para ser mais ágil
            pitch="-5Hz"   # Torna o tom levemente mais grave/robótico
        )
        fp = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                fp.write(chunk["data"])
        fp.seek(0)
        return fp

    def falar(self, texto):
        """Sintetiza e reproduz a voz neural de alta velocidade"""
        try:
            # Executa a geração assíncrona do edge-tts
            fp = asyncio.run(self._gerar_audio(texto))

            # Reproduz via Pygame
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.05)

            pygame.mixer.music.unload()
        except Exception as e:
            print(f"Erro ao falar: {e}")

    def executar(self):
        tela = '|====================================================================|'
        print(tela)
        print(" 🤖 Jarvis Online (Voz Neural Edge Rápida)")
        print(tela)
        print(" Diga 'Sair' para encerrar.\n")
        
        while True:
            texto = self.ouvir()
            
            if not texto:
                continue
            
            if texto.lower() in ["sair", "desligar", "encerrar"]:
                print("\n 🤖 Jarvis: Desligando sistemas...")
                self.falar("Desligando todos os sistemas. Até logo, senhor.")
                break
            
            resposta = self.pensar(texto)
            self.falar(resposta)

def main():
    try:
        jarvis = Jarvis()
        jarvis.executar()
    except KeyboardInterrupt:
        print("\nJARVIS DESLIGADO.")
    except Exception as e:
        print(f"ERRO CRÍTICO => {e}")

if __name__ == "__main__":
    main()