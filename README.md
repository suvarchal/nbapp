## nbapp -- Yet another [Jupyter][jupyter] notebook server for custom [REST][REST] endpoints.

This _framework_ uses dynamic reverse proxy (using _[Traefik][traefik]_) to expose containerized [Jupyter][jupyter] notebook servers in response to custom [REST][REST] endpoints. This helps to build [Binder][binder]-like abilities for a custom notebook repository or [REST][REST] endpoints. This can lead to simplified deployments then using [Jupyter Hub][jupyterhub] in certain use cases.


As an example: nbapp integrated with a scientific content management system, [RAMADDA](https://www.geodesystems.com), lets its users interact with the published [Jupyter][jupyter] notebooks with a click:
![preview_nbapp](https://github.com/suvarchal/nbapp/blob/master/docs/preview_nbapp.gif "nbapp preview with RAMADDA").

### Framework:
A python-flask app (_[nbapp](https://github.com/suvarchal/nbapp/tree/master/nbapp)_), defines routes to spawn dockerized Jupyter notebook servers with labels that lets [traefik][traefik] to reverse proxy dynamically to the notebook server. 

Although traefik and flask can run natively on linux servers, entire deployment is packaged in containers for ease of deployment using [docker-compose](https://docs.docker.com/compose/). Read section below for deployment.
    
### Deployment:
Directory [deploy](https://github.com/suvarchal/nbapp/tree/master/deploy) contains example deployments.

* Directory [traefik](https://github.com/suvarchal/nbapp/tree/master/deploy/traefik) contains docker compose files (with commentary for modifications) for some use cases. In simplest case it amounts to `docker-compose up -d` for deployment. 
 

* For Virtual Machine based deployments, a Vagrantfile sample is provided in [deploy](https://github.com/suvarchal/nbapp/tree/master/deploy). This is based on virtual box as a provider but it can be adapted to other [Vagrant][vagrant] providers.

>Please raise an [issue](https://github.com/suvarchal/nbapp/issues) about your deployment needs. We might be able to provide support.


If nginx or apache are used as webserver, sample configurations are provided (with SSL termination) in [deploy][deploy] directory using _mylabserver.com_ as an example host.  



[jupyter]: https://jupyter.org/
[jupyterhub]: https://jupyter.org/hub
[REST]: https://en.wikipedia.org/wiki/Representational_state_transfer
[RAMADDA]: https://www.geodesystems.com
[binder]: https://binder.pangeo.io
[traefik]: https://traefik.io
[vagrant]: https://www.vagrantup.com/
[deploy]: https://github.com/suvarchal/nbapp/tree/master/deploy
