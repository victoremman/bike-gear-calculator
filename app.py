from flask import Flask, render_template, request, jsonify
import math
import os
from geopy.distance import great_circle
from datetime import datetime

app = Flask(__name__)

# Configurações fixas
CRANKSET = [28, 38, 48]
FREEWHEEL = [34, 24, 22, 20, 18, 16, 14]
TARGET_CADENCE = 80  # RPM padrão

# Variáveis para armazenamento de posições
positions = []


def calcular_melhor_marcha(velocidade, aro, cadencia):
    try:
        velocidade_alvo = (velocidade / 3.6) * (60 / cadencia)
        aro_metros = aro * 0.0254
        circunferencia_roda = aro_metros * math.pi

        melhor_marcha = min(
            [(c, f, (c / f) * circunferencia_roda) for c in CRANKSET for f in FREEWHEEL],
            key=lambda x: abs(x[2] - velocidade_alvo))

        return {
            'marcha': f"{melhor_marcha[0]}/{melhor_marcha[1]}",
            'velocidade_atingida': f"{(melhor_marcha[2] * cadencia * 3.6) / 60:.1f} km/h"
        }
    except Exception as e:
        return {'erro': str(e)}


@app.route('/auto', methods=['POST'])
def modo_automatico():
    try:
        data = request.json
        aro = int(data['aro'])

        # Cálculo de velocidade via GPS
        global positions
        if len(positions) >= 2:
            distancia = great_circle(
                (positions[-2]['lat'], positions[-2]['lon']),
                (positions[-1]['lat'], positions[-1]['lon'])
            ).km

            tempo = (positions[-1]['timestamp'] - positions[-2]['timestamp'])
            velocidade = (distancia / tempo) * 3600 if tempo > 0 else 0
        else:
            velocidade = 0

        resultado = calcular_melhor_marcha(velocidade, aro, TARGET_CADENCE)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({'erro': str(e)})


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            dados = {
                'velocidade': float(request.form['velocidade']),
                'aro': int(request.form['aro']),
                'cadencia': float(request.form['cadencia'])
            }
            resultado = calcular_melhor_marcha(**dados)
            return render_template('index.html', resultado=resultado)

        except Exception as e:
            return render_template('index.html', erro=f"Erro: {str(e)}")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
