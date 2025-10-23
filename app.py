from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Necessário para flash e sessão

# 🔹 Configuração do banco MySQL (Railway)
DB_CONFIG = {
    "host": "mysql.railway.internal",
    "user": "root",
    "password": "IXwRMRfyWbNiQWXIeGomwHymWXgLvTBB",
    "database": "railway",
    "port": 3306
}

# 🔹 Função para conectar ao banco MySQL
def conectar():
    return mysql.connector.connect(**DB_CONFIG)

# ======================== LOGIN ========================
@app.route('/', methods=["GET", "POST"])
def pg_login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s AND senha = %s", (email, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            session["matricula"] = usuario[4]  # matrícula na sessão
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("pg_inicial"))
        else:
            flash("Email ou senha incorretos.", "error")
            return redirect(url_for("pg_login"))

    return render_template('pg_login.html')


# ======================== CADASTRO ========================
@app.route("/pg_cadastro", methods=["GET", "POST"])
def pg_cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        cpf = request.form["cpf"]
        email = request.form["email"]
        matricula = request.form["matricula"]
        jornada = request.form["jornada"]
        senha = request.form["senha"]
        confirm_senha = request.form["confirm_senha"]

        if senha != confirm_senha:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("pg_cadastro"))

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user (nome, cpf, email, matricula, jornada, senha)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, cpf, email, matricula, jornada, senha))
            conn.commit()
            conn.close()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("pg_login"))
        except mysql.connector.IntegrityError:
            flash("Email, CPF ou matrícula já cadastrado.", "error")
            return redirect(url_for("pg_cadastro"))

    return render_template("pg_cadastro.html")


# ======================== PÁGINAS INICIAIS ========================
@app.route("/pg_inicial")
def pg_inicial():
    return render_template("pg_inicial.html")

@app.route("/pg_senha")
def pg_senha():
    return render_template("pg_senha.html")


# ======================== BATIDA DE PONTO ========================
@app.route("/pg_mrc_ponto", methods=["GET", "POST"])
def pg_mrc_ponto():
    matricula = session.get("matricula")
    if not matricula:
        return redirect(url_for("pg_login"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, jornada FROM user WHERE matricula = %s", (matricula,))
    usuario = cursor.fetchone()

    if not usuario:
        flash("Usuário não encontrado.", "error")
        conn.close()
        return redirect(url_for("pg_login"))

    nome, jornada = usuario
    agora = datetime.now()

    cursor.execute("SELECT * FROM pontos WHERE matricula = %s AND data = %s ORDER BY id",
                   (matricula, agora.date()))
    pontos_hoje = cursor.fetchall()

    if request.method == "POST":
        entradas = [p for p in pontos_hoje if p[4] == "entrada"]
        saidas = [p for p in pontos_hoje if p[4] == "saida"]
        horas_total = sum(
            (datetime.strptime(s[3], "%H:%M") - datetime.strptime(e[3], "%H:%M")).seconds / 3600
            for e, s in zip(entradas, saidas)
        )
        ultimo = pontos_hoje[-1] if pontos_hoje else None

        if jornada.lower() == "horista":
            if len(entradas) > len(saidas):
                if horas_total >= 10:
                    flash("Horista já atingiu 10h hoje!", "error")
                else:
                    cursor.execute(
                        "INSERT INTO pontos (matricula, data, hora, tipo) VALUES (%s, %s, %s, %s)",
                        (matricula, agora.date(), agora.strftime("%H:%M"), "saida")
                    )
                    conn.commit()
                    flash("Saída registrada!", "success")
            else:
                if horas_total >= 10:
                    flash("Horista não pode iniciar novo expediente hoje.", "error")
                else:
                    cursor.execute(
                        "INSERT INTO pontos (matricula, data, hora, tipo) VALUES (%s, %s, %s, %s)",
                        (matricula, agora.date(), agora.strftime("%H:%M"), "entrada")
                    )
                    conn.commit()
                    flash("Entrada registrada!", "success")

        elif jornada.lower() == "mensalista":
            if not ultimo:
                cursor.execute(
                    "INSERT INTO pontos (matricula, data, hora, tipo) VALUES (%s, %s, %s, %s)",
                    (matricula, agora.date(), agora.strftime("%H:%M"), "entrada")
                )
                conn.commit()
                flash("Entrada registrada!", "success")
            elif ultimo[4] == "entrada":
                cursor.execute(
                    "INSERT INTO pontos (matricula, data, hora, tipo) VALUES (%s, %s, %s, %s)",
                    (matricula, agora.date(), agora.strftime("%H:%M"), "intervalo_inicio")
                )
                conn.commit()
                flash("Início do intervalo registrado!", "success")
            elif ultimo[4] == "intervalo_inicio":
                cursor.execute(
                    "INSERT INTO pontos (matricula, data, hora, tipo) VALUES (%s, %s, %s, %s)",
                    (matricula, agora.date(), agora.strftime("%H:%M"), "intervalo_fim")
                )
                conn.commit()
                flash("Fim do intervalo registrado!", "success")
            elif ultimo[4] in ["intervalo_fim", "saida"]:
                if horas_total >= 10:
                    flash("Mensalista não pode ultrapassar 2h extras (10h no total).", "error")
                else:
                    cursor.execute(
                        "INSERT INTO pontos (matricula, data, hora, tipo) VALUES (%s, %s, %s, %s)",
                        (matricula, agora.date(), agora.strftime("%H:%M"), "saida")
                    )
                    conn.commit()
                    flash("Saída registrada!", "success")

    cursor.execute("SELECT * FROM pontos WHERE matricula = %s AND data = %s ORDER BY id", (matricula, agora.date()))
    pontos_hoje = cursor.fetchall()
    conn.close()

    return render_template("pg_mrc_ponto.html", nome=nome, jornada=jornada, pontos=pontos_hoje)


# ======================== PONTOS MENSAIS ========================
@app.route("/pg_pontos_mensais")
def pg_pontos_mensais():
    matricula = session.get("matricula")
    if not matricula:
        return redirect(url_for("pg_login"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT DATE_FORMAT(data, '%%Y-%%m') AS mes
        FROM pontos
        WHERE matricula = %s
        ORDER BY mes DESC
    """, (matricula,))
    meses = [row[0] for row in cursor.fetchall()]
    conn.close()

    return render_template("pg_pontos_mensais.html", meses=meses)


@app.route("/pg_pontos_mensais/<mes>")
def pontos_mes(mes):
    matricula = session.get("matricula")
    if not matricula:
        return redirect(url_for("pg_login"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT DATE_FORMAT(data, '%%Y-%%m-%%d') AS dia
        FROM pontos
        WHERE matricula = %s AND DATE_FORMAT(data, '%%Y-%%m') = %s
        ORDER BY dia
    """, (matricula, mes))
    dias = [row[0] for row in cursor.fetchall()]
    conn.close()

    return render_template("pg_pontos_dias.html", mes=mes, dias=dias)


@app.route("/pg_pontos_mensais/<mes>/<dia>")
def pontos_dia(mes, dia):
    matricula = session.get("matricula")
    if not matricula:
        return redirect(url_for("pg_login"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hora, tipo
        FROM pontos
        WHERE matricula = %s AND data = %s
        ORDER BY id
    """, (matricula, dia))
    pontos = cursor.fetchall()
    conn.close()

    return render_template("pg_pontos_dia.html", dia=dia, pontos=pontos)


# ======================== LEMBRETES ========================
@app.route("/pg_lembrete", methods=["GET", "POST"])
def pg_lembrete():
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form.get("name")
        data = request.form.get("data")
        hora = request.form.get("hora")
        if nome and data and hora:
            cursor.execute(
                "INSERT INTO lembretes (name, data, hora) VALUES (%s, %s, %s)",
                (nome, data, hora)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("pg_lembrete"))

    cursor.execute("SELECT id, name, data, hora FROM lembretes ORDER BY data, hora")
    lembretes = cursor.fetchall()
    conn.close()

    return render_template("pg_lembrete.html", lembretes=lembretes)


# ======================== JUSTIFICATIVAS ========================
@app.route("/pg_justificativa", methods=["GET", "POST"])
def pg_justificativa():
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        nome = request.form["nome"]
        data = request.form["data"]
        motivo = request.form["motivo"]
        cursor.execute("INSERT INTO justificativas (nome, data, motivo) VALUES (%s, %s, %s)",
                       (nome, data, motivo))
        conn.commit()
        flash("✅ Sua justificativa foi enviada com sucesso!")
        return redirect(url_for("pg_justificativa"))
    conn.close()
    return render_template("pg_justificativa.html")


# ======================== DADOS PESSOAIS ========================
@app.route("/pg_dados_pessoais", methods=["GET", "POST"])
def pg_dados_pessoais():
    matricula = session.get("matricula")
    if not matricula:
        return redirect(url_for("pg_login"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT telefone, endereco, nascimento, genero FROM user_complemento WHERE matricula = %s", (matricula,))
    dados = cursor.fetchone()

    if request.method == "POST":
        telefone = request.form.get("telefone")
        endereco = request.form.get("endereco")
        nascimento = request.form.get("nascimento")
        genero = request.form.get("genero")

        if dados:
            cursor.execute("""
                UPDATE user_complemento
                SET telefone=%s, endereco=%s, nascimento=%s, genero=%s
                WHERE matricula=%s
            """, (telefone, endereco, nascimento, genero, matricula))
            flash("Dados atualizados com sucesso!", "success")
        else:
            cursor.execute("""
                INSERT INTO user_complemento (matricula, telefone, endereco, nascimento, genero)
                VALUES (%s, %s, %s, %s, %s)
            """, (matricula, telefone, endereco, nascimento, genero))
            flash("Dados cadastrados com sucesso!", "success")

        conn.commit()
        conn.close()
        return redirect(url_for("pg_dados_pessoais"))

    conn.close()
    return render_template("pg_dados_pessoais.html", dados=dados)


# ======================== SUPORTE ========================
@app.route("/pg_suporte", methods=["GET", "POST"])
def pg_suporte():
    if request.method == "POST":
        nome = request.form.get("nome")
        matricula = request.form.get("matricula")
        email = request.form.get("email")
        assunto = request.form.get("assunto")
        descricao = request.form.get("descricao")

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suporte (nome, matricula, email, assunto, descricao)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, matricula, email, assunto, descricao))
            conn.commit()
            conn.close()
            flash("Solicitação de suporte enviada com sucesso!", "success")
            return redirect(url_for("pg_suporte"))
        except mysql.connector.Error as e:
            flash(f"Erro ao enviar suporte: {str(e)}", "error")
            return redirect(url_for("pg_suporte"))

    return render_template("pg_suporte.html")


if __name__ == '__main__':
    app.run(debug=True)
