# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help:
# help: fileserver Makefile help
# help:

SHELL := /bin/bash
UNAME := $(shell uname)

.PHONY: help
# help: help				- Please use "make <target>" where <target> is one of
help:
	@grep "^# help\:" Makefile | sed 's/\# help\: //' | sed 's/\# help\://'

.PHONY: e
# help: e				- produce .env
e:
	@containers/menv.sh

.PHONY: sh
# help: sh				- interactive shell
sh:
	@docker exec -it cf_file_hold ./runner.sh shell

.PHONY: ba
# help: ba				- build application
ba:
	@COMPOSE_BAKE=true BUILDKIT_PROGRESS=plain docker compose -f docker-compose.yml up --build -d

.PHONY: ai
# help: ai				- autogenerate files e.g. make ai i=initial_migration, make ai i='Value point'
ai:
	@docker exec -i cf_file_hold alembic revision --autogenerate -m "$(i)"

.PHONY: uh
# help: uh				- alembic upgrade head
uh:
	@docker exec -i cf_file_hold alembic upgrade head

.PHONY: uhs
# help: uhs				- show sql for alembic upgrade head
uhs:
	@docker exec -i cf_file_hold alembic upgrade head --sql

.PHONY: ac
# help: ac				- alembic current
ac:
	@docker exec -i cf_file_hold alembic current

.PHONY: ah
# help: ah				- alembic history
ah:
	@docker exec -i cf_file_hold alembic history

.PHONY: n2x
# help: n2x				- talk to nginx e.g. make n2x c=restart, make nx c=status
n2x:
	@docker exec -i cf_file_server service nginx $(c) || printf "\n"

.PHONY: ex
# help: ex				- show examples of how to use make up ...
ex:
	@echo "make up t='username secret_password'"
	@echo "make up t='username secret_password --update-password new_password'"
	@echo "make up t='username secret_password --enabled False'"
	@echo "make up t='username secret_password --update-password new_password --enabled True'"

.PHONY: up
# help: up				- add username and password: type `make ex` for examples
up:
	@docker exec -it cf_file_hold python3 add_users.py $(t)

.PHONY: mv
# help: mv				- move to server
mv:
	@ssh -i ~/.ssh/iam_server iam@server "rm -f ~/devcode/fileserver/containers/proxy/migrations/versions/*.py"
	@rsync -av -e "ssh -i ~/.ssh/iam_server" --exclude='__pycache__' --exclude='if_file_hold.tar.gpg' \
	--exclude='.git' --exclude='.idea' --exclude='.env' --exclude='.gitignore' \
	--exclude='covert.py' --exclude='crashcourse.mp4' --exclude='inject.gdb' \
	--exclude='inject.sh' --exclude='README.md' --exclude='oneoff.sh' \
	~/devcode/pitch-cardinal-coding/fileserver/ \
	iam@server:~/devcode/fileserver

.PHONY: ta
# help: ta				- tar & encrypt an image
ta:
	@rm -f *.tar *gpg
	@docker save -o if_file_hold.tar fileserver-if_file_hold:latest
	@gpg --symmetric --cipher-algo AES256 --batch --yes if_file_hold.tar
	@rm -f *.tar

.PHONY: et
# help: et				- extract fileserver-if_file_hold
et:
	@echo "passw0rd" | gpg --batch --yes --pinentry-mode loopback --passphrase-fd 0 \
	    --output if_file_hold.tar --decrypt if_file_hold.tar.gpg
	@docker load -i if_file_hold.tar
	@rm -f if_file_hold.tar

.PHONY: nx
# help: nx				- extract nginx
nx:
	@echo "passw0rd" | gpg --batch --yes --pinentry-mode loopback --passphrase-fd 0 \
	    --output piccl_nginx.tar --decrypt piccl_nginx.tar.gpg
	@docker load -i piccl_nginx.tar
	@rm -f piccl_nginx.tar
