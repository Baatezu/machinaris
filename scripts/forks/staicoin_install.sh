#!/bin/env bash
#
# Installs Staicoin as per https://github.com/STATION-I/staicoin-blockchain
#

STAICOIN_BRANCH=$1
# On 2022-01-12
HASH=c72ec1bec8274d9e391fd31607511c7f1ad7c4fd

if [ -z ${STAICOIN_BRANCH} ]; then
	echo 'Skipping Staicoin install as not requested.'
else
	rm -rf /root/.cache
	git clone --branch ${STAICOIN_BRANCH} --single-branch https://github.com/STATION-I/staicoin-blockchain.git /staicoin-blockchain
	cd /staicoin-blockchain
	git submodule update --init mozilla-ca
	chmod +x install.sh
	/usr/bin/sh ./install.sh

	if [ ! -d /chia-blockchain/venv ]; then
		cd /
		rmdir /chia-blockchain
		ln -s /staicoin-blockchain /chia-blockchain
		ln -s /staicoin-blockchain/venv/bin/staicoin /chia-blockchain/venv/bin/chia
	fi
fi
