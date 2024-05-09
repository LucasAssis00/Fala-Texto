from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
import io

# Function to split text into multiple lines
def split_text(text, max_width, font_size, font):
    words = text.split()
    lines = []
    current_line = words[0]
    for word in words[1:]:
        width = c.stringWidth(current_line + ' ' + word, fontName=font, fontSize=font_size)
        if width < max_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

# Caminho para o PDF existente que você deseja editar
pdf_path = '/content/questionarios prick test.pdf'

# Página específica para adicionar o texto
target_page = 0  # Adjust as needed, considering that page numbering starts from 0

# Carregar o PDF existente
existing_pdf = PdfReader(open(pdf_path, 'rb'))
output = PdfWriter()

# Criar um novo PDF com o ReportLab para sobrepor o existente
packet = io.BytesIO()
c = canvas.Canvas(packet, pagesize=letter)

# Texto longo que precisa ser dividido em várias linhas
long_text = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod 
               tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
               quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'''

# Determinar as dimensões do retângulo de texto
text_width, text_height = 400, 200  # Ajuste conforme necessário
x, y = 100, 500  # Coordenadas do canto inferior esquerdo do retângulo

# Tamanho da fonte
font_size = 8  # Adjust the font size as needed

# Dividir o texto em linhas
lines = split_text(long_text, text_width, font_size, "Times-Roman")

# Desenhar o texto na página desejada do PDF
for line in lines:
    c.setFont("Courier", font_size)  # Set the font size
    c.drawString(x, y, line)
    y -= font_size * 1.2  # Espaçamento entre linhas

c.save()

# Mover para o início do buffer StringIO
packet.seek(0)
new_pdf = PdfReader(packet)

# Adicionar a "camada" do novo PDF ao PDF existente apenas na página desejada
for i in range(len(existing_pdf.pages)):
    page = existing_pdf.pages[i]
    if i == target_page:
        page.merge_page(new_pdf.pages[0])
    output.add_page(page)

# Salvar o PDF resultante
with open('pdf_editado22.pdf', 'wb') as output_pdf:
    output.write(output_pdf)

print("PDF editado salvo como 'pdf_editado.pdf'")