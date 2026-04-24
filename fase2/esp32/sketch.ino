#include <DHTesp.h>

const int PINO_DHT = 15;
const int PINO_LDR = 34;
const int PINO_RELE = 19;
const int PINO_N = 25;
const int PINO_P = 26;
const int PINO_K = 27;

const float PH_MINIMO = 5.5f;
const float PH_MAXIMO = 7.0f;
const float UMIDADE_LIGAR = 55.0f;
const float UMIDADE_DESLIGAR = 65.0f;
const unsigned long INTERVALO_LEITURA_MS = 2000UL;

DHTesp dhtSensor;

bool previsaoChuva = false;
bool bombaLigada = false;
unsigned long ultimaLeituraMs = 0;
String bufferSerial;

struct LeituraSolo {
  bool nitrogenioOk;
  bool fosforoOk;
  bool potassioOk;
  float umidadeSolo;
  float temperatura;
  int ldrBruto;
  float ph;
  bool leituraValida;
};

float limitar(float valor, float minimo, float maximo) {
  if (valor < minimo) {
    return minimo;
  }
  if (valor > maximo) {
    return maximo;
  }
  return valor;
}

float converterLdrParaPh(int leituraLdr) {
  float normalizado = 1.0f - (static_cast<float>(leituraLdr) / 4095.0f);
  return limitar(14.0f * normalizado, 0.0f, 14.0f);
}

String statusNutriente(bool ok) {
  return ok ? "OK" : "BAIXO";
}

LeituraSolo lerSensores() {
  TempAndHumidity dadosDht = dhtSensor.getTempAndHumidity();

  LeituraSolo leitura;
  leitura.nitrogenioOk = digitalRead(PINO_N) == LOW;
  leitura.fosforoOk = digitalRead(PINO_P) == LOW;
  leitura.potassioOk = digitalRead(PINO_K) == LOW;
  leitura.temperatura = dadosDht.temperature;
  leitura.umidadeSolo = dadosDht.humidity;
  leitura.leituraValida = !isnan(dadosDht.temperature) && !isnan(dadosDht.humidity);
  leitura.ldrBruto = analogRead(PINO_LDR);
  leitura.ph = converterLdrParaPh(leitura.ldrBruto);

  return leitura;
}

void aplicarEstadoBomba(bool ligar) {
  digitalWrite(PINO_RELE, ligar ? HIGH : LOW);
  bombaLigada = ligar;
}

String avaliarIrrigacao(const LeituraSolo &leitura, bool &ligar) {
  if (!leitura.leituraValida) {
    ligar = false;
    return "Falha na leitura do DHT22";
  }

  if (previsaoChuva) {
    ligar = false;
    return "Previsao de chuva ativa via Serial";
  }

  if (!leitura.nitrogenioOk || !leitura.fosforoOk || !leitura.potassioOk) {
    ligar = false;
    return "NPK fora do padrao escolhido para o milho";
  }

  if (leitura.ph < PH_MINIMO) {
    ligar = false;
    return "pH abaixo da faixa ideal do milho";
  }

  if (leitura.ph > PH_MAXIMO) {
    ligar = false;
    return "pH acima da faixa ideal do milho";
  }

  if (leitura.umidadeSolo <= UMIDADE_LIGAR) {
    ligar = true;
    return "Solo seco na simulacao e condicoes adequadas";
  }

  if (leitura.umidadeSolo >= UMIDADE_DESLIGAR) {
    ligar = false;
    return "Umidade simulada recuperada";
  }

  ligar = bombaLigada;
  return bombaLigada ? "Histerese: mantendo irrigacao ligada" : "Histerese: mantendo irrigacao desligada";
}

void imprimirStatus(const LeituraSolo &leitura, const String &motivo) {
  Serial.println();
  Serial.println("=== FarmTech Solutions | Fase 2 ===");
  Serial.println("Cultura escolhida: milho");
  Serial.println("N=" + statusNutriente(leitura.nitrogenioOk) +
                 " | P=" + statusNutriente(leitura.fosforoOk) +
                 " | K=" + statusNutriente(leitura.potassioOk));

  if (leitura.leituraValida) {
    Serial.println("Umidade do solo (simulada no DHT22): " + String(leitura.umidadeSolo, 1) + "%");
    Serial.println("Temperatura lida no DHT22: " + String(leitura.temperatura, 1) + "C");
  } else {
    Serial.println("Leitura do DHT22 invalida");
  }

  Serial.println("LDR bruto: " + String(leitura.ldrBruto));
  Serial.println("pH simulado: " + String(leitura.ph, 2));
  Serial.println("Previsao de chuva: " + String(previsaoChuva ? "SIM" : "NAO"));
  Serial.println("Bomba: " + String(bombaLigada ? "LIGADA" : "DESLIGADA"));
  Serial.println("Motivo: " + motivo);
  Serial.println("Comandos: CHUVA=1 | CHUVA=0 | STATUS | AJUDA");
}

void processarComandoSerial(String comando) {
  comando.trim();
  comando.toUpperCase();

  if (comando.length() == 0) {
    return;
  }

  if (comando == "CHUVA=1") {
    previsaoChuva = true;
    Serial.println("Previsao de chuva ativada. A irrigacao sera bloqueada.");
    return;
  }

  if (comando == "CHUVA=0") {
    previsaoChuva = false;
    Serial.println("Previsao de chuva desativada. A irrigacao volta ao modo automatico.");
    return;
  }

  if (comando == "AJUDA") {
    Serial.println("Use CHUVA=1, CHUVA=0, STATUS ou AJUDA.");
    return;
  }

  if (comando == "STATUS") {
    ultimaLeituraMs = 0;
    return;
  }

  Serial.println("Comando nao reconhecido. Use AJUDA para ver as opcoes.");
}

void lerSerial() {
  while (Serial.available() > 0) {
    char caractere = static_cast<char>(Serial.read());

    if (caractere == '\n' || caractere == '\r') {
      if (bufferSerial.length() > 0) {
        processarComandoSerial(bufferSerial);
        bufferSerial = "";
      }
      continue;
    }

    bufferSerial += caractere;
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  pinMode(PINO_N, INPUT_PULLUP);
  pinMode(PINO_P, INPUT_PULLUP);
  pinMode(PINO_K, INPUT_PULLUP);
  pinMode(PINO_RELE, OUTPUT);

  dhtSensor.setup(PINO_DHT, DHTesp::DHT22);
  aplicarEstadoBomba(false);

  Serial.println("Sistema de irrigacao inteligente iniciado.");
  Serial.println("Ajuste N, P, K, LDR (pH) e umidade do DHT22.");
  Serial.println("Para previsao de chuva, envie CHUVA=1 ou CHUVA=0 no Serial Monitor.");
}

void loop() {
  lerSerial();

  unsigned long agora = millis();
  if (agora - ultimaLeituraMs < INTERVALO_LEITURA_MS) {
    delay(20);
    return;
  }

  ultimaLeituraMs = agora;

  LeituraSolo leitura = lerSensores();
  bool ligarBomba = false;
  String motivo = avaliarIrrigacao(leitura, ligarBomba);

  aplicarEstadoBomba(ligarBomba);
  imprimirStatus(leitura, motivo);
}
