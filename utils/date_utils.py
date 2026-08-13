from datetime import datetime

def is_date_active(inicio, fim):
    hoje = datetime.now().date()
    hoje_md = (hoje.month, hoje.day)

    inicio_formated = datetime.strptime(inicio, "%m-%d")
    fim_formated = datetime.strptime(fim, "%m-%d")

    inicio_md = (inicio_formated.month, inicio_formated.day)
    fim_md = (fim_formated.month, fim_formated.day)
    return inicio_md <= hoje_md <= fim_md

def calculate_last_days(fim):
    hoje = datetime.now().date()
    
    fim_formated = datetime.strptime(fim, "%m-%d")
    fim_parsed = fim_formated.replace(year=hoje.year).date()
    return (fim_parsed - hoje).days

def format_end_date(data):
    hoje = datetime.now().date()
    fim_parsed = datetime.strptime(data, "%m-%d")
    fim = fim_parsed.replace(year=hoje.year).date()
    return f"{fim.day}/{fim.month}"