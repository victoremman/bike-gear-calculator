from flask import Flask, render_template, request
import math
import os

app = Flask(__name__)

# Configurações fixas
CRANKSET = [28, 38, 48]
FREEWHEEL = [34, 24, 22, 20, 18, 16, 14]

def calcular_melhor_marcha(velocidade, aro, cadencia):
    try:
        velocidade_alvo = velocidade / 3.6  # km/h para m/s
        velocidade_alvo = velocidade_alvo * 60 / cadencia  # m/rev
        
        aro_metros = aro * 0.0254  # polegadas para metros
        circunferencia_roda = aro_metros * math.pi
        
        lista_marchas = []
        for coroa in CRANKSET:
            for catraca in FREEWHEEL:
                razao = round(coroa / catraca, 2)
                lista_marchas.append((coroa, catraca, razao))
        
        lista_velocidades = [
            (marcha[0], marcha[1], round(marcha[2] * circunferencia_roda, 2))
            for marcha in lista_marchas
        ]
        
        melhor_marcha = min(lista_velocidades, 
                          key=lambda x: abs(x[2] - velocidade_alvo))
        
        return {
            'melhor_marcha': f"{melhor_marcha[0]}/{melhor_marcha[1]}",
            'velocidade_atingida': f"{melhor_marcha[2] * cadencia * 3.6 / 60:.1f} km/h"
        }
    
    except Exception as e:
        return {'erro': str(e)}

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
            return render_template('index.html', 
                                 erro=f"Erro nos dados: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
2. requirements.txt
