# Definir os Formulários do site
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import Usuario


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Fazer Login")


class FormCriarConta(FlaskForm):
    username = StringField(
        "Usuário", validators=[DataRequired(), Length(min=3, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6, max=12)])
    confirmar_senha = PasswordField(
        "Confirmar senha", validators=[DataRequired(), EqualTo("senha")]
    )
    submit = SubmitField("Criar conta")

    def validate_username(self, username):
        usuario = Usuario.query.filter_by(username=username.data).first()
        if usuario:
            raise ValidationError("Nome de usuário já cadastrado.")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado.")


class FormPostagem(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=120)])
    descricao = TextAreaField("Descrição", validators=[Length(max=1000)])
    imagem = FileField("Imagem", validators=[DataRequired()])
    submit = SubmitField("Postar")
