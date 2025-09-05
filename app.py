from flask import Flask, request, render_template, send_file
from weasyprint import HTML
import os
from datetime import datetime
import re

app = Flask(__name__)

def escape_html(text):
    """Escape HTML special characters to prevent injection."""
    if not text:
        return text
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

@app.route('/', methods=['GET', 'POST'])
def orcamento():
    if request.method == 'POST':
        # Get form data
        nome_cliente = escape_html(request.form.get('nomeCliente'))
        cpf_cnpj = escape_html(request.form.get('cpfCnpjCliente'))
        descricao_servico = escape_html(request.form.get('descricaoServico'))
        observacoes = escape_html(request.form.get('observacoes'))
        valor_total = request.form.get('valorTotal')

        # Validate form inputs
        if not nome_cliente or not descricao_servico or not valor_total:
            return "Por favor, preencha todos os campos obrigatórios.", 400

        try:
            valor_total = float(valor_total)
            if valor_total <= 0:
                return "O valor total deve ser maior que zero.", 400
        except ValueError:
            return "O valor total deve ser um número válido.", 400

        # Validate CPF/CNPJ
        if cpf_cnpj:
            cpf_cnpj_clean = re.sub(r'[^\d]', '', cpf_cnpj)
            if not re.match(r'^(\d{11}|\d{14})$', cpf_cnpj_clean):
                return "Por favor, insira um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.", 400

        # Calculate payment options
        valor_a_vista = f"{valor_total:.2f}"
        taxa_cartao = 0.05  # 5% fee
        valor_cartao = f"{valor_total * (1 + taxa_cartao):.2f}"

        # Get current date
        today = datetime.now().strftime('%d/%m/%Y')

        # Render HTML template for PDF
        html_content = render_template(
            'index.html',
            nome_cliente=nome_cliente,
            cpf_cnpj=cpf_cnpj or "Não informado",
            descricao_servico=descricao_servico,
            observacoes=observacoes or "Nenhuma observação fornecida.",
            valor_a_vista=valor_a_vista,
            valor_cartao=valor_cartao,
            today=today,
            pdf_mode=True
        )

        # Generate PDF
        pdf_path = f"orcamento_{nome_cliente}_{today.replace('/', '-')}.pdf"
        HTML(string=html_content, base_url=os.path.dirname(__file__)).write_pdf(pdf_path)

        # Send PDF as download
        return send_file(pdf_path, as_attachment=True)

    # Render form for GET request
    return render_template('index.html', pdf_mode=False)

if __name__ == '__main__':
    app.run(debug=True)
