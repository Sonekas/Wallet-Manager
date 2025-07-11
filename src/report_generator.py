import pandas as pd
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

class ReportGenerator:
    def __init__(self):
        pass

    def generate_excel_report(self, assets_data, filename="relatorio_carteira.xlsx"):
        df = pd.DataFrame(assets_data, columns=["Nome do Ativo", "Tipo", "Quantidade", "Preço de Compra", "Preço Atual", "Valor Investido", "Valor Atual", "Rentabilidade (%)"])
        try:
            df.to_excel(filename, index=False)
            print(f"Relatório Excel gerado com sucesso: {filename}")
            return True
        except Exception as e:
            print(f"Erro ao gerar relatório Excel: {e}")
            return False

    def generate_pdf_report(self, assets_data, total_invested, total_current_value, total_rentability, filename="relatorio_carteira.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Título
        story.append(Paragraph("Relatório da Carteira de Investimentos", styles['h1']))
        story.append(Spacer(1, 0.2 * 100))

        # Resumo Geral
        story.append(Paragraph("Resumo Geral:", styles['h2']))
        story.append(Paragraph(f"Valor Total Investido: R$ {total_invested:.2f}", styles['Normal']))
        story.append(Paragraph(f"Valor Atual da Carteira: R$ {total_current_value:.2f}", styles['Normal']))
        story.append(Paragraph(f"Rentabilidade Total: {total_rentability:.2f}%", styles['Normal']))
        story.append(Spacer(1, 0.2 * 100))

        # Tabela de Ativos
        story.append(Paragraph("Detalhes dos Ativos:", styles['h2']))
        data = [["Nome", "Tipo", "Qtd", "P. Compra", "P. Atual", "V. Investido", "V. Atual", "Rentab. (%)"]]
        for asset in assets_data:
            data.append(list(asset))

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * 100))

        try:
            doc.build(story)
            print(f"Relatório PDF gerado com sucesso: {filename}")
            return True
        except Exception as e:
            print(f"Erro ao gerar relatório PDF: {e}")
            return False

if __name__ == "__main__":
    # Exemplo de uso
    generator = ReportGenerator()
    sample_assets = [
        ("PETR4", "Ação", 100, 25.00, 28.50, 2500.00, 2850.00, 14.00),
        ("MXRF11", "FII", 200, 10.00, 10.20, 2000.00, 2040.00, 2.00)
    ]
    total_inv = 4500.00
    total_curr = 4890.00
    total_rent = ((total_curr - total_inv) / total_inv) * 100

    generator.generate_excel_report(sample_assets, "sample_report.xlsx")
    generator.generate_pdf_report(sample_assets, total_inv, total_curr, total_rent, "sample_report.pdf")


