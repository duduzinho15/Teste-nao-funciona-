# modelo_ia_apostapro.py
import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import json
import joblib
import os

def treinar_modelo(db_path="aposta.db", tabela="jogos_historicos", modelo_path="modelo_rf.pkl", scaler_path="scaler.pkl"):
    """Treina um modelo RandomForest para previsão de resultados de jogos."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
    conn.close()

    # Processamento de dados
    df["placar_casa"] = df["placar_casa"].fillna(0)
    df["placar_fora"] = df["placar_fora"].fillna(0)

    # Adicionar coluna de resultado
    def classificar_resultado(row):
        if row["placar_casa"] > row["placar_fora"]:
            return "casa"
        elif row["placar_casa"] < row["placar_fora"]:
            return "fora"
        else:
            return "empate"
    df["resultado"] = df.apply(classificar_resultado, axis=1)

    # Extrair estatísticas
    estatisticas = []
    for estat in df["estatisticas"]:
        if estat:
            try:
                estatisticas.append(json.loads(estat))
            except Exception:
                estatisticas.append({})
        else:
            estatisticas.append({})
    estat_df = pd.DataFrame(estatisticas)
    df = pd.concat([df, estat_df], axis=1)

    # Selecionar características
    features = ["posse_casa", "posse_fora", "chutes_casa", "chutes_fora", "escanteios_casa", "escanteios_fora"]
    # Garante que todas as features existem
    for col in features:
        if col not in df.columns:
            df[col] = 0
    X = df[features].fillna(0)
    y = df["resultado"]

    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalização
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Treinar modelo
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    # Avaliação detalhada
    y_pred = modelo.predict(X_test)
    print(f"Acurácia: {modelo.score(X_test, y_test):.2%}")
    print("Matriz de confusão:")
    print(confusion_matrix(y_test, y_pred))
    print("Classification report:")
    print(classification_report(y_test, y_pred))

    # Salvar modelo e scaler
    joblib.dump(modelo, modelo_path)
    joblib.dump(scaler, scaler_path)
    print(f"Modelo salvo em {os.path.abspath(modelo_path)}")
    print(f"Scaler salvo em {os.path.abspath(scaler_path)}")

    return modelo, scaler

if __name__ == "__main__":
    modelo, scaler = treinar_modelo()