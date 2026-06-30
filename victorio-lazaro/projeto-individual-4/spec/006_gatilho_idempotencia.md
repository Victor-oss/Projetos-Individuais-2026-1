## Projeto

Eu estou fazendo um pipeline de extração de dados de mobiliárias

#### Tarefas
- O script scrapper.py anexado faz o webscrapping da url's das prévias operacionais de 6 mobiliárias ao longo dos anos. Eu quero que você crie um projeto fast api que rode esse script a cada 10 minutos. Modifique o script para que ele retorne uma lista onde cada item da lista deve possuir 3 campos no formato string => i) nome da empresa ao qual esse arquivo pertence (MRV, Pacaembu, Plano & Plano, Tenda, Cury e Direcional); ii) url do arquivo; iii) '{trimeste do arquivo}/{ano do arquivo}
- Deve existir um banco postgresql e uma tabela scrappings_previas_operacionas com as mesmas colunas retornadas pelo script citado anteriormente (nome da empresa, url e trimeste com ano do arquivo) mais um campo id. Ao terminar de executar o scrapper.py deve-se fazer uma consulta de todos os registros em scrappings_previas_operacionas e fazer um set com as urls encontradas. Se uma URL retornada pelo script não existir no set, você deve adicionar esse novo registro na tabela
- use um docker-compose para montar a aplicação com esses dois containers