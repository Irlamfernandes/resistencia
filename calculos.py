import math

def _converter_para_base(valor, unidade, fatores_conversao):
    # Converte um valor DE sua unidade PARA a unidade base (que tem fator 1.0)
    return valor * fatores_conversao[unidade]
def _converter_de_base(valor_base, unidade_saida, fatores_conversao):
    # Converte um valor DA unidade base PARA a unidade de saída desejada
    return valor_base / fatores_conversao[unidade_saida]

CONVERSOES_FORCA = {"N": 1.0, "kgf": 10.0, "lbf": 4.44822, "kN": 1000.0} # Base N (Ajustado para 1 kgf = 10 N para corresponder aos exemplos)
CONVERSOES_PRESSAO = {"Pa": 1.0, "kgf/cm²": 1e5, "psi": 6894.76, "MPa": 1e6, "GPa": 1e9, "kN/cm²": 1e7} # Base Pa (Ajustado para 1 kgf/cm² = 1e5 Pa)
CONVERSOES_AREA = {"m²": 1.0, "cm²": 1e-4, "mm²": 1e-6, "in²": 0.00064516} # Base m²
CONVERSOES_COMPRIMENTO = {"m": 1.0, "cm": 0.01, "mm": 0.001, "in": 0.0254} # Base m
CONVERSOES_MODULO_E = {"Pa": 1.0, "MPa": 1e6, "GPa": 1e9, "kgf/cm²": 1e5, "kN/cm²": 1e7} # Base Pa (Ajustado para 1 kgf/cm² = 1e5 Pa)
CONVERSOES_CARGA_DIST = {"N/m": 1.0, "kN/m": 1000.0, "kgf/m": 10.0} # Base N/m

def calcular_forca_projeto(dados, unidade_saida):
    try:
        peso_info = next((item for item in dados if item["tipo"] == "Peso"), None)
        peso_add_info = next((item for item in dados if item["tipo"] == "Peso Adicional"), None)
        coef_forca_info = next((item for item in dados if item["tipo"] == "Coeficiente de Força"), None)

        if not all([peso_info, coef_forca_info]):
            return "Erro: Forneça valores para Peso e Coeficiente de Força."

        peso = float(peso_info["valor"].replace(',', '.'))
        coef_forca = float(coef_forca_info["valor"].replace(',', '.'))
        peso_base_N = _converter_para_base(peso, peso_info["unidade"], CONVERSOES_FORCA)

        peso_add_base_N = 0.0
        if peso_add_info:
            peso_add = float(peso_add_info["valor"].replace(',', '.'))
            peso_add_base_N = _converter_para_base(peso_add, peso_add_info["unidade"], CONVERSOES_FORCA)

        forca_base_N = (peso_base_N + peso_add_base_N) * coef_forca
        resultado_final = _converter_de_base(forca_base_N, unidade_saida, CONVERSOES_FORCA)

        return f"Força de Projeto: {resultado_final:.3f} {unidade_saida}"

    except (ValueError, TypeError):
        return "Erro: Verifique se os valores de entrada são números válidos."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_forca_por_apoio(dados, unidade_saida):
    try:
        forca_str = calcular_forca_projeto(dados, "N") # Obter força total em N
        if "Erro" in forca_str: return forca_str
        forca_proj_base_N = float(forca_str.split(':')[1].split()[0])

        qtd_apoios_info = next((item for item in dados if item["tipo"] == "Quantidade de apoios"), None)
        
        forca_por_apoio_base_N = forca_proj_base_N
        if qtd_apoios_info:
            qtd_apoios = int(qtd_apoios_info["valor"])
            if qtd_apoios > 0:
                forca_por_apoio_base_N = forca_proj_base_N / qtd_apoios

        resultado_final = _converter_de_base(forca_por_apoio_base_N, unidade_saida, CONVERSOES_FORCA)
        return f"Força por Apoio: {resultado_final:.3f} {unidade_saida}"

    except (ValueError, TypeError, ZeroDivisionError):
        return "Erro: Verifique se os valores de entrada são números válidos e maiores que zero."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_deformacao(dados, unidade_saida):
    try:
        comprimento_info = next((item for item in dados if item["tipo"] == "Comprimento Inicial"), None)
        modulo_e_info = next((item for item in dados if item["tipo"] == "Módulo de Elasticidade"), None)
        area_direta_info = next((item for item in dados if item["tipo"] == "Área de Seção"), None)
        carga_dist_info = next((item for item in dados if item["tipo"] == "Carga Distribuída"), None)
        comp_carga_info = next((item for item in dados if item["tipo"] == "Comprimento da Carga"), None)
        peso_info = next((item for item in dados if item["tipo"] == "Peso"), None)
        diam_ext_info = next((item for item in dados if item["tipo"] == "Diâmetro Externo"), None)
        espessura_info = next((item for item in dados if item["tipo"] == "Espessura da Parede"), None)

        if not all([comprimento_info, modulo_e_info]):
            return "Erro: Forneça Comprimento Inicial e Módulo de Elasticidade."

        # --- Lógica Inteligente para Força ---
        forca_servico_N = 0.0
        
        if carga_dist_info and comp_carga_info:
            carga_base_Nm = _converter_para_base(float(carga_dist_info["valor"].replace(',', '.')), carga_dist_info["unidade"], CONVERSOES_CARGA_DIST)
            comp_carga_base_m = _converter_para_base(float(comp_carga_info["valor"].replace(',', '.')), comp_carga_info["unidade"], CONVERSOES_COMPRIMENTO)
            forca_servico_N = carga_base_Nm * comp_carga_base_m
        elif peso_info:
            peso_add_info = next((item for item in dados if item["tipo"] == "Peso Adicional"), None)
            peso_base_N = _converter_para_base(float(peso_info["valor"].replace(',', '.')), peso_info["unidade"], CONVERSOES_FORCA)
            peso_add_base_N = 0.0
            if peso_add_info:
                peso_add_base_N = _converter_para_base(float(peso_add_info["valor"].replace(',', '.')), peso_add_info["unidade"], CONVERSOES_FORCA)
            forca_servico_N = peso_base_N + peso_add_base_N
        else:
            return "Erro: Forneça dados para calcular a força (Peso ou Carga Distribuída)."

        # --- Lógica Inteligente para Área ---
        area_base_m2 = 0.0

        if diam_ext_info and espessura_info:
            diam_ext_m = _converter_para_base(float(diam_ext_info["valor"].replace(',', '.')), diam_ext_info["unidade"], CONVERSOES_COMPRIMENTO)
            espessura_m = _converter_para_base(float(espessura_info["valor"].replace(',', '.')), espessura_info["unidade"], CONVERSOES_COMPRIMENTO)
            diam_int_m = diam_ext_m - (2 * espessura_m)
            area_externa = math.pi * (diam_ext_m ** 2) / 4
            area_interna = math.pi * (diam_int_m ** 2) / 4
            area_base_m2 = area_externa - area_interna
        elif area_direta_info:
            area_base_m2 = _converter_para_base(float(area_direta_info["valor"].replace(',', '.')), area_direta_info["unidade"], CONVERSOES_AREA)
        else:
            area_calculada_str = calcular_area_secao(dados, "m²")
            if "Erro" in area_calculada_str: return area_calculada_str
            area_base_m2 = float(area_calculada_str.split(':')[1].split()[0])

        comprimento_base_m = _converter_para_base(float(comprimento_info["valor"].replace(',', '.')), comprimento_info["unidade"], CONVERSOES_COMPRIMENTO) # Comprimento em m
        modulo_e_base_Pa = _converter_para_base(float(modulo_e_info["valor"].replace(',', '.')), modulo_e_info["unidade"], CONVERSOES_MODULO_E) # Módulo em Pa

        if area_base_m2 == 0 or modulo_e_base_Pa == 0:
            return "Erro: Área e Módulo de Elasticidade não podem ser zero."

        deformacao_base_m = (forca_servico_N * comprimento_base_m) / (area_base_m2 * modulo_e_base_Pa)
        resultado_final = _converter_de_base(deformacao_base_m, unidade_saida, CONVERSOES_COMPRIMENTO)

        return f"Deformação: {resultado_final:.6f} {unidade_saida}" # Maior precisão para deformação
    except (ValueError, TypeError, ZeroDivisionError):
        return "Erro: Verifique se os valores de entrada são números válidos e maiores que zero."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_deformacao_segmentada(dados, unidade_saida):
    try:
        segmentos_info = [item for item in dados if item["tipo"] == "Segmento"]
        modulo_e_info = next((item for item in dados if item["tipo"] == "Módulo de Elasticidade"), None)

        if not segmentos_info or not modulo_e_info:
            return "Erro: Forneça o Módulo de Elasticidade e pelo menos um Segmento."

        # --- Lógica para calcular a Força (reutilizada de calcular_deformacao) ---
        forca_servico_N = 0.0
        carga_dist_info = next((item for item in dados if item["tipo"] == "Carga Distribuída"), None)
        comp_carga_info = next((item for item in dados if item["tipo"] == "Comprimento da Carga"), None)
        peso_info = next((item for item in dados if item["tipo"] == "Peso"), None)

        if carga_dist_info and comp_carga_info:
            carga_base_Nm = _converter_para_base(float(carga_dist_info["valor"].replace(',', '.')), carga_dist_info["unidade"], CONVERSOES_CARGA_DIST)
            comp_carga_base_m = _converter_para_base(float(comp_carga_info["valor"].replace(',', '.')), comp_carga_info["unidade"], CONVERSOES_COMPRIMENTO)
            forca_servico_N = carga_base_Nm * comp_carga_base_m
        
        # Adiciona pesos (como os refletores) à força
        pesos_info = [item for item in dados if item["tipo"] == "Peso"]
        for peso_item in pesos_info:
             forca_servico_N += _converter_para_base(float(peso_item["valor"].replace(',', '.')), peso_item["unidade"], CONVERSOES_FORCA)

        if forca_servico_N == 0:
             return "Erro: Forneça dados para calcular a força (Peso ou Carga Distribuída)."

        # --- Lógica principal para deformação segmentada ---
        modulo_e_base_Pa = _converter_para_base(float(modulo_e_info["valor"].replace(',', '.')), modulo_e_info["unidade"], CONVERSOES_MODULO_E)
        deformacao_total_base_m = 0.0

        for seg in segmentos_info:
            # Extrair e converter valores do segmento
            comprimento_m = _converter_para_base(float(seg["comprimento"].replace(',', '.')), seg["unidade_comprimento"], CONVERSOES_COMPRIMENTO)
            diam_ext_m = _converter_para_base(float(seg["diam_ext"].replace(',', '.')), seg["unidade_diam_ext"], CONVERSOES_COMPRIMENTO)
            espessura_m = _converter_para_base(float(seg["espessura"].replace(',', '.')), seg["unidade_espessura"], CONVERSOES_COMPRIMENTO)

            # Calcular área da seção do segmento
            diam_int_m = diam_ext_m - (2 * espessura_m)
            if diam_int_m < 0: return f"Erro no segmento: Espessura (2x) maior que o diâmetro externo."
            area_externa = math.pi * (diam_ext_m ** 2) / 4
            area_interna = math.pi * (diam_int_m ** 2) / 4
            area_base_m2 = area_externa - area_interna

            if area_base_m2 <= 0 or modulo_e_base_Pa == 0:
                return "Erro: Área do segmento ou Módulo de Elasticidade não podem ser zero."

            deformacao_segmento_m = (forca_servico_N * comprimento_m) / (area_base_m2 * modulo_e_base_Pa)
            deformacao_total_base_m += deformacao_segmento_m

        resultado_final = _converter_de_base(deformacao_total_base_m, unidade_saida, CONVERSOES_COMPRIMENTO)
        return f"Deformação Total: {resultado_final:.6f} {unidade_saida}"

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique todos os valores e unidades."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_area_secao(dados, unidade_saida):
    try:
        forca_str = calcular_forca_projeto(dados, "N") # Força em N
        if "Erro" in forca_str: return forca_str
        forca_base_N = float(forca_str.split(':')[1].split()[0])

        tensao_str = calcular_tensao_admissivel(dados, "Pa") # Tensão em Pa
        if "Erro" in tensao_str: return tensao_str
        tensao_base_Pa = float(tensao_str.split(':')[1].split()[0])

        if tensao_base_Pa == 0:
            return "Erro: Tensão Admissível não pode ser zero."

        area_base_m2 = forca_base_N / tensao_base_Pa # Área em m²
        resultado_final = _converter_de_base(area_base_m2, unidade_saida, CONVERSOES_AREA)

        return f"Área de Seção Total: {resultado_final:.3f} {unidade_saida}"

    except (ValueError, TypeError):
        return "Erro: Verifique se os valores de entrada são números válidos."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_area_por_apoio(dados, unidade_saida):
    try:
        area_total_str = calcular_area_secao(dados, "m²") # Área total em m²
        if "Erro" in area_total_str: return area_total_str
        area_total_base_m2 = float(area_total_str.split(':')[1].split()[0])

        qtd_apoios_info = next((item for item in dados if item["tipo"] == "Quantidade de apoios"), None)

        area_por_apoio_base_m2 = area_total_base_m2
        if qtd_apoios_info:
            qtd_apoios = int(qtd_apoios_info["valor"])
            if qtd_apoios > 0:
                area_por_apoio_base_m2 = area_total_base_m2 / qtd_apoios

        resultado_final = _converter_de_base(area_por_apoio_base_m2, unidade_saida, CONVERSOES_AREA)
        return f"Área por Apoio: {resultado_final:.3f} {unidade_saida}"

    except (ValueError, TypeError, ZeroDivisionError):
        return "Erro: Verifique se os valores de entrada são números válidos e maiores que zero."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_tensao_admissivel(dados, unidade_saida):
    tensao_limite_info = next((item for item in dados if item["tipo"] == "Tensão Limite"), None)
    coef_resistencia_info = next((item for item in dados if item["tipo"] == "Coeficiente de Resistência"), None)

    if not tensao_limite_info:
        return "Erro: O valor da 'Tensão Limite' não foi fornecido."
    if not coef_resistencia_info:
        return "Erro: O valor do 'Coeficiente de Resistência' não foi fornecido."

    try:
        tensao_limite = float(tensao_limite_info["valor"].replace(',', '.'))
        coef_resistencia = float(coef_resistencia_info["valor"].replace(',', '.'))
        
        if coef_resistencia == 0:
            return "Erro: O Coeficiente de Resistência não pode ser zero."

        unidade_entrada_tensao = tensao_limite_info["unidade"]
        tensao_admissivel = tensao_limite / coef_resistencia
        
        if tensao_admissivel == 0:
            return "Erro: A Tensão Admissível calculada é zero. Verifique os valores de Tensão Limite e Coeficiente de Resistência."

        valor_base_Pa = _converter_para_base(tensao_admissivel, unidade_entrada_tensao, CONVERSOES_PRESSAO) # Tensão em Pa
        resultado_final = _converter_de_base(valor_base_Pa, unidade_saida, CONVERSOES_PRESSAO)
        
        return f"Tensão Admissível: {resultado_final:.3f} {unidade_saida}"

    except ValueError:
        return "Erro: Verifique se os valores de 'Tensão Limite' e 'Coeficiente' são números válidos."
    except KeyError as e:
        return f"Erro: Unidade de medida não reconhecida para conversão: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

def determinar_dimensao_apoio(dados, unidade_saida):
    try:
        qtd_apoios_info = next((item for item in dados if item["tipo"] == "Quantidade de apoios"), None)
        proporcao_info = next((item for item in dados if item["tipo"] == "Proporção entre dimensões"), None)

        tensao_str = calcular_tensao_admissivel(dados, "kgf/cm²")
        if "Erro" in tensao_str: return tensao_str # Apenas para validação, não usamos o valor aqui

        area_por_apoio_str = calcular_area_por_apoio(dados, "m²") # Área por apoio em m²
        if "Erro" in area_por_apoio_str: return area_por_apoio_str
        area_por_apoio_base_m2 = float(area_por_apoio_str.split(':')[1].split()[0])

        if proporcao_info:
            proporcao = float(proporcao_info["valor"].replace(',', '.'))
            if proporcao <= 0: return "Erro: Proporção deve ser maior que zero."
            
            a_quadrado_m2 = area_por_apoio_base_m2 / proporcao
            dimensao_a_m = math.sqrt(a_quadrado_m2)
            dimensao_b_m = dimensao_a_m * proporcao
            return f"Dimensões do apoio: {_converter_de_base(dimensao_a_m, unidade_saida, CONVERSOES_COMPRIMENTO):.2f} {unidade_saida} x {_converter_de_base(dimensao_b_m, unidade_saida, CONVERSOES_COMPRIMENTO):.2f} {unidade_saida}"
        else:
            diametro_m = math.sqrt(4 * area_por_apoio_base_m2 / math.pi)
            return f"Diâmetro do apoio: {_converter_de_base(diametro_m, unidade_saida, CONVERSOES_COMPRIMENTO):.2f} {unidade_saida}"

    except (ValueError, TypeError, ZeroDivisionError):
        return "Erro: Verifique se os valores de entrada são números válidos e maiores que zero."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_propriedades_perfil_L(dados, unidade_saida_comprimento):
    try:
        # Extrair dimensões do perfil L
        B_info = next((item for item in dados if item["tipo"] == "Largura Total (B)"), None)
        H_info = next((item for item in dados if item["tipo"] == "Altura Total (H)"), None)
        b_info = next((item for item in dados if item["tipo"] == "Espessura da Alma (b)"), None)
        h_info = next((item for item in dados if item["tipo"] == "Espessura da Mesa (h)"), None)

        if not all([B_info, H_info, b_info, h_info]):
            return "Erro: Forneça todas as 4 dimensões do perfil L (B, H, b, h)."

        # Converter todas as dimensões para a unidade base (metros)
        B = _converter_para_base(float(B_info["valor"].replace(',', '.')), B_info["unidade"], CONVERSOES_COMPRIMENTO)
        H = _converter_para_base(float(H_info["valor"].replace(',', '.')), H_info["unidade"], CONVERSOES_COMPRIMENTO)
        b = _converter_para_base(float(b_info["valor"].replace(',', '.')), b_info["unidade"], CONVERSOES_COMPRIMENTO)
        h = _converter_para_base(float(h_info["valor"].replace(',', '.')), h_info["unidade"], CONVERSOES_COMPRIMENTO)

        if not (B > b > 0 and H > h > 0):
            return "Erro: As dimensões devem ser lógicas (B > b, H > h) e positivas."

        # Dividir o L em dois retângulos
        # Retângulo 1 (Alma - vertical)
        A1 = b * (H - h)
        x1 = b / 2
        y1 = h + (H - h) / 2

        # Retângulo 2 (Mesa - horizontal)
        A2 = B * h
        x2 = B / 2
        y2 = h / 2

        # 1. Área Total
        A_total = A1 + A2

        # 2. Centro de Gravidade (Cx, Cy)
        Cx = (A1 * x1 + A2 * x2) / A_total
        Cy = (A1 * y1 + A2 * y2) / A_total

        # 3. Momento de Inércia (Teorema dos Eixos Paralelos)
        # I = I_local + A * d^2
        I_local_x1 = (b * (H - h)**3) / 12
        I_local_y1 = ((H - h) * b**3) / 12
        Ix1 = I_local_x1 + A1 * (y1 - Cy)**2
        Iy1 = I_local_y1 + A1 * (x1 - Cx)**2

        I_local_x2 = (B * h**3) / 12
        I_local_y2 = (h * B**3) / 12
        Ix2 = I_local_x2 + A2 * (y2 - Cy)**2
        Iy2 = I_local_y2 + A2 * (x2 - Cx)**2

        Ix_total = Ix1 + Ix2
        Iy_total = Iy1 + Iy2

        # 4. Raio de Giração (r = sqrt(I/A))
        rx = math.sqrt(Ix_total / A_total)
        ry = math.sqrt(Iy_total / A_total)

        # 5. Módulo de Resistência (W = I / y)
        y_superior = H - Cy
        y_inferior = Cy
        x_direita = B - Cx
        x_esquerda = Cx

        Wxs = Ix_total / y_superior if y_superior > 0 else float('inf')
        Wxi = Ix_total / y_inferior if y_inferior > 0 else float('inf')
        Wyd = Iy_total / x_direita if x_direita > 0 else float('inf')
        Wye = Iy_total / x_esquerda if x_esquerda > 0 else float('inf')

        # Formatar a saída
        u = unidade_saida_comprimento
        u3 = u + '³'
        conv_vol = {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}

        resultado = (
            f"Área (A): {_converter_de_base(A_total, u+'²', CONVERSOES_AREA):.4f} {u}²\n"
            f"Centro de Gravidade (Cx, Cy): ({_converter_de_base(Cx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(Cy, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Momento de Inércia (Ix, Iy): ({_converter_de_base(Ix_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}, {_converter_de_base(Iy_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}) {u}⁴\n"
            f"Raio de Giração (rx, ry): ({_converter_de_base(rx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(ry, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Módulo de Resistência:\n  Wxs: {_converter_de_base(Wxs, u3, conv_vol):.4f} {u3} | Wxi: {_converter_de_base(Wxi, u3, conv_vol):.4f} {u3}\n  Wyd: {_converter_de_base(Wyd, u3, conv_vol):.4f} {u3} | Wye: {_converter_de_base(Wye, u3, conv_vol):.4f} {u3}"
        )
        return resultado

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique todos os valores e unidades."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_propriedades_perfil_T(dados, unidade_saida_comprimento):
    try:
        # Extrair dimensões do perfil T
        B_info = next((item for item in dados if item["tipo"] == "Largura da Mesa (B)"), None)
        H_info = next((item for item in dados if item["tipo"] == "Altura Total (H)"), None)
        b_info = next((item for item in dados if item["tipo"] == "Espessura da Alma (b)"), None)
        h_info = next((item for item in dados if item["tipo"] == "Espessura da Mesa (h)"), None)

        if not all([B_info, H_info, b_info, h_info]):
            return "Erro: Forneça todas as 4 dimensões do perfil T (B, H, b, h)."

        # Converter todas as dimensões para a unidade base (metros)
        B = _converter_para_base(float(B_info["valor"].replace(',', '.')), B_info["unidade"], CONVERSOES_COMPRIMENTO)
        H = _converter_para_base(float(H_info["valor"].replace(',', '.')), H_info["unidade"], CONVERSOES_COMPRIMENTO)
        b = _converter_para_base(float(b_info["valor"].replace(',', '.')), b_info["unidade"], CONVERSOES_COMPRIMENTO)
        h = _converter_para_base(float(h_info["valor"].replace(',', '.')), h_info["unidade"], CONVERSOES_COMPRIMENTO)

        if not (B > b > 0 and H > h > 0):
            return "Erro: As dimensões devem ser lógicas (B > b, H > h) e positivas."

        # Dividir o T em dois retângulos
        # Retângulo 1 (Mesa/Flange - horizontal)
        A1 = B * h
        y1 = H - (h / 2)

        # Retângulo 2 (Alma/Web - vertical)
        A2 = b * (H - h)
        y2 = (H - h) / 2

        # 1. Área Total
        A_total = A1 + A2

        # 2. Centro de Gravidade (Cx, Cy)
        Cx = B / 2  # Devido à simetria
        Cy = (A1 * y1 + A2 * y2) / A_total

        # 3. Momento de Inércia (Teorema dos Eixos Paralelos)
        # I = I_local + A * d^2
        I_local_x1 = (B * h**3) / 12
        Ix1 = I_local_x1 + A1 * (y1 - Cy)**2

        I_local_x2 = (b * (H - h)**3) / 12
        Ix2 = I_local_x2 + A2 * (y2 - Cy)**2

        Ix_total = Ix1 + Ix2
        # Para Iy, os eixos locais já estão alinhados com o eixo de simetria, então d_x = 0
        Iy_total = (h * B**3) / 12 + ((H - h) * b**3) / 12

        # 4. Raio de Giração (r = sqrt(I/A))
        rx = math.sqrt(Ix_total / A_total)
        ry = math.sqrt(Iy_total / A_total)

        # 5. Módulo de Resistência (W = I / y)
        Wxs = Ix_total / (H - Cy) if (H - Cy) > 0 else float('inf')
        Wxi = Ix_total / Cy if Cy > 0 else float('inf')
        Wy = Iy_total / (B / 2) if B > 0 else float('inf') # Simétrico, então Wye = Wyd

        # Formatar a saída
        u = unidade_saida_comprimento
        resultado = (
            f"Área (A): {_converter_de_base(A_total, u+'²', CONVERSOES_AREA):.4f} {u}²\n"
            f"Centro de Gravidade (Cx, Cy): ({_converter_de_base(Cx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(Cy, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Momento de Inércia (Ix, Iy): ({_converter_de_base(Ix_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}, {_converter_de_base(Iy_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}) {u}⁴\n"
            f"Raio de Giração (rx, ry): ({_converter_de_base(rx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(ry, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Módulo de Resistência:\n  Wxs: {_converter_de_base(Wxs, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³ | Wxi: {_converter_de_base(Wxi, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³\n  Wy: {_converter_de_base(Wy, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³"
        )
        return resultado

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique todos os valores e unidades."
    except Exception as e:
        return f"Erro inesperado: {e}"


def calcular_propriedades_perfil_I(dados, unidade_saida_comprimento):
    try:
        # Extrair dimensões do perfil I
        B_sup_info = next((item for item in dados if item["tipo"] == "Largura da Mesa Superior (I)"), None)
        h_sup_info = next((item for item in dados if item["tipo"] == "Espessura da Mesa Superior (I)"), None)
        B_inf_info = next((item for item in dados if item["tipo"] == "Largura da Mesa Inferior (i)"), None)
        h_inf_info = next((item for item in dados if item["tipo"] == "Espessura da Mesa Inferior (i)"), None)
        H_info = next((item for item in dados if item["tipo"] == "Altura Total (H)"), None)
        b_info = next((item for item in dados if item["tipo"] == "Espessura da Alma (b)"), None)

        if not all([B_sup_info, h_sup_info, B_inf_info, h_inf_info, H_info, b_info]):
            return "Erro: Forneça todas as 6 dimensões do perfil I."

        # Converter todas as dimensões para a unidade base (metros)
        B_sup = _converter_para_base(float(B_sup_info["valor"].replace(',', '.')), B_sup_info["unidade"], CONVERSOES_COMPRIMENTO)
        h_sup = _converter_para_base(float(h_sup_info["valor"].replace(',', '.')), h_sup_info["unidade"], CONVERSOES_COMPRIMENTO)
        B_inf = _converter_para_base(float(B_inf_info["valor"].replace(',', '.')), B_inf_info["unidade"], CONVERSOES_COMPRIMENTO)
        h_inf = _converter_para_base(float(h_inf_info["valor"].replace(',', '.')), h_inf_info["unidade"], CONVERSOES_COMPRIMENTO)
        H = _converter_para_base(float(H_info["valor"].replace(',', '.')), H_info["unidade"], CONVERSOES_COMPRIMENTO)
        b = _converter_para_base(float(b_info["valor"].replace(',', '.')), b_info["unidade"], CONVERSOES_COMPRIMENTO)

        # 1. Component Properties (Área e Centróide Local)
        h_alma = H - h_sup - h_inf
        B_max = max(B_sup, B_inf) # Largura máxima do perfil (para centralização)

        if h_alma <= 0 or B_max <= 0 or b <= 0:
            return "Erro: As dimensões devem ser lógicas (H > h_sup+h_inf) e positivas."

        # Retângulo 1 (Mesa Superior)
        A1 = B_sup * h_sup
        y1 = H - h_sup / 2
        x1 = B_max / 2 # Centrado na largura máxima

        # Retângulo 2 (Alma)
        A2 = h_alma * b
        y2 = h_inf + h_alma / 2
        x2 = B_max / 2 # Centrado na largura máxima

        # Retângulo 3 (Mesa Inferior)
        A3 = B_inf * h_inf
        y3 = h_inf / 2
        x3 = B_max / 2 # Centrado na largura máxima

        A_total = A1 + A2 + A3

        # 2. Centro de Gravidade (Cx, Cy)
        # Para perfis estruturais, assumimos centralização horizontal:
        Cx = B_max / 2 
        # Cálculo de Cy: (A1*y1 + A2*y2 + A3*y3) / A_total
        Cy = (A1*y1 + A2*y2 + A3*y3) / A_total

        # 3. Momento de Inércia (Teorema dos Eixos Paralelos)
        
        # Ix (em relação ao eixo x-x no Cy)
        Ix1 = (B_sup * h_sup**3)/12 + A1 * (y1 - Cy)**2
        Ix2 = (b * h_alma**3)/12 + A2 * (y2 - Cy)**2
        Ix3 = (B_inf * h_inf**3)/12 + A3 * (y3 - Cy)**2
        Ix_total = Ix1 + Ix2 + Ix3

        # Iy (em relação ao eixo y-y no Cx)
        # O termo do eixo paralelo é zero, pois x1=x2=x3=Cx
        Iy1 = (h_sup * B_sup**3)/12 
        Iy2 = (h_alma * b**3)/12    
        Iy3 = (h_inf * B_inf**3)/12 
        Iy_total = Iy1 + Iy2 + Iy3

        # 4. Raio de Giração (r = sqrt(I/A))
        rx = math.sqrt(Ix_total / A_total)
        ry = math.sqrt(Iy_total / A_total)

        # 5. Módulo de Resistência (W = I / y)
        # O termo de conversão para L⁴ precisa ser definido:
        CONVERSOES_INERCIA = {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}
        # O termo de conversão para L³ (Volume) já estava definido:
        conv_vol = {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}

        # Wx (Tensão na borda superior e inferior)
        Wxs = Ix_total / (H - Cy) if (H - Cy) > 1e-9 else float('inf') # Mesa Superior (Top)
        Wxi = Ix_total / Cy if Cy > 1e-9 else float('inf')             # Mesa Inferior (Bottom)
        
        # Wy (Tensão na borda mais distante do eixo y)
        # Distância máxima é Cx e (B_max - Cx). Como Cx = B_max/2, são iguais.
        dist_y = B_max / 2
        Wyd = Iy_total / dist_y if dist_y > 1e-9 else float('inf') # Lado Direito/Esquerdo (D/E)
        Wye = Wyd # Devido à simetria horizontal

        # Formatar a saída
        u = unidade_saida_comprimento
        u2 = u + '²'
        u3 = u + '³'
        u4 = u + '⁴'

        resultado = (
            f"Área (A): {_converter_de_base(A_total, u2, CONVERSOES_AREA):.4f} {u2}\n"
            f"Centro de Gravidade (Cx, Cy): ({_converter_de_base(Cx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(Cy, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Momento de Inércia (Ix, Iy): ({_converter_de_base(Ix_total, u4, CONVERSOES_INERCIA):.4f}, {_converter_de_base(Iy_total, u4, CONVERSOES_INERCIA):.4f}) {u4}\n"
            f"Raio de Giração (rx, ry): ({_converter_de_base(rx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(ry, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Módulo de Resistência:\n"
            f"  Wxs (Superior): {_converter_de_base(Wxs, u3, conv_vol):.4f} {u3} | Wxi (Inferior): {_converter_de_base(Wxi, u3, conv_vol):.4f} {u3}\n"
            f"  Wyd (Direita): {_converter_de_base(Wyd, u3, conv_vol):.4f} {u3} | Wye (Esquerda): {_converter_de_base(Wye, u3, conv_vol):.4f} {u3}"
        )
        return resultado

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique se os valores são números e se as unidades estão corretas."
    except Exception as e:
        return f"Erro inesperado: {e}"


def calcular_propriedades_retangulo_vazado(dados, unidade_saida_comprimento):
    try:
        # Extrair dimensões do retângulo vazado
        B_info = next((item for item in dados if item["tipo"] == "Base do Retângulo (B)"), None)
        H_info = next((item for item in dados if item["tipo"] == "Altura do Retângulo (H)"), None)
        e_info = next((item for item in dados if item["tipo"] == "Espessura do Retângulo (e)"), None)

        if not all([B_info, H_info, e_info]):
            return "Erro: Forneça a Base (B), Altura (H) e Espessura (e) do retângulo."

        # Converter todas as dimensões para a unidade base (metros)
        B = _converter_para_base(float(B_info["valor"].replace(',', '.')), B_info["unidade"], CONVERSOES_COMPRIMENTO)
        H = _converter_para_base(float(H_info["valor"].replace(',', '.')), H_info["unidade"], CONVERSOES_COMPRIMENTO)
        e = _converter_para_base(float(e_info["valor"].replace(',', '.')), e_info["unidade"], CONVERSOES_COMPRIMENTO)

        # Dimensões internas
        b_interno = B - 2 * e
        h_interno = H - 2 * e

        if b_interno <= 0 or h_interno <= 0:
            return "Erro: A espessura (2x) é maior ou igual à Base ou Altura."

        # 1. Área Total (Área Externa - Área Interna)
        A_total = (B * H) - (b_interno * h_interno)

        # 2. Centro de Gravidade (Cx, Cy) - Dupla simetria
        Cx = B / 2
        Cy = H / 2

        # 3. Momento de Inércia (Inércia Externa - Inércia Interna)
        Ix_total = (B * H**3) / 12 - (b_interno * h_interno**3) / 12
        Iy_total = (H * B**3) / 12 - (h_interno * b_interno**3) / 12

        # 4. Raio de Giração (r = sqrt(I/A))
        rx = math.sqrt(Ix_total / A_total)
        ry = math.sqrt(Iy_total / A_total)

        # 5. Módulo de Resistência (W = I / y_max)
        Wx = Ix_total / (H / 2) if H > 0 else float('inf')
        Wy = Iy_total / (B / 2) if B > 0 else float('inf')

        # Formatar a saída
        u = unidade_saida_comprimento
        resultado = (
            f"Área (A): {_converter_de_base(A_total, u+'²', CONVERSOES_AREA):.4f} {u}²\n"
            f"Centro de Gravidade (Cx, Cy): ({_converter_de_base(Cx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(Cy, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Momento de Inércia (Ix, Iy): ({_converter_de_base(Ix_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}, {_converter_de_base(Iy_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}) {u}⁴\n"
            f"Raio de Giração (rx, ry): ({_converter_de_base(rx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(ry, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Módulo de Resistência:\n  Wx: {_converter_de_base(Wx, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³\n  Wy: {_converter_de_base(Wy, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³"
        )
        return resultado

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique todos os valores e unidades."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_propriedades_circulo_vazado(dados, unidade_saida_comprimento):
    try:
        # Extrair dimensões do círculo vazado
        D_info = next((item for item in dados if item["tipo"] == "Diâmetro Externo do Círculo (D)"), None)
        e_info = next((item for item in dados if item["tipo"] == "Espessura do Círculo (e)"), None)

        if not all([D_info, e_info]):
            return "Erro: Forneça o Diâmetro Externo (D) e a Espessura (e) do círculo."

        # Converter todas as dimensões para a unidade base (metros)
        D = _converter_para_base(float(D_info["valor"].replace(',', '.')), D_info["unidade"], CONVERSOES_COMPRIMENTO)
        e = _converter_para_base(float(e_info["valor"].replace(',', '.')), e_info["unidade"], CONVERSOES_COMPRIMENTO)

        # Dimensão interna
        d_interno = D - 2 * e

        if d_interno <= 0:
            return "Erro: A espessura (2x) é maior ou igual ao Diâmetro Externo."

        # 1. Área Total
        A_total = (math.pi / 4) * (D**2 - d_interno**2)

        # 2. Centro de Gravidade (Cx, Cy) - Dupla simetria
        Cx = D / 2
        Cy = D / 2

        # 3. Momento de Inércia (Ix = Iy para círculo)
        I_total = (math.pi / 64) * (D**4 - d_interno**4)

        # 4. Raio de Giração (rx = ry para círculo)
        r_total = math.sqrt(I_total / A_total)

        # 5. Módulo de Resistência (Wx = Wy para círculo)
        W_total = I_total / (D / 2) if D > 0 else float('inf')

        # Formatar a saída
        u = unidade_saida_comprimento
        resultado = (
            f"Área (A): {_converter_de_base(A_total, u+'²', CONVERSOES_AREA):.4f} {u}²\n"
            f"Centro de Gravidade (Cx, Cy): ({_converter_de_base(Cx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(Cy, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Momento de Inércia (I): {_converter_de_base(I_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f} {u}⁴\n"
            f"Raio de Giração (r): {_converter_de_base(r_total, u, CONVERSOES_COMPRIMENTO):.4f} {u}\n"
            f"Módulo de Resistência (W): {_converter_de_base(W_total, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³"
        )
        return resultado

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique todos os valores e unidades."
    except Exception as e:
        return f"Erro inesperado: {e}"

def calcular_propriedades_trapezio(dados, unidade_saida_comprimento):
    try:
        # Extrair dimensões do trapézio
        B_info = next((item for item in dados if item["tipo"] == "Base Superior do Trapézio"), None)
        b_info = next((item for item in dados if item["tipo"] == "Base Inferior do Trapézio"), None)
        H_info = next((item for item in dados if item["tipo"] == "Altura do Trapézio"), None)

        if not all([B_info, b_info, H_info]):
            return "Erro: Forneça a Base Superior, Base Inferior e Altura."

        # Converter todas as dimensões para a unidade base (metros)
        base_sup = _converter_para_base(float(B_info["valor"].replace(',', '.')), B_info["unidade"], CONVERSOES_COMPRIMENTO)
        base_inf = _converter_para_base(float(b_info["valor"].replace(',', '.')), b_info["unidade"], CONVERSOES_COMPRIMENTO)
        H = _converter_para_base(float(H_info["valor"].replace(',', '.')), H_info["unidade"], CONVERSOES_COMPRIMENTO)

        # Identificar qual é a base maior (B) e a menor (b)
        B = max(base_sup, base_inf)
        b = min(base_sup, base_inf)

        a = (B - b) / 2 # Assumindo trapézio isósceles

        if not (B > 0 and b > 0 and H > 0):
            return "Erro: As dimensões devem ser valores positivos."

        # 1. Área Total
        A_total = ((B + b) / 2) * H

        # 2. Centro de Gravidade (Cx, Cy)
        Cx = B / 2 # Devido à simetria do trapézio isósceles
        # Fórmula para Cy a partir da base inferior (b)
        # A fórmula padrão calcula a partir da base maior. Vamos ajustar.
        # Cy a partir da base MAIOR (B)
        Cy_from_B = (H / 3) * ((2 * b + B) / (b + B))

        # Se a base inferior for a maior, o Cy é calculado a partir dela.
        Cy = Cy_from_B if base_inf == B else H - Cy_from_B
        # 3. Momento de Inércia (usando Teorema dos Eixos Paralelos na decomposição)
        # Decomposição em 1 retângulo e 2 triângulos
        A_ret = b * H
        A_tri = a * H # Área dos dois triângulos juntos

        # Ix (Momento de Inércia em relação ao eixo X)
        Ix_ret = (b * H**3)/12 + A_ret * (H/2 - Cy)**2
        Ix_tri = (a * H**3)/18 + A_tri * (H/3 - Cy)**2 # Para os dois triângulos
        Ix_total = Ix_ret + Ix_tri

        # Iy (Momento de Inércia em relação ao eixo Y para trapézio isósceles)
        # Fórmula padrão: (H / 48) * (B + b) * (B^2 + 7b^2) -> Incorreta
        # Fórmula correta por decomposição:
        Iy_total = (H / 48) * (B**3 + b**3 + 3*b*B**2 + 3*B*b**2) # Incorreta
        # Fórmula correta e mais simples para Iy de um trapézio isósceles:
        Iy_total = (H / 48) * (B + b) * (B**2 + b**2)

        # 4. Raio de Giração
        rx = math.sqrt(Ix_total / A_total)
        ry = math.sqrt(Iy_total / A_total)

        # 5. Módulo de Resistência
        Wxs = Ix_total / (H - Cy)
        Wxi = Ix_total / Cy
        # Como é simétrico, Wye = Wyd
        Wy = Iy_total / (B / 2)

        # Formatar a saída
        u = unidade_saida_comprimento
        resultado = (
            f"Área (A): {_converter_de_base(A_total, u+'²', CONVERSOES_AREA):.4f} {u}²\n"
            f"Centro de Gravidade (Cx, Cy): ({_converter_de_base(Cx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(Cy, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Momento de Inércia (Ix, Iy): ({_converter_de_base(Ix_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}, {_converter_de_base(Iy_total, u+'⁴', {'m⁴': 1.0, 'cm⁴': 1e-8, 'mm⁴': 1e-12}):.4f}) {u}⁴\n"
            f"Raio de Giração (rx, ry): ({_converter_de_base(rx, u, CONVERSOES_COMPRIMENTO):.4f}, {_converter_de_base(ry, u, CONVERSOES_COMPRIMENTO):.4f}) {u}\n"
            f"Módulo de Resistência:\n  Wxs: {_converter_de_base(Wxs, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³ | Wxi: {_converter_de_base(Wxi, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³\n  Wy: {_converter_de_base(Wy, u+'³', {'m³': 1.0, 'cm³': 1e-6, 'mm³': 1e-9}):.4f} {u}³"
        )
        return resultado

    except (ValueError, TypeError, ZeroDivisionError, KeyError) as e:
        return f"Erro nos dados de entrada: {e}. Verifique todos os valores e unidades."
    except Exception as e:
        return f"Erro inesperado: {e}"