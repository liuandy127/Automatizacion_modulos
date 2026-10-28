from pathlib import Path
import csv
import json

PROJECT_ROOT=Path(__file__).resolve().parent.parent

DATA_DIR=PROJECT_ROOT/"data"
INCOMING_DIR=DATA_DIR/"incoming"
PROCESSED_DIR=DATA_DIR/"processed"

def normalizacion_del_cliente(id_cliente:str, nombre:str, producto:str, cantidad:str, precio:str) -> tuple[str,str,str,str,str]:
    id_cliente=(id_cliente or "").strip().upper()
    nombre=(nombre or "").strip().title()
    producto=(producto or "").strip().title()
    cantidad=(cantidad or "").strip()
    precio=(precio or "").strip()

    return id_cliente, nombre, producto, cantidad, precio

def validacion_del_cliente(id_cliente:str, nombre:str, producto:str, cantidad:str, precio:str) -> list[str]:

    error_en_clientes=[]

    if not id_cliente:
        error_en_clientes.append("ERROR: id vacio")

    if not nombre:
        error_en_clientes.append("ERROR: nombre vacio")

    if not producto:
        error_en_clientes.append("ERROR: producto vacio")

    if not cantidad:
        error_en_clientes.append("ERROR: cantidad vacia")
    elif not cantidad.lstrip("-").isdigit():
        error_en_clientes.append("ERROR: cantidad no numerica")
    else:
        cantidad=int(cantidad)
        if cantidad<=0:
            error_en_clientes.append("ERROR: cantidad fuera de rango")

    if not precio:
        error_en_clientes.append("ERROR: precio vacio")
    elif not precio.replace(".","", 1).lstrip("-").isdigit():
        error_en_clientes.append("ERROR: precio no numerico")
    else:
        precio=float(precio)
        if precio<=0:
            error_en_clientes.append("ERROR: precio fuera de rango")

    return error_en_clientes

def administrador_de_pedidos() -> None:
    path_pedidos=INCOMING_DIR/"pedidos.csv"
    path_pedidos_validos=PROCESSED_DIR/"pedidos_validos.csv"
    path_pedidos_rechazados=PROCESSED_DIR/"pedidos_rechazados.csv"
    path_resumen=PROCESSED_DIR/"resumen.json"

    with path_pedidos.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as pedidos:
        
        reader=csv.DictReader(pedidos)

        if reader.fieldnames is None:
            print("ERROR: CSV vacio o sin cabecera")
            return

        columnas_obligatorias={
            "id_cliente",
            "nombre",
            "producto",
            "cantidad",
            "precio"
        }
        columnas_archivos=set(reader.fieldnames)

        columnas_faltantes=[]
        for columna in columnas_obligatorias:
            if columna not in columnas_archivos:
                columnas_faltantes.append(columna)

        if columnas_faltantes:
            print(f"Falta columna obligatoria {columnas_faltantes}")
            return

        with path_pedidos_validos.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as salida_pedidos_validos, \
        path_pedidos_rechazados.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as salida_pedidos_rechazados:

            numero_pedidos_rechazados=0
            numero_pedidos_validos=0
            numero_unidades_vendidas=0
            facturacion_total=0.0

            fieldname_valido=["id_cliente", "nombre", "producto", "cantidad", "precio", "subtotal"]
            fieldname_rechazado=["id_cliente", "nombre", "producto", "cantidad", "precio", "errores"]

            writer_validos=csv.DictWriter(salida_pedidos_validos, fieldnames=fieldname_valido)
            writer_rechazados=csv.DictWriter(salida_pedidos_rechazados, fieldnames=fieldname_rechazado)


            writer_validos.writeheader()
            writer_rechazados.writeheader()



            for row in reader:
                id_cliente=row["id_cliente"]
                nombre=row["nombre"]
                producto=row["producto"]
                cantidad=row["cantidad"]
                precio=row["precio"]

                id_cliente, nombre, producto, cantidad, precio = normalizacion_del_cliente(id_cliente, nombre, producto, cantidad, precio)
                resultado = validacion_del_cliente(id_cliente, nombre, producto, cantidad, precio)

                if resultado:
                    resultado="; ".join(resultado)
                    writer_rechazados.writerow(
                        {
                            "id_cliente": id_cliente,
                            "nombre": nombre,
                            "producto": producto,
                            "cantidad": cantidad,
                            "precio": precio,
                            "errores":  resultado,
                        }
                    )
                    numero_pedidos_rechazados+=1
                else:
                    cantidad=int(cantidad)
                    precio=float(precio)
                    subtotal=cantidad*precio
                    facturacion_total+=subtotal
                    numero_pedidos_validos+=1
                    numero_unidades_vendidas+=cantidad

                    writer_validos.writerow(
                        {
                            "id_cliente": id_cliente,
                            "nombre": nombre,
                            "producto": producto,
                            "cantidad": cantidad,
                            "precio": precio,
                            "subtotal": subtotal,
                        }
                    )

            resumen_resultado={
                "pedidos_validos": numero_pedidos_validos,
                "pedidos_rechazados": numero_pedidos_rechazados,
                "unidades_vendidas": numero_unidades_vendidas,
                "facturacion_total": facturacion_total,

            }

            with path_resumen.open(
                "w",
                encoding="utf-8",
                newline=""
            ) as file_resumen:
                json.dump(
                    resumen_resultado,
                    file_resumen,
                    indent=4,
                    ensure_ascii=False,
                )


            


        

        

        
