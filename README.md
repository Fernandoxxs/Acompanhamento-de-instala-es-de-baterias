# Painel executivo de baterias

Dashboard interativo em Streamlit para analisar planilhas CSV e Excel, com visual
executivo em verde, laranja e azul-petróleo. Inclui cartões de baterias instaladas
e pendentes, Executado OMR baseado no texto OMR na data planejada, taxa de
conclusão, justificativas, filtros por UF e período, gráficos de categoria e de
linha do tempo, painel analítico flutuante e exportação dos dados filtrados.
O cartão laranja de baterias não instaladas pode ser clicado para abrir as
justificativas correspondentes à seleção atual.
Os gráficos seguem um estilo executivo em cartões escuros e mostram a evolução
temporal, a distribuição por UF, as instalações por categoria e a comparação
por UF entre Baterias Instaladas e Executado OMR, além do percentual de conclusão
por UF. O gráfico de percentual por UF inicia oculto e pode ser exibido pelo
botão correspondente.

O card de baterias não instaladas inicia oculto após a importação. Use o botão
correspondente para exibi-lo; quando exibido, clique no card para abrir as
justificativas da seleção atual.

## Executar

1. Instale Python 3.10 a 3.14 (recomendado: Python 3.12).
2. No terminal, abra a pasta do projeto e instale as dependências:

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Inicie o dashboard:

   ```powershell
   py -m streamlit run app.py
   ```

4. No navegador, use **Pesquisar arquivo** para carregar um arquivo `.csv`,
   `.xlsx` ou `.xls`. Após a importação, a tabela com os dados fica oculta;
   use **Mostrar dados importados** para exibi-la.

O painel sugere colunas de quantidade, UF, data, status, justificativa e
localização. Todos os cabeçalhos da planilha ficam disponíveis em cada seletor
do mapeamento; confira ou ajuste as sugestões na barra lateral. Para a planilha
com as colunas `Data Instalação` e `Data planejada instalação`, o card de baterias
instaladas conta as datas válidas em `Data Instalação`, e o card Executado OMR conta
as células de `Data planejada instalação` que contêm “EXECUTADO OMR”
(sem diferenciar maiúsculas e minúsculas). Células vazias (incluindo células com
espaços) em `Data Instalação`, exceto linhas identificadas como OMR, são contadas
como pendências. A taxa de conclusão considera uma linha concluída se tiver uma
data válida em `Data Instalação` ou “EXECUTADO OMR” em `Data planejada instalação`;
cada linha é contada uma só vez, e a taxa divide essas linhas concluídas pelo total
de linhas filtradas. Outros valores não reconhecidos ficam sem classificação.
Os filtros de categoria também oferecem
`(Células vazias)` para que registros sem valor não desapareçam da seleção padrão.
Se o arquivo tiver cabeçalhos genéricos (como `Unnamed: 0`) e a linha seguinte
contiver os nomes das colunas, o painel promove essa linha automaticamente a
cabeçalho e a remove dos dados analisados.
Os gráficos mostram a evolução por data, a distribuição das instalações por UF
e a comparação de Baterias Instaladas e Executado OMR por UF. O gráfico de
percentual por UF divide as linhas concluídas (data válida ou OMR) pelo total de
linhas filtradas em cada UF. Essa contagem de instalações não soma a coluna de
quantidade. O calendário e os demais filtros
atualizam cartões e gráficos. Datas ISO como `2026-09-11 00:00:00` são reconhecidas
sem inverter dia e mês.
O status é interpretado automaticamente quando contém valores como “Instalada”,
“Não instalada” ou “Pendente”; se não houver um status reconhecível, a data da
instalação é usada como alternativa. A linha do tempo pode ser agrupada por dia,
semana ou mês. CSVs com separador vírgula ou ponto e vírgula são detectados
automaticamente.
