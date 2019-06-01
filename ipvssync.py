#!/usr/bin/env python3.7
"""
Reloads IPVS configuration from /config/ipvs.json upon receiving SIGHUP signal.
For json format see facebook/gnlpy on GitHub.
"""

import json
import signal
from gnlpy.ipvs import IpvsClient, Pool


def load_pools(): # pragma: no cover
    """Load pool configuration from json file"""
    print('Loading pools from config')
    with open('/config/ipvs.json') as file:
        return json.loads(file.read())


def reload_ipvs(client: IpvsClient, pools: list) -> None:
    """Reload IPVS configuration given the passed list of pools"""
    print('Updating IPVS configuration')
    try:
        pools_to_load = Pool.load_pools_from_json_list(pools)
    except: # pylint: disable=bare-except
        print('Invalid pool configuration')
        return

    existing_pools = client.get_pools()

    services_to_load = [p.service() for p in pools_to_load]
    existing_services = [p.service() for p in existing_pools]

    for service in services_to_load:
        if service not in existing_services:
            print(f"Adding VIP {service.vip()}:{service.port()}")
            client.add_service(service.vip(),
                               service.port(),
                               protocol=service.proto_num(),
                               sched_name=service.sched())

    for service in existing_services:
        if service not in services_to_load:
            client.del_service(service.vip(),
                               service.port(),
                               protocol=service.proto_num())

    existing_pools = client.get_pools()
    for pool in pools_to_load:
        existing_pool = next(filter(lambda p: p.service() == pool.service(), existing_pools))
        for dest in pool.dests():
            if dest.ip() not in [d.ip() for d in existing_pool.dests()]:
                client.add_dest(pool.service().vip(),
                                pool.service().port(),
                                protocol=pool.service().proto_num(),
                                rip=dest.ip(),
                                weight=dest.weight(),
                                method=dest.fwd_method())
        for dest in existing_pool.dests():
            if dest.ip() not in [d.ip() for d in pool.dests()]:
                client.del_dest(pool.service().vip(),
                                pool.service().port(),
                                protocol=pool.service().proto_num(),
                                rip=dest.ip())


def flush_n_exit(client: IpvsClient) -> None:
    """Flush IPVS config and exit"""
    print('Received termination request. Flushing config')
    client.flush()
    raise SystemExit


def main(): # pylint: disable=missing-docstring
    client = IpvsClient()
    reload_ipvs(client, load_pools())

    signal.signal(signal.SIGHUP, lambda s, f: reload_ipvs(client, load_pools()))
    signal.signal(signal.SIGINT, lambda s, f: flush_n_exit(client)) # Nomad
    signal.signal(signal.SIGTERM, lambda s, f: flush_n_exit(client)) # Docker
    while True:
        print('Waiting for SIGHUP to reload ipvs config')
        signal.pause()


if __name__ == '__main__':
    main()
