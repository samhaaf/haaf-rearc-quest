# Haaf-Rearc-Quest

This repo solves the Rearc Data Quest: https://github.com/rearc-data/quest

You're going to want to do this in an Amazon Linux 2 environment (numpy -> lambda is easier). I use Cloud9.

To install deps and requirements:

```
$ git clone https://github.com/samhaaf/haaf-rearc-quest.git
$ cd ./haaf-rearc-quest
$ make install
```

To test individual modules locally:

```
$ make test-csvs
$ make test-api
$ make test-scrape
$ make test-report
```

To deploy the whole thing to aws:

```
$ make apply
```

and to tear it down:

```
$ make clean
```
