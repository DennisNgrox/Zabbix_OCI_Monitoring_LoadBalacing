## Monitoramento OCI LoadBalacing Health Check State

![https://img.shields.io/badge/version-v1-green](https://img.shields.io/badge/version-v1-green)

Passo a passo:

##### Template:

- Importar o template que se encontra nesse repositório no Zabbix.
- Alterar a Macro do template {$OID_COMPARTMENT_LOADBALACING} pelo valor da ID do compartimento aonde se encontra os load balancing

##### O template possui um item e um discovery:
```
- Item:
Type: External Scripts
LoadBalancing Get - Responsável por trazer todos os load balacings e seus backends.
```

```
Discovery:
Type: Item dependente
Load Balancing Health Check - Adiciona os valores do item LoadBalacing GET em macros.
Item prototype:
Type: External Scripts
Health Check Load Balancing Name: {#LOAD_NAME}: BackEnd {#LOAD_BACKEND_NAME} --- Responsável por criar os itens com o nome do Load Balacing, o nome do backend e nele será coletado o valor do Heath Check

Trigger Prototype:
LoadBalancer {#LOAD_NAME} : Backend {#LOAD_BACKEND_NAME} - Status: {ITEM.VALUE}
Expression: 'find(/Oracle Cloud Load Balacing by HTTP/oci_loadbalacing.py[{$OID_COMPARTMENT_LOADBALANCING},{#LOAD_BACKEND_NAME}],,"like","CRITICAL")=1'
- Alarme ocorrerá quando o valor retornado for CRITICAL, é possível editar a trigger para adicionar outros valores possíveis.
```

-------------------

#### Script:

- Necessário adicionar o script no servidor Zabbix (Server/Proxy) na pasta de scripts externos do Zabbix, por padrão: /usr/lib/zabbix/externalscripts

Dar permissão de execução e tornar o Zabbix dono do script:
```sh
chown zabbix.zabbix oci_loadbalacing.py
chmod +x zabbix.zabbix oci_loadbalacing.py
```
instalar os requerimentos:
```py
pip install -r requirements.txt 
```
Deixei o arquivo de requerimentos nesse diretório do github

1 ° Observação importante:
- No inicio do script na linha 4 tem o valor: #!/bin/python3 
- Caso o utilitario do seu python esteja em outro caminho, editar para o caminho correto. Para saber aonde está seu utilitário execute: which python3

2 ° Observação importante:

- É necessário definir os seguintes valores dentro do script:
```
config = {
    "user": "",
    "fingerprint": "",
    "key_file": "",
    "tenancy": "",
    "region": ""
}
```

Esses valores são para realizar a conexão na OCI (Oracle Cloud)


Para testar o script através da linha de comando:
```
python3 oci_loadbalacing.py <id_compartment> <backend_set_name> 
```
Se definir o backend_set_name o script buscará informações apenas desse backend em específico se não definir nenhum backend_set_name, o script trará o resultado de todos.
