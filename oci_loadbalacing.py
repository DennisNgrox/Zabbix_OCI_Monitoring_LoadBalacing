# Desenvolvido por: Dennis da Silva
# https://github.com/DennisNgrox/Zabbix_OCI_Monitoring_LoadBalacing

#!/bin/python3

import oci
import json
import sys


config = {
    "user": "",
    "fingerprint": "",
    "key_file": "",
    "tenancy": "",
    "region": ""
}


lb_client = oci.load_balancer.LoadBalancerClient(config)


def main(compartment_id, backend_name_filter=None):
    try:
        # Listar todos os Load Balancers no compartimento
        load_balancers_response = lb_client.list_load_balancers(compartment_id)
        load_balancers = load_balancers_response.data

        # Dicionário para armazenar os resultados
        output_data = []

        # Iterar sobre os Load Balancers
        for lb in load_balancers:
            lb_id = lb.id
            lb_name = lb.display_name

            # Obter os detalhes do Load Balancer
            lb_details = lb_client.get_load_balancer(lb_id).data

            # Iterar sobre os Backend Sets
            for backend_set_name, backend_set in lb_details.backend_sets.items():

                # Obter detalhes do Backend Set
                backend_set_details = lb_client.get_backend_set(
                    load_balancer_id=lb_id,
                    backend_set_name=backend_set_name
                ).data

                # Iterar sobre os backends do Backend Set
                for backend in backend_set_details.backends:
                    backend_name = backend.name
                    backend_ip_address = backend.ip_address  # Pegando o endereço IP do backend

                    # Verificar se o Backend Name é o que estamos procurando
                    if backend_name_filter and backend_name != backend_name_filter:
                        continue  # Ignorar se não corresponder ao filtro

                    try:
                        # Obter o status de saúde dos backends para o Backend Set
                        backend_health_response = lb_client.get_backend_health(
                            load_balancer_id=lb_id,
                            backend_set_name=backend_set_name,
                            backend_name=backend_name
                        )

                        # Obter o status geral dos Health Checks
                        health_check_results = backend_health_response.data.health_check_results
                        health_check_status = backend_health_response.data.status

                        # Adicionar o Load Balancer, Backend Set, status e o endereço IP ao resultado final
                        output_data.append({
                            "LoadBalancer": lb_name,
                            "BackendSet": backend_set_name,
                            "BackendName": backend_name,
                            "BackendIPAddress": backend_ip_address,  # Adicionando o IP do backend
                            "Status": health_check_status
                        })

                    except oci.exceptions.ServiceError as e:
                        print(
                            f"    Error retrieving health for backend {backend_name}: {e}")

        # Exibir o resultado final em JSON
        print(json.dumps(output_data, indent=2))

    except oci.exceptions.ServiceError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <compartment_id> [backend_name]")
        sys.exit(1)

    compartment_id = sys.argv[1]
    backend_name_filter = sys.argv[2] if len(sys.argv) > 2 else None

    main(compartment_id, backend_name_filter)
