### Docker image to reload IPVS configuration from file
Send `SIGUSR1` to reload IPVS config from `/ipvs.json` formatted for [facebook/gnlpy](https://github.com/facebook/gnlpy)'s `ipvs.Pool.load_pools_from_json_list()`.

- load `ip_vs` module on the host first with `modprobe ip_vs`
- run with `--cap-add NET_ADMIN`.
