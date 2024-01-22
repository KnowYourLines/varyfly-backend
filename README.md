# Local development
Run this API with a local postgres db for data persistence. Then access from `http://localhost:8000` on a web browser. `docker-compose.yml` defines the local environment.
```
docker-compose up
```
Stop running containers and remove images to wipe the db before testing new API changes:
```
docker-compose down --rmi all
```
To run functional tests:
```
docker exec -it varyfly-backend-web-1 python manage.py test functional_tests
```
To run unit tests:
```
docker exec -it varyfly-backend-web-1 python manage.py test api
```
To open a terminal on the running app:
```
docker exec -it varyfly-backend-web-1 bash
```
# Deploying on Render
Go to [Render Blueprints](https://dashboard.render.com/blueprints). Connect a Github account with access to this repo and select this repo when creating a new Blueprint instance.