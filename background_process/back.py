import sys
import os
# from https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from fpdf import FPDF
from datetime import datetime

from agent_background import query_agent_company, format_content
from utils.aws_services import get_s3_client, get_s3_bucket

class PDF(FPDF):
    def header(self):
        # Logo
        self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 12)
        self.cell(40)  # Move to the right of the logo

        # Title
        self.ln(20)  # Move below the logo
        self.cell(0, 10, 'Daily Report', 0, 1, 'C')

        # Date
        self.cell(0, 10, datetime.now().strftime("%Y-%m-%d"), 0, 1, 'C')
        self.ln(10)  # Line break

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Report generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}', 0, 0, 'C')

    def add_green_bar(self):
        self.set_fill_color(70, 114, 171)  # Light green color
        self.rect(0, 0, 10, 297, 'F')  # Draw rectangle

    def check_page_break(self, height=10):
        if self.get_y() + height > 270:  # 270 is an approximate page bottom margin
            self.add_page()
            self.add_green_bar()  # Add the green bar on each new page

    def add_page(self, *args, **kwargs):
        super().add_page(*args, **kwargs)
        self.add_green_bar()

    def add_section(self, company_name, text_body):
        self.check_page_break(20)  # Check if adding this section requires a new page
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, company_name, 0, 1)
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, text_body)
        self.ln(10)  # Line break

    def add_divider(self):
        self.check_page_break()
        self.set_fill_color(0, 0, 0)  # Black color
        self.cell(0, 1, '', 'B', 1, 'C', 1)
        self.ln(10)  # Line break

def upload_to_s3(bucket_name, file_name, object_name=None):
    """Upload a file to an S3 bucket"""
    if object_name is None:
        object_name = file_name
    s3_client = get_s3_client()
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

pdf = PDF()#uni=True)
pdf.add_page()

# Add green bar
pdf.add_green_bar()

# Add divider line before the first section
pdf.add_divider()
    
companies = ["Tesla", "Meta", "Amazon"]
for company in companies:
    #query = f"\n\nHuman: Is {company} a good investment choice right now? \n\nAssistant:"
    response = query_agent_company(company)
    section_body = format_content(company, response)
    section_body = section_body.replace("\u2019", "'")
    
    pdf.add_section(company, section_body)

    # Add a normal dividing line if not the last company
    if company != companies[-1]:
        pdf.cell(0, 0, '', 'B', 1)  # Adding a normal dividing line
        pdf.ln(10)  # Line break
# Add thicker divider line before the footer
pdf.add_divider()

pdf_file = f'/tmp/Daily_Report{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.pdf'
pdf.output(pdf_file)
upload_to_s3(get_s3_bucket(), pdf_file)