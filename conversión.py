import requests
import xml.etree.ElementTree as ET

def obtener_tasas_cambio():
    """Obtiene las tasas de cambio actualizadas del BCE"""
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return None

    try:
        root = ET.fromstring(respuesta.content)
        namespaces = {
            'euro': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref',
            'gesmes': 'http://www.gesmes.org/xml/2002-08-01'
        }
        
        tasas = {'EUR': 1.0}
        cubo_principal = root.find('.//euro:Cube/euro:Cube', namespaces)
        
        if cubo_principal is not None:
            for cubo in cubo_principal.findall('euro:Cube', namespaces):
                divisa = cubo.get('currency')
                tasa = cubo.get('rate')
                if divisa and tasa:
                    try:
                        tasas[divisa] = float(tasa)
                    except ValueError:
                        continue
        return tasas
    except ET.ParseError as e:
        print(f"Error al analizar XML: {e}")
        return None

def convertir_divisa(monto, origen, destino, tasas):
    """Realiza la conversión de divisas usando las tasas obtenidas"""
    if origen == destino:
        return monto
    
    for divisa in [origen, destino]:
        if divisa != 'EUR' and divisa not in tasas:
            print(f"Divisa no soportada: {divisa}")
            print(f"Divisas disponibles: {', '.join(tasas.keys())}")
            return None
    
    try:
        # Conversión a Euros primero
        if origen != 'EUR':
            valor_eur = monto / tasas[origen]
        else:
            valor_eur = monto
        
        # Conversión a divisa destino
        if destino != 'EUR':
            resultado = valor_eur * tasas[destino]
        else:
            resultado = valor_eur
            
        return round(resultado, 4)
    except ZeroDivisionError:
        print("Error: Tasa de cambio inválida (0)")
        return None

def main():
    print("\nSistema de Conversión de Divisas en Tiempo Real")
    print("Fuente de datos: Banco Central Europeo (BCE)\n")
    
    tasas = obtener_tasas_cambio()
    if not tasas:
        print("No se pudieron obtener las tasas de cambio")
        return
    
    while True:
        try:
            origen = input("Divisa origen (3 letras, ej. USD): ").upper()
            destino = input("Divisa destino (3 letras, ej. EUR): ").upper()
            monto = float(input("Monto a convertir: "))
            
            resultado = convertir_divisa(monto, origen, destino, tasas)
            
            if resultado is not None:
                print(f"\n{monto} {origen} = {resultado} {destino}\n")
            
            if input("¿Nueva conversión? (s/n): ").lower() != 's':
                break
                
        except ValueError:
            print("Error: Ingrese un monto numérico válido")
        except KeyboardInterrupt:
            print("\nOperación cancelada")
            break

if __name__ == "__main__":
    main()