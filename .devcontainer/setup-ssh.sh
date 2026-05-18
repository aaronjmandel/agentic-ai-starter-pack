#!/bin/bash
# Restore SSH credentials from environment for GitHub access.
# Requires SSH_PRIVATE_KEY to be set as an Ona environment secret.

set -e

if [ -z "$SSH_PRIVATE_KEY" ]; then
    echo "SSH_PRIVATE_KEY not set — skipping SSH setup"
    exit 0
fi

mkdir -p ~/.ssh
chmod 700 ~/.ssh

echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519

# Derive public key from private key
ssh-keygen -y -f ~/.ssh/id_ed25519 > ~/.ssh/id_ed25519.pub 2>/dev/null

# GitHub SSH over port 443 (port 22 is often blocked in container environments)
cat > ~/.ssh/config <<EOF
Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/id_ed25519
EOF
chmod 600 ~/.ssh/config

# Add GitHub host key
ssh-keyscan -p 443 ssh.github.com >> ~/.ssh/known_hosts 2>/dev/null

echo "SSH configured for GitHub"
