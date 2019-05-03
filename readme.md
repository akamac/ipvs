### Docker image to reload IPVS configuration from file
Send `SIGHUP` to reload IPVS config from `/ipvs.json` formatted for [facebook/gnlpy](https://github.com/facebook/gnlpy)'s `ipvs.Pool.load_pools_from_json_list()`.

- load `ip_vs` module on the host first with `modprobe ip_vs`
- run with `--cap-add NET_ADMIN`

### Run unit tests

```bash
docker build -t intermedia/ipvs . && docker build -t ipvs:pytest tests
docker run --cap-add=NET_ADMIN --network=host ipvs:pytest
# remote interactive debug with pyvdev 
docker run --rm --cap-add=NET_ADMIN --network=host -e PYDEV_IP=10.9.3.185 -e PYDEV_PORT=4444 ipvs:pytest
```