#!/bin/env bash
#
# Initialize Chia service, depending on mode of system requested
#


cd /ext9-blockchain

. ./activate

mkdir -p /root/.chia/ext9/log
chia init >> /root/.chia/ext9/log/init.log 2>&1 

if [[ ! -z "${blockchain_skip_download}" ]] && [[ "${mode}" == 'fullnode' ]] && [[! -f /root/.chia/ext9/db/blockchain_v1_ext9.sqlite ]]; then
  echo "Downloading N-Chain blockchain DB on first launch..."
  mkdir -p /root/.chia/ext9/db/ && cd /root/.chia/ext9/db/
  # Mega links for N-Chain blockchain DB from: https://chiaforksblockchain.com/
  mega-get https://mega.nz/folder/OEwFASDT#grirFveyT3kNRw7ZWkw56A/file/aFZUVRCK
  mega-get https://mega.nz/folder/OEwFASDT#grirFveyT3kNRw7ZWkw56A/file/aQ4kXQxS
fi

echo 'Configuring NChain...'
if [ -f /root/.chia/ext9/config/config.yaml ]; then
  sed -i 's/log_stdout: true/log_stdout: false/g' /root/.chia/ext9/config/config.yaml
  sed -i 's/log_level: WARNING/log_level: INFO/g' /root/.chia/ext9/config/config.yaml
  sed -i 's/localhost/127.0.0.1/g' /root/.chia/ext9/config/config.yaml
fi

# Loop over provided list of key paths
for k in ${keys//:/ }; do
  if [ -f ${k} ]; then
    echo "Adding key at path: ${k}"
    chia keys add -f ${k} > /dev/null
  else
    echo "Skipping 'chia keys add' as no file found at: ${k}"
  fi
done

# Loop over provided list of completed plot directories
for p in ${plots_dir//:/ }; do
    chia plots add -d ${p}
done

chmod 755 -R /root/.chia/ext9/config/ssl/ &> /dev/null
chia init --fix-ssl-permissions > /dev/null 

# Start services based on mode selected. Default is 'fullnode'
if [[ ${mode} == 'fullnode' ]]; then
  if [ ! -f ~/.chia/ext9/config/ssl/wallet/public_wallet.key ]; then
    echo "No wallet key found, so not starting farming services.  Please add your Chia mnemonic.txt to the ~/.machinaris/ folder and restart."
    exit 1
  else
    chia start farmer
  fi
elif [[ ${mode} =~ ^farmer.* ]]; then
  if [ ! -f ~/.chia/ext9/config/ssl/wallet/public_wallet.key ]; then
    echo "No wallet key found, so not starting farming services.  Please add your Chia mnemonic.txt to the ~/.machinaris/ folder and restart."
  else
    chia start farmer-only
  fi
elif [[ ${mode} =~ ^harvester.* ]]; then
  if [[ -z ${farmer_address} || -z ${farmer_port} ]]; then
    echo "A farmer peer address and port are required."
    exit
  else
    if [ ! -f /root/.chia/farmer_ca/chia_ca.crt ]; then
      mkdir -p /root/.chia/farmer_ca
      response=$(curl --write-out '%{http_code}' --silent http://${controller_host}:8929/certificates/?type=nchain --output /tmp/certs.zip)
      if [ $response == '200' ]; then
        unzip /tmp/certs.zip -d /root/.chia/farmer_ca
      else
        echo "Certificates response of ${response} from http://${controller_host}:8929/certificates/?type=nchain.  Try clicking 'New Worker' button on 'Workers' page first."
      fi
      rm -f /tmp/certs.zip 
    fi
    if [ -f /root/.chia/farmer_ca/chia_ca.crt ]; then
      chia init -c /root/.chia/farmer_ca 2>&1 > /root/.chia/ext9/log/init.log
      chmod 755 -R /root/.chia/ext9/config/ssl/ &> /dev/null
      chia init --fix-ssl-permissions > /dev/null 
    else
      echo "Did not find your farmer's certificates within /root/.chia/farmer_ca."
      echo "See: https://github.com/guydavis/machinaris/wiki/Workers#harvester"
    fi
    echo "Configuring farmer peer at ${farmer_address}:${farmer_port}"
    chia configure --set-farmer-peer ${farmer_address}:${farmer_port}
    chia configure --enable-upnp false
    chia start harvester -r
  fi
elif [[ ${mode} == 'plotter' ]]; then
    echo "Starting in Plotter-only mode.  Run Plotman from either CLI or WebUI."
fi
