import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Initialize session state for data storage
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        'Nº Pedido', 'Data', 'Empresa', 'Item', 'Quantidade', 'Valor Unitário', 'Valor Total', 'Empenho Nº'
    ])

if 'empenhos' not in st.session_state:
    st.session_state.empenhos = pd.DataFrame(columns=[
        'Empenho Nº', 'Empresa', 'Item', 'Quantidade Empenhada', 'Valor Empenhado'
    ])

# Sidebar menu
menu = st.sidebar.selectbox("Menu", ["Cadastrar Pedido", "Cadastrar Empenho", "Relatórios"])

# Cadastrar Pedido
if menu == "Cadastrar Pedido":
    st.header("📝 Cadastro de Pedido")
    with st.form("pedido_form"):
        num_pedido = st.text_input("Nº Pedido")
        data = st.date_input("Data")
        empresa = st.text_input("Empresa")
        item = st.text_input("Item")
        quantidade = st.number_input("Quantidade", min_value=0, step=1)
        valor_unitario = st.number_input("Valor Unitário", min_value=0.0, step=0.01)
        empenho_num = st.text_input("Empenho Nº")
        submitted = st.form_submit_button("Salvar Pedido")
        if submitted:
            valor_total = quantidade * valor_unitario
            novo_pedido = pd.DataFrame([{
                'Nº Pedido': num_pedido,
                'Data': data,
                'Empresa': empresa,
                'Item': item,
                'Quantidade': quantidade,
                'Valor Unitário': valor_unitario,
                'Valor Total': valor_total,
                'Empenho Nº': empenho_num
            }])
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, novo_pedido], ignore_index=True)
            st.success("Pedido salvo com sucesso!")

    st.subheader("📋 Pedidos Registrados")
    st.dataframe(st.session_state.pedidos)

# Cadastrar Empenho
elif menu == "Cadastrar Empenho":
    st.header("💼 Cadastro de Empenho")
    with st.form("empenho_form"):
        empenho_num = st.text_input("Empenho Nº")
        empresa = st.text_input("Empresa")
        item = st.text_input("Item")
        quantidade_empenhada = st.number_input("Quantidade Empenhada", min_value=0, step=1)
        valor_empenhado = st.number_input("Valor Empenhado", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Salvar Empenho")
        if submitted:
            novo_empenho = pd.DataFrame([{
                'Empenho Nº': empenho_num,
                'Empresa': empresa,
                'Item': item,
                'Quantidade Empenhada': quantidade_empenhada,
                'Valor Empenhado': valor_empenhado
            }])
            st.session_state.empenhos = pd.concat([st.session_state.empenhos, novo_empenho], ignore_index=True)
            st.success("Empenho salvo com sucesso!")

    st.subheader("📋 Empenhos Registrados")
    st.dataframe(st.session_state.empenhos)

# Relatórios
elif menu == "Relatórios":
    st.header("📊 Relatórios de Saldos")

    # Agrupar pedidos por empresa e item
    pedidos_agrupados = st.session_state.pedidos.groupby(['Empresa', 'Item']).agg({
        'Quantidade': 'sum',
        'Valor Total': 'sum'
    }).reset_index().rename(columns={
        'Quantidade': 'Quantidade Pedida',
        'Valor Total': 'Valor Pedido'
    })

    # Agrupar empenhos por empresa e item
    empenhos_agrupados = st.session_state.empenhos.groupby(['Empresa', 'Item']).agg({
        'Quantidade Empenhada': 'sum',
        'Valor Empenhado': 'sum'
    }).reset_index()

    # Mesclar dados
    saldo_df = pd.merge(empenhos_agrupados, pedidos_agrupados, on=['Empresa', 'Item'], how='left').fillna(0)
    saldo_df['Saldo Quantidade'] = saldo_df['Quantidade Empenhada'] - saldo_df['Quantidade Pedida']
    saldo_df['Saldo Valor'] = saldo_df['Valor Empenhado'] - saldo_df['Valor Pedido']

    st.subheader("📋 Saldo por Item e Empresa")
    st.dataframe(saldo_df)

    # Gráfico de uso por empresa
    st.subheader("📈 Gráfico de Uso por Empresa")
    if not saldo_df.empty:
        fig, ax = plt.subplots()
        saldo_df.groupby('Empresa')['Valor Empenhado'].sum().plot(kind='bar', ax=ax)
        ax.set_ylabel("Valor Empenhado")
        st.pyplot(fig)
