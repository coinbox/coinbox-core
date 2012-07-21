from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, \
                                                 Paragraph, Spacer

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

stylesheet = getSampleStyleSheet()
stylesheet.add(ParagraphStyle(name='Heading3Right',
                        parent=stylesheet['Heading3'],
                        alignment=TA_RIGHT),
               alias='h3-right')
stylesheet.add(ParagraphStyle(name='Subtitle',
                        parent=stylesheet['Title'],
                        fontSize=14),
               alias='subtitle')

class PDFReport:
    def __init__(self, filename, title, subtitle=None, date_range=None):
        self.doc = SimpleDocTemplate(filename)
        self.elements = []

        self.title = title
        self.subtitle = subtitle
        self.date_range = date_range

        self._init_header()
        self._init_content()
        self._init_footer()

    def _init_footer(self):
        pass

    def _init_content(self):
        pass

    def _init_header(self):
        self.elements.append(Paragraph(self.title, stylesheet['Title']))
        if self.subtitle is not None:
            self.elements.append(Paragraph(self.subtitle, stylesheet['Subtitle']))
        if self.date_range is not None:
            _from, _to = self.date_range
            if _to is not None:
                self.elements.append(Paragraph('From %s To %s' % (_from, _to), stylesheet['Subtitle']))
            else:
                self.elements.append(Paragraph('On: %s' % (_from,), stylesheet['Subtitle']))
        self.elements.append(Spacer(36,36))

    def build(self):
        self.doc.build(self.elements, onFirstPage=self.onFirstPage, onLaterPages=self.onLaterPage)
        return self.doc

    def onFirstPage(self, canvas, doc):
        self.onLaterPage(canvas, doc)

    def onLaterPage(self, canvas, doc):
        canvas.saveState()

        canvas.setFont('Times-Italic',12)
        canvas.drawRightString(523, doc.bottomMargin+doc.height, self.title)

        canvas.setFont('Times-Roman',12)
        canvas.drawCentredString(doc.leftMargin+doc.width/2, doc.bottomMargin, "Page %d" % doc.page)
        #canvas.drawString(4 * inch, 0.75 * inch, "Page %d" % doc.page)
        canvas.restoreState()


    def doTable(self, data=[], header=None, footer=None, marked_rows=[]):
        #colwidths = ['*']+['17%']*3
        #colwidths = [float(PAGE_WIDTH)/len(headers)]*len(headers)
        rows = ([list(header)] if header is not None else []) + \
               data + \
               ([list(footer)] if footer is not None else [])
        style = []
        top_offset, bottom_offset = 0, 0
        if header is not None:
            style.append(('LINEBELOW', (0,0), (-1,0), 2, colors.green))
            style.append(('ALIGN', (0,0), (-1,0), 'CENTER'))
            top_offset = 1
        if footer is not None:
            style.append(('LINEBELOW', (0,-2), (-1,-2), 2, colors.green))
            bottom_offset = 1
        
        style.append(('LINEABOVE', (0,1+top_offset), (-1,-1-bottom_offset),
                      0.25, colors.black))
        style.append(('ALIGN', (1,1), (-1,-1), 'RIGHT'))
        if footer is None:
            style.append(('LINEBELOW', (0,-1), (-1,-1), 0.25, colors.black))

        for r in marked_rows:
            style.append(('TEXTCOLOR', (0, r), (-1, r), colors.red))

        self.elements.append(Spacer(18,18))
        table = Table(data=rows,
                      #colWidths=colwidths,
                      style=TableStyle(style)
                    )
        self.elements.append(table)

        return table

import app.modules.currency.objects as currency 

class TicketlistPDFReport(PDFReport):
    
    def __init__(self, filename, title, subtitle=None, date_range=None, tickets=[]):
        self.tickets = tickets
        PDFReport.__init__(self, filename, title, subtitle, date_range)
    
    def _init_content(self):
        period_total = 0
        def_c = currency.get_default()
        headers = ('Description', 'Price', 'Amount', 'Total')
        for t in self.tickets:
            row = [Paragraph('Ticket #%.3d (%s)%s' % (t.id, t.payment_method, \
                                ' [not paid]' if not t.paid else ''), stylesheet['Heading3']),
                   Paragraph(str(t.date_close), stylesheet['Heading3Right'])]
            info_table = self.doTable(data=[row])
            #[doc.width/2.0]*2

            data = []
            tc = t.currency
            tls = t.ticketlines
            for tl in tls:
                # TODO add discount
                data.append([tl.description,
                             tc.format(tl.sell_price),
                             'x%d' % (tl.amount,),
                             tc.format(tl.amount*tl.sell_price)])
            
            total = t.total
            footer = ['', '', 'Sub Total', tc.format(total)]
            period_total += currency.convert(total, tc, def_c)

            #colwidths = ['*']+['17%']*3
            table = self.doTable(data=data, header=headers, footer=footer)

        total_para = Paragraph('Total: %s' % (def_c.format(period_total),), stylesheet['Heading3Right'])
        self.elements.append(Spacer(36,36))
        self.elements.append(total_para)
