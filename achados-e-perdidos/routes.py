#Definir as Rotas do site
import os
import uuid
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from manager import app, db, bcrypt
from models import Usuario, Foto
from forms import FormLogin, FormCriarConta, FormPostagem

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        perfil = request.form.get("perfil")
        if perfil == "aluno":
            return redirect(url_for("feed"))
        elif perfil == "admin":
            if current_user.is_authenticated and current_user.tipo == "admin":
                return redirect(url_for("admin_feed"))
            return redirect(url_for("login"))
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = FormLogin()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario)
            flash("Login realizado.", "dark")
            return redirect(
                url_for("admin_feed") if usuario.tipo == "admin" else url_for("feed")
            )
        flash("Credenciais inválidas.", "primary")
    return render_template("login.html", form=form)

@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form = FormCriarConta()
    if form.validate_on_submit():
        senha_hash = bcrypt.generate_password_hash(form.senha.data).decode("utf-8")
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            senha=senha_hash,
            tipo="admin",
        )
        db.session.add(usuario)
        db.session.commit()
        flash("Conta criada com sucesso.", "dark")
        return redirect(url_for("login"))
    return render_template("create_account.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sessão.", "dark")
    return redirect(url_for("login"))


@app.route("/feed")
def feed():
    fotos = Foto.query.order_by(Foto.data_postagem.desc()).all()
    return render_template("feed.html", fotos=fotos)


@app.route("/admin/feed")
@login_required
def admin_feed():
    if current_user.tipo != "admin":
        flash("Acesso negado.", "danger")
        return redirect(url_for("feed"))
    fotos = Foto.query.order_by(Foto.data_postagem.desc()).all()
    return render_template("admin_feed.html", fotos=fotos)


@app.route("/admin/add", methods=["GET", "POST"])
@login_required
def adicionar_item():
    if current_user.tipo != "admin":
        flash("Acesso negado.", "danger")
        return redirect(url_for("feed"))

    form = FormPostagem()
    if form.validate_on_submit():
        arquivo = request.files.get("imagem")
        if not arquivo or arquivo.filename == "":
            flash("Selecione uma imagem para o item.", "warning")
            return redirect(request.url)
        if not allowed_file(arquivo.filename):
            flash("Formato de imagem não permitido.", "danger")
            return redirect(request.url)

        nome_seguro = secure_filename(arquivo.filename)
        nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
        caminho = os.path.join(UPLOAD_FOLDER, nome_unico)
        arquivo.save(caminho)

        foto = Foto(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            caminho_imagem=f"uploads/{nome_unico}",
            usuario_id=current_user.id,
        )
        db.session.add(foto)
        db.session.commit()
        flash("Item adicionado.", "dark")
        return redirect(url_for("admin_feed"))

    return render_template("post_item.html", form=form)


@app.route("/admin/editar/<int:item_id>", methods=["GET", "POST"])
@login_required
def editar_item(item_id):
    foto = Foto.query.get_or_404(item_id)
    if current_user.tipo != "admin":
        flash("Acesso negado.", "danger")
        return redirect(url_for("feed"))

    if request.method == "POST":
        foto.titulo = request.form.get("titulo", foto.titulo)[:120]
        foto.descricao = request.form.get("descricao", foto.descricao)
        foto.local = request.form.get("local", foto.local)
        foto.data_item = request.form.get("data_item", foto.data_item)
        arquivo = request.files.get("imagem")
        if arquivo and arquivo.filename != "":
            if not allowed_file(arquivo.filename):
                flash("Formato de imagem não permitido.", "danger")
                return redirect(request.url)
            nome_seguro = secure_filename(arquivo.filename)
            nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
            caminho = os.path.join(UPLOAD_FOLDER, nome_unico)
            arquivo.save(caminho)
            try:
                antigo = os.path.join(app.root_path, "static", foto.caminho_imagem)
                if os.path.exists(antigo):
                    os.remove(antigo)
            except Exception:
                pass
            foto.caminho_imagem = f"uploads/{nome_unico}"

        db.session.commit()
        flash("Item atualizado.", "success")
        return redirect(url_for("admin_feed"))

    return render_template("edit_item.html", foto=foto)


@app.route("/admin/remover/<int:item_id>")
@login_required
def remover_item(item_id):
    foto = Foto.query.get_or_404(item_id)
    if current_user.tipo != "admin":
        flash("Acesso negado.", "danger")
        return redirect(url_for("feed"))

    try:
        caminho_f = os.path.join(app.root_path, "static", foto.caminho_imagem)
        if os.path.exists(caminho_f):
            os.remove(caminho_f)
    except Exception:
        pass

    db.session.delete(foto)
    db.session.commit()
    flash("Item removido.", "dark")
    return redirect(url_for("admin_feed"))


@app.route("/perfil/<int:usuario_id>")
@login_required
def perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template("perfil.html", usuario=usuario)
