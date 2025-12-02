from calculos import (
    calcular_tensao_admissivel, 
    calcular_forca_projeto,
    calcular_area_secao,
    determinar_dimensao_apoio,
    calcular_forca_por_apoio,
    calcular_area_por_apoio,
    calcular_deformacao,
    calcular_deformacao_segmentada,
    calcular_propriedades_perfil_L,
    calcular_propriedades_perfil_T,
    calcular_propriedades_perfil_I,
    calcular_propriedades_retangulo_vazado,
    calcular_propriedades_circulo_vazado,
    calcular_propriedades_trapezio
)

def executar_calculo(nome_calculo, conjuntos_de_campos, unidade_saida):
    dados_coletados = _extrair_valores(conjuntos_de_campos)

    if nome_calculo == "Cálculo da Tensão Admissível":
        return calcular_tensao_admissivel(dados_coletados, unidade_saida)
    elif nome_calculo == "Calcular Força de Projeto":
        return calcular_forca_projeto(dados_coletados, unidade_saida)
    elif nome_calculo == "Calcular Força por Apoio":
        return calcular_forca_por_apoio(dados_coletados, unidade_saida)
    elif nome_calculo == "Calcular Área de Projeto":
        return calcular_area_secao(dados_coletados, unidade_saida)
    elif nome_calculo == "Calcular Área por Apoio":
        return calcular_area_por_apoio(dados_coletados, unidade_saida)
    elif nome_calculo == "Determinar Dimensão do Apoio":
        return determinar_dimensao_apoio(dados_coletados, unidade_saida)
    elif nome_calculo == "Cálculo da Deformação (Simples)":
        return calcular_deformacao(dados_coletados, unidade_saida)
    elif nome_calculo == "Cálculo da Deformação (Segmentada)":
        return calcular_deformacao_segmentada(dados_coletados, unidade_saida)
    elif nome_calculo == "Propriedades de Perfil L":
        return calcular_propriedades_perfil_L(dados_coletados, unidade_saida)
    elif nome_calculo == "Propriedades de Perfil T":
        return calcular_propriedades_perfil_T(dados_coletados, unidade_saida)
    elif nome_calculo == "Propriedades de Perfil I":
        return calcular_propriedades_perfil_I(dados_coletados, unidade_saida)
    elif nome_calculo == "Propriedades de Retângulo Vazado":
        return calcular_propriedades_retangulo_vazado(dados_coletados, unidade_saida)
    elif nome_calculo == "Propriedades de Círculo Vazado":
        return calcular_propriedades_circulo_vazado(dados_coletados, unidade_saida)
    elif nome_calculo == "Propriedades de Trapézio":
        return calcular_propriedades_trapezio(dados_coletados, unidade_saida)
    else:
        return f"Cálculo '{nome_calculo}' não implementado."

def _extrair_valores(conjuntos_de_campos):
    dados_coletados = []
    for (combo_opcao, entrada_valor, combo_unidade) in conjuntos_de_campos:
        tipo_campo = combo_opcao.get()
        if tipo_campo == "Escolha um tipo":
            continue

        if tipo_campo == "Segmento":
            if hasattr(combo_opcao.master, 'dados_segmento'):
                dados_segmento = combo_opcao.master.dados_segmento
                dados_segmento['tipo'] = 'Segmento'
                dados_coletados.append(dados_segmento)
        elif entrada_valor.get():
            dados_coletados.append({
                "tipo": tipo_campo,
                "valor": entrada_valor.get(),
                "unidade": combo_unidade.get() if combo_unidade.winfo_ismapped() else "N/A"
            })
    return dados_coletados