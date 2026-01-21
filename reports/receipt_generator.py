from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import re

def number_to_words(value):
    """Converte número para extenso em português (versão simplificada)"""
    if value == 0:
        return "zero reais"
    
    reais = int(value)
    centavos = int(round((value - reais) * 100))
    
    # Listas de números
    unidades = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
    especiais = ["dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
    dezenas = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
    centenas = ["", "cem", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]
    
    def convert_number(num):
        """Converte um número inteiro para extenso"""
        if num == 0:
            return ""
        if num < 10:
            return unidades[num]
        elif num < 20:
            return especiais[num - 10]
        elif num < 100:
            dezena = num // 10
            unidade = num % 10
            if unidade == 0:
                return dezenas[dezena]
            else:
                return f"{dezenas[dezena]} e {unidades[unidade]}"
        elif num < 1000:
            centena = num // 100
            resto = num % 100
            if resto == 0:
                return centenas[centena]
            elif centena == 1:
                return f"cento e {convert_number(resto)}"
            else:
                return f"{centenas[centena]} e {convert_number(resto)}"
        else:
            # Para valores maiores, usar formato numérico
            return str(num)
    
    reais_text = convert_number(reais) if reais > 0 else ""
    centavos_text = convert_number(centavos) if centavos > 0 else ""
    
    # Montar resultado
    if reais > 0 and centavos > 0:
        return f"{reais_text} reais e {centavos_text} centavos"
    elif reais > 0:
        return f"{reais_text} reais"
    elif centavos > 0:
        return f"{centavos_text} centavos"
    else:
        return "zero reais"

def generate_receipt_pdf(client_name, client_data, order, output_path, company_data=None):
    """Gera um comprovante de pagamento em PDF"""
    
    # Informações da empresa (usar dados salvos ou padrão)
    if company_data:
        company_name = company_data.get("name", "Cantina Colégio Ativa")
        company_address = company_data.get("address", "Endereço da Cantina")
        company_cnpj = company_data.get("cnpj", "")
        company_phone = company_data.get("phone", "")
    else:
        company_name = "Cantina Colégio Ativa"
        company_address = "Endereço da Cantina"
        company_cnpj = ""
        company_phone = ""
    
    # Formatar CNPJ e telefone se existirem
    if company_cnpj:
        # Se CNPJ estiver apenas com números, formatar
        cnpj_clean = re.sub(r'\D', '', str(company_cnpj))
        if len(cnpj_clean) == 14:
            # Formatar: XX.XXX.XXX/XXXX-XX
            formatted_cnpj = f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
            company_cnpj = f"CNPJ: {formatted_cnpj}"
        else:
            company_cnpj = f"CNPJ: {company_cnpj}"
    else:
        company_cnpj = "CNPJ: Não informado"
    
    if company_phone:
        company_phone = f"Telefone: {company_phone}"
    else:
        company_phone = "Telefone: Não informado"
    
    # Criar documento PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#000000'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para labels
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#000000'),
        fontName='Helvetica-Bold',
        spaceAfter=2
    )
    
    # Estilo para valores
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#000000'),
        fontName='Helvetica',
        spaceAfter=8
    )
    
    # Conteúdo do PDF
    story = []
    
    # Cabeçalho - Nome da empresa
    story.append(Paragraph(company_name, title_style))
    story.append(Spacer(1, 5*mm))
    
    # Informações da empresa
    story.append(Paragraph(company_address, value_style))
    story.append(Paragraph(company_cnpj, value_style))
    story.append(Paragraph(company_phone, value_style))
    story.append(Spacer(1, 5*mm))
    
    # Linha separadora
    story.append(Paragraph("_" * 80, value_style))
    story.append(Spacer(1, 5*mm))
    
    # Título do comprovante
    receipt_title = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#000000'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("COMPROVANTE DE PAGAMENTO", receipt_title))
    story.append(Spacer(1, 5*mm))
    
    # Linha separadora
    story.append(Paragraph("_" * 80, value_style))
    story.append(Spacer(1, 5*mm))
    
    # Informações do cliente
    story.append(Paragraph("NOME: " + client_name, label_style))
    if client_data:
        cpf = client_data.get("cpf", "Não informado")
        matricula = client_data.get("matricula", "Não informado")
        if cpf != "Não informado":
            story.append(Paragraph(f"CPF: {cpf}", value_style))
        if matricula != "Não informado":
            story.append(Paragraph(f"ALUNO: {client_name}", label_style))
            story.append(Paragraph(f"Nº MATRÍCULA: {matricula}", value_style))
    
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("_" * 80, value_style))
    story.append(Spacer(1, 5*mm))
    
    # Detalhes do pagamento
    payment_method = order.get("payment_method", "Não especificado")
    payment_date = datetime.now().strftime("%d/%m/%Y")
    payment_time = datetime.now().strftime("%H:%M:%S")
    total = order.get("total", 0.0)
    
    story.append(Paragraph(f"VALOR PAGO: R$ {total:.2f} ({number_to_words(total)})", label_style))
    story.append(Paragraph(f"DATA DE PAGAMENTO: {payment_date}", value_style))
    story.append(Paragraph(f"FORMA DE PAGAMENTO: {payment_method} (R$ {total:.2f})", value_style))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("_" * 80, value_style))
    story.append(Spacer(1, 5*mm))
    
    # Itens da venda
    story.append(Paragraph("ITENS DA VENDA:", label_style))
    story.append(Spacer(1, 2*mm))
    
    # Tabela de itens
    items_data = [["Item", "Quantidade", "Preço Unit.", "Subtotal"]]
    
    for item in order.get("items", []):
        name = item.get("name", "")
        quantity = item.get("quantity", 1)
        price = item.get("price", 0.0)
        subtotal = price * quantity
        items_data.append([
            name,
            str(quantity),
            f"R$ {price:.2f}",
            f"R$ {subtotal:.2f}"
        ])
    
    # Adicionar linha de total
    items_data.append(["", "", "TOTAL:", f"R$ {total:.2f}"])
    
    items_table = Table(items_data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ('FONTNAME', (0, -1), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("_" * 80, value_style))
    story.append(Spacer(1, 5*mm))
    
    # Rodapé - Data de emissão
    emission_date = datetime.now().strftime("%d/%m/%Y")
    emission_time = datetime.now().strftime("%H:%M:%S")
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_RIGHT,
        fontName='Helvetica'
    )
    
    story.append(Paragraph(f"EMITIDO EM: {emission_date} ÀS {emission_time}", footer_style))
    
    # Gerar PDF
    doc.build(story)
