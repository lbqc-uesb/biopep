# run options
cutoff=""
task=""
query=""
receptor=""
site=""

.PHONY:install
install:
	@./bin/install

.PHONY:run
run:
	@./bin/run -c $(cutoff) -t $(task) -q $(query) -r $(receptor) -s $(site)
