# Import pdf library
from reportlab.pdfgen import canvas


# Function
def createPDF(logo, event, date, location, series, unumber, file):
        try:
            c = canvas.Canvas(file)
            c.drawImage(logo, 191, 620, width=200, height=200, mask=None)
        except IOError:
            pass
        c.setFont("Helvetica", 25)
        c.drawCentredString(300, 600, event)
        c.setFont("Helvetica", 16)
        c.drawCentredString(300, 570, date+" / "+location)
        c.setFont("Helvetica", 50)
        c.drawCentredString(300, 500, "INVITATION")
        c.setFont("Helvetica", 10)
        c.drawCentredString(300, 475, "( valid as regular presale ticket )")
        c.line(50, 420, 550, 420)
        c.setFont("Helvetica", 20)
        c.drawCentredString(300, 375, "Pass code:")
        c.setFont("Helvetica", 30)
        c.drawCentredString(300, 310, series + " - " + str(unumber)[:2] + " - " + str(unumber)[2:4] + " - " + str(unumber)[4:])
        c.line(50, 280, 550, 280)
        c.setFont("Helvetica", 14)
        c.drawString(80, 230, "*    this pass includes entrance to main event")
        c.drawString(80, 210, "**   pass has to be presented with valid ID or passport at the doors")
        c.drawString(80, 190, "***  we recommend not to share this unique pass code with third person,")
        c.drawString(80, 170, "      ONE code is for ONE entry")
        c.save()
