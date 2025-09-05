from flask import Flask, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
import datetime

app = Flask(__name__)

# Dados fixos da empresa do seu PDF de exemplo
dados_empresa = {
    "nome": "Nilton Nascimento Móveis Planejados",
    "cnpj": "13.744.549/0001-32",
    "endereco": "Rua Salvador Pratta, n° 460",
    "telefone": "(19) 9 8316-1919",
    "email": "niltonjoiner@hotmail.com",
    "pix": "13.744.549/0001-32"
}

@app.route('/gerar-orcamento', methods=['POST'])
def gerar_orcamento():
    data = request.json
    nome_cliente = data.get('nomeCliente')
    cpf_cnpj_cliente = data.get('cpfCnpjCliente')
    descricao_servico = data.get('descricaoServico')
    valor_total = float(data.get('valorTotal'))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Estilos de texto
    styles.add(ParagraphStyle(name='Header', fontSize=12, leading=14, alignment=1))
    styles.add(ParagraphStyle(name='Body', fontSize=10, leading=12))

    # Dados da empresa (cabeçalho)
    story.append(Paragraph(dados_empresa["nome"], styles['Header']))
    story.append(Paragraph(f'CNPJ: {dados_empresa["cnpj"]}', styles['Header']))
    story.append(Paragraph(dados_empresa["endereco"], styles['Header']))
    story.append(Paragraph(dados_empresa["telefone"], styles['Header']))
    story.append(Paragraph(dados_empresa["email"], styles['Header']))
    story.append(Spacer(1, 1*cm))

    # Título do documento
    story.append(Paragraph("<b>ORÇAMENTO</b>", styles['Header']))
    story.append(Spacer(1, 0.5*cm))

    # Data
    data_hoje = datetime.datetime.now().strftime("%d/%m/%Y")
    story.append(Paragraph(f'<b>Data:</b> {data_hoje}', styles['Body']))
    story.append(Paragraph('Orçamento válido por 7 dias.', styles['Body']))
    story.append(Spacer(1, 0.5*cm))

    # Dados do cliente
    story.append(Paragraph('<b>CLIENTE:</b>', styles['Body']))
    story.append(Paragraph(f'<b>NOME:</b> {nome_cliente}', styles['Body']))
    story.append(Paragraph(f'<b>CPF/CNPJ:</b> {cpf_cnpj_cliente if cpf_cnpj_cliente else "N/A"}', styles['Body']))
    story.append(Spacer(1, 0.5*cm))

    # Descrição do serviço
    story.append(Paragraph('<b>DESCRIÇÃO:</b>', styles['Body']))
    story.append(Paragraph(descricao_servico, styles['Body']))
    story.append(Spacer(1, 1*cm))

    # Tabela de formas de pagamento
    valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    tabela_pagamento = [
        ['À VISTA', 'ENTRADA + RESTANTE', 'CARTÃO'],
        [f'Com desconto incluso\n{valor_formatado}', f'50% de entrada\n• 50% na entrega.\n{valor_formatado}', 'Com taxa à incluir\nEm até 12x']
    ]
    
    style_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ])

    table = Table(tabela_pagamento, colWidths=[6*cm, 6*cm, 6*cm])
    table.setStyle(style_tabela)
    story.append(Paragraph('<b>FORMAS DE PAGAMENTO</b>', styles['Body']))
    story.append(Spacer(1, 0.2*cm))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    # Chave Pix
    story.append(Paragraph(f'<b>Chave Pix:</b> {dados_empresa["pix"]}', styles['Body']))

    doc.build(story)
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='orcamento.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)