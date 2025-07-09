# list of commands for local develepment
default:
  just --list

# up docker
up:
  docker-compose up

# up docker in a background
up-d:
  docker-compose up -d

# build docker images
build:
  docker-compose --build

# build and run docker images
run:
  docker-compose up --build

# build and run docker images in a background
run-d:
  docker-compose up -d --build

# show logs of all services or of specific service
logs *args:
  docker-compose logs {{args}} -f

# stop docker porccess
down:
  docker-compose down

# stop docker porccess and rm voluems
down-v:
  docker-compose down -v

# docker ps
ps:
  docker ps

# run some command in fast api
exec *args:
  docker-compose exec estate_bot {{args}}

# run shell in fast api
shell:
  docker-compose exec -it estate_bot /bin/sh

# run make migrations, `args` - is a text of revision
mm *args:
  docker-compose exec estate_bot uv run alembic revision --autogenerate -m "{{args}}"

# run migrate (applies migrations)
migrate:
  docker-compose exec estate_bot uv run alembic upgrade head

# run current (chec if migrations applyed)
acurrent:
  docker-compose exec estate_bot alembic current

# downgrade migrations to `args` version, use args='head' to downgrade to prev version
downgrade *args:
  docker-compose exec estate_bot alembic downgrade {{args}}
