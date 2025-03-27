import pdfplumber
import re
from decimal import Decimal
import tkinter as tk
from tkinter import filedialog, messagebox


def extract_paystub_data(pdf_path):
    """
    Extract financial data from a paystub PDF and calculate net income.

    Parameters:
        pdf_path (str): Path to the paystub PDF file

    Returns:
        dict: Contains gross income, taxes, benefits, net income, and percentage taken

    Raises:
        ValueError: If no text is extracted or gross income is not found
        Exception: For other PDF processing errors
    """
    gross_income = Decimal('0.00')
    total_taxes = Decimal('0.00')
    total_benefits = Decimal('0.00')

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() or ""

        if not full_text:
            raise ValueError("No text extracted from PDF.")

        full_text = full_text.lower()

        # Extract gross income
        gross_pattern = r'total gross pay\s*[^$]*\$([\d,.]+)'
        gross_match = re.search(gross_pattern, full_text)
        if gross_match:
            gross_income = Decimal(gross_match.group(1).replace(',', ''))
        else:
            raise ValueError("Gross income not found!")

        # Patterns for taxes and benefits
        tax_pattern = r'(fica|medicare tax|federal tax|federa tax|federal withholding|al state tax)\s*[-\w\s]*?\s*\$([\d,.]+)(?!\s*[-\w]*\s*(employer|ytd))'
        benefit_pattern = r'(dental coverage|flexible spending|medical coverage\s*-?\s*(?:family|single|employee plus one)?|medical phone|teacher retirement|university cellular|vision coverage|voluntary life\w*(?:employee|spouse|dependent)?)(?:\s*(?:family|single|employee plus one))?\s*.*?\$([\d,.]+)(?!\s*(employer|ytd))'

        # Extract taxes
        tax_matches = re.finditer(tax_pattern, full_text)
        for match in tax_matches:
            amount_str = match.group(2)
            if amount_str and re.match(r'^\d+[.,]?\d*$', amount_str):
                amount = Decimal(amount_str.replace(',', ''))
                total_taxes += amount

        # Extract benefits, limiting to one medical coverage
        benefit_matches = list(re.finditer(benefit_pattern, full_text))
        medical_coverage_found = False
        for match in benefit_matches:
            description = match.group(1)
            amount_str = match.group(2)
            if amount_str and re.match(r'^\d+[.,]?\d*$', amount_str):
                amount = Decimal(amount_str.replace(',', ''))
                if "medical coverage" in description:
                    if not medical_coverage_found:
                        total_benefits += amount
                        medical_coverage_found = True
                else:
                    total_benefits += amount

        # Calculate net income
        net_income = gross_income - total_taxes - total_benefits

        # Calculate percentage taken
        total_deductions = total_taxes + total_benefits
        percent_taken = (total_deductions / gross_income * Decimal('100')) if gross_income > 0 else Decimal('0.00')

    return {
        'gross_income': float(gross_income),
        'total_taxes': float(total_taxes),
        'total_benefits': float(total_benefits),
        'net_income': float(net_income),
        'percent_taken': float(percent_taken)
    }


# Set up the GUI
root = tk.Tk()
root.geometry("400x400")  # Set a larger window size
root.title("Paystub Analyzer")

# Control frame with the select button
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

select_button = tk.Button(control_frame, text="Select PDF File", command=lambda: process_pdf())
select_button.pack()

# Results frame to display output
results_frame = tk.Frame(root)
results_frame.pack(pady=10)

# Labels for displaying results
tk.Label(results_frame, text="Gross Income:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
gross_value_label = tk.Label(results_frame, text="")
gross_value_label.grid(row=0, column=1, sticky="e", padx=5, pady=2)

tk.Label(results_frame, text="Total Taxes:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
taxes_value_label = tk.Label(results_frame, text="")
taxes_value_label.grid(row=1, column=1, sticky="e", padx=5, pady=2)

tk.Label(results_frame, text="Total Benefits:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
benefits_value_label = tk.Label(results_frame, text="")
benefits_value_label.grid(row=2, column=1, sticky="e", padx=5, pady=2)

tk.Label(results_frame, text="Net Income:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
net_value_label = tk.Label(results_frame, text="")
net_value_label.grid(row=3, column=1, sticky="e", padx=5, pady=2)

tk.Label(results_frame, text="Percentage Taken:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
percent_value_label = tk.Label(results_frame, text="")
percent_value_label.grid(row=4, column=1, sticky="e", padx=5, pady=2)


def process_pdf():
    """Handle PDF file selection and processing, then update the GUI with results."""
    pdf_path = filedialog.askopenfilename(title="Select Paystub PDF", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        messagebox.showinfo("Info", "No file selected.")
        return

    try:
        results = extract_paystub_data(pdf_path)
        # Update GUI labels with formatted results
        gross_value_label.config(text=f"${results['gross_income']:.2f}")
        taxes_value_label.config(text=f"${results['total_taxes']:.2f}")
        benefits_value_label.config(text=f"${results['total_benefits']:.2f}")
        net_value_label.config(text=f"${results['net_income']:.2f}")
        percent_value_label.config(text=f"{results['percent_taken']:.2f}%")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Start the GUI event loop
root.mainloop()