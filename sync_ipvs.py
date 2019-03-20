from gnlpy.ipvs import IpvsClient, Pool
import json
import signal


def reload_ipvs(signalNumber, frame):
    with open('/ipvs.json') as f:
        pools = json.loads(f.read())

    pools_to_load = Pool.load_pools_from_json_list(pools)
    current_pools = client.get_pools()

    services_to_load = [p.service_ for p in pools_to_load]
    current_services = [p.service_ for p in current_pools]

    for service in services_to_load:
        if service not in current_services:
            client.add_service(service.vip(),
                               service.port(),
                               protocol=service.proto_num(),
                               sched_name=service.sched())

    for service in current_services:
        if service not in services_to_load:
            client.del_service(service.vip(),
                               service.port(),
                               protocol=service.proto_num())

    for pool in pools_to_load:
        current_dests = [p.dests_ for p in current_pools if p.service_ == pool.service_]
        for dest in pool.dests_:
            if dest not in current_dests:
                client.add_dest(pool.service_.vip(),
                                pool.service_.port(),
                                protocol=pool.service_.proto_num(),
                                rip=dest.ip(),
                                weight=dest.weight(),
                                method=dest.fwd_method())
        for dest in current_dests:
            if dest not in pool.dests_:
                client.del_dest(pool.service_.vip,
                                pool.service_.port,
                                pool.service_.proto_num(),
                                dest.ip())


client = IpvsClient()
signal.signal(signal.SIGUSR1, reload_ipvs)
while True:
    print('Waiting for SIGUSR1 to reload ipvs config')
    signal.sigwait([signal.SIGUSR1])
