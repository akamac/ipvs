#!/usr/bin/env python3

from gnlpy.ipvs import IpvsClient, Pool
import json
import signal


def load_pools():
    print('Loading pools from config')
    with open('/config/ipvs.json') as f:
        return json.loads(f.read())


def reload_ipvs(client, pools):
    print('Updating IPVS configuration')
    try:
        pools_to_load = Pool.load_pools_from_json_list(pools)
    except:
        print('Invalid pool configuration')
        return

    existing_pools = client.get_pools()

    services_to_load = [p.service_ for p in pools_to_load]
    existing_services = [p.service_ for p in existing_pools]

    for service in services_to_load:
        if service not in existing_services:
            print('Adding VIP {}:{}'.format(service.vip(), service.port()))
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
        existing_pool = next(filter(lambda p: p.service_ == pool.service_, existing_pools))
        for dest in pool.dests_:
            if dest.ip() not in [d.ip() for d in existing_pool.dests_]:
                client.add_dest(pool.service_.vip(),
                                pool.service_.port(),
                                protocol=pool.service_.proto_num(),
                                rip=dest.ip(),
                                weight=dest.weight(),
                                method=dest.fwd_method())
        for dest in existing_pool.dests_:
            if dest.ip() not in [d.ip() for d in pool.dests_]:
                client.del_dest(pool.service_.vip(),
                                pool.service_.port(),
                                protocol=pool.service_.proto_num(),
                                rip=dest.ip())


def flush_n_exit(client):
    print('Received termination request. Flushing config')
    client.flush()
    raise SystemExit


def main():
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