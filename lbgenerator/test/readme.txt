Testes do Rest.


A pasta teste no LBGenerator tem como função testar as operações básicas do sistema como POST/GET/PUT/DELETE da BASE e do DOC, validando assim a integridade do sistema cada vez que é feita alterações no código.


Para executar os testes é bem simples.

Você deve abrir o arquivo config_tests.py:

e adicionar a sua url de acesso ao rest nesta linha:

url_ip = 'URL'

em seguida deve executar o seguinte comando:
(apenas um exemplo pois a árvore de diretórios do seu projeto pode estar diferente)
../../../bin/noetests -v test_base.py
../../../bin/noetests -v test_dc.py


Lembrado que as bibliotecas
Unittest2
nosetestes

devem estar instaladas no seu virtualenv

Caso não estejam execute os seguintes comandos:
(apenas um exemplo pois a árvore de diretorios do seu projeto pode estar diferente)

../../bin/pip install nose

../../bin/pip install unittest2
